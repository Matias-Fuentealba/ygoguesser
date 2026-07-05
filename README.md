# YGOGuesser

Bot de Discord para adivinar cartas de Yu-Gi-Oh! con sistema de gacha, colección e intercambios.

## Modos de juego

- **Hints** — Se revelan pistas progresivas sobre la carta. Menos pistas = más puntos.
- **Zoom** — Hay que identificar la carta desde un recorte extremo de su imagen.
- **Price** — Elegir la carta más cara entre dos opciones. Un error termina la racha.

## Sistema de gacha

Abre sobres gratuitos cada hora o usa monedas para hacer pulls x10. Hay tres banners activos con pools de cartas de distintas eras del anime.

## Comandos principales

| Comando | Descripción |
|---|---|
| `/play` | Iniciar partida |
| `/hint` | Revelar siguiente pista |
| `/guess` | Adivinar la carta |
| `/zoom-hint` | Avanzar al siguiente nivel de zoom |
| `/surrender` | Abandonar la partida |
| `/pack` | Abrir sobre gratuito |
| `/gacha` | Ver info de banners y pool de cartas |
| `/collection` | Ver tu colección |
| `/sell` | Vender duplicados por monedas |
| `/protect` | Proteger/desproteger una carta de la venta |
| `/trade` | Proponer un intercambio con otro usuario |
| `/vote` | Votar en top.gg y ganar 200 monedas |
| `/ranking` | Top 10 jugadores |
| `/config` | Configurar el bot (solo admins) |

## Stack

- **Backend**: FastAPI desplegado en Vercel (webhooks de Discord)
- **Base de datos**: Supabase (PostgreSQL)
- **APIs externas**: YGOPRODeck (datos de cartas), top.gg (votos)

## Self-hosting

### 1. Requisitos

- Python 3.11+
- Cuenta en [Supabase](https://supabase.com)
- Aplicación de Discord en [Discord Developer Portal](https://discord.com/developers)
- Cuenta en [Vercel](https://vercel.com) (o cualquier hosting compatible con FastAPI)

### 2. Variables de entorno

Copia `.env.example` a `.env` y completa los valores:

```
DISCORD_TOKEN=
DISCORD_PUBLIC_KEY=
DISCORD_APPLICATION_ID=
DISCORD_GUILD_ID=       # servidor de prueba para registrar comandos
SUPABASE_URL=
SUPABASE_KEY=
TOPGG_TOKEN=            # opcional, para el comando /vote
TOPGG_WEBHOOK_SECRET=   # opcional, para recibir notificaciones de voto
```

### 3. Base de datos

Crea las tablas en Supabase ejecutando el schema SQL (tablas: users, games, collection, trades, channel_locks, guild_settings).

### 4. Registrar comandos

```bash
python register_commands.py
```

### 5. Deploy

En Vercel, agrega todas las variables de entorno del paso 2 en Settings → Environment Variables y haz deploy del repositorio. El archivo `vercel.json` ya está configurado.

---

YGOGuesser no está afiliado con Konami. Datos de cartas provistos por [YGOPRODeck](https://ygoprodeck.com).
