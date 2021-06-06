
# Colonizer

Colonizer is a tool developed to better analyze the popular board game, Settler of Catan. It can help (beginner) players make better decisions and understand their common gameplay mistakes such as placing a suboptimal initial settlement, or performing an unfavorable trade using economic theories.

Colonizer keeps track of statistics to help a player make better decisions. Currently, I am only focusing on the initial settlement placements, but eventually I'd hope that Colonizer can become a bot that can  make decisions on its own for the whole duration of the game.

This app is built in Python and uses [tkinter](https://docs.python.org/3/library/tkinter.html) for UI/UX.

## Loading a Specific Game

Games should be loaded using the GameBoards.xlsx file, 1 game per row.

For example, if we are trying to load this game as game 1:

![_](https://github.com/kennethshsu/Colonizer/blob/main/ReadMe%20Support/Setup%20Example.png)


1. In the GameBoards file, column A will be the (sequential) ID of the game.
    * For this game, we will put 1 in column A


2. Columns B:T will be the resource tiles, which should be recorded from left to right, then row by row. Note the resources need to be named as Lumber, Brick, Sheep, Wheat, Rock, and Desert.
    * For this game, it will be recorded as:
      * (row 1) lumber, brick, rock,
      * (row 2) sheep, lumber, sheep, wheat,
      * (row 3) rock, sheep, brick, desert, sheep,
      * (row 4)	wheat, lumber, brick, rock,
      * (row 5) lumber, wheat, wheat


3. Columns U:AC will be the ports, which should be recorded clockwise, starting from the port attached to the first resource tile. Note that a general port (3 for 1 port) should be recorded as a desert port.
    * For this game, it will be recorded as: rock, desert, desert, wheat, lumber, desert, desert, sheep, brick


4. In the game of Catan, the rules actually specified how the dice numbers should be assigned. The dice sequence is [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]. The sequence will be assigned starting from a randomly chosen corner resource tile, and assigned in either direction (clockwise or counter-clockwise).
    * First, look at where the 5 is, it will be one of the 6 corners, unless the first tile is a desert, then look for the 5 next to the desert. Going clockwise, the 5" Starting Location Offset will be either 0, 2, 4, 6, 8, or 10.
      * For this game, the first "5" dice sequent begins at position 0, we will record 0 in column AD
    * Next, look at where the 2 next to the 5, unless it is a desert, then go to the next tile. Which direction does the 2 follow the 5? It will be either clockwise or counter-clockwise.
      * For this game, it's counter-clockwise, so we will record False for ClockwiseDice in column AE.


5. The dice assignment is automatic.
6. Update the gameID in ```ColonizerMain.py``` to the game that we want to study. Or set it as 0 and then latest game will be choosen instead.
6. If everything is setup correctly, you should get the following board.

![_](https://github.com/kennethshsu/Colonizer/blob/main/ReadMe%20Support/Setup%20Loaded%20Board.png)

## Ranking Players' Initial Settlements

## App Usage

## Ways to Win Analysis

## Future Development

## Feedback & Contribution

While this is my first major project using Python, I really would appreciate any feedback that you may have. Feedback both good or bad will help me learn and get better.

Contributions are welcome as well. I love cooperating with people and get new ideas!

## License
[MIT](https://github.com/kennethshsu/Colonizer/blob/main/LICENSE.md)
