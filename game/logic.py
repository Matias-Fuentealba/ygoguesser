import re
import io
from datetime import datetime, timezone, timedelta
from db.database import Database
from game.yugioh import fetch_random_card, build_hints, fetch_card_for_price
from game.zoom import get_zoomed_image, zoom_score, MAX_ZOOM_LEVEL
from game.gacha import (
    pull_free, pull_x10,
    PERMANENT_BANNER, ROTATING_BANNER, X10_COST,
    RARITY_EMOJIS, RARITY_COLORS, COOLDOWN_HOURS,
)
from game.strings import t

ALL_BANNERS = {"permanent": PERMANENT_BANNER, "rotating": ROTATING_BANNER}

RARITY_SELL_VALUES = {"secret": 50, "ultra": 20, "super": 10, "rare": 5, "common": 1}

MAX_HINTS = 5


def calculate_score(hints_revealed: int) -> int:
    return max(0, 100 - hints_revealed * 20)


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.strip().lower())


def _build_price_message(champion: dict, challenger: dict, score: int, prefix: str = "", lang: str = "en") -> dict:
    return {
        "content": f"{prefix}{t('price_question', lang, score=score)}",
        "embeds": [
            {
                "title": f"{t('btn_card1', lang)}: {champion['name']}",
                "description": f"📦 {champion['set_name']}\n🏷️ {champion['set_rarity']}",
                "image": {"url": champion["image_url"]},
                "color": 0xF1C40F,
            },
            {
                "title": f"{t('btn_card2', lang)}: {challenger['name']}",
                "description": f"📦 {challenger['set_name']}\n🏷️ {challenger['set_rarity']}",
                "image": {"url": challenger["image_url"]},
                "color": 0xF1C40F,
            },
        ],
        "components": [
            {
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": t("btn_card1", lang), "custom_id": "price_1"},
                    {"type": 2, "style": 1, "label": t("btn_card2", lang), "custom_id": "price_2"},
                ],
            }
        ],
    }


def card_embed(content: str, card: dict, color: int) -> dict:
    embed = {"description": content, "color": color}
    if card.get("image_url"):
        embed["image"] = {"url": card["image_url"]}
    return {"embeds": [embed]}


class GameManager:
    def __init__(self, db: Database):
        self.db = db

    async def start_game(self, user_id: str, username: str, lang: str = "en") -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            mode = existing.get("game_mode", "hints")
            key = {
                "hints": "game_already_active_hints",
                "zoom": "game_already_active_zoom",
                "price": "game_already_active_price",
            }.get(mode, "game_already_active_other")
            return {"content": t(key, lang)}

        return {
            "content": t("welcome_body", lang),
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": t("btn_hints", lang), "custom_id": "mode_hints"},
                    {"type": 2, "style": 2, "label": t("btn_zoom", lang), "custom_id": "mode_zoom"},
                    {"type": 2, "style": 4, "label": t("btn_price", lang), "custom_id": "mode_price"},
                ],
            }],
        }

    async def start_hints_game(self, user_id: str, username: str, lang: str = "en") -> str:
        card = fetch_random_card()
        if not card:
            return t("cannot_fetch_card", lang)

        self.db.upsert_user(user_id, username)
        self.db.create_game(user_id, card["name"], card)

        hints = build_hints(card, lang)
        return t("hints_started", lang, hint=hints[0], max_hints=MAX_HINTS)

    async def get_hint(self, user_id: str, lang: str = "en") -> str:
        game = self.db.get_active_game(user_id)
        if not game:
            return t("no_active_game", lang)

        if game.get("game_mode") == "zoom":
            return t("hint_not_available_zoom", lang)

        hints_revealed = game["hints_revealed"]
        card = game["card_data"]
        hints = build_hints(card, lang)

        next_index = hints_revealed + 1
        if next_index >= MAX_HINTS:
            return t("hint_all_revealed", lang, max_hints=MAX_HINTS)

        self.db.reveal_hint(game["id"], next_index)
        score_if_correct = calculate_score(next_index)
        return t("hint_text", lang, n=next_index + 1, max_hints=MAX_HINTS, hint=hints[next_index], score=score_if_correct)

    async def guess(self, user_id: str, username: str, guess: str, lang: str = "en"):
        game = self.db.get_active_game(user_id)
        if not game:
            return t("no_active_game", lang)
        if game.get("game_mode") == "zoom":
            return await self.guess_zoom(user_id, username, guess, lang)
        return await self.make_guess(user_id, username, guess, lang)

    async def make_guess(self, user_id: str, username: str, guess: str, lang: str = "en") -> str:
        game = self.db.get_active_game(user_id)
        if not game:
            return t("no_active_game", lang)

        card = game["card_data"]
        hints_revealed = game["hints_revealed"]
        attempts = game["attempts_on_hint"]

        if normalize_name(guess) == normalize_name(card["name"]):
            score = calculate_score(hints_revealed)
            self.db.end_game(game["id"], "won")
            self.db.add_score(user_id, score, won=True)
            return card_embed(
                t("correct_hints", lang, name=card["name"], score=score, hints=hints_revealed, max_hints=MAX_HINTS),
                card, 0x2ECC71
            )

        new_attempts = attempts + 1
        self.db.increment_attempt(game["id"], attempts)

        if new_attempts < 3:
            remaining = 3 - new_attempts
            s = "" if remaining == 1 else "s"
            return t("wrong_attempts_left", lang, remaining=remaining, s=s)

        next_index = hints_revealed + 1
        if next_index >= MAX_HINTS:
            self.db.end_game(game["id"], "lost")
            self.db.add_score(user_id, 0, won=False)
            return card_embed(t("wrong_all_attempts", lang, name=card["name"]), card, 0xE74C3C)

        hints = build_hints(card, lang)
        self.db.reveal_hint(game["id"], next_index)
        score_if_correct = calculate_score(next_index)
        return t("wrong_auto_hint", lang, n=next_index + 1, max_hints=MAX_HINTS, hint=hints[next_index], score=score_if_correct)

    async def surrender(self, user_id: str, lang: str = "en") -> str | dict:
        game = self.db.get_active_game(user_id)
        if not game:
            return t("no_active_game", lang)

        game_mode = game.get("game_mode", "hints")
        self.db.end_game(game["id"], "lost")

        if game_mode == "price":
            score = game["card_data"].get("score", 0)
            self.db.add_score(user_id, score, won=False, coins=score * 5)
            return t("surrender_price", lang, score=score, coins=score * 5)

        card = game["card_data"]
        self.db.add_score(user_id, 0, won=False)
        return card_embed(t("surrender_hints", lang, name=card["name"]), card, 0xE74C3C)

    async def start_zoom(self, user_id: str, username: str, lang: str = "en") -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            mode = existing.get("game_mode", "hints")
            cmd = "/guess" if mode != "zoom" else "/guess"
            return {"content": t("zoom_already_active", lang, cmd=cmd)}

        card = fetch_random_card()
        if not card:
            return {"content": t("cannot_fetch_card", lang)}

        self.db.upsert_user(user_id, username)
        self.db.create_game(user_id, card["name"], card, game_mode="zoom")

        img = get_zoomed_image(card["image_url"], 0)
        if not img:
            return {"content": t("cannot_process_image", lang)}

        score = zoom_score(0)
        return {
            "content": t("zoom_started", lang, max_levels=MAX_ZOOM_LEVEL + 1, score=score),
            "image": img,
        }

    async def guess_zoom(self, user_id: str, username: str, guess: str, lang: str = "en") -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "zoom":
            return {"content": t("no_active_game", lang)}

        card = game["card_data"]
        zoom_level = game["zoom_level"]
        hints_revealed = game["hints_revealed"]
        attempts = game["attempts_on_hint"]

        if normalize_name(guess) == normalize_name(card["name"]):
            score = max(0, zoom_score(zoom_level) - hints_revealed * 10)
            self.db.end_game(game["id"], "won")
            self.db.add_score(user_id, score, won=True)
            if hints_revealed:
                s = "" if hints_revealed == 1 else "s"
                hints_note = t("zoom_hints_note", lang, n=hints_revealed, s=s)
            else:
                hints_note = ""
            return {
                "content": t("zoom_correct", lang, name=card["name"], score=score, level=zoom_level + 1, max_levels=MAX_ZOOM_LEVEL + 1, hints_note=hints_note),
                "embed_image_url": card["image_url"],
                "embed_color": 0x2ECC71,
            }

        new_attempts = attempts + 1
        self.db.increment_attempt(game["id"], attempts)

        if new_attempts < 3:
            remaining = 3 - new_attempts
            s = "" if remaining == 1 else "s"
            return {"content": t("zoom_wrong_attempts_left", lang, remaining=remaining, s=s)}

        next_level = zoom_level + 1
        if next_level > MAX_ZOOM_LEVEL:
            self.db.end_game(game["id"], "lost")
            self.db.add_score(user_id, 0, won=False)
            return {
                "content": t("zoom_wrong_all_attempts", lang, name=card["name"]),
                "embed_image_url": card["image_url"],
                "embed_color": 0xE74C3C,
            }

        self.db.advance_zoom(game["id"], next_level)
        img = get_zoomed_image(card["image_url"], next_level)
        score = zoom_score(next_level)
        return {
            "content": t("zoom_wrong_auto_advance", lang, level=next_level + 1, max_levels=MAX_ZOOM_LEVEL + 1, score=score),
            "image": img,
        }

    async def next_zoom(self, user_id: str, lang: str = "en") -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "zoom":
            return {"content": t("zoom_no_game", lang)}

        zoom_level = game["zoom_level"]
        next_level = zoom_level + 1

        if next_level > MAX_ZOOM_LEVEL:
            return {"content": t("zoom_hint_max", lang, level=zoom_level + 1, max_levels=MAX_ZOOM_LEVEL + 1)}

        card = game["card_data"]
        self.db.advance_zoom(game["id"], next_level)
        img = get_zoomed_image(card["image_url"], next_level)
        score = zoom_score(next_level)
        return {
            "content": t("zoom_hint_next", lang, level=next_level + 1, max_levels=MAX_ZOOM_LEVEL + 1, score=score),
            "image": img,
        }

    async def start_price_game(self, user_id: str, username: str, lang: str = "en") -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            return {"content": t("game_already_active_other", lang)}

        champion = fetch_card_for_price()
        if not champion:
            return {"content": t("price_no_cards", lang)}
        challenger = fetch_card_for_price(exclude_names={champion["name"]})
        if not challenger:
            return {"content": t("price_no_cards", lang)}

        self.db.upsert_user(user_id, username)
        state = {"champion": champion, "challenger": challenger, "champion_wins": 0, "score": 0}
        self.db.create_game(user_id, champion["name"], state, game_mode="price")

        return _build_price_message(champion, challenger, score=0, lang=lang)

    async def choose_price(self, user_id: str, choice: int, lang: str = "en") -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "price":
            return {"content": t("price_no_game", lang)}

        state = game["card_data"]
        champion = state["champion"]
        challenger = state["challenger"]
        score = state["score"]
        champion_wins = state["champion_wins"]

        correct_choice = 1 if champion["price"] >= challenger["price"] else 2
        correct_card = champion if correct_choice == 1 else challenger
        wrong_card = challenger if correct_choice == 1 else champion

        if choice == correct_choice:
            score += 1
            winner = correct_card
            new_champion_wins = (champion_wins + 1) if winner["name"] == champion["name"] else 1

            if new_champion_wins >= 2:
                new_champion = fetch_card_for_price(exclude_names={winner["name"]})
                new_champion_wins = 0
            else:
                new_champion = winner

            if not new_champion:
                self.db.end_game(game["id"], "won")
                self.db.add_score(user_id, score, won=True, coins=score * 5)
                return {"content": t("price_win", lang, score=score, coins=score * 5)}

            new_challenger = fetch_card_for_price(exclude_names={new_champion["name"]})
            if not new_challenger:
                self.db.end_game(game["id"], "won")
                self.db.add_score(user_id, score, won=True, coins=score * 5)
                return {"content": t("price_win", lang, score=score, coins=score * 5)}

            state.update({"champion": new_champion, "challenger": new_challenger, "champion_wins": new_champion_wins, "score": score})
            self.db.update_game_data(game["id"], state)

            prefix = t("price_correct_prefix", lang, card=correct_card["name"], price=correct_card["price"], other=wrong_card["price"])
            return _build_price_message(new_champion, new_challenger, score, prefix=prefix, lang=lang)

        self.db.end_game(game["id"], "lost")
        self.db.add_score(user_id, score, won=False, coins=score * 5)
        return {
            "content": t("price_wrong", lang, card=correct_card["name"], price=correct_card["price"], other=wrong_card["price"], score=score, coins=score * 5),
            "embeds": [
                {"title": f"✅ {correct_card['name']} — ${correct_card['price']:.2f}", "image": {"url": correct_card["image_url"]}, "color": 0x2ECC71},
                {"title": f"❌ {wrong_card['name']} — ${wrong_card['price']:.2f}", "image": {"url": wrong_card["image_url"]}, "color": 0xE74C3C},
            ],
            "components": [],
        }

    def _x10_buttons(self, user_id: str = "", lang: str = "en") -> list:
        return [{
            "type": 1,
            "components": [
                {"type": 2, "style": 1, "label": t("btn_x10_perm", lang, cost=X10_COST), "custom_id": f"gacha_x10:{user_id}:permanent"},
                {"type": 2, "style": 2, "label": t("btn_x10_rot", lang, cost=X10_COST), "custom_id": f"gacha_x10:{user_id}:rotating"},
            ],
        }]

    def _cooldown_check(self, user: dict):
        last_raw = (user or {}).get("last_sobre")
        if not last_raw:
            return False, 0, 0
        last_dt = datetime.fromisoformat(last_raw)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        same_hour = (last_dt.year == now.year and last_dt.month == now.month
                     and last_dt.day == now.day and last_dt.hour == now.hour)
        if not same_hour:
            return False, 0, 0
        next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        time_left = next_hour - now
        return True, int(time_left.total_seconds() // 60), int(time_left.total_seconds() % 60)

    async def open_sobre(self, user_id: str, username: str, lang: str = "en") -> dict:
        self.db.upsert_user(user_id, username)
        user = self.db.get_user(user_id)
        coins = (user.get("coins_balance") or 0) if user else 0

        blocked, mins, secs = self._cooldown_check(user)
        if blocked:
            coins_hint = "" if coins > 0 else t("pack_cooldown_hint", lang)
            return {
                "content": t("pack_cooldown", lang, mins=mins, secs=secs, coins=coins) + coins_hint,
                "components": self._x10_buttons(user_id, lang),
            }

        return {
            "content": t("pack_available", lang, coins=coins),
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": t("btn_pack_perm", lang), "custom_id": f"sobre_banner:permanent:{user_id}"},
                    {"type": 2, "style": 2, "label": t("btn_pack_rot", lang), "custom_id": f"sobre_banner:rotating:{user_id}"},
                ],
            }],
        }

    async def open_sobre_banner(self, user_id: str, username: str, banner_key: str, lang: str = "en") -> dict:
        user = self.db.get_user(user_id)
        blocked, mins, secs = self._cooldown_check(user)
        if blocked:
            return {"content": t("pack_already_used", lang, mins=mins, secs=secs), "components": []}

        existing_ids = {str(c["card_id"]) for c in self.db.get_collection(user_id)}
        banner = ALL_BANNERS.get(banner_key, PERMANENT_BANNER)
        cards = pull_free(banner)
        self.db.add_to_collection(user_id, cards)
        self.db.set_last_sobre(user_id)
        new_ids = {str(c["card_id"]) for c in cards if str(c["card_id"]) not in existing_ids}
        return self._build_pull_response(cards, t("pack_opened", lang, banner=banner["name"]), user_id, banner_key, new_ids=new_ids, lang=lang)

    async def open_sobre_x10(self, user_id: str, banner_key: str = "permanent", lang: str = "en") -> dict:
        user = self.db.get_user(user_id)
        if not user:
            return {"content": t("pack_x10_no_user", lang)}

        coins = user.get("coins_balance") or 0
        if coins < X10_COST:
            return {"content": t("pack_x10_no_coins", lang, cost=X10_COST, coins=coins)}

        if not self.db.spend_coins(user_id, X10_COST):
            return {"content": t("pack_x10_insufficient", lang)}

        existing_ids = {str(c["card_id"]) for c in self.db.get_collection(user_id)}
        banner = ALL_BANNERS.get(banner_key, PERMANENT_BANNER)
        cards = pull_x10(banner)
        self.db.add_to_collection(user_id, cards)
        new_ids = {str(c["card_id"]) for c in cards if str(c["card_id"]) not in existing_ids}

        new_balance = coins - X10_COST
        result = self._build_pull_response(cards, t("pack_x10_opened", lang, banner=banner["name"]), user_id, banner_key, new_ids=new_ids, lang=lang)
        coins_note = f" · {t('pack_new_card_footer', lang)}" if new_ids else ""
        result["embeds"][0]["footer"] = {"text": t("pack_coins_remaining", lang, coins=new_balance) + coins_note}
        return result

    def _build_pull_response(self, cards: list[dict], header: str, user_id: str = "", banner_key: str = "permanent", new_ids: set = None, lang: str = "en") -> dict:
        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        cards_sorted = sorted(cards, key=lambda x: rarity_order.index(x["rarity"]))
        new_ids = new_ids or set()

        grouped: dict[str, list[str]] = {}
        for c in cards_sorted:
            star = " <:newicon:1506143726840578139>" if str(c["card_id"]) in new_ids else ""
            grouped.setdefault(c["rarity"], []).append(f"{c['name']}{star}")

        fields = []
        for r in rarity_order:
            if r not in grouped:
                continue
            fields.append({
                "name": f"{RARITY_EMOJIS[r]} {rarity_names[r]}",
                "value": "\n".join(grouped[r]),
                "inline": False,
            })

        best = cards_sorted[0]
        return {
            "embeds": [{
                "title": header.strip(),
                "thumbnail": {"url": best["image_url"]},
                "fields": fields,
                "color": RARITY_COLORS[best["rarity"]],
                "footer": {"text": t("pack_new_card_footer", lang)} if new_ids else None,
            }],
            "components": self._x10_buttons(user_id, lang),
        }

    async def toggle_protect_card(self, user_id: str, card_name: str, lang: str = "en") -> dict:
        result = self.db.toggle_protect_card(user_id, card_name)
        if not result:
            return {"content": t("protect_not_found", lang, name=card_name)}
        key = "protect_on" if result["protected"] else "protect_off"
        return {"content": t(key, lang, name=result["card_name"])}

    async def show_sell_duplicates(self, user_id: str, lang: str = "en") -> dict:
        cards = self.db.get_collection(user_id)
        duplicates = [c for c in cards if c["count"] > 1 and not c.get("protected")]
        if not duplicates:
            protected_dups = [c for c in cards if c["count"] > 1 and c.get("protected")]
            if protected_dups:
                return {"content": t("sell_no_duplicates_protected", lang, count=len(protected_dups))}
            return {"content": t("sell_no_duplicates", lang)}

        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        duplicates_sorted = sorted(duplicates, key=lambda x: (rarity_order.index(x["rarity"]), x["card_name"]))

        total_extras = sum(c["count"] - 1 for c in duplicates_sorted)
        total_coins = sum((c["count"] - 1) * RARITY_SELL_VALUES[c["rarity"]] for c in duplicates_sorted)

        grouped: dict[str, list[str]] = {r: [] for r in rarity_order}
        for c in duplicates_sorted:
            extras = c["count"] - 1
            coins = extras * RARITY_SELL_VALUES[c["rarity"]]
            grouped[c["rarity"]].append(f"{c['card_name']} ×{extras} → {coins} 💰")

        fields = []
        for r in rarity_order:
            if not grouped[r]:
                continue
            lines = grouped[r]
            value = "\n".join(lines)
            if len(value) > 1024:
                kept, total_r = [], len(lines)
                for line in lines:
                    if len("\n".join(kept + [line])) > 980:
                        break
                    kept.append(line)
                value = "\n".join(kept) + f"\n*...and {total_r - len(kept)} more*" if lang == "en" else "\n".join(kept) + f"\n*...y {total_r - len(kept)} más*"
            fields.append({
                "name": f"{RARITY_EMOJIS[r]} {rarity_names[r]} ({RARITY_SELL_VALUES[r]} 💰/copy)" if lang == "en" else f"{RARITY_EMOJIS[r]} {rarity_names[r]} ({RARITY_SELL_VALUES[r]} 💰/copia)",
                "value": value,
                "inline": False,
            })

        return {
            "embeds": [{
                "title": t("sell_title", lang, extras=total_extras, coins=total_coins),
                "fields": fields,
                "color": 0xE74C3C,
            }],
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 4, "label": t("sell_confirm_btn", lang, coins=total_coins), "custom_id": f"vender_confirmar:{user_id}"},
                    {"type": 2, "style": 2, "label": t("sell_cancel_btn", lang), "custom_id": f"vender_cancelar:{user_id}"},
                ],
            }],
        }

    async def confirm_sell_duplicates(self, user_id: str, lang: str = "en") -> dict:
        coins_earned = self.db.sell_duplicates(user_id, RARITY_SELL_VALUES)
        if coins_earned == 0:
            return {"embeds": [{"title": t("sell_nothing", lang), "color": 0x9D9D9D}], "components": []}
        user = self.db.get_user(user_id)
        new_balance = user.get("coins_balance") or 0
        return {
            "embeds": [{
                "title": t("sell_done_title", lang),
                "description": t("sell_done_desc", lang, coins=coins_earned, balance=new_balance),
                "color": 0x2ECC71,
            }],
            "components": [],
        }

    async def get_help(self, lang: str = "en") -> dict:
        return {
            "embeds": [{
                "title": t("help_title", lang),
                "color": 0x3498DB,
                "fields": [
                    {"name": t("help_game_title", lang), "value": t("help_game_value", lang), "inline": False},
                    {"name": t("help_gacha_title", lang), "value": t("help_gacha_value", lang), "inline": False},
                    {"name": t("help_coins_title", lang), "value": t("help_coins_value", lang), "inline": False},
                ],
                "footer": {"text": t("help_footer", lang)},
            }]
        }

    async def get_gacha_info(self, user_id: str, lang: str = "en") -> dict:
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}

        owned_ids = {str(c["card_id"]) for c in self.db.get_collection(user_id)}

        def pool_line(banner: dict) -> str:
            return "  ".join(
                f"{RARITY_EMOJIS[r]} {rarity_names[r]}: {len(banner.get(r, []))}"
                for r in ("secret", "ultra", "super", "rare", "common")
            )

        def missing_summary(banner: dict) -> str:
            total = sum(len(banner.get(r, [])) for r in ("secret", "ultra", "super", "rare", "common"))
            missing = sum(1 for r in ("secret", "ultra", "super", "rare", "common") for c in banner.get(r, []) if str(c["id"]) not in owned_ids)
            if missing == 0:
                return t("gacha_complete", lang)
            return t("gacha_missing", lang, missing=missing, total=total)

        embeds = []
        for label_key, banner in [("gacha_banner_rotating", ROTATING_BANNER), ("gacha_banner_permanent", PERMANENT_BANNER)]:
            embed = {
                "title": f"🎴 {t(label_key, lang)}: {banner['name']}",
                "description": t("gacha_probs", lang,
                    secret=RARITY_EMOJIS["secret"], ultra=RARITY_EMOJIS["ultra"],
                    super=RARITY_EMOJIS["super"], rare=RARITY_EMOJIS["rare"],
                    common=RARITY_EMOJIS["common"], pool_line=pool_line(banner),
                    missing_summary=missing_summary(banner)),
                "color": 0xFFD700,
            }
            if banner.get("image_url"):
                embed["image"] = {"url": banner["image_url"]}
            embeds.append(embed)

        embeds[0]["description"] = t("gacha_how_it_works", lang, cost=X10_COST) + embeds[0]["description"]

        return {
            "embeds": embeds,
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 2, "label": t("btn_missing_rot", lang), "custom_id": "faltan:rotating"},
                    {"type": 2, "style": 2, "label": t("btn_missing_perm", lang), "custom_id": "faltan:permanent"},
                ],
            }],
        }

    async def get_missing_cards(self, user_id: str, banner_key: str, page: int = 0, lang: str = "en") -> dict:
        banner = ALL_BANNERS.get(banner_key, PERMANENT_BANNER)
        owned_ids = {str(c["card_id"]) for c in self.db.get_collection(user_id)}

        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}

        missing = [
            {"rarity": r, "name": c["name"]}
            for r in rarity_order
            for c in banner.get(r, [])
            if str(c["id"]) not in owned_ids
        ]

        if not missing:
            return {"content": t("missing_complete", lang, banner=banner["name"])}

        page_size = 15
        total_pages = max(1, (len(missing) + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        page_cards = missing[page * page_size:(page + 1) * page_size]

        grouped: dict[str, list[str]] = {}
        for c in page_cards:
            grouped.setdefault(c["rarity"], []).append(c["name"])

        fields = [
            {"name": f"{RARITY_EMOJIS[r]} {rarity_names[r]}", "value": "\n".join(grouped[r]), "inline": False}
            for r in rarity_order if r in grouped
        ]

        embed = {
            "title": t("missing_title", lang, banner=banner["name"], count=len(missing)),
            "fields": fields,
            "color": 0x95A5A6,
            "footer": {"text": f"Page {page + 1} / {total_pages}" if lang == "en" else f"Página {page + 1} / {total_pages}"},
        }

        buttons = []
        if page > 0:
            buttons.append({"type": 2, "style": 2, "label": "◀", "custom_id": f"faltan_page:{banner_key}:{page - 1}"})
        buttons.append({"type": 2, "style": 2, "label": f"{page + 1} / {total_pages}", "custom_id": "faltan_noop", "disabled": True})
        if page < total_pages - 1:
            buttons.append({"type": 2, "style": 1, "label": "▶", "custom_id": f"faltan_page:{banner_key}:{page + 1}"})

        return {"embeds": [embed], "components": [{"type": 1, "components": buttons}]}

    async def get_collection(self, user_id: str, page: int = 0, lang: str = "en") -> dict:
        cards = self.db.get_collection(user_id)
        if not cards:
            return {"content": t("collection_empty", lang)}

        banner_abbrevs = {"permanent": "OL", "rotating": "NG"}
        card_banner: dict[str, str] = {}
        for banner_key, banner in ALL_BANNERS.items():
            abbrev = banner_abbrevs[banner_key]
            for rarity in ("secret", "ultra", "super", "rare", "common"):
                for c in banner.get(rarity, []):
                    card_banner[str(c["id"])] = abbrev

        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        cards_sorted = sorted(cards, key=lambda x: (rarity_order.index(x["rarity"]), x["card_name"]))

        total_unique = len(cards_sorted)
        total_copies = sum(c["count"] for c in cards_sorted)

        page_size = 15
        total_pages = max(1, (total_unique + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        page_cards = cards_sorted[page * page_size:(page + 1) * page_size]

        grouped: dict[str, list[str]] = {}
        for c in page_cards:
            r = c["rarity"]
            abbrev = card_banner.get(str(c["card_id"]), "??")
            lock = " 🔒" if c.get("protected") else ""
            grouped.setdefault(r, []).append(f"{c['card_name']} ({abbrev}) ×{c['count']}{lock}")

        fields = []
        for r in rarity_order:
            if r not in grouped:
                continue
            value = "\n".join(grouped[r])
            if len(value) > 1024:
                value = value[:1021] + "..."
            fields.append({"name": f"{RARITY_EMOJIS[r]} {rarity_names[r]}", "value": value, "inline": False})

        best = page_cards[0]
        embed = {
            "title": t("collection_title", lang, unique=total_unique, copies=total_copies),
            "thumbnail": {"url": best.get("image_url", "")},
            "fields": fields,
            "color": RARITY_COLORS[best["rarity"]],
            "footer": {"text": t("collection_footer", lang, page=page + 1, total=total_pages)},
        }

        buttons = []
        if page > 0:
            buttons.append({"type": 2, "style": 2, "label": "◀", "custom_id": f"coleccion_page:{page - 1}"})
        buttons.append({"type": 2, "style": 2, "label": f"{page + 1} / {total_pages}", "custom_id": "coleccion_noop", "disabled": True})
        if page < total_pages - 1:
            buttons.append({"type": 2, "style": 1, "label": "▶", "custom_id": f"coleccion_page:{page + 1}"})

        return {"embeds": [embed], "components": [{"type": 1, "components": buttons}]}

    def _ranking_buttons(self, current: str, lang: str = "en") -> list:
        return [{
            "type": 1,
            "components": [
                {"type": 2, "style": 1 if current == "score" else 2, "label": t("btn_ranking_score", lang), "custom_id": "ranking_mode:score", "disabled": current == "score"},
                {"type": 2, "style": 1 if current == "collection" else 2, "label": t("btn_ranking_collection", lang), "custom_id": "ranking_mode:collection", "disabled": current == "collection"},
            ],
        }]

    async def get_ranking(self, mode: str = "score", lang: str = "en") -> dict:
        medals = ["🥇", "🥈", "🥉"]

        if mode == "collection":
            banner_card_ids = [
                card["id"]
                for banner in ALL_BANNERS.values()
                for rarity in ("secret", "ultra", "super", "rare", "common")
                for card in banner.get(rarity, [])
            ]
            total = len(banner_card_ids)
            rows = self.db.get_collection_ranking(banner_card_ids)
            if not rows:
                return {"content": t("ranking_empty_collection", lang), "components": self._ranking_buttons("collection", lang)}
            lines = []
            for i, row in enumerate(rows):
                medal = medals[i] if i < 3 else f"{i + 1}."
                pct = round(row["unique_count"] / total * 100)
                lines.append(f"{medal} **{row['username']}** — {row['unique_count']}/{total} ({pct}%)")
            return {
                "embeds": [{"title": t("ranking_title_collection", lang), "description": "\n".join(lines), "color": 0xFFD700, "footer": {"text": t("ranking_collection_footer", lang, total=total)}}],
                "components": self._ranking_buttons("collection", lang),
            }

        rows = self.db.get_ranking()
        if not rows:
            return {"content": t("ranking_empty_score", lang), "components": self._ranking_buttons("score", lang)}
        lines = []
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i + 1}."
            win_rate = round(row["games_won"] / row["games_played"] * 100) if row["games_played"] > 0 else 0
            lines.append(f"{medal} **{row['username']}** — {row['total_score']} pts ({row['games_won']}/{row['games_played']} won, {win_rate}% win rate)" if lang == "en" else f"{medal} **{row['username']}** — {row['total_score']} pts ({row['games_won']}/{row['games_played']} ganadas, {win_rate}% win rate)")
        return {
            "embeds": [{"title": t("ranking_title_score", lang), "description": "\n".join(lines), "color": 0xF1C40F}],
            "components": self._ranking_buttons("score", lang),
        }

    async def initiate_trade(self, from_user_id: str, to_user_id: str, from_card_name: str, to_card_name: str, lang: str = "en") -> dict:
        if from_user_id == to_user_id:
            return {"content": t("trade_self", lang)}

        from_card = self.db.get_collection_card(from_user_id, from_card_name)
        if not from_card:
            return {"content": t("trade_no_from_card", lang, name=from_card_name)}
        if from_card.get("protected"):
            return {"content": t("trade_from_protected", lang, name=from_card["card_name"])}

        to_card = self.db.get_collection_card(to_user_id, to_card_name)
        if not to_card:
            return {"content": t("trade_no_to_card", lang, user=to_user_id, name=to_card_name)}
        if to_card.get("protected"):
            return {"content": t("trade_to_protected", lang, name=to_card["card_name"], user=to_user_id)}

        trade = self.db.create_trade(from_user_id, from_card, to_user_id, to_card)
        trade_id = trade["id"]

        return {
            "content": t("trade_offer", lang, to=to_user_id, from_=from_user_id),
            "embeds": [{
                "color": 0x3498DB,
                "fields": [
                    {"name": t("trade_offers", lang), "value": f"{RARITY_EMOJIS[from_card['rarity']]} **{from_card['card_name']}**", "inline": True},
                    {"name": t("trade_wants", lang), "value": f"{RARITY_EMOJIS[to_card['rarity']]} **{to_card['card_name']}**", "inline": True},
                ],
            }],
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 3, "label": t("btn_trade_accept", lang), "custom_id": f"trade_accept:{trade_id}:{to_user_id}"},
                    {"type": 2, "style": 4, "label": t("btn_trade_reject", lang), "custom_id": f"trade_reject:{trade_id}:{to_user_id}"},
                ],
            }],
        }

    async def accept_trade(self, trade_id: str, user_id: str, lang: str = "en") -> dict:
        trade = self.db.get_trade(trade_id)
        if not trade:
            return {"content": t("trade_not_found", lang), "components": []}
        if trade["status"] != "pending":
            return {"content": t("trade_not_active", lang), "components": []}

        success = self.db.complete_trade(trade_id)
        if not success:
            return {"content": t("trade_failed", lang), "embeds": [], "components": []}

        return {
            "content": t("trade_completed", lang, from_=trade["from_user_id"], to_card=trade["to_card_name"], to=trade["to_user_id"], from_card=trade["from_card_name"]),
            "embeds": [],
            "components": [],
        }

    async def reject_trade(self, trade_id: str, user_id: str, lang: str = "en") -> dict:
        trade = self.db.get_trade(trade_id)
        if not trade:
            return {"content": t("trade_not_found", lang), "components": []}
        if trade["status"] != "pending":
            return {"content": t("trade_not_active", lang), "components": []}

        self.db.cancel_trade(trade_id)
        return {"content": t("trade_rejected", lang, user=user_id), "embeds": [], "components": []}

    async def handle_config(self, guild_id: str, accion: str, command: str | None, channel_id: str | None, language: str | None, lang: str = "en") -> dict:
        if language:
            if language not in ("en", "es"):
                return {"content": "❌ Valid languages: `en`, `es`."}
            self.db.set_guild_language(guild_id, language)
            label = "English" if language == "en" else "Español"
            return {"content": t("config_lang_set", lang, label=label)}

        if accion == "ver" or accion == "view":
            locks = self.db.get_all_channel_locks(guild_id)
            if not locks:
                return {"content": t("config_no_locks", lang)}
            lines = [f"`/{r['command']}` → <#{r['channel_id']}>" for r in locks]
            return {"embeds": [{"title": t("config_locks_title", lang), "description": "\n".join(lines), "color": 0x3498DB}]}

        if not command:
            return {"content": t("config_no_command", lang)}

        if accion in ("lock", "lockear"):
            if not channel_id:
                return {"content": t("config_no_channel", lang)}
            self.db.set_command_channel(guild_id, command, channel_id)
            return {"content": t("config_locked", lang, cmd=command, channel=channel_id)}

        if accion in ("unlock", "desbloquear"):
            self.db.remove_command_channel(guild_id, command)
            return {"content": t("config_unlocked", lang, cmd=command)}

        return {"content": t("config_bad_action", lang)}
