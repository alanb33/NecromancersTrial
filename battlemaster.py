import random

from player import Player
from monster import Monster
from minion import Minion
import util
from stats import Stats
from variables import Variables


class BattleMaster:
    """A class to help handle battles, taking some of the responsibility away from DM."""

    def __init__(self, player: Player, monster: Monster):
        self._player = player
        self._monster = monster

        # Warn the player during the final boss fight.
        self._runekeeper_first_time_bone_spirit = True

        if player == None:
            raise ValueError("BattleMaster tried to track non-existent player.")
        if monster == None:
            raise ValueError("BattleMaster tried to track non-existent monster.")

        self._fled = False

    @property
    def fled(self) -> bool:
        return self._fled

    @fled.setter
    def fled(self, mode: bool) -> None:
        self._fled = mode

    @property
    def commanding_undead(self) -> bool:
        return self._commanding_undead

    @commanding_undead.setter
    def commanding_undead(self, mode: bool) -> None:
        self._commanding_undead = mode

    @property
    def player(self) -> Player:
        return self._player

    @property
    def monster(self) -> Monster:
        return self._monster

    def do_battle(self) -> None:
        """Main battle loop.

        This occurs in several steps:

        1. Player chooses their action.
        2. If BONE SPIRIT was cast, end battle. Award level but no souls.
        3. If Monster's heal reaches 0, end battle. Award level and soul.
        4. Any attacking minions deal damage.
        5. If Monster's heal reaches 0, end battle. Award level and soul.
        6. Monster attacks, dealing damage to minions first if possible.
        7. Command undead resolves.
        8. Begin new round.

        """

        while True:
            util.clear()
            self._reset_variables()

            self._print_battle_status()
            self._print_battle_choices()

            choice: str = self._get_player_choice()

            util.clear()

            self._resolve_player_choice(choice)

            if choice == "CAST_BONE_SPIRIT" and self.monster.name != "Runekeeper":
                # Victory is done in _resolve_player_choice
                break

            if self.fled:
                self._heal_living_minions()
                break

            if self._monster_dead():
                self._do_victory(self._get_monster_death_description(choice))
                break

            self._do_minion_damage()

            if self._monster_dead():
                self._do_victory(
                    monster_death_description="is ripped apart by an army of undead!"
                )
                break

            self._do_monster_attack()

            if self._player_dead():
                # Let DM handle this
                break

            # util.continue_prompt()

    def _print_battle_status(self) -> None:
        """Report on the status of the battle."""

        info = f"You are fighting the {self.monster.name}."

        if self.player.level < self.monster.level:
            info += "\nIt looks stronger than you.\n"
        elif self.player.level > self.monster.level:
            info += "\nIt looks weaker than you.\n"
        else:
            info += "\n"

        info += f"\nYou have {self.player.hp} out of {self.player.max_hp} health."
        info += f"\n\nThe {self.monster.name} has {self.monster.hp} health remaining."
        info += f"\nThe {self.monster.name} will deal {self.monster.damage} damage this turn."

        if self.player.minion_count > 0:
            defenders = self.player.minions_defending
            attackers = self.player.minions_attacking

            info += f"\n\nYou have {defenders} {util.make_plural('minion', defenders)} defending you and {attackers} {util.make_plural('minion', attackers)} on the attack."

            if attackers > 0:
                damage_sum = 0
                for minion in self.player.minions:
                    if minion.attacking:
                        damage_sum += minion.damage

                info += f"\nYour attacking {util.make_plural('minion', attackers)} will deal {damage_sum} damage before the enemy can act."
            if defenders > 0:
                hp_sum = 0
                for minion in self.player.minions:
                    if minion.defending and minion.hp > 0:
                        hp_sum += minion.hp
                info += f"\nYour defending {util.make_plural('minion', defenders)} can absorb {hp_sum} damage this turn."

        if self.player.armor == 0:
            info += f"\n\nYour Shadowcloak is not yet powerful enough to deflect blows."
        else:
            minion_str = " "
            if self.player.minions_defending > 0:
                minion_str = " or your minions "
            info += f"\n\nYour Shadowcloak will absorb {self.player.armor} damage before you{minion_str}are struck."

        print(info)

    def _print_battle_choices(self) -> None:
        """
        "ATTACK",
        "CAST_PAIN",
        "CAST_VAMPIRIC_TOUCH",
        "CAST_BONE_SPIRIT",
        "DRINK_POTION",
        "COMMAND_MINION_ATTACK",
        "COMMAND_MINION_DEFNED",
        "TRY_DODGE",
        "TRY_FLEE",
        """

        print("\nActions:")
        print(
            f"\n1. Attack the enemy with {self.player._get_weapon_descriptor()} ({self.player.weapon} damage)"
        )
        print(
            f"2. Cast Spell: Pain. ({self._get_pain_damage()} damage, make enemy deal reduced damage of {self._get_pained_damage()} for this turn.)"
        )
        print(
            f"3. Cast Spell: Vampiric Touch. ({self._get_vampiric_touch_damage()} damage, heal for damage dealt.)"
        )
        print(
            f"4. Cast Spell: Dealt Bolt. ({self._get_death_bolt_damage()} damage, but you take {self._get_death_bolt_self_damage()} in exchange.)"
        )
        if self.monster.name != "Runekeeper":
            print(
                f"5. Cast Spell: Bone Spirit. (Instant kill, but costs a soul to use and destroys the monster's soul. You have {self.player.souls} {util.make_plural('soul', self.player.souls)}.)"
            )
        else:
            print(
                f"5. Cast Spell: Bone Spirit. (This cannot kill the Runekeeper, but will deal {self._get_bone_spirit_damage()} damage. You have {self.player.souls} {util.make_plural('soul', self.player.souls)}."
            )
        print(
            f"6. Drink a healing potion. (-1 Potion, +{Variables.POTION_VALUE} HP. You have {self.player.potions} remaining.)"
        )
        print(
            f"7. Command a minion to attack. (One minion swaps from defense to offense.{self._get_damage_forecast_offensive_swap()})"
        )
        print(
            f"8. Command a minion to defend. (One minion swaps from offense to defense.{self._get_damage_forecast_defensive_swap()})"
        )
        print(
            f"9. Try to dodge the enemy's attack. ({self._get_dodge_chance()}% chance of success)"
        )
        print(f"\n0. Try to flee! ({self._get_flee_chance()}% chance of success)\n")

    def _get_flee_chance(self) -> int:
        flee_chance = Variables.FLEE_BASE_CHANCE
        level_diff = self.player.level - self.monster.level
        flee_chance += level_diff * Variables.FLEE_LEVEL_VARIANCE

        if flee_chance < 0:
            return 0

        return flee_chance

    def _get_bone_spirit_damage(self) -> int:
        return self.player.level + self.player.weapon + self.player.souls

    def _get_dodge_chance(self) -> int:
        dodge_chance = Variables.DODGE_BASE_CHANCE
        level_diff = self.monster.level - self.player.level
        dodge_chance -= level_diff * Variables.DODGE_LEVEL_VARIANCE

        if dodge_chance < 0:
            return 0

        return dodge_chance

    def _get_damage_forecast_offensive_swap(self) -> str:
        damage_str = ""
        if self.player.minion_count > 0 and self.player.minions_defending > 0:
            damage_str = f" The enemy will take {self.player.minions[0].damage} additional damage this turn."
        return damage_str

    def _get_damage_forecast_defensive_swap(self) -> str:
        damage_str = ""
        if self.player.minion_count > 0 and self.player.minions_attacking > 0:
            damage_str = f" The enemy will take {self.player.minions[0].damage} less damage this turn."
        return damage_str

    def _do_monster_attack(self):
        """Now the self.monster.attacks the self.player.

        The self.monster.s damage is equal to its level.
        If the self.monster.is pained, it will deal reduced damage.
        First, the self.monster.will deal damage to any defending minions.
        If the minion HP reaches 0, it is destroyed.

        If no defending minions remain, the self.player.themselves will take damage.
        """

        # Calculate damage.

        monster_damage = self.monster.damage
        if self.monster.pained:
            monster_damage = self._get_pained_damage()

        if monster_damage == 0 and self.monster.pained:
            print(
                f"\nThe {self.monster.name} rears up to strike, but falters from the pain."
            )
        else:
            # Reduce incoming damage by Shadowcloak first.

            print(f"\nThe {self.monster.name} springs forward to strike!")

            if self.player.armor > 0:
                Stats.add_damage_deflected(self.player.armor)
                monster_damage -= self.player.armor
                if monster_damage > 0:
                    print(
                        f"\nYour Shadowcloak whirls in protection, absorbing {self.player.armor} damage as the monster tries to land a hit."
                    )
                else:
                    print(
                        f"\nYour Shadowcloak surges with power, deflecting the blow entirely!"
                    )

            # Now try to hit minions.

            if monster_damage > 0:
                # Monster damage remains, so let minions absorb it.
                if self.player.minions_defending > 0:
                    for minion in self.player.minions:
                        if minion.defending and minion.hp > 0:
                            max_possible_damage = minion.hp
                            minion.hp -= monster_damage

                            if minion.hp <= 0:
                                print(
                                    f"\nThe {self.monster.name} strikes the {minion.name} for {max_possible_damage} damage, pummeling it into lifelessness! (-1 minion for this fight)"
                                )
                                Stats.add_fallen_minion()
                                Stats.add_damage_taken_minion(max_possible_damage)

                                monster_damage -= max_possible_damage  # Reduce the damage so we can move on the next minion
                                if monster_damage == 0:
                                    break
                            else:
                                if monster_damage > 0:
                                    print(
                                        f"\nThe {self.monster.name} strikes the {minion.name} for {monster_damage} damage! Your minion has {minion.hp} HP remaining."
                                    )
                                    Stats.add_damage_taken_minion(monster_damage)
                                    monster_damage -= monster_damage

            # Minions have taken all damage, or they are all destroyed.

            if monster_damage > 0:
                # Here's the last chance to dodge!
                if self.player.dodging and self._dodge_successful():
                    print(f"\nYou manage to evade the {self.monster.name}'s blow!")
                    Stats.add_damage_dodged(monster_damage)
                else:
                    if self.player.dodging:
                        print(
                            f"\nYou try to dodge away, but the {self.monster.name} cuts you off! It strikes you heavily!"
                        )
                    else:
                        print(f"\nThe {self.monster.name} mauls you!")

                    if monster_damage > 0:
                        self._player_take_damage(monster_damage)

        util.continue_prompt()

    def _player_take_damage(self, monster_damage: int) -> None:
        Stats.add_damage_taken_personal(monster_damage)
        self.player.hp -= monster_damage
        print(
            f"You suffer {monster_damage} damage, bringing you to {self.player.hp} health."
        )

    def _dodge_successful(self) -> bool:
        dodge_chance = Variables.DODGE_BASE_CHANCE
        level_diff = self.monster.level - self.player.level
        dodge_chance -= level_diff * Variables.DODGE_LEVEL_VARIANCE

        return random.randint(0, 100) < dodge_chance

    def _reset_variables(self) -> None:
        """At the top of the round, reset any temporary variables."""

        self.player.dodging = False
        self.monster.pained = False

    def _get_monster_death_description(self, choice: str) -> str:
        match choice:
            case "ATTACK":
                return f"is slain by a well-placed blow from {self.player._get_weapon_descriptor().removesuffix('.')}."
            case "CAST_PAIN":
                return "writhes in agony until it moves no more, its heart stopped."
            case "CAST_VAMPIRIC_TOUCH":
                return "collapses to the floor, colorless and drained of life."
            case "CAST_DEATH_BOLT":
                return "is thrown lifelessly against the wall of the chamber like a rag doll from the force of the death bolt."
            case _:
                if choice == "CAST_BONE_SPIRIT" and self.monster.name == "Runekeeper":
                    return "thunders to the ground in a ragged pile of spirit-ravaged wounds."
                else:
                    return f"expires in some mysterious way. ({choice})"

    def _player_dead(self):
        return self.player.hp <= 0

    def _cast_bone_spirit(self):
        """A Bone Spirit cast instantly kills the self.monster. but a soul is used
        and the self.player.does not gain a new one.

        However, the Runekeeper is not killed, but takes damage instead!"""

        print(
            f"\nDrawing forth a vengeful soul from your death lantern, you release it in the direction of the {self.monster.name}!"
        )
        self.player.souls -= 1

        if self.monster.name != "Runekeeper":
            death = "dies in agony, the screaming Bone Spirit scouring its bones clean and consuming its soul before vanishing into the darkness!"
            Stats.add_spirit()
            self._do_victory(monster_death_description=death, soul=False)
        else:
            print("\nThe screaming Bone Spirit flies towards the monster!")
            print(
                "After a moment of violence, the monsters roars and releases an anti-magic shockwave, destroying the Bone Spirit!"
            )
            damage = self._get_bone_spirit_damage()
            print(
                f"It looks worse for wear; it suffered {damage + 1} damage from the spirit's assault."
            )  # +1 from the spirit used
            self.monster.hp -= damage
            util.continue_prompt()

    def _do_minion_damage(self):
        if self.player.minions_attacking == 1:
            minion_name = self.player.minions[0].name
            minion_damage: int = self.player.minions[0].damage

            print(
                f"\nYour {minion_name} lunges at the {self.monster.name} and deals {minion_damage} damage!"
            )

            self.monster.hp -= minion_damage
            Stats.add_damage_dealt_minions(minion_damage)

        elif self.player.minions_attacking > 1:
            damage = 0

            for minion in self.player.minions:
                if minion.attacking:
                    damage += minion.damage

            print(
                f"\nYour minions charge at the {self.monster.name} and deal a collective {damage} damage!"
            )

            self.monster.hp -= damage
            Stats.add_damage_dealt_minions(damage)

    def _monster_dead(self) -> bool:
        return self.monster.hp <= 0

    def _do_victory(self, monster_death_description, soul=True):
        print(f"\nThe {self.monster.name} {monster_death_description}")
        if soul:
            self.player.souls += 1
            print(
                "\nYou hold out your death lantern, absorbing the creature's soul into it."
            )
        self.player.level_up()
        self.player.doom = 0
        self._heal_living_minions()
        util.continue_prompt()
        Stats.add_kill()

        if "Bone Spirit" in monster_death_description:
            self.monster.name = f"skeletal {self.monster.name}"

        if self.monster.name != "Runekeeper":
            self._prompt_for_necromancy(self.monster)

    def _prompt_for_necromancy(self, monster):
        util.clear()

        print(
            f"As the dust settles, you must decide what to do with the corpse of the {monster.name}."
        )

        print(
            f"\n1. Raise it as a new minion.\t(+1 minion)\t(You have {self.player.minion_count} {util.make_plural('minion', self.player.minion_count)}.)"
        )
        print(
            f"2. Butcher it for food.\t\t(+1 ration)\t(You have {self.player.food} {util.make_plural('ration', self.player.food)} and {self.player.hunger}% hunger.)"
        )

        choice = util.prompt_for_number_safely("\nWhat will you do?", 2)
        match choice:
            case 1:
                new_minion = Minion(name=self.monster.name, master=self.player)
                print(
                    f'\n"Come, my minion, rise for your master!" The {new_minion.name} joins your army.'
                )
                self.player.add_minion(new_minion)
                Stats.add_raise()
            case 2:
                print("\nYou carefully prepare the body...")
                self.player.food += 1
                Stats.add_butchery()
            case _:
                raise ValueError("Received an unknown choice for necromancy: {choice}")

        util.continue_prompt()

    def _heal_living_minions(self):
        """Called at the end of battle.
        If any minions are low on health, heal them.
        """

        reanimated = 0

        for minion in self.player.minions:
            if minion.hp == 0:
                reanimated += 1
            minion.hp = minion.max_hp

        if reanimated > 0:
            print(
                f"\nYou reanimate the {reanimated} {util.make_plural('minion', reanimated)} that fell during the battle."
            )

    def _get_player_choice(self) -> str:
        while True:
            try:
                choice = input("What action will you take? ")
                try:
                    choice = int(choice)
                    match choice:
                        case 1:
                            return "ATTACK"
                        case 2:
                            return "CAST_PAIN"
                        case 3:
                            return "CAST_VAMPIRIC_TOUCH"
                        case 4:
                            return "CAST_DEATH_BOLT"
                        case 5:
                            if self.player.souls > 0:
                                if (
                                    self._runekeeper_first_time_bone_spirit
                                    and self.monster.name == "Runekeeper"
                                ):
                                    print(
                                        "\nBone Spirit will not instantly kill the Runekeeper. Are you sure? (You will only be asked once.)"
                                    )
                                    self._runekeeper_first_time_bone_spirit = False
                                    while True:
                                        choice = input("\nChoice (y/n): ")
                                        match choice.lower():
                                            case "y":
                                                return "CAST_BONE_SPIRIT"
                                            case "n":
                                                print()
                                                break
                                            case _:
                                                print("Unknown choice.")
                                else:
                                    return "CAST_BONE_SPIRIT"
                            else:
                                print("\nYou have no souls to cast Bone Spirit with!\n")
                        case 6:
                            if self.player.potions == 0:
                                print("\nYou have no potions to drink!\n")
                            else:
                                return "DRINK_POTION"
                        case 7:
                            if self.player.minions_defending > 0:
                                return "COMMAND_MINION_ATTACK"
                            else:
                                print("\nYou have no defending minions to command!\n")
                        case 8:
                            if self.player.minions_attacking > 0:
                                print("\nReturning COMMAND_MINION_DEFEND")
                                util.continue_prompt()
                                return "COMMAND_MINION_DEFEND"
                            else:
                                print("\nYou have no attacking minions to command!\n")
                        case 9:
                            return "TRY_DODGE"
                        case 0:
                            if self.monster.name == "Runekeeper":
                                print("\nThere is no escape from this battle!\n")
                            else:
                                return "TRY_FLEE"
                        case _:
                            print("\nUnknown command.")
                except ValueError:
                    print("\nUnknown command.")
            except (EOFError, KeyboardInterrupt):
                print("\nUnknown command.")

    def _resolve_player_choice(self, choice: str) -> None:
        """choice is a coded str that indicates what the self.player.chose to do."""

        match choice:
            case "ATTACK":
                self._do_player_attack()
            case "CAST_PAIN":
                self._cast_pain()
            case "CAST_VAMPIRIC_TOUCH":
                self._cast_vampiric_touch()
            case "CAST_DEATH_BOLT":
                self._cast_death_bolt()
            case "CAST_BONE_SPIRIT":
                self._cast_bone_spirit()
            case "DRINK_POTION":
                self._drink_potion()
            case "COMMAND_MINION_ATTACK":
                self._command_minion_attack()
            case "COMMAND_MINION_DEFEND":
                self._command_minion_defend()
            case "TRY_DODGE":
                self._try_dodging()
            case "TRY_FLEE":
                self._try_fleeing()
            case _:
                raise ValueError(f"Tried to resolve an invalid choice: {choice}")

    def _do_player_attack(self) -> None:
        print(
            f"You swing {self.player._get_weapon_descriptor().removesuffix('.')} at the {self.monster.name} and deal {self.player.weapon} damage!"
        )
        self.monster.hp -= self.player.weapon
        Stats.add_damage_dealt_personal(self.player.weapon)

    def _get_pained_damage(self) -> int:
        """The reduced damage a monster will deal as a result of the player casting Pain."""

        monster_damage = self.monster.damage / Variables.SPELL_PAIN_RATIO
        if monster_damage < 1:
            return 0
        else:
            return round(monster_damage)

    def _get_death_bolt_self_damage(self) -> int:
        return self.player.weapon

    def _get_death_bolt_damage(self) -> int:
        return self._get_spell_damage(Variables.SPELL_DEATH_BOLT_RATIO)

    def _cast_death_bolt(self) -> None:
        damage = self._get_death_bolt_damage()

        print(f"You form cursed sigils with your hands, invoking the energy of death!")
        print(
            f"\nA bolt of darkness is cast into {self.monster.name}, blasting it for {damage} damage!"
        )

        self_damage = self._get_death_bolt_self_damage()
        self.player.hp -= self_damage
        print(
            f"Your body shudders from the magical backlash. You take {self_damage} damage, reducing you to {self.player.hp} out of a maximum possible {self.player.max_hp}."
        )

        self.monster.hp -= damage
        Stats.add_damage_dealt_personal(damage)
        Stats.add_damage_taken_personal(self_damage)

    def _get_pain_damage(self) -> int:
        """The damage caused by casting Pain on the monster."""

        if self.player.weapon == 1:
            damage = 0
        else:
            damage = self._get_spell_damage(Variables.SPELL_PAIN_RATIO)
        return damage

    def _cast_pain(self) -> None:
        damage = self._get_pain_damage()

        print(
            f"Tendrils of darkness extend from your fingers and lance into the {self.monster.name}, causing it to writhe in pain for {damage} damage!"
        )

        self.monster.pained = True
        self.monster.hp -= self._get_pain_damage()
        Stats.add_damage_dealt_personal(damage)

    def _get_vampiric_touch_damage(self) -> int:
        """Return the damage that would be inflicted by Vampiric Touch."""
        if self.player.weapon == 1:
            damage = 1
        else:
            damage = self._get_spell_damage(Variables.SPELL_VAMPIRIC_TOUCH_RATIO)
        return damage

    def _cast_vampiric_touch(self) -> None:
        damage = self._get_vampiric_touch_damage()

        print(
            f"You reach out an imperious claw and touch the {self.monster.name}, draining its life force into you for {damage} damage!"
        )
        self.player.hp += damage
        print(
            f"\nYou gain {damage} health, healing to {self.player.hp} out of a maximum possible {self.player.max_hp}."
        )

        self.monster.hp -= damage
        Stats.add_damage_dealt_personal(damage)

    def _get_spell_damage(self, ratio: int) -> int:
        damage = round(self.player.weapon / ratio)
        if damage <= 0:
            damage = 1

        return damage

    def _drink_potion(self):
        print(f"\nYou quickly pop the cork of a potion and chug it down!")

        self.player.potions -= 1
        self.player.hp += Variables.POTION_VALUE
        Stats.add_potion_drink()
        print(
            f"\nYou gain {Variables.POTION_VALUE} health, healing to {self.player.hp} out of a maximum possible {self.player.max_hp}."
        )

    # TODO: Resume action definition from commanding minions to attack and further on.

    def _command_minion_attack(self):
        """Move one minion from defense to offense.

        Assume that we do have a minion per conditions to call this."""

        for minion in self.player.minions:
            if minion.defending:
                minion.attacking = True
                print(f"\nYour {minion.name} charges at the {self.monster.name}!")
                break  # Stop on first minion change

    def _command_minion_defend(self):
        """Move one minion from offense to defense.

        Assume that we do have a minion per conditions to call this."""

        for minion in self.player.minions:
            if minion.attacking:
                minion.defending = True
                print(f"\nYour {minion.name} falls back to defend you!")
                break  # Stop on first minion change

    def _try_dodging(self):
        """Flip on a dodging flag that will give the enemy a chance to miss if damage comes directly to the self.player."""

        print(
            f"\nYou begin to move evasively, trying to predict the attack of the {self.monster.name}!"
        )
        self.player.dodging = True

    def _try_fleeing(self):
        """Try to flee the battle. If Player flees, reset Doom but gain no souls or XP. Low chance to succeed."""

        flee_chance = Variables.FLEE_BASE_CHANCE  # 30
        level_diff = (
            self.player.level - self.monster.level
        )  # Player 3 and self.monster.1 is 2 diff. Player 1 and self.monster.3 is -2 diff.
        flee_chance += (
            level_diff * Variables.FLEE_LEVEL_VARIANCE
        )  # Turn it into a 0-100 number
        # 30 + (2 * 10) = 50% chance to flee self.monster.2 levels below.
        # 30 + (-2 * 10) = 10% chance to flee self.monster.2 levels above.

        print(f"\nYou try to escape the {self.monster.name}...")
        if random.randint(0, 100) < flee_chance:
            self.fled = True
            print("...and manage to get away!")
        else:
            print("...but it keeps up with you!")
        util.continue_prompt()
