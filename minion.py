class Minion:

    """A minion's stats are based on the Player's.
    Their names are based on the monster you defeated!"""

    def __init__(self, name, master):
        if "skeletal" not in name:
            self._name = f"zombified {name}"
        else:
            self._name = name

        self._master = master

        self._max_hp = 1
        self._hp = self._max_hp

        self._damage = 1

        self._attacking = False
        self._defending = True

    @property
    def name(self) -> str:
        return self._name

    @property
    def max_hp(self) -> int:
        return self._max_hp

    @max_hp.setter
    def max_hp(self, amt) -> None:
        self._max_hp = amt
        if self._max_hp <= 0:
            raise ValueError("Minion tried to set an invalid max HP.")
        elif self._max_hp < self._hp:
            self.hp = self._max_hp

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, new_hp) -> int:
        self._hp = new_hp

    @property
    def damage(self) -> int:
        return self._damage

    @damage.setter
    def damage(self, amt) -> None:
        self._damage = amt
        if self._damage <= 0:
            raise ValueError("Minion tried to set an invalid damage.")

    @property
    def attacking(self) -> bool:
        return self._attacking

    @property
    def defending(self) -> bool:
        return self._defending

    @attacking.setter
    def attacking(self, mode: bool) -> None:
        self._attacking = mode
        self._defending = not mode

    @defending.setter
    def defending(self, mode: bool) -> None:
        self._defending = mode
        self._attacking = not mode
