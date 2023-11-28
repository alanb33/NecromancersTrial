# THE NECROMANCER'S TRIAL
#### Description:
The Necromancer's Trial is a text adventure resource management dungeon crawler videogame. You take the role of a necromancer who has been thrown into the Dungeon of Despair, and you must use your unique skills to find the Runes of Escape and get out of the dungeon.

One key principle of this game is transparency. I feel that games sometimes don't do the best job at explaining their mechanics, so I tried to give details about the possible actions you can take as well as sharing details of their consequences. I didn't want anyone to get irritated by poorly-explained mechanics, like I have from some videogames in the past.

There were some major design changes as I was writing The Necromancer's Trial. Originally, you could choose from one of three classes: the Barbarian, the Thief, and the Necromancer. The Barbarian would've had more HP and do more damage. The Thief would've been better at dodging attacks, and there was originally a stealth mechanic to avoid fights. The Necromancer behaved the same as they do now. I found that the Necromancer's gameplay was a lot more interesting than the Barbarian's and the Thief's playstyles, so I opted to focus entirely on the Necromancer.

The dungeon was also originally had a map and the ability to manually move between rooms. Rooms would've had exits in cardinal directions, and you would've had to have kept track of where you've been to navigate the dungeon successfully. I found that this entailed a lot of backtracking and confusion about where you had been and where you needed to go, so I opted for a more simple room exploration method instead.

Truthfully, the code is a bit messily-organized, and I would like to review the code again to move what I can to their proper places. Unfortunately, I only just started my software engineering class!

Here are the files and what they do.

	data/adjectives.txt
	data/monsters.txt
	data/rooms_armory.txt
	data/rooms_generic.txt
	data/rooms_kitchen.txt
	data/rooms_workshop.txt

		These .txt files contain a list of words that the game uses to randomly generate rooms and monster names.

	battlemaster.py
	
		This file controls the battle system -- the engagement between the player, their minions, and a single monster.

	dm.py

		This file controls a lot of the game logic, and truthfully has too many responsibilities. The lines between DM and project.py are blurred, but the DM's intent is to be the primary communicator between different objects.

	minion.py

		This file is a small class that holds some information about the player's undead minions. I'm happy about the name property, which pulls the minion names from the monster that was defeated, but prepends 'zombified' or 'skeletal' depending on the context.

	monster.py

		Another small class that holds info about monsters in the dungeon. Truthfully, all monsters are the same. There is a special monster, the final boss, who has some different behavior, but that logic is defined in the BattleMaster.

	player.py

		This is a larger file that could be broken up into two pieces; the player data itself and a minion manager that maintains information about the player's minions.

	project.py

		The main file of the program. This file holds the messiest code -- it and DM.py hold most of the logical responsibilities, but those are slightly more centralized in the DM. If I had to choose a single file for refactoring, it would definitely be this main file.

	room.py

		A small class file that also includes some special logic for searching different room types.

	stats.py

		A fun stats printer that reports on various metrics once you beat the game. How many monsters you killed, how much damage your minions did in total, etc.

	util.py

		A utility file with some common functions used throughout the program.

	variables.py

		A class holding a variety of game variables. I tried to avoid hardcoding numbers as much as possible -- a lot of what the game does refers back to this file for guidance. It made tweaking the hunger rate easy during my playtesting, as well as playing with some other variables.