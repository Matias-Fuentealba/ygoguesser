"""
Run once to register slash commands with Discord:
  python register_commands.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
BOT_TOKEN = os.environ["DISCORD_TOKEN"]

GUILD_ID = "916429226171826236"

COMMANDS = [
    {
        "name": "jugar",
        "description": "Inicia una nueva partida de YGOGuesser.",
    },
    {
        "name": "pista",
        "description": "Revela la siguiente pista sobre la carta (reduce el puntaje posible).",
    },
    {
        "name": "adivinar",
        "description": "Intenta adivinar el nombre de la carta.",
        "options": [
            {
                "name": "carta",
                "description": "Nombre de la carta que quieres adivinar",
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "adivinar-zoom",
        "description": "Intenta adivinar la carta en el modo zoom.",
        "options": [
            {
                "name": "carta",
                "description": "Nombre de la carta que quieres adivinar",
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "zoom-pista",
        "description": "Avanza al siguiente nivel de zoom (reduce el puntaje posible).",
    },
    {
        "name": "rendirse",
        "description": "Abandona la partida actual.",
    },
    {
        "name": "ranking",
        "description": "Muestra el top 10 de jugadores.",
    },
    {
        "name": "sobre",
        "description": "Abre un sobre gratis (1h de cooldown) y obtén cartas del banner actual.",
    },
    {
        "name": "coleccion",
        "description": "Muestra todas las cartas que has conseguido.",
    },
]

url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"
headers = {"Authorization": f"Bot {BOT_TOKEN}"}

resp = requests.put(url, headers=headers, json=COMMANDS)
if resp.status_code == 200:
    for cmd in resp.json():
        print(f"✅ /{cmd['name']}")
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")
