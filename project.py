import sys

import util

from battlemaster import BattleMaster
from dm import DM
from room import Room
from stats import Stats
from variables import Variables


def main():
    print_intro()
    name = get_name()
    length = get_dungeon_length()

    # name = "Lucky"
    # length = 10

    if setup_game(name, length):
        play_game(length)


def setup_game(player_name: str, dungeon_length: int):
    DM.setup_player(player_name)

    DM.load_data()
    DM.place_runes(dungeon_length)

    return True


def play_game(length: int) -> None:
    room_count = 1
    room = Room(f"Entryway to the Dungeon of {length} Despairs")

    while True:
        skip_hunger = False
        while True:
            util.clear()

            if room_count == length:
                _do_final_boss()

            if DM.player.doom >= 100:
                do_battle()

            print(f"You are {DM.player.name} the Necromancer.")
            if room_count == 1:
                print(f"You stand in the {room.name}.")
            else:
                print(
                    f"You stand in the {room.name}, {room_count} rooms deep into the dungeon."
                )

            if room.times_searched > 0:
                search_str = f"You have searched this room {room.times_searched}"
                if room.times_searched == 1:
                    search_str += " time."
                else:
                    search_str += " times."
                print(search_str)

            DM.print_player_info(room_count)

            if (feeling := DM.get_bad_feeling()) != "":
                print(f"{feeling}")

            # CHOICES
            # 1. Search the room.
            # 2. Rest here a while.
            # 3. Look for a fight.
            # 4. Continue exploring.
            # 5. Manage your undead army.
            # 6. Drink a healing potion.
            # Q. Surrender.

            print_choices()

            try:
                choice = input("\nChoose an option: ")
                try:
                    choice = int(choice)
                    match choice:
                        case 1:
                            # search the room
                            if room.search_chance > 0:
                                print("\nYou search the room...")
                                print(do_search_result(room.search()))
                                room.times_searched += 1
                                util.continue_prompt()
                                break
                            else:
                                print(
                                    "\nYou have searched the room enough times that you don't think you will find anything else here."
                                )
                                util.continue_prompt()
                                skip_hunger = True
                                break
                        case 2:
                            # rest
                            if (
                                DM.player.hp < DM.player.max_hp
                                and DM.player.hunger + Variables.RESTING_HUNGER_RATE
                                < 100
                            ):
                                print("\nYou prepare to rest your weary bones...\n")
                                while True:
                                    try:
                                        print(
                                            "How long do you want to rest? You will gain that much in HP and twice that hunger."
                                        )
                                        print(
                                            f"You are at {DM.player.hp} of {DM.player.max_hp} possible health."
                                        )
                                        print(f"You are at {DM.player.hunger}% hunger.")
                                        wait_time = input(
                                            "\nRest length (0 to cancel): "
                                        )
                                        try:
                                            wait_time = int(wait_time)
                                            if wait_time == 0:
                                                print("\nYou decide against resting.")
                                                util.continue_prompt()
                                                break
                                            else:
                                                starvation = 100 - DM.player.hunger
                                                hp_diff = (
                                                    DM.player.max_hp - DM.player.hp
                                                )
                                                if (wait_time * 2) >= starvation:
                                                    print(
                                                        "\nYou can't wait that long -- you'll starve to death!"
                                                    )
                                                elif wait_time > hp_diff:
                                                    print(
                                                        "\nYou will not benefit from resting for that long."
                                                    )
                                                else:
                                                    print("\nYou rest for a while...")
                                                    DM.player.hp += wait_time
                                                    DM.player.hunger += wait_time * 2
                                                    print(
                                                        f"HP increases to {DM.player.hp}."
                                                    )
                                                    print(
                                                        f"Hunger increases to {DM.player.hunger}%."
                                                    )
                                                    DM.increase_doom()
                                                    util.continue_prompt()
                                                    break
                                        except ValueError:
                                            print("Unknown input.")
                                    except (EOFError, ValueError):
                                        print("You decide against resting.")
                                    util.continue_prompt()
                                    break
                                skip_hunger = True
                                break
                            else:
                                if DM.player.hp == DM.player.max_hp:
                                    print("\nYou need no rest; you are fully healthy.")
                                if (
                                    DM.player.hunger + Variables.RESTING_HUNGER_RATE
                                    >= 100
                                ):
                                    print(
                                        "\nYou have no time to wait -- you are about to starve to death!"
                                    )
                                util.continue_prompt()
                                skip_hunger = True
                        case 3:
                            # start fight
                            do_battle(self_triggered=True)
                            break
                        case 4:
                            # continue exploring
                            util.clear()
                            print("You delve deeper into the dungeon.")
                            room_count += 1
                            room = DM.generate_room()
                            print(
                                f"You find yourself entering a new room: the {room.name}."
                            )
                            give_room_hints(room.room_type)
                            DM.try_find_rune(room_count)
                            util.continue_prompt()
                            break
                        case 5:
                            # manage undead ratios
                            manage_undead_ratio()
                            skip_hunger = True
                            break
                        case 6:
                            # drink a healing potion
                            if DM.player.potions > 0:
                                util.clear()
                                print(
                                    "You pop the cork of a healing potion and take a swig. Refreshing!"
                                )
                                DM.player.potions -= 1
                                DM.player.hp += Variables.POTION_VALUE
                                Stats.add_potion_drink()
                                print(
                                    f"\nYou gain {Variables.POTION_VALUE} health, bringing your health to {DM.player.hp} out of a maximum possible {DM.player.max_hp}."
                                )
                            else:
                                print("\nUnfortunately, you have no healing potions.")
                            skip_hunger = True
                            util.continue_prompt()
                        case _:
                            print("Unknown choice.")
                except ValueError:
                    if choice.lower() == "q":
                        util.close(DM.player.name)
                    else:
                        print("Unknown choice.")
            except (EOFError, KeyboardInterrupt):
                print("Unknown choice.")

        DM.update_minion_stats()

        if not skip_hunger:
            DM.player.hunger += Variables.HUNGER_RATE

            _try_eat_food()

            if DM.player.hunger >= 100:
                DM.do_bad_ending("starvation")

            DM.increase_doom()


def _try_eat_food() -> None:
    if DM.player.hunger >= Variables.FOOD_VALUE and DM.player.food > 0:
        print(f"\nYou eat one of your food rations. (-{Variables.FOOD_VALUE}% hunger)")
        DM.player.food -= 1
        DM.player.hunger -= Variables.FOOD_VALUE
        Stats.add_ration_eat()
        util.continue_prompt()


def manage_undead_ratio() -> None:
    """Attacking minions will attack during a fight.
    Defending minions will take damage in the player's place.
    """

    if DM.player.minion_count == 0:
        print("\nNo minions serve under your command.")
        util.continue_prompt()
    else:
        util.clear()
        _print_minions()
        _print_ratio()
        _do_ratio_management()
        util.continue_prompt()


def _do_ratio_management():
    print("\nWhat do you want to do?")
    print("\n1. Set minions to offensive.")
    print("2. Set minions to defensive.")
    print(
        f"3. Set minion default behavior. (Currently {DM.player.minion_default.capitalize()})"
    )
    print("Q. Finish making changes.")

    while True:
        try:
            choice = input("\nChoice: ")
            try:
                choice = int(choice)
                if choice == 1:
                    if _move_minions_to_attacking():
                        break
                elif choice == 2:
                    if _move_minions_to_defending():
                        break
                elif choice == 3:
                    DM.player._prompt_for_default_behavior()
                    break
                else:
                    print("\nUnknown choice.")
            except ValueError:
                if choice.lower() == "q":
                    print("\nYou return your focus to the dungeon.")
                    break
                else:
                    print("\nUnknown choice.")
        except (EOFError, KeyboardInterrupt):
            print("\nUnknown choice.")


def _move_minions_to_attacking() -> bool:
    """Move minions from defending to attacking.
    You cannot move minions if none are defending.

    Return True if we are breaking out of the ratio management.
    """
    if DM.player.minions_defending == 0:
        print("\nYou have no defending minions to command.")
    else:
        max = DM.player.minions_defending
        while True:
            try:
                choice = input(
                    f"\nHow many minions will move to offense? (max {max}): "
                )
                try:
                    choice = int(choice)
                    if choice > max:
                        print("\nYou do not have that many minions to move.")
                    elif choice < 0:
                        print("\nYou cannot move a negative amount of minions.")
                    elif choice == 0:
                        print("\nYou decide to make no changes.")
                        return False
                    else:
                        # Select the first n minions that are defending and set them to attacking.
                        set = 0
                        for minion in DM.player.minions:
                            if minion.defending:
                                minion.attacking = True
                                set += 1
                            if set == choice:
                                break
                        print(
                            f"\nYou command {choice} {util.make_plural('minion', choice)} to attack."
                        )
                        print(
                            f"\nDefending minions remaining: {DM.player.minions_defending}"
                        )
                        return True
                except ValueError:
                    print("\nUnknown choice.")
            except (EOFError, KeyboardInterrupt):
                print("\nUnknown choice.")


def _move_minions_to_defending() -> bool:
    """Move minions from attacking to defending.
    You cannot move minions if none are attacking.

    Return True if we are breaking out of the ratio management.
    """
    if DM.player.minions_attacking == 0:
        print("\nYou have no attacking minions to command.")
    else:
        max = DM.player.minions_attacking
        while True:
            try:
                choice = input(
                    f"\nHow many minions will move to defense? (max {max}): "
                )
                try:
                    choice = int(choice)
                    if choice > max:
                        print("\nYou do not have that many minions to move.")
                    elif choice < 0:
                        print("\nYou cannot move a negative amount of minions.")
                    elif choice == 0:
                        print("You decide to make no changes.")
                        return False
                    else:
                        # Select the first n minions that are defending and set them to attacking.
                        set = 0
                        for minion in DM.player.minions:
                            if minion.attacking:
                                minion.defending = True
                                set += 1
                            if set == choice:
                                break
                        print(
                            f"\nYou command {choice} {util.make_plural('minion', choice)} to defend."
                        )
                        print(
                            f"\nAttacking minions remaining: {DM.player.minions_attacking}"
                        )
                        return True
                except ValueError:
                    print("\nUnknown choice.")
            except (EOFError, KeyboardInterrupt):
                print("\nUnknown choice.")


def _print_minions():
    print("These minions serve under your command...")
    for minion in DM.player.minions:
        print(f"\t{minion.name}")
    print(f"Total: {DM.player.minion_count}")


def _print_ratio():
    print(f"\nMinions attacking: {DM.player.minions_attacking}")
    print(f"Minions defending: {DM.player.minions_defending}")

    print("\nAttacking minions will attack your enemies every turn.")
    print(f"Currently, they will deal {DM._get_minion_attack()} damage per turn.")

    print("\nDefending minions will take attacks intended for you.")
    print(
        f"Currently, a minion can withstand {DM._get_minion_defense()} damage before being destroyed."
    )


def _do_final_boss() -> None:
    util.clear()

    print(
        "As you enter the final chamber of the dungeon, you notice an unsettling silence permeating the area."
    )
    print("\nSuddenly, there is a noise, the clinking of chains in the darkness.")
    print(
        "A fell growl fills the chamber as a ragged, towering figure, shackles around its wrists and ankles, shambles into the light of your death lantern."
    )
    print(
        "\nThe creature snatches away the final Rune of Escape and charges towards you with a feral roar!"
    )

    util.continue_prompt()

    boss = DM.generate_final_boss()
    bm = BattleMaster(DM.player, boss)
    bm.do_battle()

    util.clear()

    check_player_dead(boss.name)
    DM.do_victory()


def do_battle(self_triggered=False) -> None:
    util.clear()

    monster = DM.generate_monster()

    if self_triggered:
        print(f"You are the darkness that stalks these halls...")
        print(f"You come upon the {monster.name}!")
    else:
        print("A dreadful noise echoes from up ahead!")
        print(f"\nThe {monster.name} emerges from the darkness!")

    util.continue_prompt()

    bm = BattleMaster(DM.player, monster)
    bm.do_battle()

    DM.player.doom = 0
    util.clear()

    check_player_dead(monster.name)


def check_player_dead(killer: str) -> None:
    if DM.player.hp <= 0:
        DM.do_bad_ending("damage", killer=killer)


def give_room_hints(room_type: str) -> None:
    match room_type:
        case "kitchen":
            print("You think you could find some food here.")
        case "armory":
            print("You may be able to find weapons or armor here.")
        case "workshop":
            print("You might be able to find potions here.")


def print_choices() -> None:
    print("\nWhat do you do?\n")
    print(
        f"1. Search the room.\t\t(+{Variables.HUNGER_RATE}% hunger, chance to find items, food, and skeletons)"
    )
    print("2. Rest here a while.\t\t(Gain HP and Hunger)")
    print("3. Look for a fight.\t\t(Immediately start a battle)")
    print(
        f"4. Continue exploring.\t\t(+{Variables.HUNGER_RATE}% hunger, enter a new room)"
    )
    print(
        f"5. Manage your undead army.\t(Change Attack/Defense Ratio, currently {DM.player.minions_attacking}/{DM.player.minions_defending})"
    )
    print(f"6. Drink a healing potion.\t(-1 Potion, +{Variables.POTION_VALUE} HP)")
    print("\nQ. Surrender to the darkness...")


def do_search_result(result: str) -> str:
    """See Room.POSSIBLE_SEARCHES for types."""

    match result:
        case "nothing":
            return "...but you find nothing of use."
        case "skeleton":
            print("...and you find the skeleton of a previous tenant. Rise!")
            DM.add_generic_minion()
            return ""
        case "weapon":
            DM.player.weapon += 1
            if DM.player.weapon == 6:
                # Finding the scythe
                return "...amazing! You find an intact Blackmetal scythe! Now you may empower it with wandering souls..."
            if DM.player.weapon > 6:
                return (
                    "...and you find a wandering soul to empower your scythe further!"
                )
            else:
                return "...and you find an intact weapon!"
        case "armor":
            DM.player.armor += 1
            return "...and you find servicable armor! Your Shadowcloak consumes it to grow in power."
        case "potion":
            DM.player.potions += 1
            return "...and you find a potion of healing!"
        case "food":
            DM.player.add_food(1)
            return "...and you find some edible food!"


def print_intro() -> None:
    """Print the intro text."""
    util.clear()

    intro = """\n\n\t\tYou are a necromancer who has been thrown into the Dungeon of Despair for your crimes.
            \tIn order to escape, you must find the three magical runes and return to the entrance.
            \tA hungering curse has been placed upon you, and you must move quickly.

            \tAs you enter the dungeon, you find the skeleton of a prisoner who came before you.
            \tWith your necromancy, you give them new life... in your service!
            """

    print(intro)

    util.continue_prompt()


def get_name() -> str:
    util.clear()

    try:
        while True:
            name = input("What is your name? ")
            if name.isspace() or len(name) == 0:
                print("Please enter a name.")
            else:
                return name
    except (EOFError, KeyboardInterrupt):
        util.close()


def get_dungeon_length() -> int:
    while True:
        print(
            """What is the length of the dungeon?

              1. Short (10 rooms)
              2. Medium (20 rooms)
              3. Long (30 rooms)
              4. Custom Length
              Q. Quit
              """
        )
        try:
            choice = input("Choice: ")
            if choice.lower() == "q":
                util.close()
            try:
                choice = int(choice)
                match choice:
                    case 1:
                        return 10
                    case 2:
                        return 20
                    case 3:
                        return 30
                    case 4:
                        while True:
                            length = input(
                                "How many rooms are in the dungeon? (Minimum 10, maximum 100) "
                            )
                            try:
                                length = int(length)
                                if length < 10:
                                    print("Too few rooms!")
                                elif length > 100:
                                    print("Too many rooms!")
                                else:
                                    return length
                            except ValueError:
                                print("Invalid input.")
                    case _:
                        print("Invalid input")
            except ValueError:
                print("Unknown choice.")
        except KeyboardInterrupt:
            util.close()
        except EOFError:
            util.close()


if __name__ == "__main__":
    main()
