STRINGS = {
    "en": {
        # General
        "no_active_game": "You don't have an active game. Use `/play` to start one.",
        "cannot_fetch_card": "Could not fetch a card. Please try again later.",
        "cannot_process_image": "Could not process the image. Please try again.",

        # start_game
        "game_already_active_hints": "You already have an active game. Use `/hint` and `/guess` or `/surrender`.",
        "game_already_active_zoom": "You already have an active game. Use `/zoom-hint` and `/guess` or `/surrender`.",
        "game_already_active_price": "You already have an active game. Use the buttons or `/surrender`.",
        "game_already_active_other": "You already have an active game. Use `/surrender` to abandon it.",
        "welcome_body": (
            "🎮 **Welcome to YGOGuesser!**\n\n"
            "Test your Yu-Gi-Oh! card knowledge. Choose a mode:\n\n"
            "🃏 **Hints Mode** — Progressive hints are revealed about a card. The fewer hints you use, the more points you earn.\n"
            "🔍 **Zoom Mode** — A heavily zoomed-in image of the card is shown. If you're wrong, the zoom slowly pulls back.\n"
            "💰 **Price Mode** — Two cards are shown. Guess which one is more expensive on the TCG market. One wrong answer ends your streak!\n"
        ),
        "btn_hints": "🃏 Hints Mode",
        "btn_zoom": "🔍 Zoom Mode",
        "btn_price": "💰 Price Mode",

        # hints game
        "hints_started": (
            "🃏 **Hints Mode started!**\n\n"
            "Here's the first hint:\n{hint}\n\n"
            "You have up to **{max_hints} hints** available.\n"
            "➡️ Use `/hint` for more hints or `/guess card:<name>` to attempt."
        ),
        "hint_all_revealed": "You've already revealed all hints ({max_hints}/{max_hints}). Use `/guess` or `/surrender`.",
        "hint_text": "💡 Hint {n}/{max_hints}:\n{hint}\n\nAnswering now is worth **{score} points**.",
        "hint_not_available_zoom": "❌ `/hint` is not available in Zoom Mode. Use `/zoom-hint` to advance the zoom.",

        # guess
        "correct_hints": "✅ **Correct!** The card was **{name}**.\n🏆 You earned **{score} points** (hints used: {hints}/{max_hints}).",
        "wrong_attempts_left": "❌ **Wrong.** You have **{remaining} attempt{s}** left with the current hint.",
        "wrong_all_attempts": "💀 **Out of attempts.** The card was **{name}**.",
        "wrong_auto_hint": (
            "❌ Used up all 3 attempts for this hint. Here's the next hint automatically:\n\n"
            "💡 Hint {n}/{max_hints}:\n{hint}\n\nAnswering now is worth **{score} points**."
        ),

        # surrender
        "surrender_price": "🏳️ You surrendered the price game. Final score: **{score} points** · **{coins} coins** 💰.",
        "surrender_hints": "🏳️ You surrendered. The card was **{name}**.",

        # zoom
        "zoom_already_active": "You already have an active game. Use `{cmd}` or `/surrender`.",
        "zoom_started": (
            "🔍 **Zoom Mode started!**\n"
            "Guess the card at zoom level 1/{max_levels}.\n"
            "Answering now is worth **{score} points**. You have **3 attempts** per level.\n"
            "➡️ `/guess card:<name>` to attempt.\n"
            "➡️ `/zoom-hint` to see more of the image (lowers the score)."
        ),
        "zoom_correct": "✅ **Correct!** The card was **{name}**.\n🏆 You earned **{score} points** (zoom level {level}/{max_levels}{hints_note}).",
        "zoom_hints_note": " · {n} hint{s} used",
        "zoom_wrong_attempts_left": "❌ **Wrong.** You have **{remaining} attempt{s}** left at this zoom level.",
        "zoom_wrong_all_attempts": "💀 **Out of attempts.** The card was **{name}**.",
        "zoom_wrong_auto_advance": (
            "❌ Out of attempts. Here's the next zoom level:\n"
            "🔍 Zoom level {level}/{max_levels} — Answering now is worth **{score} points**."
        ),
        "zoom_hint_next": "🔍 Zoom level {level}/{max_levels} — Answering now is worth **{score} points**.",
        "zoom_hint_max": "You're already at the maximum zoom level ({level}/{max_levels}). Use `/guess` or `/surrender`.",
        "zoom_no_game": "❌ `/zoom-hint` is only available in Zoom Mode. Use `/play` to start.",

        # price
        "price_no_cards": "Could not fetch cards with prices. Please try again.",
        "price_question": "💰 **Which card is more expensive?** | Score: **{score}**",
        "price_correct_prefix": "✅ Correct! **{card}** was worth **${price:.2f}** vs **${other:.2f}** (+5 💰)\n\n",
        "price_win": "✅ Correct! No more cards available. Final score: **{score} points** · **{coins} coins** 💰.",
        "price_wrong": (
            "❌ **Wrong.** The most expensive was **{card}** "
            "at **${price:.2f}** (vs **${other:.2f}**).\n"
            "🏆 Final score: **{score} points** · **{coins} coins** 💰."
        ),
        "price_no_game": "You don't have an active price game. Use `/play` to start.",
        "btn_card1": "Card 1",
        "btn_card2": "Card 2",

        # gacha / packs
        "pack_cooldown": (
            "⏳ Your next free pack will be available in **{mins}m {secs}s**.\n"
            "💰 You have **{coins} coins** available."
        ),
        "pack_cooldown_hint": "\n> 💡 Earn coins by playing games with `/play`.",
        "pack_available": "🎴 **Pack available!** Which banner do you want to pull from?\n💰 You have **{coins} coins** available.",
        "pack_already_used": "⏳ Pack already used. Next one available in **{mins}m {secs}s**.",
        "pack_opened": "🎴 Pack opened! — {banner}",
        "pack_x10_opened": "🎴 Opened 10 packs! — {banner}",
        "pack_x10_no_user": "Use `/pack` first to register.",
        "pack_x10_no_coins": "❌ You need **{cost} coins** but you only have **{coins}**.",
        "pack_x10_insufficient": "❌ Not enough coins.",
        "pack_new_card_footer": "<:newicon:1506143726840578139> = new card in your collection",
        "pack_coins_remaining": "💰 Coins remaining: {coins}",
        "btn_pack_perm": "✨ Original Legends",
        "btn_pack_rot": "🆕 Next Generation",
        "btn_x10_perm": "x10 Original Legends ({cost}💰)",
        "btn_x10_rot": "x10 Next Generation ({cost}💰)",

        # collection
        "collection_empty": "You don't have any cards yet. Use `/pack` to open your first pack.",
        "collection_title": "📦 Collection — {unique} unique · {copies} copies",
        "collection_footer": "Page {page} / {total}  •  Use /pack to get more cards",

        # sell
        "sell_no_duplicates": "You have no duplicate cards to sell.",
        "sell_no_duplicates_protected": "You have no sellable duplicates. You have **{count}** protected duplicate(s) 🔒.",
        "sell_title": "🗑️ Sell duplicates — {extras} extra copies → {coins} coins",
        "sell_confirm_btn": "🗑️ Confirm sale ({coins} coins)",
        "sell_cancel_btn": "Cancel",
        "sell_nothing": "No duplicates to sell.",
        "sell_done_title": "✅ Duplicates sold",
        "sell_done_desc": "You earned **{coins} coins** 💰\nCurrent balance: **{balance} coins**",
        "sell_cancelled": "Sale cancelled.",

        # protect
        "protect_not_found": "❌ You don't have any card matching **{name}** in your collection.",
        "protect_on": "🔒 **{name}** is now protected.",
        "protect_off": "🔓 **{name}** is now unprotected.",

        # ranking
        "ranking_empty_score": "No games registered yet.",
        "ranking_empty_collection": "Nobody has any cards yet.",
        "ranking_title_score": "🏆 Ranking — Top 10 Points",
        "ranking_title_collection": "📦 Collection Ranking — All banners",
        "ranking_collection_footer": "{total} unique cards in total",
        "btn_ranking_score": "🏆 Points",
        "btn_ranking_collection": "📦 Collection",

        # gacha info
        "gacha_how_it_works": (
            "**How it works?**\n"
            "You earn **coins** by playing — they're stored separately from the ranking, spending them doesn't lower your position.\n\n"
            "🆓 **`/pack`** — 5 free cards every hour (choose banner)\n"
            "💰 **x10** — 10 cards for **{cost} coins**, guarantees at least 1 Ultra Rare\n\n"
            "🔗 [See all cards in the pool](https://ygoguesser.vercel.app/banner)\n\n"
        ),
        "gacha_probs": (
            "**Odds:**\n"
            "{secret} Secret Rare — 1%\n"
            "{ultra} Ultra Rare — 4%\n"
            "{super} Super Rare — 15%\n"
            "{rare} Rare — 30%\n"
            "{common} Common — 50%\n\n"
            "**Pool:** {pool_line}\n"
            "{missing_summary}"
        ),
        "gacha_complete": "✅ Complete collection",
        "gacha_missing": "📋 You're missing **{missing}/{total}** cards",
        "gacha_banner_rotating": "🔄 Rotating banner",
        "gacha_banner_permanent": "♾️ Permanent banner",
        "btn_missing_rot": "📋 Missing Next Generation",
        "btn_missing_perm": "📋 Missing Original Legends",

        # missing cards
        "missing_complete": "✅ You have all cards from **{banner}**!",
        "missing_title": "📋 Missing cards — {banner} ({count} remaining)",

        # trade
        "trade_self": "❌ You can't trade cards with yourself.",
        "trade_no_from_card": "❌ You don't have any card matching **{name}**.",
        "trade_from_protected": "❌ **{name}** is protected. Unprotect it first with `/protect`.",
        "trade_no_to_card": "❌ <@{user}> doesn't have any card matching **{name}**.",
        "trade_to_protected": "❌ **{name}** from <@{user}> is protected.",
        "trade_offer": "<@{to}> — <@{from_}> is proposing a trade:",
        "trade_offers": "📤 Offers",
        "trade_wants": "📥 Wants",
        "trade_not_found": "❌ Trade not found.",
        "trade_not_active": "❌ This trade is no longer active.",
        "trade_wrong_user_accept": "❌ Only the user the trade was proposed to can accept it.",
        "trade_wrong_user_reject": "❌ Only the user the trade was proposed to can reject it.",
        "trade_failed": "❌ Trade failed. One of you no longer has the card.",
        "trade_completed": "✅ Trade completed!\n<@{from_}> received **{to_card}**\n<@{to}> received **{from_card}**",
        "trade_rejected": "❌ <@{user}> rejected the trade.",
        "btn_trade_accept": "✅ Accept",
        "btn_trade_reject": "❌ Reject",

        # config
        "config_no_locks": "No commands are locked to any channel.",
        "config_locks_title": "🔒 Configured channels",
        "config_no_command": "❌ You must specify a command.",
        "config_no_channel": "❌ You must specify a channel.",
        "config_locked": "✅ `/{cmd}` can now only be used in <#{channel}>.",
        "config_unlocked": "✅ `/{cmd}` no longer has a channel restriction.",
        "config_bad_action": "❌ Unrecognized action.",
        "config_no_admin": "❌ Only administrators can use this command.",
        "config_lang_set": "✅ Bot language set to **{label}**.",

        # help
        "help_title": "📖 YGOGuesser Commands",
        "help_game_title": "🎮 Game",
        "help_game_value": (
            "`/play` — Start a game (choose mode)\n"
            "`/guess card:<name>` — Guess the current card\n"
            "`/hint` — Reveal the next hint (Hints mode)\n"
            "`/zoom-hint` — Advance to the next zoom (Zoom mode)\n"
            "`/surrender` — Abandon the current game\n"
            "`/ranking` — Top 10 players"
        ),
        "help_gacha_title": "🎴 Gacha",
        "help_gacha_value": (
            "`/pack` — Open a free pack (once per hour)\n"
            "`/collection` — View your collected cards\n"
            "`/sell` — Sell your duplicate cards for coins\n"
            "`/gacha` — Info on the current banner and odds"
        ),
        "help_coins_title": "💰 Coins",
        "help_coins_value": (
            "You earn coins by playing games — they're stored separately from the ranking. "
            "Spending them **does not lower your position**."
        ),
        "help_footer": "YGOGuesser • ygoguesser.vercel.app",

        # hints content
        "hint1_extra": "🃏 It's a **{type}** monster, attribute **{attr}**, type **{race}**",
        "hint1_normal": "🃏 It's a monster with attribute **{attr}**, type **{race}**, level **{level_range}**",
        "level_range_low": "low (1–4)",
        "level_range_mid": "medium (5–6)",
        "level_range_high": "high (7+)",
        "hint2": "⚙️ **{level_label}**, ATK **{atk_label}**",
        "hint3_archetype": "🎯 Belongs to the **{archetype}** archetype",
        "hint3_stats": "🎯 Exact ATK: **{atk}** / Exact DEF: **{def_}**",
        "hint4_unique": "🔤 Has {word_str} and **{letters}** letters (no spaces or hyphens). The unique part starts with **\"{char}\"**",
        "hint5_unique": "💥 The unique part of the name starts with: **\"{frag}\"**",
        "hint4_full": "🔤 The name starts with **\"{char}\"**, has {word_str} and **{letters}** letters (no spaces or hyphens)",
        "hint5_full": "💥 The name starts with: **\"{frag}\"**",
        "word_singular": "**{n}** word",
        "word_plural": "**{n}** words",
        "atk_unknown": "unknown",
        "atk_very_high": "very high (3000+)",
        "atk_high": "high (2500+)",
        "atk_mid_high": "medium-high (2000+)",
        "atk_mid": "medium (1500+)",
        "atk_low": "low (under 1500)",
        "level_link": "Link {val}",
        "level_rank_low": "Low Rank ({val})",
        "level_rank_mid": "Mid Rank ({val})",
        "level_rank_high": "High Rank ({val})",
        "level_low": "Low Level ({val}★)",
        "level_mid": "Mid Level ({val}★)",
        "level_high": "High Level ({val}★)",
        "level_very_high": "Very High Level ({val}★)",

        # misc
        "channel_locked": "❌ `/{cmd}` can only be used in <#{channel}>.",
        "unrecognized_action": "Unrecognized action.",
    },

    "es": {
        # General
        "no_active_game": "No tienes una partida activa. Usa `/jugar` para empezar.",
        "cannot_fetch_card": "No se pudo obtener una carta. Intenta de nuevo más tarde.",
        "cannot_process_image": "No se pudo procesar la imagen. Intenta de nuevo.",

        # start_game
        "game_already_active_hints": "Ya tienes una partida activa. Usa `/pista` y `/adivinar` o `/rendirse`.",
        "game_already_active_zoom": "Ya tienes una partida activa. Usa `/zoom-pista` y `/adivinar` o `/rendirse`.",
        "game_already_active_price": "Ya tienes una partida activa. Usa los botones o `/rendirse`.",
        "game_already_active_other": "Ya tienes una partida activa. Usa `/rendirse` para abandonarla.",
        "welcome_body": (
            "🎮 **¡Bienvenido a YGOGuesser!**\n\n"
            "Pon a prueba tu conocimiento de cartas Yu-Gi-Oh! Elige un modo:\n\n"
            "🃏 **Modo Pistas** — Se revelan pistas progresivas sobre una carta. Cuantas menos pistas uses, más puntos ganas.\n"
            "🔍 **Modo Zoom** — Se muestra una imagen muy zoomeada de la carta. Si fallas, el zoom se aleja poco a poco.\n"
            "💰 **Modo Precio** — Se muestran dos cartas. Adivina cuál es más cara en el mercado TCG. ¡Un fallo y termina la racha!\n"
        ),
        "btn_hints": "🃏 Modo Pistas",
        "btn_zoom": "🔍 Modo Zoom",
        "btn_price": "💰 Modo Precio",

        # hints game
        "hints_started": (
            "🃏 **¡Modo Pistas iniciado!**\n\n"
            "Aquí va la primera pista:\n{hint}\n\n"
            "Tienes hasta **{max_hints} pistas** disponibles.\n"
            "➡️ Usa `/pista` para más pistas o `/adivinar carta:<nombre>` para intentar."
        ),
        "hint_all_revealed": "Ya revelaste todas las pistas ({max_hints}/{max_hints}). Usa `/adivinar` o `/rendirse`.",
        "hint_text": "💡 Pista {n}/{max_hints}:\n{hint}\n\nAcertar ahora vale **{score} puntos**.",
        "hint_not_available_zoom": "❌ `/pista` no está disponible en modo Zoom. Usa `/zoom-pista` para avanzar el zoom.",

        # guess
        "correct_hints": "✅ **¡Correcto!** La carta era **{name}**.\n🏆 Ganaste **{score} puntos** (pistas usadas: {hints}/{max_hints}).",
        "wrong_attempts_left": "❌ **Incorrecto.** Te quedan **{remaining} intento{s}** con la pista actual.",
        "wrong_all_attempts": "💀 **Agotaste todos los intentos.** La carta era **{name}**.",
        "wrong_auto_hint": (
            "❌ Agotaste los 3 intentos de esta pista. Siguiente pista automática:\n\n"
            "💡 Pista {n}/{max_hints}:\n{hint}\n\nAcertar ahora vale **{score} puntos**."
        ),

        # surrender
        "surrender_price": "🏳️ Abandonaste el modo precio. Puntaje final: **{score} puntos** · **{coins} monedas** 💰.",
        "surrender_hints": "🏳️ Te rendiste. La carta era **{name}**.",

        # zoom
        "zoom_already_active": "Ya tienes una partida activa. Usa `{cmd}` o `/rendirse`.",
        "zoom_started": (
            "🔍 **¡Modo Zoom iniciado!**\n"
            "Adivina la carta con zoom nivel 1/{max_levels}.\n"
            "Acertar ahora vale **{score} puntos**. Tienes **3 intentos** por nivel.\n"
            "➡️ `/adivinar carta:<nombre>` para intentar.\n"
            "➡️ `/zoom-pista` para ver más de la imagen (baja el puntaje)."
        ),
        "zoom_correct": "✅ **¡Correcto!** La carta era **{name}**.\n🏆 Ganaste **{score} puntos** (zoom nivel {level}/{max_levels}{hints_note}).",
        "zoom_hints_note": " · {n} pista{s} usada{s}",
        "zoom_wrong_attempts_left": "❌ **Incorrecto.** Te quedan **{remaining} intento{s}** en este nivel de zoom.",
        "zoom_wrong_all_attempts": "💀 **Agotaste todos los intentos.** La carta era **{name}**.",
        "zoom_wrong_auto_advance": (
            "❌ Agotaste los intentos. Aquí va el siguiente nivel de zoom:\n"
            "🔍 Zoom nivel {level}/{max_levels} — Acertar ahora vale **{score} puntos**."
        ),
        "zoom_hint_next": "🔍 Zoom nivel {level}/{max_levels} — Acertar ahora vale **{score} puntos**.",
        "zoom_hint_max": "Ya estás en el nivel máximo de zoom ({level}/{max_levels}). Usa `/adivinar` o `/rendirse`.",
        "zoom_no_game": "❌ `/zoom-pista` solo está disponible en modo Zoom. Usa `/jugar` para empezar.",

        # price
        "price_no_cards": "No se pudieron obtener cartas con precio. Intenta de nuevo.",
        "price_question": "💰 **¿Cuál carta es más cara?** | Puntaje: **{score}**",
        "price_correct_prefix": "✅ ¡Correcto! **{card}** valía **${price:.2f}** vs **${other:.2f}** (+5 💰)\n\n",
        "price_win": "✅ ¡Correcto! No hay más cartas disponibles. Puntaje final: **{score} puntos** · **{coins} monedas** 💰.",
        "price_wrong": (
            "❌ **Incorrecto.** La más cara era **{card}** "
            "con **${price:.2f}** (vs **${other:.2f}**).\n"
            "🏆 Puntaje final: **{score} puntos** · **{coins} monedas** 💰."
        ),
        "price_no_game": "No tienes una partida de precio activa. Usa `/jugar` para empezar.",
        "btn_card1": "Carta 1",
        "btn_card2": "Carta 2",

        # gacha / packs
        "pack_cooldown": (
            "⏳ Tu próximo sobre gratis estará disponible en **{mins}m {secs}s**.\n"
            "💰 Tienes **{coins} monedas** disponibles."
        ),
        "pack_cooldown_hint": "\n> 💡 Gana monedas jugando partidas con `/jugar`.",
        "pack_available": "🎴 **¡Sobre disponible!** ¿De qué banner quieres tirar?\n💰 Tienes **{coins} monedas** disponibles.",
        "pack_already_used": "⏳ El sobre ya fue usado. Próximo disponible en **{mins}m {secs}s**.",
        "pack_opened": "🎴 ¡Abriste un sobre! — {banner}",
        "pack_x10_opened": "🎴 ¡Abriste 10 sobres! — {banner}",
        "pack_x10_no_user": "Primero usa `/sobre` para registrarte.",
        "pack_x10_no_coins": "❌ Necesitas **{cost} monedas** pero tienes **{coins}**.",
        "pack_x10_insufficient": "❌ No tienes suficientes monedas.",
        "pack_new_card_footer": "<:newicon:1506143726840578139> = carta nueva en tu colección",
        "pack_coins_remaining": "💰 Monedas restantes: {coins}",
        "btn_pack_perm": "✨ Original Legends",
        "btn_pack_rot": "🆕 Next Generation",
        "btn_x10_perm": "x10 Original Legends ({cost}💰)",
        "btn_x10_rot": "x10 Next Generation ({cost}💰)",

        # collection
        "collection_empty": "No tienes cartas aún. Usa `/sobre` para abrir tu primer sobre.",
        "collection_title": "📦 Colección — {unique} únicas · {copies} copias",
        "collection_footer": "Página {page} / {total}  •  Usa /sobre para conseguir más cartas",

        # sell
        "sell_no_duplicates": "No tienes cartas duplicadas para vender.",
        "sell_no_duplicates_protected": "No tienes duplicadas vendibles. Tienes **{count}** carta(s) duplicada(s) protegidas 🔒.",
        "sell_title": "🗑️ Vender duplicadas — {extras} copias extra → {coins} monedas",
        "sell_confirm_btn": "🗑️ Confirmar venta ({coins} monedas)",
        "sell_cancel_btn": "Cancelar",
        "sell_nothing": "No había duplicadas para vender.",
        "sell_done_title": "✅ Vendiste tus duplicadas",
        "sell_done_desc": "Ganaste **{coins} monedas** 💰\nSaldo actual: **{balance} monedas**",
        "sell_cancelled": "Venta cancelada.",

        # protect
        "protect_not_found": "❌ No tienes ninguna carta que coincida con **{name}** en tu colección.",
        "protect_on": "🔒 **{name}** ahora está protegida.",
        "protect_off": "🔓 **{name}** ahora está desprotegida.",

        # ranking
        "ranking_empty_score": "Todavía no hay partidas registradas.",
        "ranking_empty_collection": "Todavía nadie tiene cartas.",
        "ranking_title_score": "🏆 Ranking — Top 10 Puntos",
        "ranking_title_collection": "📦 Ranking Colección — Todos los banners",
        "ranking_collection_footer": "{total} cartas únicas en total",
        "btn_ranking_score": "🏆 Puntos",
        "btn_ranking_collection": "📦 Colección",

        # gacha info
        "gacha_how_it_works": (
            "**¿Cómo funciona?**\n"
            "Ganas **monedas** jugando — se guardan por separado del ranking, gastarlas no baja tu posición.\n\n"
            "🆓 **`/sobre`** — 5 cartas gratis cada hora (elige banner)\n"
            "💰 **x10** — 10 cartas por **{cost} monedas**, garantiza al menos 1 Ultra Rare\n\n"
            "🔗 [Ver todas las cartas del pool](https://ygoguesser.vercel.app/banner)\n\n"
        ),
        "gacha_probs": (
            "**Probabilidades:**\n"
            "{secret} Secret Rare — 1%\n"
            "{ultra} Ultra Rare — 4%\n"
            "{super} Super Rare — 15%\n"
            "{rare} Rare — 30%\n"
            "{common} Common — 50%\n\n"
            "**Pool:** {pool_line}\n"
            "{missing_summary}"
        ),
        "gacha_complete": "✅ Colección completa",
        "gacha_missing": "📋 Te faltan **{missing}/{total}** cartas",
        "gacha_banner_rotating": "🔄 Banner rotativo",
        "gacha_banner_permanent": "♾️ Banner permanente",
        "btn_missing_rot": "📋 Faltantes Next Generation",
        "btn_missing_perm": "📋 Faltantes Original Legends",

        # missing cards
        "missing_complete": "✅ ¡Tienes todas las cartas del banner **{banner}**!",
        "missing_title": "📋 Cartas faltantes — {banner} ({count} restantes)",

        # trade
        "trade_self": "❌ No puedes intercambiar cartas contigo mismo.",
        "trade_no_from_card": "❌ No tienes ninguna carta que coincida con **{name}**.",
        "trade_from_protected": "❌ **{name}** está protegida. Desprotégela primero con `/proteger`.",
        "trade_no_to_card": "❌ <@{user}> no tiene ninguna carta que coincida con **{name}**.",
        "trade_to_protected": "❌ La carta **{name}** de <@{user}> está protegida.",
        "trade_offer": "<@{to}> — <@{from_}> te propone un intercambio:",
        "trade_offers": "📤 Ofrece",
        "trade_wants": "📥 Pide",
        "trade_not_found": "❌ Intercambio no encontrado.",
        "trade_not_active": "❌ Este intercambio ya no está activo.",
        "trade_wrong_user_accept": "❌ Solo el usuario al que se le propuso el intercambio puede aceptarlo.",
        "trade_wrong_user_reject": "❌ Solo el usuario al que se le propuso el intercambio puede rechazarlo.",
        "trade_failed": "❌ El intercambio falló. Alguno de los dos ya no tiene la carta.",
        "trade_completed": "✅ ¡Intercambio completado!\n<@{from_}> recibió **{to_card}**\n<@{to}> recibió **{from_card}**",
        "trade_rejected": "❌ <@{user}> rechazó el intercambio.",
        "btn_trade_accept": "✅ Aceptar",
        "btn_trade_reject": "❌ Rechazar",

        # config
        "config_no_locks": "No hay comandos bloqueados a ningún canal.",
        "config_locks_title": "🔒 Canales configurados",
        "config_no_command": "❌ Debes especificar un comando.",
        "config_no_channel": "❌ Debes especificar un canal.",
        "config_locked": "✅ `/{cmd}` ahora solo puede usarse en <#{channel}>.",
        "config_unlocked": "✅ `/{cmd}` ya no tiene restricción de canal.",
        "config_bad_action": "❌ Acción no reconocida.",
        "config_no_admin": "❌ Solo los administradores pueden usar este comando.",
        "config_lang_set": "✅ Idioma del bot configurado a **{label}**.",

        # help
        "help_title": "📖 Comandos de YGOGuesser",
        "help_game_title": "🎮 Juego",
        "help_game_value": (
            "`/jugar` — Inicia una partida (elige modo)\n"
            "`/adivinar carta:<nombre>` — Adivina la carta actual\n"
            "`/pista` — Revela la siguiente pista (modo Pistas)\n"
            "`/zoom-pista` — Avanza al siguiente zoom (modo Zoom)\n"
            "`/rendirse` — Abandona la partida actual\n"
            "`/ranking` — Top 10 de jugadores"
        ),
        "help_gacha_title": "🎴 Gacha",
        "help_gacha_value": (
            "`/sobre` — Abre un sobre gratis (1 vez por hora)\n"
            "`/coleccion` — Ve tus cartas conseguidas\n"
            "`/vender` — Vende tus cartas duplicadas por monedas\n"
            "`/gacha` — Info del banner actual y probabilidades"
        ),
        "help_coins_title": "💰 Monedas",
        "help_coins_value": (
            "Ganas monedas jugando partidas — son los mismos puntos del ranking "
            "pero se guardan por separado. Gastarlas **no baja tu posición**."
        ),
        "help_footer": "YGOGuesser • ygoguesser.vercel.app",

        # hints content
        "hint1_extra": "🃏 Es un monstruo **{type}**, atributo **{attr}**, tipo **{race}**",
        "hint1_normal": "🃏 Es un monstruo de atributo **{attr}**, tipo **{race}**, nivel **{level_range}**",
        "level_range_low": "bajo (1–4)",
        "level_range_mid": "medio (5–6)",
        "level_range_high": "alto (7+)",
        "hint2": "⚙️ **{level_label}**, ATK **{atk_label}**",
        "hint3_archetype": "🎯 Pertenece al arquetipo **{archetype}**",
        "hint3_stats": "🎯 ATK exacto: **{atk}** / DEF exacto: **{def_}**",
        "hint4_unique": "🔤 Tiene {word_str} y **{letters}** letras (sin espacios ni guiones). La parte única empieza con **\"{char}\"**",
        "hint5_unique": "💥 La parte única del nombre comienza con: **\"{frag}\"**",
        "hint4_full": "🔤 El nombre empieza con **\"{char}\"**, tiene {word_str} y **{letters}** letras (sin espacios ni guiones)",
        "hint5_full": "💥 El nombre comienza con: **\"{frag}\"**",
        "word_singular": "**{n}** palabra",
        "word_plural": "**{n}** palabras",
        "atk_unknown": "desconocido",
        "atk_very_high": "muy alto (3000+)",
        "atk_high": "alto (2500+)",
        "atk_mid_high": "medio-alto (2000+)",
        "atk_mid": "medio (1500+)",
        "atk_low": "bajo (menos de 1500)",
        "level_link": "Link {val}",
        "level_rank_low": "Rango bajo ({val})",
        "level_rank_mid": "Rango medio ({val})",
        "level_rank_high": "Rango alto ({val})",
        "level_low": "Nivel bajo ({val}★)",
        "level_mid": "Nivel medio ({val}★)",
        "level_high": "Nivel alto ({val}★)",
        "level_very_high": "Nivel muy alto ({val}★)",

        # misc
        "channel_locked": "❌ `/{cmd}` solo puede usarse en <#{channel}>.",
        "unrecognized_action": "Acción no reconocida.",
    },
}


def t(key: str, lang: str = "en", **kwargs) -> str:
    text = STRINGS.get(lang, STRINGS["en"]).get(key) or STRINGS["en"].get(key, key)
    return text.format(**kwargs) if kwargs else text
