import os
import sys


def clear() -> None:
    """Clear the terminal."""

    if os.name == "nt":
        os.system("cls")
    else:
        os.system("clear")


def continue_prompt() -> None:
    """Prompt the Player to press Enter to continue.

    Avoids some throws from trying to cancel out.
    """

    try:
        input("\nPress enter to continue.")
    except KeyboardInterrupt:
        pass
    except EOFError:
        pass


def close(name: str = "necromancer") -> None:
    if name != "necromancer":
        sys.exit(f"\nUntil next time, {name} the Necromancer...\n")
    else:
        sys.exit(f"\nUntil next time, {name}...")


def make_plural(word, amt, ending="s") -> str:
    if amt == 1:
        return word
    else:
        return f"{word}{ending}"


def prompt_for_number_safely(question, num_choices):
    if num_choices <= 0:
        raise ValueError("Can't prompt for non-positive number of choices.")

    while True:
        try:
            choice = input(f"{question} ")
            try:
                choice = int(choice)
                if choice == 0 or choice > num_choices:
                    print("\nUnknown choice.")
                else:
                    return choice

            except ValueError:
                print("\nUnknown choice.")
        except (EOFError, KeyboardInterrupt):
            print("\nUnknown choice.")
