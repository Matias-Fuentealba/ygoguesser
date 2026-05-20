import os
import sys
import io
import json
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
import nacl.signing
import nacl.encoding
import nacl.exceptions
from dotenv import load_dotenv

from db.database import Database
from game.logic import GameManager

load_dotenv()

app = FastAPI()

DISCORD_PUBLIC_KEY = os.environ.get("DISCORD_PUBLIC_KEY", "")
APPLICATION_ID = os.environ.get("DISCORD_APPLICATION_ID", "")


def verify_signature(body: bytes, signature: str, timestamp: str) -> bool:
    try:
        verify_key = nacl.signing.VerifyKey(DISCORD_PUBLIC_KEY, encoder=nacl.encoding.HexEncoder)
        verify_key.verify(f"{timestamp}{body.decode()}".encode(), bytes.fromhex(signature))
        return True
    except Exception:
        return False


async def send_followup(token: str, response: str | dict):
    url = f"https://discord.com/api/v10/webhooks/{APPLICATION_ID}/{token}/messages/@original"

    async with httpx.AsyncClient() as client:
        # Response with image file (zoom mode)
        if isinstance(response, dict) and response.get("image"):
            img: io.BytesIO = response["image"]
            payload = {"content": response.get("content", "")}
            await client.patch(
                url,
                data={"payload_json": json.dumps(payload)},
                files={"files[0]": ("card.png", img, "image/png")},
            )

        # Response with embed (win/lose showing card)
        elif isinstance(response, dict) and response.get("embed_image_url"):
            embed = {
                "description": response.get("content", ""),
                "color": response.get("embed_color", 0x2ECC71),
                "image": {"url": response["embed_image_url"]},
            }
            await client.patch(url, json={"embeds": [embed]})

        # Response with embeds dict (hints mode win/lose)
        elif isinstance(response, dict) and response.get("embeds"):
            r = await client.patch(url, json=response)
            if r.status_code >= 400:
                print(f"[Discord 400] payload={response}\nresponse={r.text}")

        # Plain text or simple dict with content (and optional components)
        elif isinstance(response, dict):
            r = await client.patch(url, json=response)
            if r.status_code >= 400:
                print(f"[Discord 400] payload={response}\nresponse={r.text}")

        else:
            r = await client.patch(url, json={"content": response})
            if r.status_code >= 400:
                print(f"[Discord 400] payload={{'content': {response}}}\nresponse={r.text}")


UNLOCKED_COMMANDS = {"config", "help", "ranking"}

from game.strings import t as _t


async def process_command(payload: dict, token: str):
    command = payload["data"]["name"]
    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user", {})
    user_id = user.get("id", "")
    username = user.get("username", "unknown")
    guild_id = payload.get("guild_id", "")
    channel_id = payload.get("channel_id", "")

    db = Database()
    gm = GameManager(db)
    lang = db.get_guild_language(guild_id)

    try:
        # Channel lock check
        if command not in UNLOCKED_COMMANDS:
            allowed = db.get_command_channel(guild_id, command)
            if allowed and channel_id != allowed:
                await send_followup(token, {"content": _t("channel_locked", lang, cmd=command, channel=allowed)})
                return

        if command == "play":
            response = await gm.start_game(user_id, username, lang)
        elif command == "hint":
            response = await gm.get_hint(user_id, lang)
        elif command == "guess":
            options = payload["data"].get("options", [])
            guess = options[0]["value"] if options else ""
            response = await gm.guess(user_id, username, guess, lang)
        elif command == "zoom-hint":
            response = await gm.next_zoom(user_id, lang)
        elif command == "surrender":
            response = await gm.surrender(user_id, lang)
        elif command == "ranking":
            response = await gm.get_ranking(lang=lang)
        elif command == "pack":
            response = await gm.open_sobre(user_id, username, lang)
        elif command == "collection":
            response = await gm.get_collection(user_id, lang=lang)
        elif command == "gacha":
            response = await gm.get_gacha_info(user_id, lang)
        elif command == "sell":
            response = await gm.show_sell_duplicates(user_id, lang)
        elif command == "protect":
            options = payload["data"].get("options", [])
            card_name = options[0]["value"] if options else ""
            response = await gm.toggle_protect_card(user_id, card_name, lang)
        elif command == "trade":
            opts = {o["name"]: o["value"] for o in payload["data"].get("options", [])}
            to_user_id = opts.get("user", "")
            from_card_name = opts.get("my_card", "")
            to_card_name = opts.get("their_card", "")
            response = await gm.initiate_trade(user_id, to_user_id, from_card_name, to_card_name, lang)
        elif command == "help":
            response = await gm.get_help(lang)
        elif command == "config":
            if not bool(int(member.get("permissions", "0")) & 0x8):
                response = {"content": _t("config_no_admin", lang)}
            else:
                options = {o["name"]: o["value"] for o in payload["data"].get("options", [])}
                accion = options.get("action", "view")
                cmd = options.get("command")
                ch = options.get("channel")
                language = options.get("language")
                response = await gm.handle_config(guild_id, accion, cmd, ch, language, lang)
        else:
            response = _t("unrecognized_action", lang)
    except Exception as e:
        response = f"⚠️ Internal error: `{type(e).__name__}: {e}`"

    await send_followup(token, response)


async def process_component(payload: dict, token: str):
    custom_id = payload["data"]["custom_id"]
    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user", {})
    user_id = user.get("id", "")
    username = user.get("username", "unknown")
    guild_id = payload.get("guild_id", "")

    db = Database()
    gm = GameManager(db)
    lang = db.get_guild_language(guild_id)

    try:
        if custom_id == "mode_hints":
            response = await gm.start_hints_game(user_id, username, lang)
        elif custom_id == "mode_zoom":
            response = await gm.start_zoom(user_id, username, lang)
        elif custom_id == "mode_price":
            response = await gm.start_price_game(user_id, username, lang)
        elif custom_id in ("price_1", "price_2"):
            choice = int(custom_id[-1])
            response = await gm.choose_price(user_id, choice, lang)
        elif custom_id.startswith("sobre_banner:"):
            parts = custom_id.split(":")
            banner_key, owner_id = parts[1], parts[2]
            if user_id != owner_id:
                response = {"content": "❌ Only the user who used `/pack` can choose the banner.", "components": []}
            else:
                response = await gm.open_sobre_banner(user_id, username, banner_key, lang)
        elif custom_id.startswith("gacha_x10:"):
            parts = custom_id.split(":")
            owner_id = parts[1]
            banner_key = parts[2] if len(parts) > 2 else "ol"
            if user_id != owner_id:
                response = {"content": "❌ Only the user who opened the pack can use this button."}
            else:
                response = await gm.open_sobre_x10(user_id, banner_key, lang)
        elif custom_id.startswith("coleccion_page:"):
            page = int(custom_id.split(":")[1])
            response = await gm.get_collection(user_id, page, lang)
        elif custom_id.startswith("vender_confirmar:"):
            owner_id = custom_id.split(":")[1]
            if user_id != owner_id:
                response = {"content": "❌ Only the user who started the sale can confirm it.", "components": []}
            else:
                response = await gm.confirm_sell_duplicates(user_id, lang)
        elif custom_id.startswith("vender_cancelar:"):
            owner_id = custom_id.split(":")[1]
            if user_id != owner_id:
                response = {"content": "❌ Only the user who started the sale can cancel it.", "components": []}
            else:
                response = {"embeds": [{"title": _t("sell_cancelled", lang), "color": 0x9D9D9D}], "components": []}
        elif custom_id.startswith("ranking_mode:"):
            mode = custom_id.split(":")[1]
            response = await gm.get_ranking(mode, lang)
        elif custom_id.startswith("faltan:"):
            banner_key = custom_id.split(":")[1]
            response = await gm.get_missing_cards(user_id, banner_key, lang=lang)
        elif custom_id.startswith("faltan_page:"):
            parts = custom_id.split(":")
            banner_key, page = parts[1], int(parts[2])
            response = await gm.get_missing_cards(user_id, banner_key, page, lang)
        elif custom_id.startswith("trade_accept:"):
            parts = custom_id.split(":", 2)
            trade_id, owner_id = parts[1], parts[2]
            if user_id != owner_id:
                response = {"content": _t("trade_wrong_user_accept", lang)}
            else:
                response = await gm.accept_trade(trade_id, user_id, lang)
        elif custom_id.startswith("trade_reject:"):
            parts = custom_id.split(":", 2)
            trade_id, owner_id = parts[1], parts[2]
            if user_id != owner_id:
                response = {"content": _t("trade_wrong_user_reject", lang)}
            else:
                response = await gm.reject_trade(trade_id, user_id, lang)
        elif custom_id == "faltan_noop" or custom_id == "coleccion_noop":
            return
        else:
            response = _t("unrecognized_action", lang)
    except Exception as e:
        response = f"⚠️ Internal error: `{type(e).__name__}: {e}`"

    await send_followup(token, response)


@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
      <title>YGOGuesser</title>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
          font-family: sans-serif;
          background: #0d0d1a;
          color: #eee;
          min-height: 100vh;
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          padding: 40px 20px;
          text-align: center;
        }
        h1 { font-size: 2.8rem; color: #FFD700; margin-bottom: 12px; }
        p.sub { color: #aaa; font-size: 1.1rem; max-width: 500px; margin-bottom: 40px; }
        .cards {
          display: flex;
          flex-wrap: wrap;
          gap: 16px;
          justify-content: center;
          margin-bottom: 40px;
        }
        .card {
          background: #1a1a2e;
          border: 1px solid #333;
          border-radius: 12px;
          padding: 20px 24px;
          width: 200px;
        }
        .card .icon { font-size: 2rem; margin-bottom: 8px; }
        .card .icon img { width: 48px; height: 48px; object-fit: contain; }
        .card h3 { font-size: 1rem; color: #FFD700; margin-bottom: 6px; }
        .card p { font-size: 0.85rem; color: #999; }
        .links { display: flex; gap: 12px; flex-wrap: wrap; justify-content: center; }
        a.btn {
          background: #FFD700;
          color: #0d0d1a;
          font-weight: bold;
          padding: 12px 24px;
          border-radius: 8px;
          text-decoration: none;
          font-size: 0.95rem;
          transition: opacity 0.2s;
        }
        a.btn:hover { opacity: 0.85; }
        a.btn.secondary {
          background: transparent;
          color: #FFD700;
          border: 1px solid #FFD700;
        }
        footer { margin-top: 48px; color: #555; font-size: 0.8rem; }
      </style>
    </head>
    <body>
      <img src="https://i.imgur.com/HEF1czj.png" alt="YGOGuesser" style="width:180px;height:180px;border-radius:50%;margin-bottom:24px;box-shadow:0 0 40px rgba(255,215,0,0.3)">
      <h1>YGOGuesser</h1>
      <p class="sub">A Yu-Gi-Oh! Discord bot. Guess cards, collect them, trade with friends.</p>

      <div class="cards">
        <div class="card">
          <div class="icon"><img src="https://cdn.discordapp.com/emojis/1506144706218950718.png" alt="Hints"></div>
          <h3>Hints Mode</h3>
          <p>Guess the card from progressive clues. Fewer hints = more points.</p>
        </div>
        <div class="card">
          <div class="icon">🔍</div>
          <h3>Zoom Mode</h3>
          <p>Identify the card from an extreme close-up image.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="https://cdn.discordapp.com/emojis/1506149435179143248.png" alt="Price"></div>
          <h3>Price Mode</h3>
          <p>Pick the more expensive card. One wrong answer ends your streak.</p>
        </div>
        <div class="card">
          <div class="icon"><img src="https://cdn.discordapp.com/emojis/1506144706218950718.png" alt="Gacha"></div>
          <h3>Gacha</h3>
          <p>Open packs, collect cards, sell duplicates and trade with others.</p>
        </div>
      </div>

      <div class="links">
        <a class="btn" href="https://discord.com/oauth2/authorize?client_id=1313541894407716987&scope=bot+applications.commands&permissions=2048" target="_blank">Add to Discord</a>
        <a class="btn secondary" href="/banner">View Card Pool</a>
        <a class="btn secondary" href="/terms">Terms</a>
        <a class="btn secondary" href="/privacy">Privacy</a>
      </div>

      <footer>YGOGuesser is not affiliated with Konami. Card data by <a href="https://ygoprodeck.com" style="color:#FFD700">YGOPRODeck</a>.</footer>
    </body>
    </html>
    """


@app.get("/original-legends.png")
async def banner_image():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "public", "original-legends.png")
    return FileResponse(path, media_type="image/png")


@app.get("/terms", response_class=HTMLResponse)
async def terms():
    return """
    <html><head><title>YGOGuesser — Terms of Service</title></head>
    <body style="font-family:sans-serif;max-width:700px;margin:40px auto;padding:0 20px">
    <h1>Terms of Service</h1>
    <p><strong>Last updated:</strong> 2026</p>
    <p>By using the YGOGuesser Discord bot you agree to these terms.</p>
    <h2>1. Use of the Bot</h2>
    <p>YGOGuesser is a free entertainment bot. You agree to use it only for its intended purpose and not to abuse, exploit or attempt to disrupt its functionality.</p>
    <h2>2. Data</h2>
    <p>We store your Discord user ID, username and game scores to provide the ranking feature. No other personal data is collected.</p>
    <h2>3. Disclaimer</h2>
    <p>YGOGuesser is not affiliated with Konami and does not claim any rights over the Yu-Gi-Oh! trademark. All card data is provided by <a href="https://ygoprodeck.com">YGOPRODeck</a>.</p>
    <h2>4. Changes</h2>
    <p>We reserve the right to modify these terms at any time. Continued use of the bot constitutes acceptance of the updated terms.</p>
    <h2>Contact</h2>
    <p>For questions contact us via the bot's Discord server.</p>
    </body></html>
    """


@app.get("/privacy", response_class=HTMLResponse)
async def privacy():
    return """
    <html><head><title>YGOGuesser — Privacy Policy</title></head>
    <body style="font-family:sans-serif;max-width:700px;margin:40px auto;padding:0 20px">
    <h1>Privacy Policy</h1>
    <p><strong>Last updated:</strong> 2026</p>
    <h2>1. Data We Collect</h2>
    <p>When you use YGOGuesser we collect and store:</p>
    <ul>
      <li>Your Discord user ID</li>
      <li>Your Discord username</li>
      <li>Your game scores and results</li>
    </ul>
    <h2>2. How We Use It</h2>
    <p>This data is used exclusively to power the in-game ranking system. We do not sell, share or use your data for any other purpose.</p>
    <h2>3. Data Storage</h2>
    <p>Data is stored securely in Supabase. We do not store messages, server information or any other Discord data.</p>
    <h2>4. Data Deletion</h2>
    <p>To request deletion of your data, contact us via the bot's Discord server.</p>
    <h2>5. Contact</h2>
    <p>For privacy concerns contact us via the bot's Discord server.</p>
    </body></html>
    """


@app.get("/banner", response_class=HTMLResponse)
async def banner():
    from game.gacha import DUEL_MONSTERS_BANNER, GX_BANNER, FIVE_DS_BANNER

    ALL_BANNERS_WEB = [
        (DUEL_MONSTERS_BANNER, "Permanent banner"),
        (GX_BANNER, "Permanent banner"),
        (FIVE_DS_BANNER, "Current rotating banner"),
    ]

    rarity_labels = {"secret": "Secret Rare", "ultra": "Ultra Rare", "super": "Super Rare", "rare": "Rare", "common": "Common"}
    rarity_colors = {"secret": "#FFD700", "ultra": "#FFA500", "super": "#C0C0C0", "rare": "#0070DD", "common": "#9D9D9D"}
    rarity_probs = {"secret": "1%", "ultra": "4%", "super": "15%", "rare": "30%", "common": "50%"}
    rarity_emoji_imgs = {
        "secret": "https://cdn.discordapp.com/emojis/1506142199526461610.png",
        "ultra":  "https://cdn.discordapp.com/emojis/1506142184632746075.png",
        "super":  "https://cdn.discordapp.com/emojis/1506141953769865388.png",
        "rare":   "https://cdn.discordapp.com/emojis/1506141758222897262.png",
        "common": "https://cdn.discordapp.com/emojis/1506141315249733662.png",
    }

    def build_banner_html(b: dict) -> str:
        img_html = (
            f'<img src="{b["image_url"]}" style="max-width:100%;border-radius:12px;margin-bottom:24px;display:block">'
            if b.get("image_url") else ""
        )
        sections = ""
        for rarity in ("secret", "ultra", "super", "rare", "common"):
            cards = b.get(rarity, [])
            color = rarity_colors[rarity]
            emoji_img = f'<img src="{rarity_emoji_imgs[rarity]}" style="width:32px;height:32px;vertical-align:middle;margin-right:8px">'
            cards_html = "".join(
                f"""<div style="text-align:center;width:120px">
                      <img src="https://images.ygoprodeck.com/images/cards/{c['id']}.jpg"
                           width="100" style="border-radius:6px;border:2px solid {color}">
                      <div style="font-size:11px;margin-top:4px;color:#ddd">{c['name']}</div>
                    </div>"""
                for c in cards
            )
            sections += f"""
            <div style="margin-bottom:32px">
              <h3 style="color:{color};margin-bottom:4px">{emoji_img}{rarity_labels[rarity]} <span style="font-size:14px;color:#aaa">— {rarity_probs[rarity]}</span></h3>
              <p style="color:#888;margin:0 0 12px">{len(cards)} cards in pool</p>
              <div style="display:flex;flex-wrap:wrap;gap:12px">{cards_html}</div>
            </div>"""
        return f"{img_html}{sections}"

    ygo_icon = '<img src="https://cdn.discordapp.com/emojis/1506144706218950718.png" style="width:40px;height:40px;vertical-align:middle;margin-right:10px">'
    body_parts = []
    for i, (banner, label) in enumerate(ALL_BANNERS_WEB):
        if i > 0:
            body_parts.append('<hr style="border-color:#333;margin:48px 0">')
        body_parts.append(f'<h1 style="color:#FFD700">{ygo_icon}{banner["name"]} <span style="font-size:16px;color:#aaa">— {label}</span></h1>')
        body_parts.append(build_banner_html(banner))
    banners_html = "\n".join(body_parts)

    return f"""
    <html>
    <head><title>YGOGuesser — Banners</title><meta charset="utf-8"></head>
    <body style="font-family:sans-serif;background:#1a1a2e;color:#eee;max-width:1000px;margin:40px auto;padding:0 20px">
      {banners_html}
    </body>
    </html>
    """


@app.post("/")
async def interactions(request: Request, background_tasks: BackgroundTasks):
    signature = request.headers.get("X-Signature-Ed25519", "")
    timestamp = request.headers.get("X-Signature-Timestamp", "")
    body = await request.body()

    if not verify_signature(body, signature, timestamp):
        raise HTTPException(status_code=401, detail="Invalid request signature")

    payload = json.loads(body)

    if payload["type"] == 1:
        return JSONResponse({"type": 1})

    if payload["type"] == 2:
        background_tasks.add_task(process_command, payload, payload["token"])
        return JSONResponse({"type": 5})

    if payload["type"] == 3:
        custom_id = payload["data"]["custom_id"]
        background_tasks.add_task(process_component, payload, payload["token"])
        # Buttons that update in-place vs create a new message
        updates_in_place = (
            custom_id.startswith("price_") or
            custom_id.startswith("coleccion_") or
            custom_id.startswith("vender_confirmar:") or
            custom_id.startswith("vender_cancelar:") or
            custom_id.startswith("gacha_x10:") or
            custom_id.startswith("ranking_mode:") or
            custom_id.startswith("sobre_banner:") or
            custom_id.startswith("faltan_page:") or
            custom_id.startswith("trade_accept:") or
            custom_id.startswith("trade_reject:")
        )
        response_type = 6 if updates_in_place else 5
        return JSONResponse({"type": response_type})

    return JSONResponse({"type": 1})
