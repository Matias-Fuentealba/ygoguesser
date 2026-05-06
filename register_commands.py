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
        "name": "help",
        "description": "Muestra todos los comandos disponibles.",
    },
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
    {
        "name": "gacha",
        "description": "Info del banner actual: probabilidades, pool de cartas y cómo funciona.",
    },
    {
        "name": "vender",
        "description": "Vende tus cartas duplicadas a cambio de monedas.",
    },
    {
        "name": "proteger",
        "description": "Protege o desprotege una carta de tu colección para evitar que se venda.",
        "options": [
            {
                "name": "carta",
                "description": "Nombre de la carta a proteger/desproteger",
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "config",
        "description": "Configura restricciones de canal para los comandos (solo admins).",
        "options": [
            {
                "name": "accion",
                "description": "Acción a realizar",
                "type": 3,
                "required": True,
                "choices": [
                    {"name": "lockear", "value": "lockear"},
                    {"name": "desbloquear", "value": "desbloquear"},
                    {"name": "ver", "value": "ver"},
                ],
            },
            {
                "name": "comando",
                "description": "Nombre del comando a configurar",
                "type": 3,
                "required": False,
            },
            {
                "name": "canal",
                "description": "Canal donde se permitirá el comando",
                "type": 7,
                "required": False,
            },
        ],
    },
]

headers = {"Authorization": f"Bot {BOT_TOKEN}"}

# Guild (instantáneo, para testing)
guild_url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/guilds/{GUILD_ID}/commands"
resp = requests.put(guild_url, headers=headers, json=COMMANDS)
print(f"Guild ({GUILD_ID}):")
if resp.status_code == 200:
    for cmd in resp.json():
        print(f"  ✅ /{cmd['name']}")
else:
    print(f"  ❌ Error {resp.status_code}: {resp.text}")

# Global (hasta 1h para propagar a todos los servers)
global_url = f"https://discord.com/api/v10/applications/{APPLICATION_ID}/commands"
resp = requests.put(global_url, headers=headers, json=COMMANDS)
print(f"\nGlobal:")
if resp.status_code == 200:
    for cmd in resp.json():
        print(f"  ✅ /{cmd['name']}")
else:
    print(f"  ❌ Error {resp.status_code}: {resp.text}")
