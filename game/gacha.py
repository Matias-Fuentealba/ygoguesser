import random

COOLDOWN_HOURS = 1
CARDS_PER_FREE_PULL = 5
X10_COST = 500

RARITY_WEIGHTS = {"secret": 1, "ultra": 4, "super": 15, "rare": 30, "common": 50}

RARITY_EMOJIS = {
    "secret": "✨✨✨",
    "ultra": "⭐⭐",
    "super": "⭐",
    "rare": "🔹",
    "common": "◻️",
}

RARITY_COLORS = {
    "secret": 0xFFD700,
    "ultra": 0xFFA500,
    "super": 0xC0C0C0,
    "rare": 0x0070DD,
    "common": 0x9D9D9D,
}

DUEL_MONSTERS_BANNER = {
    "name": "Original Legends",
    "image_url": "https://i.imgur.com/9GkdSgo.jpeg",
    "secret": [
        {"id": 23995346, "name": "Blue-Eyes Ultimate Dragon"},
        {"id": 33396948, "name": "Exodia the Forbidden One"},
        {"id": 98502113, "name": "Dark Paladin"},
    ],
    "ultra": [
        {"id": 46986414, "name": "Dark Magician"},
        {"id": 89631139, "name": "Blue-Eyes White Dragon"},
        {"id": 74677422, "name": "Red-Eyes B. Dragon"},
        {"id": 70781052, "name": "Summoned Skull"},
        {"id": 77585513, "name": "Jinzo"},
        {"id": 38033121, "name": "Dark Magician Girl"},
        {"id": 78193831, "name": "Buster Blader"},
        {"id": 64631466, "name": "Relinquished"},
    ],
    "super": [
        {"id": 40640057, "name": "Kuriboh"},
        {"id": 26202165, "name": "Sangan"},
        {"id": 78010363, "name": "Witch of the Black Forest"},
        {"id": 83764718, "name": "Monster Reborn"},
        {"id": 44095762, "name": "Mirror Force"},
        {"id": 12580477, "name": "Raigeki"},
        {"id": 55144522, "name": "Pot of Greed"},
        {"id": 53129443, "name": "Dark Hole"},
        {"id": 19613556, "name": "Heavy Storm"},
        {"id": 4031928,  "name": "Change of Heart"},
        {"id": 31560081, "name": "Magician of Faith"},
        {"id": 69140098, "name": "Gemini Elf"},
        {"id": 79575620, "name": "Injection Fairy Lily"},
        {"id": 21417692, "name": "Dark Elf"},
        {"id": 54652250, "name": "Man-Eater Bug"},
    ],
    "rare": [
        {"id": 91152256, "name": "Celtic Guardian"},
        {"id": 76812113, "name": "Harpie Lady"},
        {"id": 24094653, "name": "Polymerization"},
        {"id": 5318639,  "name": "Mystical Space Typhoon"},
        {"id": 12607053, "name": "Waboku"},
        {"id": 4206964,  "name": "Trap Hole"},
        {"id": 13039848, "name": "Giant Soldier of Stone"},
        {"id": 32274490, "name": "Skull Servant"},
        {"id": 31786629, "name": "Thunder Dragon"},
        {"id": 45231177, "name": "Flame Swordsman"},
        {"id": 97590747, "name": "La Jinn the Mystical Genie of the Lamp"},
        {"id": 13945283, "name": "Wall of Illusion"},
        {"id": 41392891, "name": "Feral Imp"},
        {"id": 3819470,  "name": "Seven Tools of the Bandit"},
        {"id": 50045299, "name": "Dragon Capture Jar"},
        {"id": 76184692, "name": "Hitotsu-Me Giant"},
        {"id": 88819587, "name": "Baby Dragon"},
        {"id": 32452818, "name": "Beaver Warrior"},
        {"id": 90357090, "name": "Silver Fang"},
        {"id": 15025844, "name": "Mystical Elf"},
    ],
    "common": [
        {"id": 6368038,  "name": "Gaia The Fierce Knight"},
        {"id": 28279543, "name": "Curse of Dragon"},
        {"id": 95727991, "name": "Catapult Turtle"},
        {"id": 87796900, "name": "Winged Dragon, Guardian of the Fortress #1"},
        {"id": 40374923, "name": "Mammoth Graveyard"},
        {"id": 15480588, "name": "Armored Lizard"},
        {"id": 89904598, "name": "Anthrosaurus"},
        {"id": 14977074, "name": "Garoozis"},
        {"id": 66362965, "name": "The Fiend Megacyber"},
        {"id": 56594520, "name": "Gaia Power"},
        {"id": 17814387, "name": "Reinforcements"},
        {"id": 68005187, "name": "Soul Exchange"},
        {"id": 98495314, "name": "Sword of Deep-Seated"},
        {"id": 55763552, "name": "Dragon Piper"},
        {"id": 43641473, "name": "Tailor of the Fickle"},
        {"id": 88279736, "name": "Robbin' Goblin"},
        {"id": 37120512, "name": "Sword of Dark Destruction"},
        {"id": 756652,   "name": "Doron"},
        {"id": 70681994, "name": "Dragoness the Wicked Knight"},
        {"id": 87557188, "name": "The Stern Mystic"},
        {"id": 17078030, "name": "Wall of Revealing Light"},
        {"id": 89558090, "name": "Dark Prisoner"},
        {"id": 80741828, "name": "Witch's Apprentice"},
        {"id": 59383041, "name": "Toon Alligator"},
        {"id": 62671448, "name": "Toad Master"},
        {"id": 14181608, "name": "Mushroom Man"},
        {"id": 93900406, "name": "Mushroom Man #2"},
        {"id": 32344688, "name": "Dark Chimera"},
        {"id": 84133008, "name": "Monster Eye"},
        {"id": 77007920, "name": "Laser Cannon Armor"},
    ],
}


def _image_url(card_id: int) -> str:
    return f"https://images.ygoprodeck.com/images/cards/{card_id}.jpg"


def _pull_single(banner: dict, weight_override: dict = None) -> dict:
    weights = weight_override or RARITY_WEIGHTS
    rarities = list(weights.keys())
    chosen = random.choices(rarities, weights=[weights[r] for r in rarities], k=1)[0]
    pool = banner.get(chosen) or banner["common"]
    card = random.choice(pool)
    return {
        "card_id": card["id"],
        "name": card["name"],
        "rarity": chosen,
        "image_url": _image_url(card["id"]),
    }


def pull_free(banner: dict) -> list[dict]:
    return [_pull_single(banner) for _ in range(CARDS_PER_FREE_PULL)]


def pull_x10(banner: dict) -> list[dict]:
    results = []
    has_ultra_plus = False

    for _ in range(9):
        card = _pull_single(banner)
        if card["rarity"] in ("ultra", "secret"):
            has_ultra_plus = True
        results.append(card)

    guaranteed = _pull_single(banner, {"secret": 10, "ultra": 90}) if not has_ultra_plus else _pull_single(banner)
    results.append(guaranteed)
    return results
