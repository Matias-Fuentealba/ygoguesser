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

COMMANDS = [
    {
        "name": "jugar",
        "description": "Inicia una nueva partida de adivinanza de cartas Yu-Gi-Oh.",
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
                "description": "Nombre de la carta que querés adivinar",
                "type": 3,  # STRING
                "required": True,
            }
        ],
    },
    {
        "name": "rendirse",
        "description": "Abandona la partida actual y revela la carta.",
    },
    {
        "name": "ranking",
        "description": "Muestra el top 10 de jugadores.",
    },
    {
        "name": "zoom",
        "description": "Inicia una partida de zoom: adivina la carta a partir de una imagen muy zoomeada.",
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
]

url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"
headers = {"Authorization": f"Bot {BOT_TOKEN}"}

resp = requests.put(url, headers=headers, json=COMMANDS)
if resp.status_code == 200:
    for cmd in resp.json():
        print(f"✅ /{cmd['name']}")
else:
    print(f"❌ Error {resp.status_code}: {resp.text}")
