class Variables:
    """An object to contain various game variables."""

    """Generation variables"""

    ROOM_GENERIC_CHANCE = 65
    ROOM_SIZE_DIFFERENCE_CHANCE = 25
    ROOM_AVG_SEARCHES = 3
    ROOM_MIN_SEARCHES = 2
    ROOM_MAX_SEARCHES = 4

    """Game variables."""

    HUNGER_RATE = 2
    RESTING_HUNGER_RATE = HUNGER_RATE * 2
    FOOD_VALUE = 10
    POTION_VALUE = 3
    DOOM_VARIANCE = 50
    MAX_DOOM = 100

    """Player starting variables."""

    PLAYER_MAX_HP = 10
    PLAYER_STARTING_FOOD = 0
    PLAYER_STARTING_POTIONS = 1

    """ Search variables. """

    ROOM_BASE_SEARCH_CHANCE = 80

    """Minion variables."""

    MINION_ARMOR_RATIO = 1
    MINION_DAMAGE_RATIO = 3

    """Spell variables."""

    SPELL_VAMPIRIC_TOUCH_RATIO = 3
    SPELL_PAIN_RATIO = 2
    SPELL_DEATH_BOLT_RATIO = 0.5

    """Battle variables."""

    FLEE_BASE_CHANCE = 30
    FLEE_LEVEL_VARIANCE = 10

    DODGE_BASE_CHANCE = 55
    DODGE_LEVEL_VARIANCE = 20

    # Monster generation variables.

    LEVEL_TIER1_CHANCE = 25
    LEVEL_TIER2_CHANCE = 5

    LEVEL_TIER1_DIFF = 1
    LEVEL_TIER2_DIFF = 2

    # Final boss variables.

    FINAL_BOSS_ADDITIONAL_LEVELS = 3
    FINAL_BOSS_LEVEL_MULTIPLIER = 1.5
