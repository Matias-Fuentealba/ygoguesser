import re
import io
from db.database import Database
from game.yugioh import fetch_random_card, build_hints
from game.zoom import get_zoomed_image, zoom_score, MAX_ZOOM_LEVEL

MAX_HINTS = 5


def calculate_score(hints_revealed: int) -> int:
    return max(0, 100 - hints_revealed * 20)


def normalize_name(name: str) -> str:
    return re.sub(r"[^a-z0-9]", "", name.lower())


def card_embed(content: str, card: dict, color: int) -> dict:
    embed = {"description": content, "color": color}
    if card.get("image_url"):
        embed["image"] = {"url": card["image_url"]}
    return {"embeds": [embed]}


class GameManager:
    def __init__(self, db: Database):
        self.db = db

    async def start_game(self, user_id: str, username: str) -> str:
        existing = self.db.get_active_game(user_id)
        if existing:
            return "Ya tienes una partida activa. Usa `/adivinar`, `/pista` o `/rendirse`."

        card = fetch_random_card()
        if not card:
            return "No se pudo obtener una carta. Intenta de nuevo más tarde."

        self.db.upsert_user(user_id, username)
        self.db.create_game(user_id, card["name"], card)

        hints = build_hints(card)
        return (
            f"🎮 **¡Nueva partida iniciada!**\n\n"
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

    async def surrender(self, user_id: str) -> str:
        game = self.db.get_active_game(user_id)
        if not game:
            return "No tienes una partida activa. Usa `/jugar` para empezar."

        card = game["card_data"]
        self.db.end_game(game["id"], "lost")
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
                f"➡️ Usa `/adivinar-zoom carta:<nombre>` para intentar."
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
