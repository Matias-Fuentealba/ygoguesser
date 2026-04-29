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
            await client.patch(url, json=response)

        # Plain text or simple dict with content (and optional components)
        elif isinstance(response, dict):
            await client.patch(url, json=response)

        else:
            await client.patch(url, json={"content": response})


async def process_command(payload: dict, token: str):
    command = payload["data"]["name"]
    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user", {})
    user_id = user.get("id", "")
    username = user.get("username", "unknown")

    db = Database()
    gm = GameManager(db)

    if command == "jugar":
        response = await gm.start_game(user_id, username)
    elif command == "pista":
        response = await gm.get_hint(user_id)
    elif command == "adivinar":
        options = payload["data"].get("options", [])
        guess = options[0]["value"] if options else ""
        response = await gm.make_guess(user_id, username, guess)
    elif command == "rendirse":
        response = await gm.surrender(user_id)
    elif command == "ranking":
        response = await gm.get_ranking()
    elif command == "sobre":
        response = await gm.open_sobre(user_id, username)
    elif command == "coleccion":
        response = await gm.get_collection(user_id)
    elif command == "gacha":
        response = await gm.get_gacha_info()
    elif command == "adivinar-zoom":
        options = payload["data"].get("options", [])
        guess = options[0]["value"] if options else ""
        response = await gm.guess_zoom(user_id, username, guess)
    elif command == "zoom-pista":
        response = await gm.next_zoom(user_id)
    else:
        response = "Comando no reconocido."

    await send_followup(token, response)


async def process_component(payload: dict, token: str):
    custom_id = payload["data"]["custom_id"]
    member = payload.get("member") or {}
    user = member.get("user") or payload.get("user", {})
    user_id = user.get("id", "")
    username = user.get("username", "unknown")

    db = Database()
    gm = GameManager(db)

    if custom_id == "mode_hints":
        response = await gm.start_hints_game(user_id, username)
    elif custom_id == "mode_zoom":
        response = await gm.start_zoom(user_id, username)
    elif custom_id == "mode_price":
        response = await gm.start_price_game(user_id, username)
    elif custom_id in ("price_1", "price_2"):
        choice = int(custom_id[-1])
        response = await gm.choose_price(user_id, choice)
    elif custom_id == "gacha_x10":
        response = await gm.open_sobre_x10(user_id)
    else:
        response = "Acción no reconocida."

    await send_followup(token, response)


@app.get("/")
async def health():
    return {"status": "ok"}


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
    <p><strong>Last updated:</strong> 2025</p>
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
    <p><strong>Last updated:</strong> 2025</p>
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
    from game.gacha import DUEL_MONSTERS_BANNER, RARITY_EMOJIS

    rarity_labels = {
        "secret": "Secret Rare",
        "ultra":  "Ultra Rare",
        "super":  "Super Rare",
        "rare":   "Rare",
        "common": "Common",
    }
    rarity_colors = {
        "secret": "#FFD700",
        "ultra":  "#FFA500",
        "super":  "#C0C0C0",
        "rare":   "#0070DD",
        "common": "#9D9D9D",
    }

    rarity_probs = {"secret": "1%", "ultra": "4%", "super": "15%", "rare": "30%", "common": "50%"}

    sections = ""
    for rarity in ("secret", "ultra", "super", "rare", "common"):
        cards = DUEL_MONSTERS_BANNER.get(rarity, [])
        emoji = RARITY_EMOJIS[rarity]
        label = rarity_labels[rarity]
        color = rarity_colors[rarity]
        prob = rarity_probs[rarity]
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
          <h2 style="color:{color};margin-bottom:4px">{emoji} {label} <span style="font-size:16px;color:#aaa">— {prob}</span></h2>
          <p style="color:#888;margin:0 0 12px">{len(cards)} cartas en el pool</p>
          <div style="display:flex;flex-wrap:wrap;gap:12px">{cards_html}</div>
        </div>"""

    banner_img = DUEL_MONSTERS_BANNER.get("image_url", "")
    banner_img_html = (
        f'<img src="{banner_img}" style="max-width:100%;border-radius:12px;margin-bottom:24px;display:block">'
        if banner_img else ""
    )

    return f"""
    <html>
    <head>
      <title>YGOGuesser — Banner: {DUEL_MONSTERS_BANNER['name']}</title>
      <meta charset="utf-8">
    </head>
    <body style="font-family:sans-serif;background:#1a1a2e;color:#eee;max-width:1000px;margin:40px auto;padding:0 20px">
      <h1 style="color:#FFD700">🎴 Banner: {DUEL_MONSTERS_BANNER['name']}</h1>
      {banner_img_html}
      {sections}
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
        # Price buttons update the existing message; everything else creates a new one
        response_type = 6 if custom_id.startswith("price_") else 5
        return JSONResponse({"type": response_type})

    return JSONResponse({"type": 1})
