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

    def __init__(self, name, room_type="generic"):
        self._max_searches = self._roll_room_size()
        self._name = self._get_name(name)
        self._times_searched = 0
        self._search_chance = Variables.ROOM_BASE_SEARCH_CHANCE
        self._search_reduction = Variables.ROOM_BASE_SEARCH_CHANCE / self._max_searches

        if room_type not in Room.VALID_ROOM_TYPES:
            raise ValueError(f"New room was provided invalid type {room_type}.")
        else:
            self._room_type = room_type

    @property
    def max_searches(self) -> int:
        return self._max_searches

    @property
    def times_searched(self) -> int:
        return self._times_searched

    @times_searched.setter
    def times_searched(self, amt):
        self._times_searched = amt

    @property
    def search_chance(self) -> int:
        return self._search_chance

    @property
    def searches_left(self) -> int:
        return self._max_searches - self._times_searched

    @property
    def name(self) -> str:
        return self._name

    @property
    def room_type(self) -> str:
        return self._room_type

    def _roll_room_size(self) -> int:
        # TODO: Max room #1 always be size 3.
        diff_size_chance = Variables.ROOM_SIZE_DIFFERENCE_CHANCE
        
        roll = random.randint(0, 100)
        if (roll < diff_size_chance):
            return Variables.ROOM_MIN_SEARCHES
        elif (roll >= 100 - diff_size_chance):
            return Variables.ROOM_MAX_SEARCHES
        else:
            return Variables.ROOM_AVG_SEARCHES

    def _get_name(self, name) -> str:
        prepend = ""
        if self._max_searches < Variables.ROOM_AVG_SEARCHES:
            prepend = "small "
        elif self._max_searches > Variables.ROOM_AVG_SEARCHES:
            prepend = "large "
        return f"{prepend}{name}"

    def search(self) -> str:
        """Roll to find something in the room.
        The returned string corresponds with what gets generated."""

        success = random.randint(0, 100) < self._search_chance
        self._search_chance -= self._search_reduction
        self._times_searched += 1

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
