import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


class Database:
    def __init__(self):
        self.client = get_client()

    # ---------- users ----------

    def upsert_user(self, discord_id: str, username: str):
        self.client.table("users").upsert(
            {"discord_id": discord_id, "username": username},
            on_conflict="discord_id",
            ignore_duplicates=True,
        ).execute()

    def add_score(self, discord_id: str, score: int, won: bool):
        user = (
            self.client.table("users")
            .select("total_score, games_played, games_won, coins_balance")
            .eq("discord_id", discord_id)
            .single()
            .execute()
            .data
        )
        self.client.table("users").update({
            "total_score": user["total_score"] + score,
            "games_played": user["games_played"] + 1,
            "games_won": user["games_won"] + (1 if won else 0),
            "coins_balance": (user.get("coins_balance") or 0) + score,
        }).eq("discord_id", discord_id).execute()

    def get_ranking(self, limit: int = 10) -> list:
        result = (
            self.client.table("users")
            .select("username, total_score, games_played, games_won")
            .order("total_score", desc=True)
            .limit(limit)
            .execute()
        )
        return result.data

    def get_collection_ranking(self, banner_card_ids: list, limit: int = 10) -> list:
        from collections import defaultdict
        result = (
            self.client.table("collection")
            .select("discord_id, card_id")
            .in_("card_id", banner_card_ids)
            .execute()
        )
        counts = defaultdict(set)
        for row in result.data:
            counts[row["discord_id"]].add(row["card_id"])
        if not counts:
            return []
        users = (
            self.client.table("users")
            .select("discord_id, username")
            .in_("discord_id", list(counts.keys()))
            .execute()
        ).data
        username_map = {u["discord_id"]: u["username"] for u in users}
        ranking = [
            {"username": username_map.get(did, "unknown"), "unique_count": len(cards)}
            for did, cards in counts.items()
        ]
        return sorted(ranking, key=lambda x: x["unique_count"], reverse=True)[:limit]

    # ---------- games ----------

    def get_active_game(self, discord_id: str) -> dict | None:
        result = (
            self.client.table("games")
            .select("*")
            .eq("discord_id", discord_id)
            .eq("status", "active")
            .execute()
        )
        return result.data[0] if result.data else None

    def create_game(self, discord_id: str, card_name: str, card_data: dict, game_mode: str = "hints") -> dict:
        result = (
            self.client.table("games")
            .insert({
                "discord_id": discord_id,
                "card_name": card_name,
                "card_data": card_data,
                "hints_revealed": 0,
                "attempts_on_hint": 0,
                "game_mode": game_mode,
                "zoom_level": 0,
                "status": "active",
            })
            .execute()
        )
        return result.data[0]

    def advance_zoom(self, game_id: str, zoom_level: int):
        self.client.table("games").update(
            {"zoom_level": zoom_level, "attempts_on_hint": 0}
        ).eq("id", game_id).execute()

    def reveal_hint(self, game_id: str, hints_revealed: int):
        self.client.table("games").update(
            {"hints_revealed": hints_revealed, "attempts_on_hint": 0}
        ).eq("id", game_id).execute()

    def increment_attempt(self, game_id: str, current: int):
        self.client.table("games").update(
            {"attempts_on_hint": current + 1}
        ).eq("id", game_id).execute()

    def update_game_data(self, game_id: str, card_data: dict):
        self.client.table("games").update(
            {"card_data": card_data}
        ).eq("id", game_id).execute()

    def end_game(self, game_id: str, status: str):
        self.client.table("games").update(
            {"status": status}
        ).eq("id", game_id).execute()

    # ---------- gacha ----------

    def get_user(self, discord_id: str) -> dict | None:
        result = (
            self.client.table("users")
            .select("*")
            .eq("discord_id", discord_id)
            .execute()
        )
        return result.data[0] if result.data else None

    def spend_coins(self, discord_id: str, amount: int) -> bool:
        user = self.get_user(discord_id)
        if not user or (user.get("coins_balance") or 0) < amount:
            return False
        self.client.table("users").update(
            {"coins_balance": user["coins_balance"] - amount}
        ).eq("discord_id", discord_id).execute()
        return True

    def set_last_sobre(self, discord_id: str):
        from datetime import datetime, timezone
        self.client.table("users").update(
            {"last_sobre": datetime.now(timezone.utc).isoformat()}
        ).eq("discord_id", discord_id).execute()

    def add_to_collection(self, discord_id: str, cards: list[dict]):
        from collections import Counter
        pull_counts = Counter(c["card_id"] for c in cards)
        card_by_id = {c["card_id"]: c for c in cards}

        existing = (
            self.client.table("collection")
            .select("card_id, count")
            .eq("discord_id", discord_id)
            .in_("card_id", list(pull_counts.keys()))
            .execute()
        ).data
        existing_map = {row["card_id"]: row["count"] for row in existing}

        to_insert = []
        for card_id, qty in pull_counts.items():
            card = card_by_id[card_id]
            if card_id in existing_map:
                self.client.table("collection").update(
                    {"count": existing_map[card_id] + qty}
                ).eq("discord_id", discord_id).eq("card_id", card_id).execute()
            else:
                to_insert.append({
                    "discord_id": discord_id,
                    "card_id": card_id,
                    "card_name": card["name"],
                    "rarity": card["rarity"],
                    "image_url": card["image_url"],
                    "count": qty,
                })
        if to_insert:
            self.client.table("collection").insert(to_insert).execute()

    def sell_duplicates(self, discord_id: str, rarity_values: dict) -> int:
        cards = self.get_collection(discord_id)
        duplicates = [c for c in cards if c["count"] > 1]
        if not duplicates:
            return 0

        total_coins = 0
        for card in duplicates:
            extras = card["count"] - 1
            total_coins += extras * rarity_values.get(card["rarity"], 1)
            self.client.table("collection").update({"count": 1}).eq("discord_id", discord_id).eq("card_id", card["card_id"]).execute()

        user = self.get_user(discord_id)
        self.client.table("users").update({
            "coins_balance": (user.get("coins_balance") or 0) + total_coins
        }).eq("discord_id", discord_id).execute()
        return total_coins

    def get_collection(self, discord_id: str) -> list[dict]:
        result = (
            self.client.table("collection")
            .select("card_id, card_name, rarity, image_url, count")
            .eq("discord_id", discord_id)
            .execute()
        )
        return result.data

    # ---------- channel locks ----------

    def get_command_channel(self, guild_id: str, command: str) -> str | None:
        result = (
            self.client.table("channel_locks")
            .select("channel_id")
            .eq("guild_id", guild_id)
            .eq("command", command)
            .execute()
        )
        return result.data[0]["channel_id"] if result.data else None

    def get_all_channel_locks(self, guild_id: str) -> list[dict]:
        result = (
            self.client.table("channel_locks")
            .select("command, channel_id")
            .eq("guild_id", guild_id)
            .execute()
        )
        return result.data

    def set_command_channel(self, guild_id: str, command: str, channel_id: str):
        self.client.table("channel_locks").upsert(
            {"guild_id": guild_id, "command": command, "channel_id": channel_id},
            on_conflict="guild_id,command",
        ).execute()

    def remove_command_channel(self, guild_id: str, command: str):
        self.client.table("channel_locks").delete().eq("guild_id", guild_id).eq("command", command).execute()
