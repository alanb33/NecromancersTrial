from variables import Variables

import random


class Room:

    def __init__(self, name, room_type="generic"):
        
        if room_type not in Room.VALID_ROOM_TYPES:
            raise ValueError(f"New room was provided invalid type {room_type}.")
        else:
            self._room_type = room_type

        self._size = self._roll_room_size()
        self._max_searches = self.size
        self._name = self._get_name(name)

        self._times_searched = 0
        self._search_chance = Variables.ROOM_BASE_SEARCH_CHANCE
        self._search_reduction = Variables.ROOM_BASE_SEARCH_CHANCE / self._max_searches

    # Normal methods

    def search(self) -> str:
        """Roll to find something in the room.
        The returned string corresponds with what gets generated.
        
        TODO: Relying on strings seems like a bad idea; think about 
                better solutions.
        """

        success = random.randint(0, 100) < self.search_chance
        self.times_searched += 1

        if success:
            return self._roll_for_item()
        else:
            return "nothing"
    
    # Private methods

    def _get_name(self, name) -> str:
        """From a given name, prepend 'small' or 'large' depending on
        the internal _max_searches variable.
        
        Example of returns:

        'small noxious chamber' where _max_searches is < Variables.ROOM_AVG_SEARCHES
        'large evil scullery' where _max_searches is > Variables.ROOM_AVG_SEARCHES
        'cursed armory' where _max_searches == Variables.ROOM_AVG_SEARCHES

        TODO: Write a test case for this. Room size must be specified
                by a mock. Rooms less than AVG_SEARCHES should be
                prepended by "small " and more than AVG_SEARCHES should
                be prepended by "large ". AVG_SEARCHES size should have
                no prepend.
        """

        prepend = ""
        if self.max_searches < Variables.ROOM_AVG_SEARCHES:
            prepend = "small "
        elif self.max_searches > Variables.ROOM_AVG_SEARCHES:
            prepend = "large "
        return f"{prepend}{name}"

    def _reduce_search_chance(self) -> None:
        """Each search reduces the chance to find another item.
        
        TODO: TEST CASE: search_chance after calling search() should be
                less than before it was called.
        """

        self.search_chance -= self.search_reduction

    def _roll_room_size(self) -> int:
        """Roll a random number to determine the room size. The chances
        are delimited by Variables.ROOM_SIZE_DIFFERENCE_CHANCE.

        Returns room sizes as defined in Variables.

        TODO: Room #1, the Entryway, should always be size 3.
        TODO: TEST CASE: Room.size should only be >= ROOM_MIN_SEARCHES 
                and <= ROOM_MAX_SEARCHES.
        """

        diff_size_chance = Variables.ROOM_SIZE_DIFFERENCE_CHANCE
        
        roll = random.randint(0, 100)
        if (roll < diff_size_chance):
            return Variables.ROOM_MIN_SEARCHES
        elif (roll >= 100 - diff_size_chance):
            return Variables.ROOM_MAX_SEARCHES
        else:
            return Variables.ROOM_AVG_SEARCHES

    def _roll_for_item(self) -> str:
        """Roll for a random item. Depending on the room type, do a
        reroll if we don't get the expected item type.
        
        TODO: Consider turning the results into classes rather than
                having them as strings -- how should I go about that?
        """

        result: str = random.choice(Room.POSSIBLE_SEARCHES)
        
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

    # Properties

    @property
    def max_searches(self) -> int:
        return self._max_searches

    @property
    def name(self) -> str:
        return self._name

    @property
    def room_type(self) -> str:
        return self._room_type

    @property
    def search_chance(self) -> int:
        return self._search_chance

    @search_chance.setter
    def search_chance(self, new_chance) -> None:
        self._search_chance = new_chance
        if self._search_chance < 0:
            self._search_chance = 0

    @property
    def search_reduction(self) -> int:
        return self._search_reduction

    @property
    def searches_left(self) -> int:
        return self.max_searches - self.times_searched

    @property
    def size(self) -> int:
        return self._size

    @property
    def times_searched(self) -> int:
        return self._times_searched

    @times_searched.setter
    def times_searched(self, amt) -> None:
        self._times_searched = amt

    # Constants
    # TODO: Should these be stored a different way?

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