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
            .select("total_score, games_played, games_won")
            .eq("discord_id", discord_id)
            .single()
            .execute()
            .data
        )
        self.client.table("users").update({
            "total_score": user["total_score"] + score,
            "games_played": user["games_played"] + 1,
            "games_won": user["games_won"] + (1 if won else 0),
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
