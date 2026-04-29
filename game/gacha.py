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
    "name": "Clásico Duel Monsters",
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
        {"id": 7902349,  "name": "Beaver Warrior"},
        {"id": 92387330, "name": "Silver Fang"},
        {"id": 62015408, "name": "Mystical Elf"},
    ],
    "common": [
        {"id": 30832864, "name": "Gaia The Fierce Knight"},
        {"id": 89102552, "name": "Curse of Dragon"},
        {"id": 32452818, "name": "Catapult Turtle"},
        {"id": 15025844, "name": "Winged Dragon, Guardian of the Fortress #1"},
        {"id": 71039598, "name": "Mammoth Graveyard"},
        {"id": 76009260, "name": "Armored Lizard"},
        {"id": 35261759, "name": "Anthrosaurus"},
        {"id": 34502691, "name": "Garoozis"},
        {"id": 95638658, "name": "The Fiend Megacyber"},
        {"id": 93553943, "name": "Gaia Power"},
        {"id": 27324313, "name": "Reinforcements"},
        {"id": 69162969, "name": "Soul Exchange"},
        {"id": 86318356, "name": "Sword of Deep-Seated"},
        {"id": 2314238,  "name": "Dragon Piper"},
        {"id": 39507162, "name": "Tailor of the Fickle"},
        {"id": 65584936, "name": "Robbin' Goblin"},
        {"id": 51267887, "name": "Sword of Dark Destruction"},
        {"id": 57728570, "name": "Doron"},
        {"id": 12607953, "name": "Dragoness the Wicked Knight"},
        {"id": 71044499, "name": "The Stern Mystic"},
        {"id": 34684801, "name": "Wall of Revealing Light"},
        {"id": 61740673, "name": "Dark Prisoner"},
        {"id": 30827995, "name": "Witch's Apprentice"},
        {"id": 5682682,  "name": "Toon Alligator"},
        {"id": 55835941, "name": "Toad Master"},
        {"id": 30161053, "name": "Mushroom Man"},
        {"id": 14291024, "name": "Mushroom Man #2"},
        {"id": 56789759, "name": "Dark Chimera"},
        {"id": 36119641, "name": "Monster Eye"},
        {"id": 65854280, "name": "Laser Cannon Armor"},
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
