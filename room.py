from variables import Variables

import random


class Room:

    """Constants"""

    VALID_ROOM_TYPES = (
        "generic",
        "armory",
        "kitchen",
        "workshop",
    )

    POSSIBLE_SEARCHES = (
        "skeleton",
        "food",
        "weapon",
        "armor",
        "potion",
    )

    """Instance variables"""

    _search_chance = Variables.ROOM_BASE_SEARCH_CHANCE
    _search_reduction = Variables.ROOM_BASE_SEARCH_CHANCE / Variables.MAX_ROOM_SEARCHES

    def __init__(self, name, room_type="generic"):
        self._name = name
        self._times_searched = 0

        if room_type not in Room.VALID_ROOM_TYPES:
            raise ValueError(f"New room was provided invalid type {room_type}.")
        else:
            self._room_type = room_type

    @property
    def times_searched(self):
        return self._times_searched

    @times_searched.setter
    def times_searched(self, amt):
        self._times_searched = amt

    @property
    def search_chance(self):
        return self._search_chance

    @property
    def name(self):
        return self._name

    @property
    def room_type(self):
        return self._room_type

    def search(self) -> str:
        """Roll to find something in the room.
        The returned string corresponds with what gets generated."""

        success = random.randint(0, 100) < self.search_chance
        self._search_chance -= self._search_reduction

        if success:
            result = self._roll_for_item()
            if self._search_chance < 0:
                self._search_chance = 0

            # Rerolls below. Room types have special cases that allow a
            # reroll.
            match self.room_type:
                case "armory":
                    if result != "weapon" and result != "armor":
                        result = self._roll_for_item()
                case "kitchen":
                    if result != "food":
                        result = self._roll_for_item()
                case "workshop":
                    if result != "skeleton" and result != "potion":
                        result = self._roll_for_item()

            return result

        else:
            return "nothing"

    def _roll_for_item(self) -> str:
        return random.choice(Room.POSSIBLE_SEARCHES)
