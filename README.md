
# Colonizer

Colonizer is a tool developed to better analyze the popular board game, Settler of Catan. It can help (beginner) players make better decisions and understand their common gameplay mistakes such as placing a suboptimal initial settlement, or performing an unfavorable trade using economic theories.

Colonizer keeps track of statistics to help a player make better decisions. Currently, I am only focusing on the initial settlement placements, but eventually I'd hope that Colonizer can become a bot that can  make decisions on its own for the whole duration of the game.

This app is built in Python and uses [tkinter](https://docs.python.org/3/library/tkinter.html) for UI/UX.

## Loading a Specific Game

Games should be loaded using the GameBoards.xlsx file, 1 game per row.

For example, if we are trying to load this specific game (that I actually played played on [Colonist](https://colonist.io)) as game 1 :

![.](https://github.com/kennethshsu/Colonizer/blob/main/ReadMe%20Support/Board%20Sample.png)


1. In the GameBoards file, column A will be the (sequential) ID of the games that we can load.
    * For this game, we will put 1 in column A


2. Columns B:T will be the resource tiles, which should be recorded from left to right, then row by row from top to bottom. Note the resources need to be named as Lumber, Brick, Sheep, Wheat, Rock, and Desert.
    * For this game, the resource tiles should be recorded as:
      * (row 1) lumber, brick, rock,
      * (row 2) sheep, lumber, sheep, wheat,
      * (row 3) rock, sheep, brick, desert, sheep,
      * (row 4)	wheat, lumber, brick, rock,
      * (row 5) lumber, wheat, wheat


3. Columns U:AC will be for the ports, which should be recorded clockwise, starting from the port attached to the first resource tile at the upper left corner. Note that general ports (3 for 1 ports) should be recorded as desert ports.
    * For this game, it will be recorded as: rock, desert, desert, wheat, lumber, desert, desert, sheep, brick


4. In the game of Catan, the rules actually specified how the dice numbers should be assigned. The sequence is [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11], and needs to be assigned starting from a randomly chosen cornered resource tile, and assigned in either direction (clockwise or counter-clockwise), from the outer-most ring to the most central resource hex.
    * First, look at where the 5 is, it will be on one of the 6 corner hex tiles, unless the first tile is a desert, then look for a 5 next to the desert. Going clockwise, the "5" Starting Location Offset will be either 0, 2, 4, 6, 8, or 10.
      * For this game, the first 5 dice sequent begins at position 0, we will record 0 in column AD
      * Just for reference:
        * Offset of 2 is currently taken by rock 8
        * Offset of 4 is currently taken by sheep 11
        * Offset of 6 is currently taken by wheat 9
        * Offset of 8 is currently taken by lumber 8
        * Offset of 10 is currently taken by rock 6
    * Next, look at where the 2 is next to the initial 5, unless it is a desert, then go to the next tile. Which direction does the 2 follow the 5? It will be either clockwise or counter-clockwise.
      * For this game, it's counter-clockwise, so we will record False for ClockwiseDice in column AE.


5. Colonizer will check to make sure the board is a valid board (having the correct number of tiles, etc). And the dice number will be automatically assigned based on the initial position and the direction of assignment.
6. Update the gameID in ```ColonizerMain.py``` to the game that we want to study. Or set it as 0 and then latest game will be choosen instead.
  * For this game, it'll be 1.
6. If everything is setup correctly, you should get the following board.

![.](https://github.com/kennethshsu/Colonizer/blob/main/ReadMe%20Support/Loaded%20Board.png)

## Ranking Players' Initial Settlements

We can compare how well each player setup their initial settlements using a few different methods to evaluate their performance.

Let's supposed that the players placed their initial settlements like this:

![.](https://github.com/kennethshsu/Colonizer/blob/main/ReadMe%20Support/Initial%20Settlements%20Placed.png)

Methodologies:
  * **Getting the Most Resources**: Players are ranked by their total resource production ability. Here is a sample calculation for Orange:
    * 10 brick has probability of 0.0833
    * 8 rock has probability of 0.1389
    * 3 sheep has probability of 0.0556
    * 3 wheat has probability of 0.0556
    * 5 lumber has probability of 0.1111
    * 8 lumber has probability of 0.1389
    * Total probability (score) = 0.583

  | Orange's Rank (and Score) | Black's Rank (and Score) | Blue's Rank (and Score) | Red's Rank (and Score) |
  | ------------------------- | ------------------------ | ----------------------- | ---------------------- |
  | **1 (0.583)**                 | 4 (0.500)                | 3 (0.528)               | 2 (0.556)              |

  * **Getting the Most & Diverse Resources (Sharpe Ratio)**: Players are ranked by their total resource production ability, divided by the standard deviation between their resource productions. Here is a sample calculation for Orange:
    * Total lumber production of 0.1111 + 0.1389 = 0.2500
    * Total brick production of 0.0833
    * Total sheep production of 0.0556
    * Total wheat production of 0.0556
    * Total rock production of 0.1389
    * Mean of production = 0.1167
    * Standard deviation of production = 0.0733
    * Sharpe ratio (score) = 0.1167 / 0.0733 = 1.592

  | Orange's Rank (and Score) | Black's Rank (and Score) | Blue's Rank (and Score) | Red's Rank (and Score) |
  | ------------------------- | ------------------------ | ----------------------- | ---------------------- |
  | 2 (1.592)                 | **1 (2.654)**                | 4 (1.440)               | 3 (1.534)              |

  * **Getting the Most Rare Resources by Tiles Available**: Players are ranked by their resource production ability; but resource values are weighted depending on how many resource tiles are available. For example, because there are always 4 lumber tiles available, but only 3 brick tiles, 4 lumbers are worth the same as 3 bricks. Here is a sample calculation for Orange:
    * Because there are 4 lumber tiles, 3 brick tiles, 4 sheep tiles, 4 wheat tiles, and 3 rock ties
      * The average resource value is (4 + 3 + 4 + 4 + 3) / 5 = 3.6
      * The relative lumber value is 3.6/4
      * The relative brick value is 3.6/3 (more valuable than lumber)
      * The relative sheep value is 3.6/4 (just as valuable as lumber)
      * The relative wheat value is 3.6/4
      * The relative rock value is 3.6/3
    * Total lumber production of (0.1111 + 0.1389) * 3.6/4 = 0.2250
    * Total brick production of 0.08333 * 3.6/3 = 0.1000
    * Total sheep production of 0.0556 * 3.6/4 = 0.0500
    * Total wheat production of 0.0556 * 3.6/4 = 0.0500
    * Total rock production of 0.1389 * 3.6/3 = 0.1667
    * Total production score = 0.2550 + 0.1000 + 0.0500 + 0.0500 + 0.1667 = 0.592

    | Orange's Rank (and Score) | Black's Rank (and Score) | Blue's Rank (and Score) | Red's Rank (and Score) |
    | ------------------------- | ------------------------ | ----------------------- | ---------------------- |
    | **1 (0.592)**                 | 4 (0.508)                | 3 (0.542)               | 2 (0.542)              |

  * **Getting the Most Rare Resources by Tiles' Probability**: Players are ranked by their resource production ability; but resource values are weighted depending on how the board is set up randomly. For example, if there are less rock tiles available, like the example game above, then rocks are worth more.

  | Orange's Rank (and Score) | Black's Rank (and Score) | Blue's Rank (and Score) | Red's Rank (and Score) |
  | ------------------------- | ------------------------ | ----------------------- | ---------------------- |
  | 2 (0.548)                 | 3 (0.542)                | 4 (0.475)               | **1 (0.554)**              |

  * **Getting the Most Rarely Produced Resources**: Players are ranked by their resource production ability; but resource values are weighted depending on what resources are occupied by all players. For example, if rocks are rare (like the example game), but still occupied more than another resource (even after taking probability into account), rock's value will be driven down.

  | Orange's Rank (and Score) | Black's Rank (and Score) | Blue's Rank (and Score) | Red's Rank (and Score) |
  | ------------------------- | ------------------------ | ----------------------- | ---------------------- |
  | 3 (0.544)                 | 2 (0.555)                | 4 (0.494)               | **1 (0.574)**              |

## App Usage

## Ways to Win Analysis

## Future Development

## Feedback & Contribution

While this is my first major project using Python, I really would appreciate any feedback that you may have. Feedback both good or bad will help me learn and get better.

Contributions are welcome as well. I love cooperating with people and get new ideas!

## License
[MIT](https://github.com/kennethshsu/Colonizer/blob/main/LICENSE.md)
