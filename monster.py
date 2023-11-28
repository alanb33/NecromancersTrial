class Monster:

    """Monster game variables."""

    """Create a new Monster. Its level determines many of its stats.
    Its name is purely flavor text, no monster is different aside from their level.
    """

    def __init__(self, name, level=1, health_ratio=3, damage_ratio=1):
        self._name = name
        self._level = level if level > 1 else 1

        self._hp = self._level * health_ratio
        self._damage = self._level * damage_ratio

        self._pained = False
        self._dead = False

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, amt):
        self._hp = amt
        if self._hp <= 0:
            self._dead = True

    @property
    def damage(self):
        return self._damage

    @property
    def dead(self):
        return self._dead

    @property
    def pained(self):
        return self._pained

    @pained.setter
    def pained(self, mode: bool):
        self._pained = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def level(self):
        return self._level
