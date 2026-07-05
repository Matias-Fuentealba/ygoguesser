"""
Ejecutar una vez para registrar los slash commands en Discord:
  python register_commands.py
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv()

APPLICATION_ID = os.environ["DISCORD_APPLICATION_ID"]
BOT_TOKEN = os.environ["DISCORD_TOKEN"]

GUILD_ID = os.environ["DISCORD_GUILD_ID"]

ES = ["es-ES", "es-419"]


def es(name: str) -> dict:
    return {code: name for code in ES}


COMMANDS = [
    {
        "name": "help",
        "description": "Shows all available commands.",
        "description_localizations": {code: "Muestra todos los comandos disponibles." for code in ES},
    },
    {
        "name": "play",
        "name_localizations": es("jugar"),
        "description": "Start a new YGOGuesser game.",
        "description_localizations": {code: "Inicia una nueva partida de YGOGuesser." for code in ES},
    },
    {
        "name": "hint",
        "name_localizations": es("pista"),
        "description": "Reveal the next hint about the card (reduces possible score).",
        "description_localizations": {code: "Revela la siguiente pista sobre la carta (reduce el puntaje posible)." for code in ES},
    },
    {
        "name": "guess",
        "name_localizations": es("adivinar"),
        "description": "Try to guess the name of the card.",
        "description_localizations": {code: "Intenta adivinar el nombre de la carta." for code in ES},
        "options": [
            {
                "name": "card",
                "name_localizations": es("carta"),
                "description": "Name of the card you want to guess",
                "description_localizations": {code: "Nombre de la carta que quieres adivinar" for code in ES},
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "zoom-hint",
        "name_localizations": es("zoom-pista"),
        "description": "Advance to the next zoom level (reduces possible score).",
        "description_localizations": {code: "Avanza al siguiente nivel de zoom (reduce el puntaje posible)." for code in ES},
    },
    {
        "name": "surrender",
        "name_localizations": es("rendirse"),
        "description": "Abandon the current game.",
        "description_localizations": {code: "Abandona la partida actual." for code in ES},
    },
    {
        "name": "ranking",
        "description": "Shows the top 10 players.",
        "description_localizations": {code: "Muestra el top 10 de jugadores." for code in ES},
    },
    {
        "name": "pack",
        "name_localizations": es("sobre"),
        "description": "Open a free pack (1h cooldown) and get cards from the current banner.",
        "description_localizations": {code: "Abre un sobre gratis (1h de cooldown) y obtén cartas del banner actual." for code in ES},
    },
    {
        "name": "collection",
        "name_localizations": es("coleccion"),
        "description": "Shows all the cards you've collected.",
        "description_localizations": {code: "Muestra todas las cartas que has conseguido." for code in ES},
    },
    {
        "name": "gacha",
        "description": "Current banner info: odds, card pool and how it works.",
        "description_localizations": {code: "Info del banner actual: probabilidades, pool de cartas y cómo funciona." for code in ES},
    },
    {
        "name": "sell",
        "name_localizations": es("vender"),
        "description": "Sell your duplicate cards in exchange for coins.",
        "description_localizations": {code: "Vende tus cartas duplicadas a cambio de monedas." for code in ES},
    },
    {
        "name": "protect",
        "name_localizations": es("proteger"),
        "description": "Protect or unprotect a card from being sold.",
        "description_localizations": {code: "Protege o desprotege una carta de tu colección para evitar que se venda." for code in ES},
        "options": [
            {
                "name": "card",
                "name_localizations": es("carta"),
                "description": "Name of the card to protect/unprotect",
                "description_localizations": {code: "Nombre de la carta a proteger/desproteger" for code in ES},
                "type": 3,
                "required": True,
            }
        ],
    },
    {
        "name": "trade",
        "name_localizations": es("intercambiar"),
        "description": "Propose a card trade with another user.",
        "description_localizations": {code: "Propone un intercambio de cartas con otro usuario." for code in ES},
        "options": [
            {
                "name": "user",
                "name_localizations": es("usuario"),
                "description": "User to trade with",
                "description_localizations": {code: "Usuario con quien intercambiar" for code in ES},
                "type": 6,
                "required": True,
            },
            {
                "name": "my_card",
                "name_localizations": es("mi_carta"),
                "description": "Card you are offering",
                "description_localizations": {code: "Carta que ofreces" for code in ES},
                "type": 3,
                "required": True,
            },
            {
                "name": "their_card",
                "name_localizations": es("su_carta"),
                "description": "Card you want in return",
                "description_localizations": {code: "Carta que pides a cambio" for code in ES},
                "type": 3,
                "required": True,
            },
        ],
    },
    {
        "name": "vote",
        "description": "Vote for YGOGuesser on top.gg and earn 200 coins.",
        "description_localizations": {code: "Vota por YGOGuesser en top.gg y gana 200 monedas." for code in ES},
    },
    {
        "name": "config",
        "description": "Configure channel restrictions for commands (admins only).",
        "description_localizations": {code: "Configura restricciones de canal para los comandos (solo admins)." for code in ES},
        "options": [
            {
                "name": "action",
                "name_localizations": es("accion"),
                "description": "Action to perform",
                "description_localizations": {code: "Acción a realizar" for code in ES},
                "type": 3,
                "required": True,
                "choices": [
                    {"name": "lock", "name_localizations": es("lockear"), "value": "lock"},
                    {"name": "unlock", "name_localizations": es("desbloquear"), "value": "unlock"},
                    {"name": "view", "name_localizations": es("ver"), "value": "view"},
                ],
            },
            {
                "name": "command",
                "name_localizations": es("comando"),
                "description": "Command name to configure",
                "description_localizations": {code: "Nombre del comando a configurar" for code in ES},
                "type": 3,
                "required": False,
            },
            {
                "name": "channel",
                "name_localizations": es("canal"),
                "description": "Channel where the command will be allowed",
                "description_localizations": {code: "Canal donde se permitirá el comando" for code in ES},
                "type": 7,
                "required": False,
            },
            {
                "name": "language",
                "name_localizations": es("idioma"),
                "description": "Set bot language for this server (en / es)",
                "description_localizations": {code: "Idioma del bot para este servidor (en / es)" for code in ES},
                "type": 3,
                "required": False,
                "choices": [
                    {"name": "English", "value": "en"},
                    {"name": "Español", "value": "es"},
                ],
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
