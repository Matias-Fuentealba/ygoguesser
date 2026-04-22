import os
import sys
import io
import json
import httpx

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
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

        # Plain text or simple dict with content
        elif isinstance(response, dict):
            await client.patch(url, json={"content": response.get("content", "")})

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
    elif command == "zoom":
        response = await gm.start_zoom(user_id, username)
    elif command == "adivinar-zoom":
        options = payload["data"].get("options", [])
        guess = options[0]["value"] if options else ""
        response = await gm.guess_zoom(user_id, username, guess)
    elif command == "zoom-pista":
        response = await gm.next_zoom(user_id)
    else:
        response = "Comando no reconocido."

    await send_followup(token, response)


@app.get("/")
async def health():
    return {"status": "ok"}


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

    return JSONResponse({"type": 1})
