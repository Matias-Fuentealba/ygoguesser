import discord
from discord.ext import commands
import random
import requests
import re
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

juegos = {}


def obtener_carta_aleatoria():
    tipos_de_monstruo = [
        "Normal Monster", "Effect Monster", "Fusion Monster", "Ritual Monster",
        "Synchro Monster", "XYZ Monster", "Link Monster"
    ]
    cartas = []
    try:
        for tipo in tipos_de_monstruo:
            url = f"https://db.ygoprodeck.com/api/v7/cardinfo.php?type={tipo.replace(' ', '%20')}"
            response = requests.get(url)
            if response.status_code == 200:
                datos = response.json()
                if "data" in datos:
                    for carta in datos["data"]:
                        if "Monster" in carta["type"]:
                            cartas.append(carta)
        return random.choice(cartas) if cartas else None
    except requests.exceptions.RequestException as e:
        print(f"Error al conectar con la API: {e}")
        return None


def inicializar_juego():
    carta = obtener_carta_aleatoria()
    if carta:
        palabra_secreta_original = carta['name']
        palabra_secreta = re.sub(r'[^a-zA-Z0-9]', '', palabra_secreta_original).lower()
        pistas = [
            f"Tipo de carta: {carta['type']}",
            f"Nivel: {carta.get('level', 'N/A')}",
            f"Tipo de monstruo: {carta.get('race', 'Desconocido')}",
            f"Atributo: {carta.get('attribute', 'Sin atributo')}",
            f"Ataque: {carta.get('atk', 'N/A')}",
        ]
        random.shuffle(pistas)
        return {
            'palabra_secreta': palabra_secreta,
            'estado_palabra': ["_"] * len(palabra_secreta),
            'intentos_restantes': 6,
            'letras_adivinadas': [],
            'pistas': pistas,
            'pistas_reveladas': 0,
            'carta_info': {
                'imagen': carta['card_images'][0]['image_url'] if carta.get('card_images') else '',
                'descripcion': carta.get('desc', 'Descripción no disponible.'),
                'tipo': carta['type'],
                'nombre_original': palabra_secreta_original
            }
        }
    return None


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user}')


@bot.command()
async def start(ctx):
    juego = inicializar_juego()
    if juego:
        juegos[ctx.author.id] = juego
        await ctx.send(f"¡Juego iniciado! La palabra tiene {len(juego['palabra_secreta'])} letras. Usa `!guess <letra>` para adivinar.")
    else:
        await ctx.send("No se pudo obtener una carta. Intenta de nuevo más tarde.")


@bot.command()
async def guess(ctx, letra: str):
    juego = juegos.get(ctx.author.id)
    if not juego:
        await ctx.send("No tienes un juego en curso. Usa `!start` para iniciar uno.")
        return

    letra = letra.lower()
    if len(letra) != 1 or not letra.isalnum():
        await ctx.send("Por favor, ingresa una sola letra o número válido.")
        return

    if letra in juego['letras_adivinadas']:
        await ctx.send("¡Ya adivinaste esa letra!")
        return

    juego['letras_adivinadas'].append(letra)

    if letra in juego['palabra_secreta']:
        for i, l in enumerate(juego['palabra_secreta']):
            if l == letra:
                juego['estado_palabra'][i] = letra

        palabra_con_guiones = " ".join([
            estado if estado != "_" else "_"
            if not original.isspace() else " "
            for original, estado in zip(juego['carta_info']['nombre_original'], juego['estado_palabra'])
        ]).strip()

        await ctx.send(f"¡Correcto! Estado actual: {palabra_con_guiones}")

        if "_" not in juego['estado_palabra']:
            await enviar_resultado(ctx, juego, 'ganaste')
            juegos.pop(ctx.author.id)
    else:
        juego['intentos_restantes'] -= 1

        if juego['intentos_restantes'] <= 0:
            await enviar_resultado(ctx, juego, 'perdiste')
            juegos.pop(ctx.author.id)
            return

        palabra_con_guiones = " ".join([
            estado if estado != "_" else "_"
            if not original.isspace() else " "
            for original, estado in zip(juego['carta_info']['nombre_original'], juego['estado_palabra'])
        ]).strip()

        await ctx.send(f"Incorrecto. Intentos restantes: {juego['intentos_restantes']}\nEstado actual: {palabra_con_guiones}")


async def enviar_resultado(ctx, juego, estado):
    carta_info = juego['carta_info']
    embed = discord.Embed(
        title="¡Resultado del juego!",
        description=f"Estado: {'¡Ganaste! 🎉' if estado == 'ganaste' else '¡Perdiste! 😢'}",
        color=discord.Color.green() if estado == 'ganaste' else discord.Color.red()
    )
    embed.add_field(name="La palabra era:", value=carta_info['nombre_original'], inline=False)
    embed.add_field(name="Descripción de la carta:", value=carta_info['descripcion'], inline=False)
    if carta_info['imagen']:
        embed.set_image(url=carta_info['imagen'])
    await ctx.send(embed=embed)


@bot.command()
async def pistas(ctx):
    juego = juegos.get(ctx.author.id)
    if not juego:
        await ctx.send("No tienes un juego en curso. Usa `!start` para iniciar uno.")
        return

    intentos_fallidos = 6 - juego['intentos_restantes']
    pistas_disponibles = juego['pistas'][:intentos_fallidos]

    if pistas_disponibles:
        await ctx.send("Pistas disponibles:\n" + "\n".join(pistas_disponibles))
    else:
        await ctx.send("Aún no has desbloqueado ninguna pista.")


TOKEN = os.environ.get("DISCORD_TOKEN")
if not TOKEN:
    raise ValueError("Falta la variable de entorno DISCORD_TOKEN")
bot.run(TOKEN)
