from minion import Minion
import util
from variables import Variables


class Player:
    def __init__(self, name):
        self._name = name
        self._minions = []
        self._food = 0
        self._hunger = 0
        self._level = 1
        self._souls = 0
        self._potions = 0
        self._runes = 0

        self._doom = 0

        self._max_hp = Variables.PLAYER_MAX_HP
        self._hp = self._max_hp

        self._dodging = False

        self._armor = 0
        self._weapon = 1

        self._minion_default = "ask"

    @property
    def minion_default(self) -> str:
        return self._minion_default

    @minion_default.setter
    def minion_default(self, new_behavior: str) -> None:
        if new_behavior in ("ask", "attack", "defend"):
            self._minion_default = new_behavior
        else:
            raise ValueError(
                f"Invalid minion default behavior requested: {new_behavior}"
            )

    @property
    def souls(self) -> int:
        return self._souls

    @souls.setter
    def souls(self, amt) -> None:
        self._souls = amt

    @property
    def dodging(self) -> bool:
        return self._dodging

    @dodging.setter
    def dodging(self, mode: bool) -> None:
        self._dodging = mode

    @property
    def armor(self) -> int:
        return self._armor

    @armor.setter
    def armor(self, new_armor) -> None:
        self._armor = new_armor
        if self._armor < 0:
            self._armor = 0

    @property
    def weapon(self) -> int:
        return self._weapon

    @weapon.setter
    def weapon(self, new_weapon) -> None:
        self._weapon = new_weapon
        if self._weapon <= 0:
            self._weapon = 1

    @property
    def doom(self) -> int:
        return self._doom

    @doom.setter
    def doom(self, amt) -> None:
        self._doom = amt

    @property
    def runes(self) -> int:
        return self._runes

    @runes.setter
    def runes(self, amt) -> None:
        self._runes = amt

    @property
    def potions(self) -> int:
        return self._potions

    @potions.setter
    def potions(self, amt) -> None:
        self._potions = amt

    @property
    def level(self) -> int:
        return self._level

    @level.setter
    def level(self, new_level) -> None:
        self._level = new_level

    @property
    def food(self) -> int:
        return self._food

    @food.setter
    def food(self, amt) -> None:
        self._food = amt

    @property
    def hunger(self) -> int:
        return self._hunger

    @hunger.setter
    def hunger(self, amt) -> None:
        self._hunger = amt

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @max_hp.setter
    def max_hp(self, amt) -> None:
        self._max_hp = amt

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, amt) -> None:
        self._hp = amt
        if self._hp > self._max_hp:
            self._hp = self._max_hp
        if self._hp < 0:
            self._hp = 0

    @property
    def name(self) -> str:
        return self._name

    @property
    def minions(self) -> list:
        return self._minions

    @property
    def minion_count(self) -> int:
        return len(self._minions)

    def _get_armor_descriptor(self, with_level=False) -> str:
        """Descriptive text that tells how powerful the player's armor is."""
        if self.armor < 3:
            armor_str = "a wisp of Shadowcloak."
        elif self.armor < 5:
            armor_str = "whirling tendrils of Shadowcloak."
        elif self.armor < 7:
            armor_str = "a wildly-swirling Shadowcloak."
        else:
            armor_str = "an oppressively billowing Shadowcloak."

        if with_level:
            armor_str += f" (Level {self.armor})"

        return armor_str

    def _get_weapon_descriptor(self, with_level=False) -> str:
        """Descriptive text to describe the player's weapon."""
        if self.weapon <= 1:
            weapon_str = "your fists."
        elif self.weapon == 2:
            weapon_str = "a rusted dagger."
        elif self.weapon == 3:
            weapon_str = "a servicable axe."
        elif self.weapon == 4:
            weapon_str = "a shining longsword."
        elif self.weapon == 5:
            weapon_str = "a terrifying scourge."
        elif self.weapon == 6:
            weapon_str = "a dormant Blackmetal scythe."
        elif self.weapon >= 7:
            weapon_str = f"a menacing, soul-empowered Blackmetal scythe."

        if with_level:
            weapon_str += f" (Level {self.weapon})"

        return weapon_str

    def add_minion(self, minion: Minion, silent=False) -> None:
        if not silent:
            match self.minion_default:
                case "ask":
                    behavior = self._ask_minion_behavior()
                    match behavior:
                        case "attack":
                            minion.attacking = True
                        case "defend":
                            minion.defending = True
                        case _:
                            raise ValueError(
                                f"add_minion tried to set an unusual behavior: {behavior}"
                            )
                case "attack":
                    minion.attacking = True
                case "defend":
                    minion.defending = True
                case _:
                    raise ValueError(
                        f"add_minion tried to set an unusual behavior: {self.minion_default}"
                    )
        else:
            minion.defending = True
        self._minions.append(minion)

    def _print_current_minion_roster(self) -> None:
        print(
            f"You currently have {self.minions_attacking} {util.make_plural('minion', self.minions_attacking)} attacking."
        )
        print(
            f"You currently have {self.minions_defending} {util.make_plural('minion', self.minions_defending)} defending."
        )

    def _ask_minion_behavior(self) -> str:
        """Set the new minion into either attack or defend mode.

        Returns a str: attack or defend.
        """

        print("\nWhat will the new minion do?\n")

        self._print_current_minion_roster()

        print("\n1. Attack")
        print("2. Defend")
        print("3. Attack, and don't ask again")
        print("4. Defend, and don't ask again")

        choice = util.prompt_for_number_safely("\nChoice: ", 4)

        match choice:
            case 1:
                print("\nThe minion joins your attacking force.")
                return "attack"
            case 2:
                print("\nThe minion joins your defending ranks.")
                return "defend"
            case 3:
                print("\nThe minion joins your attacking force.")
                self.minion_default = "attack"
                return "attack"
            case 4:
                print("\nThe minion joins your defending ranks.")
                self.minion_default = "defend"
                return "defend"

    def _prompt_for_default_behavior(self) -> None:
        """As _ask_minion_behavior.

        Sets ask, attack, or defend."""

        print("\nWhat will new minions do?\n")

        self._print_current_minion_roster()

        print("\n1. Ask for minion behavior every time.")
        print("2. All new minions will attack.")
        print("3. All new minions will defend.")

        choice = util.prompt_for_number_safely("\nChoice: ", 3)

        match choice:
            case 1:
                print("\nNew minions will ask for behavior every time.")
                self.minion_default = "ask"
            case 2:
                print("\nNew minions will now always attack.")
                self.minion_default = "attack"
            case 3:
                print("\nNew minions will now always defend.")
                self.minion_default = "defend"

    def destroy_minion(self, minion: Minion) -> None:
        if minion in self._minions:
            self._minions.remove(minion)
        else:
            raise ValueError(
                "Tried to remove a minion that wasn't already in the minions list."
            )

    def heal(self, amt) -> None:
        self.hp += amt

    def take_damage(self, amt) -> None:
        self.hp -= amt

    def add_food(self, amt) -> None:
        self.food += amt

    def eat_food(self, amt) -> None:
        self.food -= amt

    def get_minion_count_str(self) -> str:
        if self.minion_count == 0:
            return "No minions are under your control."
        elif self.minion_count == 1:
            return "A single minion is under your control."
        elif self.minion_count < 5:
            return f"You command a group of {self.minion_count} minions."
        else:
            return f"You command an army of {self.minion_count} minions."

    def level_up(self) -> None:
        """Called on winning a battle."""

        self.level += 1
        self.max_hp += 1

    @property
    def minions_attacking(self) -> int:
        return self._get_attacking_minion_count()

    @property
    def minions_defending(self) -> int:
        return self._get_defending_minion_count()

    def _get_attacking_minion_count(self) -> int:
        count = 0
        if self.minion_count > 0:
            for minion in self.minions:
                if minion.attacking:
                    count += 1
        return count

    def _get_defending_minion_count(self) -> int:
        count = 0
        if self.minion_count > 0:
            for minion in self.minions:
                if minion.defending and minion.hp > 0:
                    count += 1
        return count
