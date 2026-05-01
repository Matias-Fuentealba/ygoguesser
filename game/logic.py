import re
import io
from datetime import datetime, timezone, timedelta
from db.database import Database
from game.yugioh import fetch_random_card, build_hints, fetch_card_for_price
from game.zoom import get_zoomed_image, zoom_score, MAX_ZOOM_LEVEL
from game.gacha import (
    pull_free, pull_x10,
    DUEL_MONSTERS_BANNER, X10_COST,
    RARITY_EMOJIS, RARITY_COLORS, COOLDOWN_HOURS,
)

RARITY_SELL_VALUES = {"secret": 50, "ultra": 20, "super": 10, "rare": 5, "common": 1}

MAX_HINTS = 5


def calculate_score(hints_revealed: int) -> int:
    return max(0, 100 - hints_revealed * 20)


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.strip().lower())


def _build_price_message(champion: dict, challenger: dict, score: int, prefix: str = "") -> dict:
    return {
        "content": f"{prefix}💰 **¿Cuál carta es más cara?** | Puntaje: **{score}**",
        "embeds": [
            {
                "title": f"Carta 1: {champion['name']}",
                "description": f"📦 {champion['set_name']}\n🏷️ {champion['set_rarity']}",
                "image": {"url": champion["image_url"]},
                "color": 0xF1C40F,
            },
            {
                "title": f"Carta 2: {challenger['name']}",
                "description": f"📦 {challenger['set_name']}\n🏷️ {challenger['set_rarity']}",
                "image": {"url": challenger["image_url"]},
                "color": 0xF1C40F,
            },
        ],
        "components": [
            {
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": "Carta 1", "custom_id": "price_1"},
                    {"type": 2, "style": 1, "label": "Carta 2", "custom_id": "price_2"},
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

    async def start_game(self, user_id: str, username: str) -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            mode = existing.get("game_mode", "hints")
            hints_map = {"hints": "`/pista` y `/adivinar`", "zoom": "`/zoom-pista` y `/adivinar-zoom`", "price": "los botones"}
            return {"content": f"Ya tienes una partida activa. Usa {hints_map.get(mode, '`/rendirse`')} o `/rendirse`."}

        return {
            "content": (
                "🎮 **Bienvenido a YGOGuesser!**\n\n"
                "Pon a prueba tu conocimiento de cartas Yu-Gi-Oh! Elige un modo:\n\n"
                "🃏 **Modo Pistas** — Se revelan pistas progresivas sobre una carta. Cuantas menos pistas uses, más puntos ganas.\n"
                "🔍 **Modo Zoom** — Se muestra una imagen muy zoomeada de la carta. Si fallas, el zoom se aleja poco a poco.\n"
                "💰 **Modo Precio** — Se muestran dos cartas. Adivina cuál es más cara en el mercado TCG. ¡Un fallo y termina la racha!\n"
            ),
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 1, "label": "🃏 Modo Pistas", "custom_id": "mode_hints"},
                    {"type": 2, "style": 2, "label": "🔍 Modo Zoom", "custom_id": "mode_zoom"},
                    {"type": 2, "style": 4, "label": "💰 Modo Precio", "custom_id": "mode_price"},
                ],
            }],
        }

    async def start_hints_game(self, user_id: str, username: str) -> str:
        card = fetch_random_card()
        if not card:
            return "No se pudo obtener una carta. Intenta de nuevo más tarde."

        self.db.upsert_user(user_id, username)
        self.db.create_game(user_id, card["name"], card)

        hints = build_hints(card)
        return (
            f"🃏 **¡Modo Pistas iniciado!**\n\n"
            f"Aquí va la primera pista:\n{hints[0]}\n\n"
            f"Tienes hasta **{MAX_HINTS} pistas** disponibles.\n"
            f"➡️ Usa `/pista` para más pistas o `/adivinar carta:<nombre>` para intentar."
        )

    async def get_hint(self, user_id: str) -> str:
        game = self.db.get_active_game(user_id)
        if not game:
            return "No tienes una partida activa. Usa `/jugar` para empezar."

        hints_revealed = game["hints_revealed"]
        card = game["card_data"]
        hints = build_hints(card)

        next_index = hints_revealed + 1
        if next_index >= MAX_HINTS:
            return f"Ya revelaste todas las pistas ({MAX_HINTS}/{MAX_HINTS}). Usa `/adivinar` o `/rendirse`."

        self.db.reveal_hint(game["id"], next_index)

        score_if_correct = calculate_score(next_index)
        return (
            f"💡 Pista {next_index + 1}/{MAX_HINTS}:\n{hints[next_index]}\n\n"
            f"Acertar ahora vale **{score_if_correct} puntos**."
        )

    async def guess(self, user_id: str, username: str, guess: str):
        game = self.db.get_active_game(user_id)
        if not game:
            return "No tienes una partida activa. Usa `/jugar` para empezar."
        if game.get("game_mode") == "zoom":
            return await self.guess_zoom(user_id, username, guess)
        return await self.make_guess(user_id, username, guess)

    async def make_guess(self, user_id: str, username: str, guess: str) -> str:
        game = self.db.get_active_game(user_id)
        if not game:
            return "No tienes una partida activa. Usa `/jugar` para empezar."

        card = game["card_data"]
        hints_revealed = game["hints_revealed"]
        attempts = game["attempts_on_hint"]

        if normalize_name(guess) == normalize_name(card["name"]):
            score = calculate_score(hints_revealed)
            self.db.end_game(game["id"], "won")
            self.db.add_score(user_id, score, won=True)
            return card_embed(
                f"✅ **¡Correcto!** La carta era **{card['name']}**.\n"
                f"🏆 Ganaste **{score} puntos** (pistas usadas: {hints_revealed}/{MAX_HINTS}).",
                card, 0x2ECC71
            )

        new_attempts = attempts + 1
        self.db.increment_attempt(game["id"], attempts)

        if new_attempts < 3:
            remaining = 3 - new_attempts
            return (
                f"❌ **Incorrecto.** Te quedan **{remaining} intento{'s' if remaining > 1 else ''}** "
                f"con la pista actual."
            )

        # Agotó los 3 intentos de esta pista
        next_index = hints_revealed + 1
        if next_index >= MAX_HINTS:
            self.db.end_game(game["id"], "lost")
            self.db.add_score(user_id, 0, won=False)
            return card_embed(
                f"💀 **Agotaste todos los intentos.** La carta era **{card['name']}**.",
                card, 0xE74C3C
            )

        hints = build_hints(card)
        self.db.reveal_hint(game["id"], next_index)
        score_if_correct = calculate_score(next_index)
        return (
            f"❌ Agotaste los 3 intentos de esta pista. Siguiente pista automática:\n\n"
            f"💡 Pista {next_index + 1}/{MAX_HINTS}:\n{hints[next_index]}\n\n"
            f"Acertar ahora vale **{score_if_correct} puntos**."
        )

    async def surrender(self, user_id: str) -> str | dict:
        game = self.db.get_active_game(user_id)
        if not game:
            return "No tienes una partida activa. Usa `/jugar` para empezar."

        game_mode = game.get("game_mode", "hints")
        self.db.end_game(game["id"], "lost")

        if game_mode == "price":
            score = game["card_data"].get("score", 0)
            self.db.add_score(user_id, score, won=False)
            return f"🏳️ Abandonaste el modo precio. Puntaje final: **{score} puntos**."

        card = game["card_data"]
        self.db.add_score(user_id, 0, won=False)
        return card_embed(
            f"🏳️ Te rendiste. La carta era **{card['name']}**.",
            card, 0xE74C3C
        )

    async def start_zoom(self, user_id: str, username: str) -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            mode = existing.get("game_mode", "hints")
            cmd = "/adivinar-zoom" if mode == "zoom" else "/adivinar"
            return {"content": f"Ya tienes una partida activa. Usa `{cmd}` o `/rendirse`."}

        card = fetch_random_card()
        if not card:
            return {"content": "No se pudo obtener una carta. Intenta de nuevo más tarde."}

        self.db.upsert_user(user_id, username)
        self.db.create_game(user_id, card["name"], card, game_mode="zoom")

        img = get_zoomed_image(card["image_url"], 0)
        if not img:
            return {"content": "No se pudo procesar la imagen. Intenta de nuevo."}

        score = zoom_score(0)
        return {
            "content": (
                f"🔍 **¡Modo Zoom iniciado!**\n"
                f"Adivina la carta con zoom nivel 1/{MAX_ZOOM_LEVEL + 1}.\n"
                f"Acertar ahora vale **{score} puntos**. Tienes **3 intentos** por nivel.\n"
                f"➡️ `/adivinar-zoom carta:<nombre>` para intentar.\n"
                f"➡️ `/zoom-pista` para ver más de la imagen (baja el puntaje)."
            ),
            "image": img,
        }

    async def guess_zoom(self, user_id: str, username: str, guess: str) -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "zoom":
            return {"content": "No tienes una partida de zoom activa. Usa `/zoom` para empezar."}

        card = game["card_data"]
        zoom_level = game["zoom_level"]
        attempts = game["attempts_on_hint"]

        if normalize_name(guess) == normalize_name(card["name"]):
            score = zoom_score(zoom_level)
            self.db.end_game(game["id"], "won")
            self.db.add_score(user_id, score, won=True)
            return {
                "content": (
                    f"✅ **¡Correcto!** La carta era **{card['name']}**.\n"
                    f"🏆 Ganaste **{score} puntos** (zoom nivel {zoom_level + 1}/{MAX_ZOOM_LEVEL + 1})."
                ),
                "embed_image_url": card["image_url"],
                "embed_color": 0x2ECC71,
            }

        new_attempts = attempts + 1
        self.db.increment_attempt(game["id"], attempts)

        if new_attempts < 3:
            remaining = 3 - new_attempts
            return {
                "content": (
                    f"❌ **Incorrecto.** Te quedan **{remaining} intento{'s' if remaining > 1 else ''}** "
                    f"en este nivel de zoom."
                )
            }

        # Agotó los 3 intentos de este nivel
        next_level = zoom_level + 1
        if next_level > MAX_ZOOM_LEVEL:
            self.db.end_game(game["id"], "lost")
            self.db.add_score(user_id, 0, won=False)
            return {
                "content": f"💀 **Agotaste todos los intentos.** La carta era **{card['name']}**.",
                "embed_image_url": card["image_url"],
                "embed_color": 0xE74C3C,
            }

        self.db.advance_zoom(game["id"], next_level)
        img = get_zoomed_image(card["image_url"], next_level)
        score = zoom_score(next_level)

        return {
            "content": (
                f"❌ Agotaste los intentos. Aquí va el siguiente nivel de zoom:\n"
                f"🔍 Zoom nivel {next_level + 1}/{MAX_ZOOM_LEVEL + 1} — "
                f"Acertar ahora vale **{score} puntos**."
            ),
            "image": img,
        }

    async def next_zoom(self, user_id: str) -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "zoom":
            return {"content": "No tienes una partida de zoom activa. Usa `/zoom` para empezar."}

        zoom_level = game["zoom_level"]
        next_level = zoom_level + 1

        if next_level > MAX_ZOOM_LEVEL:
            return {"content": f"Ya estás en el nivel máximo de zoom ({zoom_level + 1}/{MAX_ZOOM_LEVEL + 1}). Usa `/adivinar-zoom` o `/rendirse`."}

        card = game["card_data"]
        self.db.advance_zoom(game["id"], next_level)
        img = get_zoomed_image(card["image_url"], next_level)
        score = zoom_score(next_level)

        return {
            "content": (
                f"🔍 Zoom nivel {next_level + 1}/{MAX_ZOOM_LEVEL + 1} — "
                f"Acertar ahora vale **{score} puntos**."
            ),
            "image": img,
        }

    async def start_price_game(self, user_id: str, username: str) -> dict:
        existing = self.db.get_active_game(user_id)
        if existing:
            return {"content": "Ya tienes una partida activa. Usa `/rendirse` para abandonarla."}

        champion = fetch_card_for_price()
        if not champion:
            return {"content": "No se pudieron obtener cartas con precio. Intenta de nuevo."}
        challenger = fetch_card_for_price(exclude_names={champion["name"]})
        if not challenger:
            return {"content": "No se pudieron obtener cartas con precio. Intenta de nuevo."}

        self.db.upsert_user(user_id, username)
        state = {"champion": champion, "challenger": challenger, "champion_wins": 0, "score": 0}
        self.db.create_game(user_id, champion["name"], state, game_mode="price")

        return _build_price_message(champion, challenger, score=0)

    async def choose_price(self, user_id: str, choice: int) -> dict:
        game = self.db.get_active_game(user_id)
        if not game or game.get("game_mode") != "price":
            return {"content": "No tienes una partida de precio activa. Usa `/precio` para empezar."}

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
                self.db.add_score(user_id, score, won=True)
                return {"content": f"✅ ¡Correcto! No hay más cartas disponibles. Puntaje final: **{score} puntos**."}

            new_challenger = fetch_card_for_price(exclude_names={new_champion["name"]})
            if not new_challenger:
                self.db.end_game(game["id"], "won")
                self.db.add_score(user_id, score, won=True)
                return {"content": f"✅ ¡Correcto! No hay más cartas disponibles. Puntaje final: **{score} puntos**."}

            state.update({"champion": new_champion, "challenger": new_challenger, "champion_wins": new_champion_wins, "score": score})
            self.db.update_game_data(game["id"], state)

            prefix = (
                f"✅ ¡Correcto! **{correct_card['name']}** valía **${correct_card['price']:.2f}** "
                f"vs **${wrong_card['price']:.2f}**.\n\n"
            )
            return _build_price_message(new_champion, new_challenger, score, prefix=prefix)

        # Incorrecto — fin de partida
        self.db.end_game(game["id"], "lost")
        self.db.add_score(user_id, score, won=False)
        return {
            "content": (
                f"❌ **Incorrecto.** La más cara era **{correct_card['name']}** "
                f"con **${correct_card['price']:.2f}** (vs **${wrong_card['price']:.2f}**).\n"
                f"🏆 Puntaje final: **{score} puntos**."
            ),
            "embeds": [
                {"title": f"✅ {correct_card['name']} — ${correct_card['price']:.2f}", "image": {"url": correct_card["image_url"]}, "color": 0x2ECC71},
                {"title": f"❌ {wrong_card['name']} — ${wrong_card['price']:.2f}", "image": {"url": wrong_card["image_url"]}, "color": 0xE74C3C},
            ],
            "components": [],
        }

    def _x10_button(self, user_id: str = "") -> list:
        return [{
            "type": 1,
            "components": [
                {"type": 2, "style": 1, "label": f"🎴 x10 ({X10_COST} monedas)", "custom_id": f"gacha_x10:{user_id}"},
            ],
        }]

    async def open_sobre(self, user_id: str, username: str) -> dict:
        self.db.upsert_user(user_id, username)
        user = self.db.get_user(user_id)
        coins = (user.get("coins_balance") or 0) if user else 0

        last_raw = (user or {}).get("last_sobre")
        if last_raw:
            last_dt = datetime.fromisoformat(last_raw)
            if last_dt.tzinfo is None:
                last_dt = last_dt.replace(tzinfo=timezone.utc)
            now = datetime.now(timezone.utc)
            # Cooldown hasta el próximo cambio de hora en punto
            same_hour = last_dt.year == now.year and last_dt.month == now.month \
                        and last_dt.day == now.day and last_dt.hour == now.hour
            if same_hour:
                next_hour = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
                time_left = next_hour - now
                mins = int(time_left.total_seconds() // 60)
                secs = int(time_left.total_seconds() % 60)
                coins_hint = "" if coins > 0 else "\n> 💡 Gana monedas jugando partidas con `/jugar`."
                return {
                    "content": (
                        f"⏳ Tu próximo sobre gratis estará disponible en **{mins}m {secs}s**.\n"
                        f"💰 Tienes **{coins} monedas** disponibles.{coins_hint}"
                    ),
                    "components": self._x10_button(user_id),
                }

        cards = pull_free(DUEL_MONSTERS_BANNER)
        self.db.add_to_collection(user_id, cards)
        self.db.set_last_sobre(user_id)

        return self._build_pull_response(cards, f"🎴 ¡Abriste un sobre! — {DUEL_MONSTERS_BANNER['name']}", user_id)

    async def open_sobre_x10(self, user_id: str) -> dict:
        user = self.db.get_user(user_id)
        if not user:
            return {"content": "Primero usa `/sobre` para registrarte."}

        coins = user.get("coins_balance") or 0
        if coins < X10_COST:
            return {"content": f"❌ Necesitas **{X10_COST} monedas** pero tienes **{coins}**."}

        if not self.db.spend_coins(user_id, X10_COST):
            return {"content": "❌ No tienes suficientes monedas."}

        cards = pull_x10(DUEL_MONSTERS_BANNER)
        self.db.add_to_collection(user_id, cards)

        new_balance = coins - X10_COST
        result = self._build_pull_response(cards, f"🎴 ¡Abriste 10 sobres! — {DUEL_MONSTERS_BANNER['name']}", user_id)
        result["embeds"][0]["footer"] = {"text": f"💰 Monedas restantes: {new_balance}"}
        return result

    def _build_pull_response(self, cards: list[dict], header: str, user_id: str = "") -> dict:
        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        cards_sorted = sorted(cards, key=lambda x: rarity_order.index(x["rarity"]))

        best = cards_sorted[0]
        fields = [
            {
                "name": f"{RARITY_EMOJIS[c['rarity']]} {c['name']}",
                "value": rarity_names[c["rarity"]],
                "inline": True,
            }
            for c in cards_sorted
        ]

        return {
            "embeds": [{
                "title": header.strip(),
                "thumbnail": {"url": best["image_url"]},
                "fields": fields,
                "color": RARITY_COLORS[best["rarity"]],
            }],
            "components": self._x10_button(user_id),
        }

    async def show_sell_duplicates(self, user_id: str) -> dict:
        cards = self.db.get_collection(user_id)
        duplicates = [c for c in cards if c["count"] > 1]
        if not duplicates:
            return {"content": "No tienes cartas duplicadas para vender."}

        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        duplicates_sorted = sorted(duplicates, key=lambda x: (rarity_order.index(x["rarity"]), x["card_name"]))

        total_extras = sum(c["count"] - 1 for c in duplicates_sorted)
        total_coins = sum((c["count"] - 1) * RARITY_SELL_VALUES[c["rarity"]] for c in duplicates_sorted)

        fields = []
        for c in duplicates_sorted:
            extras = c["count"] - 1
            coins = extras * RARITY_SELL_VALUES[c["rarity"]]
            fields.append({
                "name": f"{RARITY_EMOJIS[c['rarity']]} {c['card_name']}",
                "value": f"×{extras} → {coins} 💰",
                "inline": True,
            })

        return {
            "embeds": [{
                "title": f"🗑️ Vender duplicadas — {total_extras} copias → {total_coins} monedas",
                "description": (
                    f"◻️ Common ×1 = **{RARITY_SELL_VALUES['common']}** 💰  "
                    f"🔹 Rare ×1 = **{RARITY_SELL_VALUES['rare']}** 💰  "
                    f"⭐ Super ×1 = **{RARITY_SELL_VALUES['super']}** 💰  "
                    f"⭐⭐ Ultra ×1 = **{RARITY_SELL_VALUES['ultra']}** 💰  "
                    f"✨✨✨ Secret ×1 = **{RARITY_SELL_VALUES['secret']}** 💰"
                ),
                "fields": fields,
                "color": 0xE74C3C,
            }],
            "components": [{
                "type": 1,
                "components": [
                    {"type": 2, "style": 4, "label": f"🗑️ Confirmar venta ({total_coins} monedas)", "custom_id": f"vender_confirmar:{user_id}"},
                    {"type": 2, "style": 2, "label": "Cancelar", "custom_id": f"vender_cancelar:{user_id}"},
                ],
            }],
        }

    async def confirm_sell_duplicates(self, user_id: str) -> dict:
        coins_earned = self.db.sell_duplicates(user_id, RARITY_SELL_VALUES)
        if coins_earned == 0:
            return {"embeds": [{"title": "No había duplicadas para vender.", "color": 0x9D9D9D}], "components": []}
        user = self.db.get_user(user_id)
        new_balance = user.get("coins_balance") or 0
        return {
            "embeds": [{
                "title": f"✅ Vendiste tus duplicadas",
                "description": f"Ganaste **{coins_earned} monedas** 💰\nSaldo actual: **{new_balance} monedas**",
                "color": 0x2ECC71,
            }],
            "components": [],
        }

    async def get_help(self) -> dict:
        return {
            "embeds": [{
                "title": "📖 Comandos de YGOGuesser",
                "color": 0x3498DB,
                "fields": [
                    {
                        "name": "🎮 Juego",
                        "value": (
                            "`/jugar` — Inicia una partida (elige modo)\n"
                            "`/adivinar carta:<nombre>` — Adivina la carta actual\n"
                            "`/pista` — Revela la siguiente pista (modo Pistas)\n"
                            "`/zoom-pista` — Avanza al siguiente zoom (modo Zoom)\n"
                            "`/rendirse` — Abandona la partida actual\n"
                            "`/ranking` — Top 10 de jugadores"
                        ),
                        "inline": False,
                    },
                    {
                        "name": "🎴 Gacha",
                        "value": (
                            "`/sobre` — Abre un sobre gratis (1 vez por hora)\n"
                            "`/coleccion` — Ve tus cartas conseguidas\n"
                            "`/vender` — Vende tus cartas duplicadas por monedas\n"
                            "`/gacha` — Info del banner actual y probabilidades"
                        ),
                        "inline": False,
                    },
                    {
                        "name": "💰 Monedas",
                        "value": (
                            "Ganas monedas jugando partidas — son los mismos puntos del ranking "
                            "pero se guardan por separado. Gastarlas **no baja tu posición**."
                        ),
                        "inline": False,
                    },
                ],
                "footer": {"text": "YGOGuesser • ygoguesser.vercel.app"},
            }]
        }

    async def get_gacha_info(self) -> dict:
        banner = DUEL_MONSTERS_BANNER
        pool_sizes = {r: len(banner.get(r, [])) for r in ("secret", "ultra", "super", "rare", "common")}
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        pool_lines = "  ".join(
            f"{RARITY_EMOJIS[r]} {rarity_names[r]}: {pool_sizes[r]} cartas"
            for r in ("secret", "ultra", "super", "rare", "common")
        )

        embed = {
            "title": f"🎴 Banner: {banner['name']}",
            "description": (
                "**¿Cómo funciona?**\n"
                "Ganas **monedas** jugando — son los mismos puntos del ranking pero se guardan por separado, así que gastarlas no baja tu posición.\n\n"
                f"🆓 **`/sobre`** — Sobre gratis de 5 cartas cada **1 hora**\n"
                f"💰 **Botón x10** — 10 cartas por **{X10_COST} monedas**, garantiza al menos 1 Ultra Rare\n\n"
                "**Probabilidades:**\n"
                f"{RARITY_EMOJIS['secret']} Secret Rare — 1%\n"
                f"{RARITY_EMOJIS['ultra']} Ultra Rare — 4%\n"
                f"{RARITY_EMOJIS['super']} Super Rare — 15%\n"
                f"{RARITY_EMOJIS['rare']} Rare — 30%\n"
                f"{RARITY_EMOJIS['common']} Common — 50%\n\n"
                f"**Pool del banner:**\n{pool_lines}\n\n"
                "🔗 [Ver todas las cartas del pool](https://ygoguesser.vercel.app/banner)"
            ),
            "color": 0xFFD700,
        }
        if banner.get("image_url"):
            embed["image"] = {"url": banner["image_url"]}

        return {"embeds": [embed]}

    async def get_collection(self, user_id: str, page: int = 0) -> dict:
        cards = self.db.get_collection(user_id)
        if not cards:
            return {"content": "No tienes cartas aún. Usa `/sobre` para abrir tu primer sobre."}

        rarity_order = ["secret", "ultra", "super", "rare", "common"]
        rarity_names = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
        cards_sorted = sorted(cards, key=lambda x: (rarity_order.index(x["rarity"]), x["card_name"]))

        total_unique = len(cards_sorted)
        total_copies = sum(c["count"] for c in cards_sorted)

        page_size = 15
        total_pages = max(1, (total_unique + page_size - 1) // page_size)
        page = max(0, min(page, total_pages - 1))
        page_cards = cards_sorted[page * page_size:(page + 1) * page_size]

        best = page_cards[0]
        fields = []
        for c in page_cards:
            fields.append({
                "name": f"{RARITY_EMOJIS[c['rarity']]} {c['card_name']}",
                "value": f"×{c['count']}",
                "inline": True,
            })

        embed = {
            "title": f"📦 Colección — {total_unique} únicas · {total_copies} copias",
            "thumbnail": {"url": best.get("image_url", "")},
            "fields": fields,
            "color": RARITY_COLORS[best["rarity"]],
            "footer": {"text": f"Página {page + 1} / {total_pages}  •  Usa /sobre para conseguir más cartas"},
        }

        buttons = []
        if page > 0:
            buttons.append({"type": 2, "style": 2, "label": "◀", "custom_id": f"coleccion_page:{page - 1}"})
        buttons.append({"type": 2, "style": 2, "label": f"{page + 1} / {total_pages}", "custom_id": "coleccion_noop", "disabled": True})
        if page < total_pages - 1:
            buttons.append({"type": 2, "style": 1, "label": "▶", "custom_id": f"coleccion_page:{page + 1}"})

        return {"embeds": [embed], "components": [{"type": 1, "components": buttons}]}

    async def get_ranking(self) -> str:
        rows = self.db.get_ranking()
        if not rows:
            return "Todavía no hay partidas registradas."

        lines = ["🏆 **Ranking — Top 10**\n"]
        medals = ["🥇", "🥈", "🥉"]
        for i, row in enumerate(rows):
            medal = medals[i] if i < 3 else f"{i + 1}."
            win_rate = (
                round(row["games_won"] / row["games_played"] * 100)
                if row["games_played"] > 0 else 0
            )
            lines.append(
                f"{medal} **{row['username']}** — {row['total_score']} pts "
                f"({row['games_won']}/{row['games_played']} ganadas, {win_rate}% win rate)"
            )

        return "\n".join(lines)
