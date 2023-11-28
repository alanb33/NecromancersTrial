import util


class Stats:
    """A structure to present fun game stats on victory."""

    _kills = 0
    _raised = 0
    _fallen_minions = 0
    _butchered = 0
    _spirits = 0

    _rations_eaten = 0
    _potions_drank = 0

    _damage_deflected = 0
    _damage_dodged = 0
    _damage_taken_personal = 0
    _damage_taken_minions = 0
    _damage_dealt_personal = 0
    _damage_dealt_minions = 0

    @classmethod
    def add_damage_taken_minion(cls, amt=1) -> None:
        cls._damage_taken_minions += amt

    @classmethod
    def add_damage_taken_personal(cls, amt=1) -> None:
        cls._damage_taken_personal += amt

    @classmethod
    def add_damage_deflected(cls, amt=1) -> None:
        cls._damage_deflected += amt

    @classmethod
    def add_damage_dodged(cls, amt=1) -> None:
        cls._damage_dodged += amt

    @classmethod
    def add_damage_dealt_personal(cls, amt=1) -> None:
        cls._damage_dealt_personal += amt

    @classmethod
    def add_damage_dealt_minions(cls, amt=1) -> None:
        cls._damage_dealt_minions += amt

    @classmethod
    def add_kill(cls, amt=1) -> None:
        cls._kills += amt

    @classmethod
    def add_raise(cls, amt=1) -> None:
        cls._raised += amt

    @classmethod
    def add_butchery(cls, amt=1) -> None:
        cls._butchered += amt

    @classmethod
    def add_spirit(cls, amt=1) -> None:
        cls._spirits += amt

    @classmethod
    def add_ration_eat(cls, amt=1) -> None:
        cls._rations_eaten += amt

    @classmethod
    def add_potion_drink(cls, amt=1) -> None:
        cls._potions_drank += amt

    @classmethod
    def add_fallen_minion(cls, amt=1) -> None:
        cls._fallen_minions += amt

    @classmethod
    def print_stats(cls) -> None:
        cls._print_general_stats()
        print()  # Divider
        cls._print_damage_stats()
        print()  # Divider
        cls._print_item_stats()

    @classmethod
    def _print_general_stats(cls) -> None:
        cls._print_kills()
        cls._print_raised()
        cls._print_fallen_minions()
        cls._print_butchered()
        cls._print_spirits()

    @classmethod
    def _print_damage_stats(cls) -> None:
        cls._print_damage_dealt_personal()
        cls._print_damage_dealt_minions()
        cls._print_damage_taken_personal()
        cls._print_damage_taken_minions()
        cls._print_damage_deflected()
        cls._print_damage_dodged()

    @classmethod
    def _print_item_stats(cls) -> None:
        cls._print_rations_eaten()
        cls._print_potions_drank()

    """ General stats START """

    @classmethod
    def _print_kills(cls) -> None:
        if cls._kills > 0:
            print(f"You killed {cls._kills} {util.make_plural('monster', cls._kills)}.")
        else:
            print(f"No monsters were felled by your hand.")

    @classmethod
    def _print_raised(cls) -> None:
        if cls._raised > 0:
            print(
                f"You raised {cls._raised} new {util.make_plural('minion', cls._kills)} to serve in your army."
            )
        else:
            print(f"No minions have joined your army of the dead, for now.")

    @classmethod
    def _print_fallen_minions(cls) -> None:
        if cls._fallen_minions > 0:
            print(
                f"In battle, {cls._fallen_minions} {util.make_plural('minion', cls._fallen_minions)} fell in your defense, only to rise again."
            )
        else:
            print("None of your minions fell to the creatures of the dungeon.")

    @classmethod
    def _print_butchered(cls) -> None:
        if cls._butchered > 0:
            print(
                f"You butchered {cls._butchered} {util.make_plural('monster', cls._kills)} for food."
            )
        else:
            print(f"No monsters were butchered for food.")

    @classmethod
    def _print_spirits(cls) -> None:
        if cls._spirits > 0:
            print(
                f"Due to your actions, {cls._spirits} new {util.make_plural('bone spirit', cls._spirits)} haunt the earth."
            )
        else:
            print(f"You refrained from releasing new bone spirits upon the world.")

    """ Damage stats START """

    @classmethod
    def _print_damage_dealt_personal(cls) -> None:
        if cls._damage_dealt_personal > 0:
            print(
                f"By your hands, your enemies suffered {cls._damage_dealt_personal} damage."
            )
        else:
            print("Your hands are unsullied by combat; you dealt no damage personally.")

    @classmethod
    def _print_damage_dealt_minions(cls) -> None:
        if cls._damage_dealt_minions > 0:
            print(
                f"Your army of the dead collectively dealt {cls._damage_dealt_minions} damage to your enemies."
            )
        else:
            print("Your undead army inflicted no wounds on your enemies.")

    @classmethod
    def _print_damage_taken_personal(cls) -> None:
        if cls._damage_taken_personal > 0:
            print(
                f"You suffered {cls._damage_taken_personal} damage from the denizens of the dungeon."
            )
        else:
            print("Like a ghost, you were untouched by your enemies.")

    @classmethod
    def _print_damage_taken_minions(cls) -> None:
        if cls._damage_taken_minions > 0:
            print(
                f"Acting in your defense, your minions suffered {cls._damage_taken_minions} damage."
            )
        else:
            print("None of your minions suffered harm in the dungeon.")

    @classmethod
    def _print_damage_deflected(cls) -> None:
        if cls._damage_deflected > 0:
            print(
                f"Protected by your Shadowcloak, it absorbed {cls._damage_deflected} damage intended for you."
            )
        else:
            print("Your Shadowcloak absorbed no damage intended for you.")

    @classmethod
    def _print_damage_dodged(cls) -> None:
        if cls._damage_dodged > 0:
            print(
                f"Fleeting as a shadow, you managed to evade {cls._damage_dodged} damage intended for you."
            )
        else:
            print("You did not evade any damage.")

    """ Item stats START """

    @classmethod
    def _print_rations_eaten(cls) -> None:
        if cls._rations_eaten > 0:
            print(
                f"During your stay in the dungeon, you ate {cls._rations_eaten} {util.make_plural('ration', cls._rations_eaten)}. Some of them may have been former residents."
            )
        else:
            print("In your relentless pursuit for freedom, you ate no food at all.")

    @classmethod
    def _print_potions_drank(cls) -> None:
        if cls._potions_drank > 0:
            print(
                f"Through your body courses the remnant, tainted magic of {cls._potions_drank} healing {util.make_plural('potion', cls._potions_drank)}."
            )
        else:
            print("Your body remains untainted by the contents of healing potions.")
