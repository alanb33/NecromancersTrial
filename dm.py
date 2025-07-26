import math
import random

from player import Player
from monster import Monster
from room import Room
from minion import Minion
import util
from stats import Stats
from variables import Variables


class DM:

    """An object with static methods to help build Rooms, Monsters, and Items.
    It also controls much of the game logic.
    This object has too many responsibilities and should be refactored
    into many smaller pieces.
    """

    """Loaded data stores"""

    adjectives: list = []
    rooms: dict = {}
    monsters: list = []

    """Class methods"""

    @classmethod
    def load_data(cls) -> None:
        cls.adjectives = cls._load_file("data/adjectives.txt")
        cls.monsters = cls._load_file("data/monsters.txt")
        cls.rooms = cls._load_rooms()

    @classmethod
    def setup_player(cls, name) -> None:
        """Set up initial player variables."""

        cls.player = Player(name)

        cls.player.potions = Variables.PLAYER_STARTING_POTIONS
        cls.player.food = Variables.PLAYER_STARTING_FOOD

        cls.add_generic_minion(silent=True)

    @classmethod
    def _load_file(cls, file) -> list:
        data = []

        with open(file) as f:
            for line in f.readlines():
                data.append(line.strip())

        return data

    @classmethod
    def _load_rooms(cls) -> dict:
        rooms = {
            "generic": [],
            "armory": [],
            "kitchen": [],
            "workshop": [],
        }

        rooms["generic"] = cls._load_file("data/rooms_generic.txt")
        rooms["armory"] = cls._load_file("data/rooms_armory.txt")
        rooms["kitchen"] = cls._load_file("data/rooms_kitchen.txt")
        rooms["workshop"] = cls._load_file("data/rooms_workshop.txt")

        return rooms

    @classmethod
    def generate_final_boss(cls) -> Monster:
        """The final boss! It must killed to win."""

        boss_level = round(
            (cls.player.level + Variables.FINAL_BOSS_ADDITIONAL_LEVELS)
            * Variables.FINAL_BOSS_LEVEL_MULTIPLIER
        )
        return Monster("Runekeeper", level=boss_level)

    @classmethod
    def generate_monster(cls) -> Monster:
        """Generate a new Monster. Monster names are purely flavor text."""

        if len(cls.monsters) == 0:
            raise ValueError("Monsters list is empty.")

        adjective = cls._get_adjective()
        monster_name = f"{adjective} {random.choice(cls.monsters)}"

        level: int = cls._randomize_monster_level()

        return Monster(monster_name, level=level)

    @classmethod
    def _randomize_monster_level(cls) -> int:
        """Generate a monster whose level is in a specific range.

        LEVEL_TIER1_CHANCE = 25
        LEVEL_TIER2_CHANCE  = 5

        LEVEL_TIER1_DIFF = 1
        LEVEL_TIER2_DIFF = 2
        """

        randomization_max_roll = 100

        level_roll = random.randint(0, randomization_max_roll)

        if level_roll < Variables.LEVEL_TIER2_CHANCE:
            level = cls.player.level - Variables.LEVEL_TIER2_DIFF
        elif level_roll < Variables.LEVEL_TIER1_CHANCE:
            level = cls.player.level - Variables.LEVEL_TIER1_DIFF
        elif level_roll < randomization_max_roll - Variables.LEVEL_TIER1_CHANCE:
            level = cls.player.level
        elif level_roll < randomization_max_roll - Variables.LEVEL_TIER2_CHANCE:
            level = cls.player.level + 1
        else:
            level = cls.player.level + 2

        if level <= 0:
            level = 1

        return level

    # TODO: Move this to Room or a room helper
    @classmethod
    def generate_room(cls) -> Room:
        """Generate a new Room. Room types determine what can be looted there."""

        if len(cls.rooms) == 0:
            raise ValueError("Rooms dict is empty.")

        adjective = cls._get_adjective()
        room_type = cls._get_room_type()
        room_name = f"{adjective} {random.choice(cls.rooms[room_type])}"

        return Room(room_name, room_type)

    @classmethod
    def _get_adjective(cls) -> str:
        if len(cls.adjectives) == 0:
            raise ValueError("Adjectives list is empty.")
        else:
            return random.choice(cls.adjectives)

    # TODO: Move this to Room or a room helper
    @classmethod
    def _get_room_type(cls) -> str:
        roll = random.randint(0, 100)

        if roll < Variables.ROOM_GENERIC_CHANCE:
            room_type = "generic"
        else:
            room_files = ["armory", "kitchen", "workshop"]
            room_type = random.choice(room_files)

        return room_type

    @classmethod
    def increase_doom(cls) -> None:
        doom_increase = random.randint(0, Variables.DOOM_VARIANCE)
        cls.player.doom += doom_increase

    @classmethod
    def get_bad_feeling(cls) -> str:
        """A descriptive indicator of the DOOM level.
        When DOOM reaches 100, a battle will begin."""

        feeling = ""
        if DM.player.doom >= Variables.MAX_DOOM:
            feeling = "\nYou hear something rapidly approaching!"
        elif DM.player.doom >= Variables.MAX_DOOM * 0.75:
            feeling = (
                "\nA feeling of doom settles into your stomach like an iron weight."
            )
        elif DM.player.doom >= Variables.MAX_DOOM * 0.5:
            feeling = "\nWas that a noise somewhere up ahead...?"
        elif DM.player.doom >= Variables.MAX_DOOM * 0.25:
            feeling = "\nYou feel unnerved... something is watching you."

        return feeling

    @classmethod
    def destroy_minion(cls, minion: Minion) -> None:
        DM.player.destroy_minion(minion)

    @classmethod
    def add_generic_minion(cls, silent=False) -> None:
        minion = Minion("skeletal prisoner", DM.player)
        DM.player.add_minion(minion, silent=silent)
        DM.update_minion_stats()
        Stats.add_raise()

    @classmethod
    def update_minion_stats(cls) -> None:
        """Called whenever there is a change in armor or weapon,
        or when a minion is raised for the first time."""

        for minion in DM.player.minions:
            minion.hp = DM._get_minion_defense()
            minion.max_hp = DM._get_minion_defense()
            minion.damage = DM._get_minion_attack()

    @classmethod
    def _get_minion_defense(cls) -> int:
        """Calculate the minion defense, which is their HP.
        It's based on the player's armor level, and when minions
        get destroyed, the player's armor is damaged as well.
        """

        if cls.player.armor == 0:
            return 1
        else:
            return math.ceil(cls.player.armor / Variables.MINION_ARMOR_RATIO)

    @classmethod
    def _get_minion_attack(cls) -> int:
        """Calculate the minion attack damage.
        It's based on the player's weapon level."""

        return math.ceil(cls.player.weapon / Variables.MINION_DAMAGE_RATIO)

    @classmethod
    def print_player_info(cls, room_count: int) -> None:
        # info = f"You are {self.name} the Necromancer."
        info = "\n" + cls.player.get_minion_count_str()
        info += (
            f"\nYour health is at {cls.player.hp} of a maximum of {cls.player.max_hp}."
        )
        info += f"\nYou are at {cls.player.hunger}% hunger."
        info += f"\nFood remaining: {cls.player.food}"
        info += f"\nHealing potions available: {cls.player.potions}"
        info += f"\nVengeful souls: {cls.player.souls}"
        info += f"\n\nYou hold {cls.player.runes} of the {cls._get_rune_count()} Runes of Escape."
        info += cls._do_rune_sense(room_count)

        info += (
            f"\n\nYou are wielding {cls.player._get_weapon_descriptor(with_level=True)}"
        )
        if cls.player.minions_attacking > 0:
            info += f"\nEmpowered by your weapon, your attacking {util.make_plural('minion', cls.player.minions_attacking)} will deal {cls.player.minions_attacking * cls._get_minion_attack()} damage each turn in combat."
        info += f"\nYou are protected by {cls.player._get_armor_descriptor(with_level=True)}"
        if cls.player.minions_defending > 0:
            info += f"\nEmpowered by your Shadowcloak, your defending {util.make_plural('minion', cls.player.minions_attacking)} can absorb {cls.player.minions_defending * cls._get_minion_defense()} damage each turn in combat."

        print(info)

    @classmethod
    def _get_rune_count(cls) -> int:
        return len(cls._rune_rooms)

    @classmethod
    def place_runes(cls, dungeon_length: int) -> list:
        cls._rune_rooms = []

        rune_count = 3

        for i in range(rune_count, 0, -1):
            cls._rune_rooms.append(int(dungeon_length / i))

    @classmethod
    def _do_rune_sense(cls, room_count: int) -> str:
        if cls._get_rune_count() > 0:
            for rune in cls._rune_rooms:
                if rune > room_count:
                    rune_diff = rune - room_count
                    if rune_diff == 1:
                        return "\nYou sense the next rune just up ahead!"
                    else:
                        return f"\nYou sense a rune {rune_diff} rooms ahead."
        else:
            raise ValueError("Failed to sense next rune.")

    @classmethod
    def try_find_rune(cls, room_count: int) -> None:
        for rune_room in cls._rune_rooms:
            if room_count == rune_room:
                print("\nThere it is! One of the Runes of Escape!")
                DM.player.runes += 1
                rune_diff = cls._get_rune_count() - DM.player.runes
                if rune_diff > 1:
                    print(f"Only {rune_diff} runes remain to be found!")
                elif rune_diff == 1:
                    print("Only one rune remains to be found! You're almost free!")
                else:
                    print("\nYou enter the chamber of the final Rune of Escape...")

    @classmethod
    def do_bad_ending(cls, ending_type: str, killer: str = None) -> None:
        """Do the bad ending. In the event of death in battle, killer should be given a value."""

        util.clear()
        match ending_type:
            case "starvation":
                print(
                    "You collapse to the floor, a starved, withered husk, much like your former servants.\n"
                )
            case "damage":
                if killer == None:
                    raise ValueError(
                        "Player was killed by an unknown monster. Was the killer parameter not supplied?"
                    )
                else:
                    print(
                        f"You fall to the ground, streaked with blood and unable to move your limbs. The {killer} descends upon your barely-living body, looking hungry..."
                    )
            case _:
                print("You collapse to the floor, expiring from old age.")
        if DM.player.minion_count > 0:
            print(
                "Your minions, no longer bound to your will, begin to wander the dungeon aimlessly."
            )
            print("Perhaps an unfortunate future prisoner will encounter them...")
        if DM.player.runes > 0:
            print(
                "The last thing you see is the light of the Runes of Escape as they return to the darkness..."
            )

        end_str = "\n(BAD ENDING: "
        match ending_type:
            case "starvation":
                end_str += "STARVATION)"
            case "damage":
                if killer == "Runekeeper":
                    end_str += "SLAIN BY THE RUNEKEEPER)"
                else:
                    end_str += "SLAIN BY A MONSTER)"
            case _:
                end_str += "SOMETHING WEIRD)"
        print(end_str)

        util.close(DM.player.name)

    @classmethod
    def do_victory(self):
        util.clear()
        print(
            "With the creature's death, the final Rune of Escape is released from its grasp and enters your possession."
        )
        print(
            "Without giving it a second glance, you turn and leave, your Shadowcloak swirling behind you."
        )
        print(
            "\nYou return to the magically-locked barrier at the entrance of the Dungeon of Despair."
        )
        print(
            "Releasing the three Runes of Escape from your grasp, you intone the magic word that they form."
        )
        print("The final syllable reverberates through the darkness of the dungeon.")
        print(
            "Before you take your next breath, there is the sound of glass shattering."
        )
        print(
            "The magical barrier that barred your escape has collapsed into a thousand fading shards."
        )
        print(
            "\nWith a triumphant grin on your face, you ascend the stairs to the world above."
        )
        print("They should've known they could not contain you for long...")
        util.continue_prompt()
        self._do_victory_statistics()

    @classmethod
    def _do_victory_statistics(self) -> None:
        util.clear()
        Stats.print_stats()
        util.close(DM.player.name)
