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


GX_BANNER = {
    "name": "Next Generation",
    "image_url": "https://i.imgur.com/b0lQLid.jpeg",
    "secret": [
        {"id": 1546123,  "name": "Cyber End Dragon"},
        {"id": 35809262, "name": "Elemental HERO Flame Wingman"},
        {"id": 83104731, "name": "Ancient Gear Golem"},
    ],
    "ultra": [
        {"id": 25366484, "name": "Elemental HERO Shining Flare Wingman"},
        {"id": 70095154, "name": "Cyber Dragon"},
        {"id": 73879377, "name": "Armed Dragon LV7"},
        {"id": 61204971, "name": "Elemental HERO Thunder Giant"},
        {"id": 6007213,  "name": "Uria, Lord of Searing Flames"},
        {"id": 32491822, "name": "Hamon, Lord of Striking Thunder"},
        {"id": 69890967, "name": "Raviel, Lord of Phantasms"},
        {"id": 10248389, "name": "Cyber Blader"},
    ],
    "super": [
        {"id": 21844576, "name": "Elemental HERO Avian"},
        {"id": 58932615, "name": "Elemental HERO Burstinatrix"},
        {"id": 79979666, "name": "Elemental HERO Bubbleman"},
        {"id": 20721928, "name": "Elemental HERO Sparkman"},
        {"id": 86188410, "name": "Elemental HERO Wildheart"},
        {"id": 46384672, "name": "Armed Dragon LV5"},
        {"id": 10509340, "name": "Ancient Gear Beast"},
        {"id": 37630732, "name": "Power Bond"},
        {"id": 63035430, "name": "Skyscraper"},
        {"id": 45906428, "name": "Miracle Fusion"},
        {"id": 63703130, "name": "O - Oversoul"},
        {"id": 44729197, "name": "Steamroid"},
        {"id": 23299957, "name": "Vehicroid Connection Zone"},
        {"id": 59793705, "name": "Elemental HERO Bladedge"},
        {"id": 11460577, "name": "Etoile Cyber"},
    ],
    "rare": [
        {"id": 980973,   "name": "Armed Dragon LV3"},
        {"id": 84327329, "name": "Elemental HERO Clayman"},
        {"id": 30190809, "name": "Gear Golem the Moving Fortress"},
        {"id": 92001300, "name": "Ancient Gear Castle"},
        {"id": 76763417, "name": "Cyber Gymnast"},
        {"id": 22020907, "name": "Hero Signal"},
        {"id": 61968753, "name": "Bubble Shuffle"},
        {"id": 46910446, "name": "Chthonian Alliance"},
        {"id": 191749,   "name": "Hero Flash!!"},
        {"id": 21323861, "name": "Acid Rain"},
        {"id": 47737087, "name": "Elemental HERO Rampart Blaster"},
        {"id": 29343734, "name": "Elemental HERO Electrum"},
        {"id": 79109599, "name": "King of the Swamp"},
        {"id": 36378213, "name": "Ambulanceroid"},
        {"id": 71218746, "name": "Drillroid"},
        {"id": 984114,   "name": "Expressroid"},
        {"id": 25573054, "name": "Transcendent Wings"},
        {"id": 77754944, "name": "Widespread Ruin"},
        {"id": 18511384, "name": "Fusion Recovery"},
        {"id": 95281259, "name": "The Warrior Returning Alive"},
    ],
    "common": [
        {"id": 98266377, "name": "Elemental HERO Heat"},
        {"id": 95362816, "name": "Elemental HERO Lady Heat"},
        {"id": 37195861, "name": "Elemental HERO Ocean"},
        {"id": 75434695, "name": "Elemental HERO Woodsman"},
        {"id": 26902560, "name": "Fusion Sage"},
        {"id": 41234315, "name": "Fake Explosion"},
        {"id": 18271561, "name": "Chthonian Blast"},
        {"id": 34664411, "name": "Lucky Iron Axe"},
        {"id": 41482598, "name": "Mirage of Nightmare"},
        {"id": 67169062, "name": "Pot of Avarice"},
        {"id": 22589918, "name": "Reload"},
        {"id": 61068510, "name": "Tornado"},
        {"id": 59744639, "name": "Windstorm of Etaqua"},
        {"id": 97017120, "name": "Giant Rat"},
        {"id": 83011278, "name": "Mystic Tomato"},
        {"id": 60806437, "name": "UFO Turtle"},
        {"id": 93187568, "name": "Spell Striker"},
        {"id": 10080320, "name": "Jurassic World"},
        {"id": 70156997, "name": "Spiritual Earth Art - Kurogane"},
        {"id": 42945701, "name": "Spiritual Fire Art - Kurenai"},
        {"id": 6540606,  "name": "Spiritual Water Art - Aoi"},
        {"id": 79333300, "name": "Spiritual Wind Art - Miyabi"},
        {"id": 90440725, "name": "Cyber Shadow Gardna"},
        {"id": 49375719, "name": "Cyber Tutu"},
        {"id": 76103404, "name": "Cyber Petit Angel"},
        {"id": 25796442, "name": "Ritual Cage"},
        {"id": 75041269, "name": "Clock Tower Prison"},
        {"id": 6186304,  "name": "D - Force"},
        {"id": 9744376,  "name": "Good Goblin Housekeeping"},
        {"id": 83968380, "name": "Jar of Greed"},
    ],
}

PERMANENT_BANNER = DUEL_MONSTERS_BANNER
ROTATING_BANNER = GX_BANNER


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
