# %%
# load the required packages
import numpy as np
import pandas as pd
import tkinter as tk
import sys

# %%
gameBoards = pd.read_excel("./GameBoards.xlsx")

# select which game board to load, gameID is selected above
# picks a custom game here
gameID = 0
# if no game is selected, pick the latest game
gameID = len(gameBoards) if gameID == 0 else gameID
selectedGameBoard = gameBoards[gameBoards["Game"] == gameID]

# checking to make sure the board is a valid board
# (e.g. it has 4 lumbers hexes, 3 bricks, ..., 1 lumber port, 1 brick port, etc)
validBoard = pd.DataFrame(
    {
        "resource": ["lumber", "brick", "sheep", "wheat", "rock", "desert"],
        "hexCount": [4, 3, 4, 4, 3, 1],
        "portCount": [1, 1, 1, 1, 1, 4],
    }
)

selectedGameHexes = selectedGameBoard.T[gameID - 1].iloc[1:20]
selectedGamePorts = selectedGameBoard.T[gameID - 1].iloc[20:29]
gameBoardValid = True

for index, row in validBoard.iterrows():
    hexCount = sum(1 for x in selectedGameHexes if x == row["resource"])
    portCount = sum(1 for x in selectedGamePorts if x == row["resource"])

    # checking resource hexes
    if hexCount != row["hexCount"]:
        print(
            "Error: selected game does not have",
            row["hexCount"],
            row["resource"],
            "hexes (got",
            hexCount,
            "instead)",
        )
        gameBoardValid = False

    # checking resource ports
    if portCount != row["portCount"]:
        print(
            "Error: selected game does not have",
            row["portCount"],
            row["resource"],
            "ports (got",
            portCount,
            "instead)",
        )
        gameBoardValid = False

if not gameBoardValid:
    print("Exiting Colonizer...")
    sys.exit()

# %%
gameWindowWidth = 1600
gameWindowHeight = 900
xBoardCenter = 400
yBoardCenter = 450
radius = 65
gapSize = 7

# declare the the game
colonizer = tk.Tk()
colonizer.canvas = tk.Canvas(width=gameWindowWidth, height=gameWindowHeight)
colonizer.title("Colonizer - Game " + str(gameID))
colonizer.canvas.pack()
colonizer.focus_force()  # forces the window to be at the top and focused

# useful global variables
currentRoll = 0
resolveRobberPending = False
rollNumberObj = 0

currentActivePlayer = 0
currentAction = None


# %%
# debugger
pd.set_option("display.max_rows", None, "display.max_columns", None)

debugMode = False
debugMsg = ["Enable Debug Mode", "Disable Debug Mode"]


def ToggleDebugMode():
    global debugMode

    # toggle the value
    debugMode = not debugMode
    DebugToggle.config(text=debugMsg[debugMode])

    if debugMode:
        # print hex coordinates
        for index, row in hexTiles.iterrows():
            colonizer.canvas.itemconfig(
                hexTiles.at[index, "hexCoordTextObj"],
                text="(" + str(row["xHexOffset"]) + ", " + str(row["yHexOffset"]) + ")",
            )

        # print road number
        for index, row in roadConnections.iterrows():
            colonizer.canvas.itemconfig(
                roadConnections.at[index, "roadTextObj"],
                text=roadConnections.at[index, "roadNum"],
            )
            colonizer.canvas.itemconfig(
                roadConnections.at[index, "roadShapeObj"], fill="#e2e2e2"
            )

        # print building number
        for index, row in buildingLocation.iterrows():
            colonizer.canvas.itemconfig(
                buildingLocation.at[index, "buildingTextObj"],
                text=buildingLocation.at[index, "BuildingNum"],
            )
            colonizer.canvas.itemconfig(
                buildingLocation.at[index, "buildingShapeObj"], fill="#e2e2e2"
            )

    else:
        # not printing coordinates
        for index, row in hexTiles.iterrows():
            colonizer.canvas.itemconfig(hexTiles.at[index, "hexCoordTextObj"], text="")

        # not printing any road info
        for index, row in roadConnections.iterrows():
            colonizer.canvas.itemconfig(
                roadConnections.at[index, "roadTextObj"], text="",
            )
            colonizer.canvas.itemconfig(
                roadConnections.at[index, "roadShapeObj"],
                fill="#FFFFFF"
                if roadConnections.loc[index, "occupiedPlayer"] == 0
                else playerColor[
                    playerStats.loc[
                        roadConnections.loc[index, "occupiedPlayer"], "color"
                    ]
                ],
            )

        # print building location value
        for index, row in buildingLocation.iterrows():
            colonizer.canvas.itemconfig(
                buildingLocation.at[index, "buildingTextObj"],
                text="{0:0.2f}".format(buildingLocation.at[index, "LocValue"] * 10),
            )
            colonizer.canvas.itemconfig(
                buildingLocation.at[index, "buildingShapeObj"],
                fill="#FFFFFF"
                if buildingLocation.loc[index, "OccupiedPlayer"] == 0
                else playerColor[
                    playerStats.loc[
                        buildingLocation.loc[index, "OccupiedPlayer"], "color"
                    ]
                ],
            )


DebugToggle = tk.Button(colonizer, text=debugMsg[0], command=ToggleDebugMode)
DebugToggle.place(x=100, y=20, anchor="c")


# %%
# algorithms to evaluate starting positions
def EvaluatePlayerRank(*args):
    evalMethod = evaluationMethod.get()
    playerRank = pd.DataFrame({"playerID": [0, 1, 2, 3, 4]})

    for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
        playerRank[resourceType + "Prod"] = playerStats[
            (playerStats["playerID"] != 0) & (playerStats["inPlay"])
        ][resourceType + "Prod"]

    playerRank["totalProd"] = playerStats[
        (playerStats["playerID"] != 0) & (playerStats["inPlay"])
    ]["totalProd"]

    # Getting the Most Resources: highest probability
    if evalMethod == evalMethods[0]:
        playerRank["score"] = playerRank["totalProd"]

    # Getting the Most & Diverse Resources (Sharpe Ratio): highest probability & lower
    # variance across resources
    elif evalMethod == evalMethods[1]:
        playerRank["resourceSTD"] = playerRank.loc[
            :, ["lumberProd", "brickProd", "sheepProd", "wheatProd", "rockProd"]
        ].std(
            axis=1, ddof=0
        )  # using population variance
        playerRank["score"] = (playerRank["totalProd"] / 5) / playerRank["resourceSTD"]

    # Getting the Most Rare Resources by Tiles: based on number of tiles available to
    # determine scarcity
    elif evalMethod == evalMethods[2]:
        resourceScarcity = pd.DataFrame(
            {
                "resource": ["lumber", "brick", "sheep", "wheat", "rock"],
                "scarcity": [4.0, 3.0, 4.0, 4.0, 3.0],
            }
        )
        resourceScarcity["scarcity"] = 1 / (
            resourceScarcity["scarcity"] / resourceScarcity["scarcity"].mean()
        )
        resourceScarcity = resourceScarcity.set_index("resource")

        playerRank["score"] = 0
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            playerRank["score"] += (
                playerStats[(playerStats["playerID"] != 0) & (playerStats["inPlay"])][
                    resourceType + "Prod"
                ]
                * resourceScarcity.loc[resourceType, "scarcity"]
            )

    # Getting the Most Rare Resources by Tiles' Probability: based on probability of
    # tiles to determine scarcity
    elif evalMethod == evalMethods[3]:
        resourceScarcity = pd.DataFrame(
            {
                "resource": ["lumber", "brick", "sheep", "wheat", "rock"],
                "scarcity": [0.0, 0.0, 0.0, 0.0, 0.0],
            }
        )
        resourceScarcity = resourceScarcity.set_index("resource")

        for index, row in hexTiles.iterrows():
            if row["hexResource"] != "desert":
                resourceScarcity.loc[row["hexResource"], "scarcity"] += diceRoll.loc[
                    row["diceNumber"], "prob"
                ]

        resourceScarcity["scarcity"] = 1 / (
            resourceScarcity["scarcity"] / resourceScarcity["scarcity"].mean()
        )

        playerRank["score"] = 0
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            playerRank["score"] += (
                playerStats[(playerStats["playerID"] != 0) & (playerStats["inPlay"])][
                    resourceType + "Prod"
                ]
                * resourceScarcity.loc[resourceType, "scarcity"]
            )

    # Getting the Most Rarely Produced Resources: based on probability & scarcity of
    # resources occupied by players
    elif evalMethod == evalMethods[4]:
        resourceScarcity = pd.DataFrame(
            {
                "resource": ["lumber", "brick", "sheep", "wheat", "rock"],
                "scarcity": [0.0, 0.0, 0.0, 0.0, 0.0],
            }
        )
        resourceScarcity = resourceScarcity.set_index("resource")

        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            resourceScarcity.loc[resourceType, "scarcity"] = playerStats.loc[
                0, resourceType + "Prod"
            ]

        resourceScarcity["scarcity"] = 1 / (
            resourceScarcity["scarcity"] / resourceScarcity["scarcity"].mean()
        )

        playerRank["score"] = 0
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            playerRank["score"] += playerStats[
                (playerStats["playerID"] != 0) & (playerStats["inPlay"])
            ][resourceType + "Prod"] * (
                resourceScarcity.loc[resourceType, "scarcity"]
                if not np.isinf(resourceScarcity.loc[resourceType, "scarcity"])
                else 0
            )

    # Print rankings
    playerRank["rank"] = playerRank["score"].rank(ascending=False)
    # print(playerRank)

    for playerID in [1, 2, 3, 4]:
        if playerStats.loc[playerID, "inPlay"]:
            colonizer.canvas.itemconfig(
                playerStats.loc[playerID, "initPositionScoreObj"],
                text="Rank: "
                + str(int(playerRank.loc[playerID, "rank"]))
                + " ("
                + "{0:0.3f}".format(playerRank.loc[playerID, "score"])
                + ")",
            )


evalMethods = [
    "Getting the Most Resources",
    "Getting the Most & Diverse Resources (Sharpe Ratio)",
    "Getting the Most Rare Resources by Tiles Available",
    "Getting the Most Rare Resources by Tiles' Probability",
    "Getting the Most Rarely Produced Resources",
]

evaluationMethod = tk.StringVar()
evaluationMethod.set("Rank Players...")
evaluationMethodDropdown = tk.OptionMenu(
    colonizer, evaluationMethod, *evalMethods, command=EvaluatePlayerRank
)
evaluationMethodDropdown.config(width=40)
evaluationMethodDropdown.place(x=400, y=22.5, anchor="c")


# %%
# some useful dictionaries
# resrouce color
resourceColor = {
    "lumber": "#11933B",
    "brick": "#DC5539",
    "sheep": "#9CBD29",
    "wheat": "#F2BA24",
    "rock": "#9FA5A1",
    "desert": "#EBE5B5",
}

playerColor = {
    "red": "#FE5555",
    "blue": "#6D83FD",
    "orange": "#FE9A55",
    "green": "#55FE5D",
    "black": "#8A8A8A",
}

# dice probability
diceRoll = pd.DataFrame(
    {
        "roll": [2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,],
        "prob": [
            1 / 36,
            2 / 36,
            3 / 36,
            4 / 36,
            5 / 36,
            6 / 36,
            5 / 36,
            4 / 36,
            3 / 36,
            2 / 36,
            1 / 36,
        ],
        "rolledThisGame": 0,
        "rollStats1TextObj": 0,
        "rollStats2TextObj": 0,
    }
)
diceRoll = diceRoll.set_index("roll")

# keep track of players
playerStats = pd.DataFrame(
    {
        "playerID": [0, 1, 2, 3, 4],
        "color": ["white", "white", "white", "white", "white"],
        "inPlay": [True, False, False, False, False],
        "knownVictoryPoints": [0, 0, 0, 0, 0],
        "currentRoadLength": [0, 0, 0, 0, 0],
        "hasLongestRoad": [False, False, False, False, False],
        "currentArmySize": [0, 0, 0, 0, 0],
        "hasLargestArmy": [False, False, False, False, False],
        "road": [0, 15, 15, 15, 15],
        "settlement": [0, 5, 5, 5, 5],
        "city": [0, 4, 4, 4, 4],
        "lumber": [19, 0, 0, 0, 0],
        "brick": [19, 0, 0, 0, 0],
        "sheep": [19, 0, 0, 0, 0],
        "wheat": [19, 0, 0, 0, 0],
        "rock": [19, 0, 0, 0, 0],
        "resourceTotalObj": [0, 0, 0, 0, 0],
        "lumberProd": [0, 0, 0, 0, 0],
        "brickProd": [0, 0, 0, 0, 0],
        "sheepProd": [0, 0, 0, 0, 0],
        "wheatProd": [0, 0, 0, 0, 0],
        "rockProd": [0, 0, 0, 0, 0],
        "totalProd": [0, 0, 0, 0, 0],
        "acquiredKnight": [14, 0, 0, 0, 0],
        "acquiredVictoryPoint": [5, 0, 0, 0, 0],
        "acquiredMonopoly": [2, 0, 0, 0, 0],
        "acquiredRoadBuilding": [2, 0, 0, 0, 0],
        "acquiredYearOfPlenty": [2, 0, 0, 0, 0],
        "acquiredDevCardTotal": [25, 0, 0, 0, 0],
        "acquiredDevCardTotalObj": [0, 0, 0, 0, 0],
        "playedKnight": [0, 0, 0, 0, 0],
        "playedVictoryPoint": [0, 0, 0, 0, 0],
        "playedMonopoly": [0, 0, 0, 0, 0],
        "playedRoadBuilding": [0, 0, 0, 0, 0],
        "playedYearOfPlenty": [0, 0, 0, 0, 0],
        "lumberObj": [0, 0, 0, 0, 0],
        "brickObj": [0, 0, 0, 0, 0],
        "sheepObj": [0, 0, 0, 0, 0],
        "wheatObj": [0, 0, 0, 0, 0],
        "rockObj": [0, 0, 0, 0, 0],
        "lumberProdObj": [0, 0, 0, 0, 0],
        "brickProdObj": [0, 0, 0, 0, 0],
        "sheepProdObj": [0, 0, 0, 0, 0],
        "wheatProdObj": [0, 0, 0, 0, 0],
        "rockProdObj": [0, 0, 0, 0, 0],
        "resourceTotalProdObj": [0, 0, 0, 0, 0],
        "initPositionScoreObj": [0, 0, 0, 0, 0],
    }
)


# %%
# load the board, hexes will get a default diceNumber of 0,
# it will be assigned later

# load the hexes
hexTiles = pd.DataFrame(
    [
        # Row 1
        [selectedGameBoard.iloc[0, 1], -2, -4, 3, 0, 0],
        [selectedGameBoard.iloc[0, 2], 0, -4, 3, 0, 0],
        [selectedGameBoard.iloc[0, 3], 2, -4, 3, 0, 0],
        # Row 2
        [selectedGameBoard.iloc[0, 4], -3, -2, 3, 0, 0],
        [selectedGameBoard.iloc[0, 5], -1, -2, 2, 0, 0],
        [selectedGameBoard.iloc[0, 6], 1, -2, 2, 0, 0],
        [selectedGameBoard.iloc[0, 7], 3, -2, 3, 0, 0],
        # Row 3
        [selectedGameBoard.iloc[0, 8], -4, 0, 3, 0, 0],
        [selectedGameBoard.iloc[0, 9], -2, 0, 2, 0, 0],
        [selectedGameBoard.iloc[0, 10], 0, 0, 1, 0, 0],
        [selectedGameBoard.iloc[0, 11], 2, 0, 2, 0, 0],
        [selectedGameBoard.iloc[0, 12], 4, 0, 3, 0, 0],
        # Row 4
        [selectedGameBoard.iloc[0, 13], -3, 2, 3, 0, 0],
        [selectedGameBoard.iloc[0, 14], -1, 2, 2, 0, 0],
        [selectedGameBoard.iloc[0, 15], 1, 2, 2, 0, 0],
        [selectedGameBoard.iloc[0, 16], 3, 2, 3, 0, 0],
        # Row 5
        [selectedGameBoard.iloc[0, 17], -2, 4, 3, 0, 0],
        [selectedGameBoard.iloc[0, 18], 0, 4, 3, 0, 0],
        [selectedGameBoard.iloc[0, 19], 2, 4, 3, 0, 0],
    ],
    columns=[
        "hexResource",
        "xHexOffset",
        "yHexOffset",
        "ring",
        "diceNumber",
        "hexCoordTextObj",
    ],
)

# load the ports
portTiles = pd.DataFrame(
    [
        [selectedGameBoard.iloc[0, 20], -2, -4, "NW"],
        [selectedGameBoard.iloc[0, 21], 0, -4, "NE"],
        [selectedGameBoard.iloc[0, 22], 3, -2, "NE"],
        [selectedGameBoard.iloc[0, 23], 4, 0, "E"],
        [selectedGameBoard.iloc[0, 24], 3, 2, "SE"],
        [selectedGameBoard.iloc[0, 25], 0, 4, "SE"],
        [selectedGameBoard.iloc[0, 26], -2, 4, "SW"],
        [selectedGameBoard.iloc[0, 27], -3, 2, "W"],
        [selectedGameBoard.iloc[0, 28], -3, -2, "W"],
    ],
    columns=["portType", "xHexOffset", "yHexOffset", "portDirection"],
)


# %%
# assigning dice numbers to the hexes
diceSetupHexOffset = selectedGameBoard.iloc[0, 29]
diceSetupClockwise = selectedGameBoard.iloc[0, 30]

# the order of hexes on the outer ring, followed by the first hex
diceOrderRing1 = pd.DataFrame(
    [
        [-2, -4],
        [0, -4],
        [2, -4],
        [3, -2],
        [4, 0],
        [3, 2],
        [2, 4],
        [0, 4],
        [-2, 4],
        [-3, 2],
        [-4, 0],
        [-3, -2],
    ]
)
diceOrderRing1 = pd.DataFrame.append(
    diceOrderRing1.iloc[diceSetupHexOffset:12],
    diceOrderRing1.iloc[0:diceSetupHexOffset],
)

# the order of hexes on the middle ring, followed by the first hex
diceOrderRing2 = pd.DataFrame([[-1, -2], [1, -2], [2, 0], [1, 2], [-1, 2], [-2, 0]])
diceOrderRing2 = pd.DataFrame.append(
    diceOrderRing2.iloc[int(diceSetupHexOffset / 2) : 6],
    diceOrderRing2.iloc[0 : int(diceSetupHexOffset / 2)],
)

diceOrderRing3 = pd.DataFrame([[0, 0]])

# setting up the order of hexes to get assigned dice numbers
if diceSetupClockwise:
    diceAssignmentOrder = diceOrderRing1
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing2)
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing3)

else:
    diceAssignmentOrder = diceOrderRing1.iloc[0:1].append(
        diceOrderRing1.iloc[1:18].iloc[::-1]
    )
    diceAssignmentOrder = diceAssignmentOrder.append(
        diceOrderRing2.iloc[0:1].append(diceOrderRing2.iloc[1:18].iloc[::-1])
    )
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing3)


diceAssignmentOrder.columns = ["xHexOffset", "yHexOffset"]

diceSetupOrder = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
diceCounter = 0

for index, row in diceAssignmentOrder.iterrows():
    # non-desert tiles
    if (
        hexTiles.loc[
            (hexTiles["xHexOffset"] == row["xHexOffset"])
            & (hexTiles["yHexOffset"] == row["yHexOffset"]),
            "hexResource",
        ].all()
        != "desert"
    ):
        hexTiles.loc[
            (hexTiles["xHexOffset"] == row["xHexOffset"])
            & (hexTiles["yHexOffset"] == row["yHexOffset"]),
            "diceNumber",
        ] = diceSetupOrder[diceCounter]
        diceCounter += 1

        hexTiles.loc[
            (hexTiles["xHexOffset"] == row["xHexOffset"])
            & (hexTiles["yHexOffset"] == row["yHexOffset"]),
            "robberOccupied",
        ] = False

    else:
        hexTiles.loc[
            (hexTiles["xHexOffset"] == row["xHexOffset"])
            & (hexTiles["yHexOffset"] == row["yHexOffset"]),
            "diceNumber",
        ] = 7

        hexTiles.loc[
            (hexTiles["xHexOffset"] == row["xHexOffset"])
            & (hexTiles["yHexOffset"] == row["yHexOffset"]),
            "robberOccupied",
        ] = True

# %%
# hex coordinates by ring
HexOrder = pd.DataFrame(
    [
        # Inner ring, 1 hex
        [1, 0, 0],
        # Center ring, 6 hexes
        [2, 1, -2],
        [2, 2, 0],
        [2, 1, 2],
        [2, -1, 2],
        [2, -2, 0],
        [2, -1, -2],
        # Outer ring, 12 hexes
        [3, 0, -4],
        [3, 2, -4],
        [3, 3, -2],
        [3, 4, 0],
        [3, 3, 2],
        [3, 2, 4],
        [3, 0, 4],
        [3, -2, 4],
        [3, -3, 2],
        [3, -4, 0],
        [3, -3, -2],
        [3, -2, -4],
        # Helper ring, 18 hexes
        [4, 1, -6],
        [4, 3, -6],
        [4, 4, -4],
        [4, 5, -2],
        [4, 6, 0],
        [4, 5, 2],
        [4, 4, 4],
        [4, 3, 6],
        [4, 1, 6],
        [4, -1, 6],
        [4, -3, 6],
        [4, -4, 4],
        [4, -5, 2],
        [4, -6, 0],
        [4, -5, -2],
        [4, -4, -4],
        [4, -3, -6],
        [4, -1, -6],
    ],
    columns=["Ring", "xHexOffset", "yHexOffset"],
)

# %%
# init empty settlement/city spaces
# the inner ring has 6 buildable locations, center ring has 18, outer ring has 30
buildingLocationArray = []
buildingNumber = 1
ringSize = [
    6,
    18,
    30,
]

for ring in range(3):
    for buildingInRing in range(ringSize[ring]):
        buildingLocationArray.append([buildingNumber, ring + 1, buildingInRing + 1])
        buildingNumber += 1

buildingLocation = pd.DataFrame(
    buildingLocationArray, columns=["BuildingNum", "Ring", "RingBuildingNum"]
)

buildingLocation["OccupiedPlayer"] = int(0)
buildingLocation["isCity"] = False
buildingLocation["buildingShapeObj"] = int(0)
buildingLocation["buildingTextObj"] = int(0)
buildingLocation["neighbor1"] = int(0)
buildingLocation["neighbor2"] = int(0)
buildingLocation["neighbor3"] = int(0)


for index, row in buildingLocation.iterrows():

    if row["Ring"] == 1:
        buildingLocation.at[index, "Hex1_X"] = HexOrder.iloc[0][1]
        buildingLocation.at[index, "Hex1_Y"] = HexOrder.iloc[0][2]
        buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 2].iloc[
            (row["RingBuildingNum"] - 1) % 6 - 1
        ]["xHexOffset"]
        buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 2].iloc[
            (row["RingBuildingNum"] - 1) % 6 - 1
        ]["yHexOffset"]
        buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 2].iloc[
            (row["RingBuildingNum"]) % 6 - 1
        ]["xHexOffset"]
        buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 2].iloc[
            (row["RingBuildingNum"]) % 6 - 1
        ]["yHexOffset"]

        buildingLocation.at[index, "neighbor1"] = (index + 1) % 6 + 1
        buildingLocation.at[index, "neighbor2"] = (index + 5) % 6 + 1
        buildingLocation.at[index, "neighbor3"] = (index + 1) * 3 + 4

    elif row["Ring"] == 2:
        buildingLocation.at[index, "neighbor1"] = index + 2 if index != 23 else 7
        buildingLocation.at[index, "neighbor2"] = index if index != 6 else 24

        # these buildings are adjacent to two hexes on ring 2
        if row["RingBuildingNum"] % 3 == 1:
            buildingLocation.at[index, "Hex1_X"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3) - 1) % 6
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex1_Y"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3) - 1) % 6
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3)) % 6
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3)) % 6
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round(row["RingBuildingNum"] / 3)) * 2
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round(row["RingBuildingNum"] / 3)) * 2
            ]["yHexOffset"]

            buildingLocation.at[index, "neighbor3"] = (index - 3) / 3

        # these buildings are adjacent to two hexes on ring 3
        else:
            buildingLocation.at[index, "Hex1_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] + 1) / 3 * 2) - 2) % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex1_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] + 1) / 3 * 2) - 2) % 12
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3) - 1) % 6
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 2].iloc[
                (round(row["RingBuildingNum"] / 3) - 1) % 6
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] + 1) / 3 * 2) - 1) % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] + 1) / 3 * 2) - 1) % 12
            ]["yHexOffset"]

            if row["RingBuildingNum"] % 3 == 2:
                buildingLocation.at[index, "neighbor3"] = (
                    row["BuildingNum"] - 2
                ) / 3 * 5 + 16
            else:
                buildingLocation.at[index, "neighbor3"] = (
                    row["BuildingNum"] - 3
                ) / 3 * 5 + 19

    elif row["Ring"] == 3:
        buildingLocation.at[index, "neighbor1"] = index + 2 if index != 53 else 25
        buildingLocation.at[index, "neighbor2"] = index if index != 24 else 54

        # these buildings are adjacent to one hex on ring 3 (i.e. outer coast)
        if row["RingBuildingNum"] % 5 != 2 & row["RingBuildingNum"] % 5 != 5:
            buildingLocation.at[index, "Hex1_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 2))
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex1_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 2))
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 3 - 1) % 18)
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 3 - 1) % 18)
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 3) % 18)
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                (round((row["RingBuildingNum"] - 1) / 5 * 3) % 18)
            ]["yHexOffset"]

        # these buildings are adjacent to two hexes on ring 3 (i.e. inner coast)
        elif row["RingBuildingNum"] % 5 == 2:
            buildingLocation.at[index, "Hex1_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2)
                % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex1_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2)
                % 12
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2 + 1)
                % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2 + 1)
                % 12
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                round((row["RingBuildingNum"] - 2) / 5 * 3) % 18
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                round((row["RingBuildingNum"] - 2) / 5 * 3) % 18
            ]["yHexOffset"]

            buildingLocation.at[index, "neighbor3"] = (
                row["BuildingNum"] - 1
            ) / 5 * 3 - 7

        elif row["RingBuildingNum"] % 5 == 0:
            buildingLocation.at[index, "Hex1_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2 - 1)
                % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex1_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2 - 1)
                % 12
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex2_X"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2)
                % 12
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex2_Y"] = HexOrder[HexOrder["Ring"] == 3].iloc[
                round((row["RingBuildingNum"] - row["RingBuildingNum"] % 5) / 5 * 2)
                % 12
            ]["yHexOffset"]
            buildingLocation.at[index, "Hex3_X"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                round(row["RingBuildingNum"] / 5 * 3 - 1) % 18
            ]["xHexOffset"]
            buildingLocation.at[index, "Hex3_Y"] = HexOrder[HexOrder["Ring"] == 4].iloc[
                round(row["RingBuildingNum"] / 5 * 3 - 1) % 18
            ]["yHexOffset"]

            buildingLocation.at[index, "neighbor3"] = (
                row["BuildingNum"] - 4
            ) / 5 * 3 - 6

# calculate the value of each building location
resourceEconValue = {"lumber": 0, "brick": 0, "sheep": 0, "wheat": 0, "rock": 0}

# calcuate the scarcity of each resource
for index, row in hexTiles.iterrows():
    if row["hexResource"] != "desert":
        resourceEconValue[row["hexResource"]] += diceRoll.loc[row["diceNumber"], "prob"]

for index, row in buildingLocation.iterrows():
    buildingLocValue = 0

    for hexes in [1, 2, 3]:
        currentTile = hexTiles[
            (hexTiles["xHexOffset"] == row["Hex" + str(hexes) + "_X"])
            & (hexTiles["yHexOffset"] == row["Hex" + str(hexes) + "_Y"])
        ]

        if not currentTile.empty:
            currentTile = currentTile.iloc[0]  # convert from dataframe to an array

        if currentTile.empty:
            buildingLocValue += 0
        elif currentTile["hexResource"] == "desert":
            buildingLocValue += 0
        else:
            currentTileProb = diceRoll.loc[currentTile["diceNumber"], "prob"]
            buildingLocValue += (
                1 / resourceEconValue[currentTile["hexResource"]] * currentTileProb
            )

    buildingLocation.at[index, "LocValue"] = buildingLocValue

# prepare unique roads
roadConnections = pd.DataFrame(columns=["from", "to"])
roadConnections = roadConnections.append(
    buildingLocation[["BuildingNum", "neighbor1"]].rename(
        columns={"BuildingNum": "from", "neighbor1": "to"}
    )
)
roadConnections = roadConnections.append(
    buildingLocation[["BuildingNum", "neighbor2"]].rename(
        columns={"BuildingNum": "from", "neighbor2": "to"}
    )
)
roadConnections = roadConnections.append(
    buildingLocation[["BuildingNum", "neighbor3"]].rename(
        columns={"BuildingNum": "from", "neighbor3": "to"}
    )
)
# drop rows with only 2 neighbors
roadConnections = roadConnections[roadConnections["to"] != 0]
roadConnections.reset_index(drop=True, inplace=True)

# re-arrange the order of road direction:
# always go from smaller location ID to larger location ID
for index, row in roadConnections.iterrows():
    if row["from"] > row["to"]:
        holdingValue = row["from"]
        roadConnections.at[index, "from"] = row["to"]
        roadConnections.at[index, "to"] = holdingValue

# drops the same roads
roadConnections = roadConnections.drop_duplicates(subset=["from", "to"])
roadConnections.reset_index(drop=True, inplace=True)
roadConnections["roadNum"] = roadConnections.index + 1
roadConnections = roadConnections[["roadNum", "from", "to"]]
roadConnections.loc[:, "occupiedPlayer"] = int(0)
roadConnections.loc[:, "roadShapeObj"] = int(0)
roadConnections.loc[:, "roadTextObj"] = int(0)


# %%
# setting up the board
# setting up buildings
def SetupBoard():
    def HexClicked(hexIndex):
        global resolveRobberPending

        if resolveRobberPending:
            # remove the current robber
            currentRobberDF = hexTiles.loc[
                hexTiles.loc[:, "robberOccupied"],
            ]
            for index, row in currentRobberDF.iterrows():
                colonizer.canvas.itemconfig(
                    row["robberShapeObj"], fill="",
                )
            hexTiles.loc[hexTiles.loc[:, "robberOccupied"], "robberOccupied"] = False

            # moving the robber to new location
            hexTiles.loc[hexIndex, "robberOccupied"] = True
            colonizer.canvas.itemconfig(
                hexTiles.loc[hexIndex, "robberShapeObj"], fill="#464646",
            )

            resolveRobberPending = False
            # print(hexTiles)
            # need to implement stealing here

    def LoadHex(hexResource, xHexOffset, yHexOffset, diceNumber, index):
        # calculate the center of each hex tile
        xHexCenter = (
            xBoardCenter + np.sqrt(3) / 2 * radius * xHexOffset + gapSize * xHexOffset
        )
        yHexCenter = yBoardCenter + 3 / 4 * radius * yHexOffset + gapSize * yHexOffset

        # coordinates of the 6 points of the hex
        points = [
            xHexCenter + np.sqrt(3) / 2 * radius,
            yHexCenter - radius / 2,
            xHexCenter + 0,
            yHexCenter - radius,
            xHexCenter - np.sqrt(3) / 2 * radius,
            yHexCenter - radius / 2,
            xHexCenter - np.sqrt(3) / 2 * radius,
            yHexCenter + radius / 2,
            xHexCenter + 0,
            yHexCenter + radius,
            xHexCenter + np.sqrt(3) / 2 * radius,
            yHexCenter + radius / 2,
        ]
        hexTiles.at[index, "hexShapeObj"] = colonizer.canvas.create_polygon(
            points,
            outline="#000000",
            fill=resourceColor[hexResource],
            width=2,
            tags="Hex" + str(index),
        )

        # this is the dice roll number
        hexTiles.at[index, "diceTextObj"] = colonizer.canvas.create_text(
            xHexCenter,
            yHexCenter,
            text=str(diceNumber) if diceNumber != 7 else "",
            font=("Helvetica", 32),
            fill="#000000",
            tags="Hex" + str(index),
        )

        # this is the hex location coordinates
        hexTiles.at[index, "hexCoordTextObj"] = colonizer.canvas.create_text(
            xHexCenter,
            yHexCenter + radius / 3.5,
            text="",
            font=("Helvetica", 10),
            tags="Hex" + str(index),
        )

        # this is the robber circle
        hexTiles.at[index, "robberShapeObj"] = colonizer.canvas.create_oval(
            xHexCenter - radius / 7,
            yHexCenter - radius / 7,
            xHexCenter - radius / 1.5,
            yHexCenter - radius / 1.5,
            fill="#464646" if diceNumber == 7 else "",
            outline="",
            tags="Hex" + str(index),
        )

        colonizer.canvas.tag_bind(
            "Hex" + str(index), "<Button-1>", lambda event: HexClicked(index),
        )

    # setting up hex by hex, row by row from upper left tile
    for index, row in hexTiles.iterrows():
        LoadHex(
            row["hexResource"],
            row["xHexOffset"],
            row["yHexOffset"],
            row["diceNumber"],
            index,
        )

    def LoadPort(portType, xHexOffset, yHexOffset, portDirection):
        # calculate the center of each hex tile
        xHexCenter = (
            xBoardCenter + np.sqrt(3) / 2 * radius * xHexOffset + gapSize * xHexOffset
        )
        yHexCenter = yBoardCenter + 3 / 4 * radius * yHexOffset + gapSize * yHexOffset

        if portDirection == "E":
            points = [
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize * 2,
                yHexCenter - radius / 2,
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize * 2,
                yHexCenter + radius / 2,
                xHexCenter
                + np.sqrt(3) / 2 * radius
                + np.sqrt(3) / 2 * radius
                + gapSize * 2,
                yHexCenter + 0,
            ]
        elif portDirection == "SE":
            points = [
                xHexCenter + 0 + gapSize,
                yHexCenter + radius + np.sqrt(3) * gapSize,
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize,
                yHexCenter + radius / 2 + np.sqrt(3) * gapSize,
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize,
                yHexCenter + radius / 2 + radius + np.sqrt(3) * gapSize,
            ]
        elif portDirection == "SW":
            points = [
                xHexCenter - 0 - gapSize,
                yHexCenter + radius + np.sqrt(3) * gapSize,
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize,
                yHexCenter + radius / 2 + np.sqrt(3) * gapSize,
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize,
                yHexCenter + radius / 2 + radius + np.sqrt(3) * gapSize,
            ]
        elif portDirection == "W":
            points = [
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize * 2,
                yHexCenter - radius / 2,
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize * 2,
                yHexCenter + radius / 2,
                xHexCenter
                - np.sqrt(3) / 2 * radius
                - np.sqrt(3) / 2 * radius
                - gapSize * 2,
                yHexCenter + 0,
            ]
        elif portDirection == "NW":
            points = [
                xHexCenter - 0 - gapSize,
                yHexCenter - radius - np.sqrt(3) * gapSize,
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize,
                yHexCenter - radius / 2 - np.sqrt(3) * gapSize,
                xHexCenter - np.sqrt(3) / 2 * radius - gapSize,
                yHexCenter - radius / 2 - radius - np.sqrt(3) * gapSize,
            ]
        elif portDirection == "NE":
            points = [
                xHexCenter + 0 + gapSize,
                yHexCenter - radius - np.sqrt(3) * gapSize,
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize,
                yHexCenter - radius / 2 - np.sqrt(3) * gapSize,
                xHexCenter + np.sqrt(3) / 2 * radius + gapSize,
                yHexCenter - radius / 2 - radius - np.sqrt(3) * gapSize,
            ]
        colonizer.canvas.create_polygon(
            points, outline="#000000", fill=resourceColor[portType], width=2
        )

    # setting up ports
    for index, row in portTiles.iterrows():
        LoadPort(
            row["portType"], row["xHexOffset"], row["yHexOffset"], row["portDirection"],
        )

    def DiceRolled(diceNumber):
        # resolve robber
        if diceNumber == 7:
            global resolveRobberPending
            resolveRobberPending = True

        # distribute resources
        else:
            indexForRoll = hexTiles["diceNumber"] == diceNumber
            indexForNonRobber = hexTiles["robberOccupied"] == False
            resourcesRolledDF = hexTiles[indexForRoll & indexForNonRobber]

            for index, row in resourcesRolledDF.iterrows():
                xHexOffsetTarget = row["xHexOffset"]
                yHexOffsetTarget = row["yHexOffset"]
                currentHexResource = row["hexResource"]

                for hexes in [1, 2, 3]:
                    nearbyBuildings = buildingLocation[
                        (
                            buildingLocation["Hex" + str(hexes) + "_X"]
                            == xHexOffsetTarget
                        )
                        & (
                            buildingLocation["Hex" + str(hexes) + "_Y"]
                            == yHexOffsetTarget
                        )
                    ]
                    nearbyPlayers = nearbyBuildings[
                        nearbyBuildings["OccupiedPlayer"] != 0
                    ]

                    for index, row in nearbyPlayers.iterrows():
                        ResourceIncrement(row["OccupiedPlayer"], currentHexResource)
                        if row["isCity"]:
                            ResourceIncrement(row["OccupiedPlayer"], currentHexResource)

        # update dice tracker
        diceRoll.loc[diceNumber, "rolledThisGame"] += 1
        totalRollsThisGame = diceRoll["rolledThisGame"].sum()
        # update total roll number
        colonizer.canvas.itemconfig(
            rollNumberObj, text="Roll: " + str(totalRollsThisGame),
        )

        # update each dice roll's statistics
        for number in range(2, 13):
            actualRolls = diceRoll.loc[number, "rolledThisGame"]
            actualRollsPct = (
                diceRoll.loc[number, "rolledThisGame"] / totalRollsThisGame * 100
            )
            expectedRolls = diceRoll.loc[number, "prob"] * totalRollsThisGame
            expectedRollsPct = diceRoll.loc[number, "prob"] * 100

            if actualRollsPct > expectedRollsPct:
                color = "#A52A2A"  # red
            elif actualRollsPct < expectedRollsPct:
                color = "#008000"  # green
            else:
                color = "#000000"  # black

            colonizer.canvas.itemconfig(
                diceRoll.loc[number, "rollStats1TextObj"],
                text="("
                + "{0:0.1f}".format(expectedRolls)
                + " - "
                + "{0:0.1f}".format(expectedRollsPct)
                + "%)",
                # fill = color,
            )
            colonizer.canvas.itemconfig(
                diceRoll.loc[number, "rollStats2TextObj"],
                text=str(actualRolls) + " - " "{0:0.1f}".format(actualRollsPct) + "%",
                fill=color,
            )

    def SetupDiceRoll(diceNumber):
        # build bank & players' borders
        diceXCenter = xBoardCenter + (radius + gapSize) * 6 + gapSize * 2
        diceYCenter = gameWindowHeight / 2 + (gameWindowHeight / 13 + gapSize) * (
            diceNumber - 7
        )

        colonizer.canvas.create_polygon(
            [
                diceXCenter - radius + gapSize * 3,
                diceYCenter + radius / 2,
                diceXCenter + radius - gapSize * 3,
                diceYCenter + radius / 2,
                diceXCenter + radius - gapSize * 3,
                diceYCenter - radius / 2,
                diceXCenter - radius + gapSize * 3,
                diceYCenter - radius / 2,
            ],
            outline="#000000",
            fill="#FFFFFF",
            width=2,
            tags="diceRoll" + str(diceNumber),
        )
        colonizer.canvas.create_text(
            diceXCenter,
            diceYCenter - gapSize,
            text=diceNumber,
            font=("Helvetica", 24),
            tags="diceRoll" + str(diceNumber),
        )
        diceRoll.loc[diceNumber, "rollStats1TextObj"] = colonizer.canvas.create_text(
            diceXCenter,
            diceYCenter + gapSize * 1.5,
            text="(0 - "
            + "{0:0.1f}".format(diceRoll.loc[diceNumber, "prob"] * 100)
            + "%)",
            font=("Helvetica", 8),
            tags="diceRoll" + str(diceNumber),
            anchor="c",
        )
        diceRoll.loc[diceNumber, "rollStats2TextObj"] = colonizer.canvas.create_text(
            diceXCenter,
            diceYCenter + gapSize * 3,
            text="0 - 0.0%",
            font=("Helvetica", 10),
            tags="diceRoll" + str(diceNumber),
            anchor="c",
        )
        colonizer.canvas.tag_bind(
            "diceRoll" + str(diceNumber),
            "<Button-1>",
            lambda event: DiceRolled(diceNumber),
        )

    # setting up dice rolls
    hexTiles["hexShapeObj"] = hexTiles["hexShapeObj"].astype(int)
    hexTiles["diceTextObj"] = hexTiles["diceTextObj"].astype(int)
    hexTiles["robberShapeObj"] = hexTiles["robberShapeObj"].astype(int)
    for diceNumber in range(2, 13):
        SetupDiceRoll(diceNumber)

    global rollNumberObj
    rollNumberObj = colonizer.canvas.create_text(
        xBoardCenter + (radius + gapSize) * 6 + gapSize * 2,
        gameWindowHeight / 2 - (gameWindowHeight / 13 + gapSize) * (5.7),
        text="Roll: -",
        font=("Helvetica", 20),
        anchor="c",
    )

    def SetupRoad(roadNumber, fromBuildingNum, toBuildingNum):
        # prepare the attributes for the "from" building
        fromBuilding = buildingLocation.iloc[fromBuildingNum - 1]
        fromXOffset = (
            fromBuilding["Hex1_X"] + fromBuilding["Hex2_X"] + fromBuilding["Hex3_X"]
        ) / 3
        fromYOffset = (
            fromBuilding["Hex1_Y"] + fromBuilding["Hex2_Y"] + fromBuilding["Hex3_Y"]
        ) / 3
        fromXCenter = (
            xBoardCenter + np.sqrt(3) / 2 * radius * fromXOffset + gapSize * fromXOffset
        )
        fromYCenter = (
            yBoardCenter + 3 / 4 * radius * fromYOffset + gapSize * fromYOffset
        )

        # prepare the attributes for the "to" building
        toBuilding = buildingLocation.iloc[toBuildingNum - 1]
        toXOffset = (
            toBuilding["Hex1_X"] + toBuilding["Hex2_X"] + toBuilding["Hex3_X"]
        ) / 3
        toYOffset = (
            toBuilding["Hex1_Y"] + toBuilding["Hex2_Y"] + toBuilding["Hex3_Y"]
        ) / 3
        toXCenter = (
            xBoardCenter + np.sqrt(3) / 2 * radius * toXOffset + gapSize * toXOffset
        )
        toYCenter = yBoardCenter + 3 / 4 * radius * toYOffset + gapSize * toYOffset

        roadConnections.at[
            roadNumber - 1, "roadShapeObj"
        ] = colonizer.canvas.create_line(
            fromXCenter,
            fromYCenter,
            toXCenter,
            toYCenter,
            width=gapSize * 1.5,
            fill="#FFFFFF",
            tags="Road" + str(roadNumber),
        )
        roadConnections.at[
            roadNumber - 1, "roadTextObj"
        ] = colonizer.canvas.create_text(
            (fromXCenter + toXCenter) / 2,
            (fromYCenter + toYCenter) / 2,
            text="",
            font=("Helvetica", 11),
            tags="Road" + str(roadNumber),
        )
        colonizer.canvas.tag_bind(
            "Road" + str(roadNumber),
            "<Button-1>",
            lambda event: StructureClicked(roadNumber),
        )

    for index, row in roadConnections.iterrows():
        SetupRoad(row["roadNum"], row["from"], row["to"])

    # setting up buildings
    def SetupBuilding(buildingNumber, x, y, r, printText, color):
        # setup settlement circle
        x0 = x - r * 2.5
        y0 = y - r * 2.5
        x1 = x + r * 2.5
        y1 = y + r * 2.5
        buildingLocation.at[
            buildingNumber - 1, "buildingShapeObj"
        ] = colonizer.canvas.create_oval(
            x0, y0, x1, y1, fill=color, tags="Building" + str(buildingNumber), width=1
        )

        # setup texts
        buildingLocation.at[
            buildingNumber - 1, "buildingTextObj"
        ] = colonizer.canvas.create_text(
            (x0 + x1) / 2,
            (y0 + y1) / 2,
            text=printText,
            font=("Helvetica", 11),
            tags="Building" + str(buildingNumber),
        )
        colonizer.canvas.tag_bind(
            "Building" + str(buildingNumber),
            "<Button-1>",
            lambda event: StructureClicked(buildingNumber),
        )

    def StructureClicked(structureNumber):
        global currentActivePlayer, currentAction

        if currentAction == "Road":
            # mark the player
            roadConnections.at[
                structureNumber - 1, "occupiedPlayer"
            ] = currentActivePlayer
            # color the building location
            colonizer.canvas.itemconfig(
                roadConnections.at[structureNumber - 1, "roadShapeObj"],
                fill=playerColor[playerStats.loc[currentActivePlayer, "color",]],
            )

        elif currentAction == "Settlement":
            # mark the player
            buildingLocation.at[
                structureNumber - 1, "OccupiedPlayer"
            ] = currentActivePlayer
            # color the building location
            colonizer.canvas.itemconfig(
                buildingLocation.at[structureNumber - 1, "buildingShapeObj"],
                fill=playerColor[playerStats.loc[currentActivePlayer, "color",]],
            )

            UpdateEconProdValue()

        elif currentAction == "City":
            # mark the player
            buildingLocation.at[
                structureNumber - 1, "OccupiedPlayer"
            ] = currentActivePlayer
            buildingLocation.at[structureNumber - 1, "isCity"] = True
            # color the building location and change the thickness
            colonizer.canvas.itemconfig(
                buildingLocation.at[structureNumber - 1, "buildingShapeObj"],
                fill=playerColor[playerStats.loc[currentActivePlayer, "color",]],
                width=5,
            )

            UpdateEconProdValue()

        elif currentAction == "Dev_Card":
            print(currentActivePlayer, "wants to buy a dev card")

        # unmark the player
        currentAction = None
        currentActivePlayer = None

    for index, row in buildingLocation.iterrows():
        # calculate the center of each hex tile
        xOffset = (row["Hex1_X"] + row["Hex2_X"] + row["Hex3_X"]) / 3
        yOffset = (row["Hex1_Y"] + row["Hex2_Y"] + row["Hex3_Y"]) / 3
        xCenter = xBoardCenter + np.sqrt(3) / 2 * radius * xOffset + gapSize * xOffset
        yCenter = yBoardCenter + 3 / 4 * radius * yOffset + gapSize * yOffset

        SetupBuilding(
            row["BuildingNum"],
            xCenter,
            yCenter,
            gapSize,
            "{0:0.2f}".format(buildingLocation.at[index, "LocValue"] * 10),
            "#FFFFFF",
        )

    def UpdateEconProdValue():
        # reset all production stats
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            playerStats[resourceType + "Prod"] = 0

        # loop through all buildingLocation to calculate only players' economic power
        for index, row in buildingLocation.iterrows():
            if row["OccupiedPlayer"] != 0:
                for nearbyHexNum in ["1", "2", "3"]:
                    currentHexValue = HexValueInfo(
                        row["Hex" + nearbyHexNum + "_X"],
                        row["Hex" + nearbyHexNum + "_Y"],
                    )

                    if currentHexValue[0] != "No Resource":
                        valueOfHex = currentHexValue[1] * (2 if row["isCity"] else 1)
                        playerStats.loc[
                            row["OccupiedPlayer"], currentHexValue[0] + "Prod"
                        ] += valueOfHex

        # add up the total economic power by summing over players
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            playerStats.loc[0, resourceType + "Prod"] = sum(
                playerStats.loc[1:4, resourceType + "Prod"]
            )

        # print to the screen
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            colonizer.canvas.itemconfig(
                playerStats.loc[0, resourceType + "ProdObj"],
                text="+" + "{0:0.3f}".format(playerStats.loc[0, resourceType + "Prod"]),
            )

        for playerID in [1, 2, 3, 4]:
            for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
                if playerStats.loc[playerID, "inPlay"]:
                    colonizer.canvas.itemconfig(
                        playerStats.loc[playerID, resourceType + "ProdObj"],
                        text="+"
                        + "{0:0.3f}".format(
                            playerStats.loc[playerID, resourceType + "Prod"]
                        ),
                    )


# %%
# update resource production value, returns an array [resource, probability], of the hex
def HexValueInfo(X_coor, Y_coor):
    hexResource = hexTiles.loc[
        (hexTiles["xHexOffset"] == X_coor) & (hexTiles["yHexOffset"] == Y_coor)
    ]["hexResource"].any()

    if not hexResource:
        return ["No Resource", 0]
    elif hexResource == "desert":
        return ["No Resource", diceRoll.loc[7, "prob"]]
    else:
        diceNumber = hexTiles.loc[
            (hexTiles["xHexOffset"] == X_coor) & (hexTiles["yHexOffset"] == Y_coor)
        ]["diceNumber"].item()
        return [hexResource, diceRoll.loc[diceNumber, "prob"]]


# to increment and decrement resources
def ResourceIncrement(playerID, resourceType):
    if playerStats.at[0, resourceType] > 0:
        playerStats.at[playerID, resourceType] += 1
        playerStats.at[0, resourceType] -= 1
    colonizer.canvas.itemconfig(
        playerStats.at[playerID, resourceType + "Obj"],
        text=playerStats.at[playerID, resourceType],
    )
    colonizer.canvas.itemconfig(
        playerStats.at[playerID, "resourceTotalObj"],
        text=sum(playerStats.iloc[playerID, 12:17]),
    )
    colonizer.canvas.itemconfig(
        playerStats.at[0, resourceType + "Obj"], text=playerStats.at[0, resourceType]
    )


def ResourceDecrement(playerID, resourceType):
    if playerStats.at[playerID, resourceType] > 0:
        playerStats.at[playerID, resourceType] -= 1
        playerStats.at[0, resourceType] += 1
    colonizer.canvas.itemconfig(
        playerStats.at[playerID, resourceType + "Obj"],
        text=playerStats.at[playerID, resourceType],
    )
    colonizer.canvas.itemconfig(
        playerStats.at[playerID, "resourceTotalObj"],
        text=sum(playerStats.iloc[playerID, 12:17]),
    )
    colonizer.canvas.itemconfig(
        playerStats.at[0, resourceType + "Obj"], text=playerStats.at[0, resourceType]
    )


def PurchaseItem(playerID, purchaseItem):
    print("player", playerID, "buys", purchaseItem)
    # resolve develpoment card purchase right away
    if purchaseItem == "Dev_Card":
        playerStats.loc[playerID, "acquiredDevCardTotal"] += 1
        colonizer.canvas.itemconfig(
            playerStats.at[playerID, "acquiredDevCardTotalObj"],
            text = playerStats.loc[playerID, "acquiredDevCardTotal"],
        )

        playerStats.loc[0, "acquiredDevCardTotal"] -= 1
        colonizer.canvas.itemconfig(
            playerStats.at[0, "acquiredDevCardTotalObj"],
            text = playerStats.loc[0, "acquiredDevCardTotal"],
        )

    # buying a structure, requires further instruction (i.e. which structure)
    else:
        global currentActivePlayer, currentAction
        currentActivePlayer = playerID
        currentAction = purchaseItem


def SetupPlayerStatsTracker():
    def PlayerBoraderTopLeftCoord(playerID):
        return [
            xBoardCenter + (radius + gapSize) * 7,
            gameWindowHeight / 5 * playerID + 3,
        ]

    def DevCardAcquired(playerID, itemType):
        print(playerID, "acquired dev card", itemType)


    def DevCardUsed(playerID, itemType):
        print(playerID, "used dev card", itemType)


    def SetupCardButton(playerID, itemType, isResource):
        top_left_x = PlayerBoraderTopLeftCoord(playerID)[0]
        top_left_y = PlayerBoraderTopLeftCoord(playerID)[1]

        itemXOffset = {
            "lumber": 0, "brick": 1, "sheep": 2, "wheat": 3, "rock": 4,
            "Knight": 0, "VictoryPoint": 1, "Monopoly": 2, "RoadBuilding": 3, "YearOfPlenty": 4
        }

        # building the resource box with button and commands
        colonizer.canvas.create_polygon(
            [
                top_left_x + 230 + itemXOffset[itemType] * 70,
                top_left_y + 5 + (0 if isResource else 90),
                top_left_x + 280 + itemXOffset[itemType] * 70,
                top_left_y + 5 + (0 if isResource else 90),
                top_left_x + 280 + itemXOffset[itemType] * 70,
                top_left_y + 85 + (0 if isResource else 90),
                top_left_x + 230 + itemXOffset[itemType] * 70,
                top_left_y + 85 + (0 if isResource else 90),
            ],
            outline="#000000",
            fill=resourceColor[itemType] if isResource else resourceColor["desert"],
            tags="PlayerID" + str(playerID) + "Resource" + itemType,
        )

        # print the number of resource or development card type
        playerStats.at[playerID, itemType + "Obj"] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0]
            + (230 + 280) / 2
            + itemXOffset[itemType] * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 25 + (0 if isResource else 90),
            text=playerStats.at[playerID, itemType] if isResource else playerStats.at[playerID, "acquired"+itemType],
            anchor="c",
            font=("Helvetica", 24),
            tags="PlayerID" + str(playerID) + "Item" + itemType,
        )
        colonizer.canvas.tag_bind(
            "PlayerID" + str(playerID) + "Item" + itemType,
            "<Button-1>",
            lambda event: ResourceIncrement(playerID, itemType) if isResource else DevCardAcquired(playerID, itemType),
        )
        colonizer.canvas.tag_bind(
            "PlayerID" + str(playerID) + "Item" + itemType,
            "<Button-2>",
            lambda event: ResourceDecrement(playerID, itemType) if isResource else DevCardUsed(playerID, itemType),
        )

        # production value
        playerStats.at[
            playerID, itemType + "ProdObj"
        ] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0]
            + (230 + 280) / 2
            + itemXOffset[itemType] * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 45 + (0 if isResource else 90),
            text="+0.000" if isResource else itemType,
            anchor="c",
            font=("Helvetica", 12 if isResource else 8),
        )


    def SetupPlayerColor(playerID):
        top_left_x = PlayerBoraderTopLeftCoord(playerID)[0]
        top_left_y = PlayerBoraderTopLeftCoord(playerID)[1]

        # player color selector
        if playerID == 0:
            # Show player ID and color
            colonizer.canvas.create_text(
                top_left_x + 10, top_left_y + 15, text="Bank", anchor="w"
            )
        else:

            def PlayerColorChange(*args):
                playerStats.at[playerID, "color"] = playerIDColor.get()
                playerStats.at[playerID, "inPlay"] = True
                SetupPlayerInit(playerID)

            # show player ID and color
            colonizer.canvas.create_text(
                top_left_x + 10,
                top_left_y + 15,
                text="Player " + str(playerID) + ":",
                anchor="w",
            )

            # assigns color to a player with a dropdown menu
            playerIDColor = tk.StringVar()
            playerIDColor.set("Select Color")
            playerColorDropdown = tk.OptionMenu(
                colonizer, playerIDColor, *playerColor.keys(), command=PlayerColorChange
            )
            playerColorDropdown.config(width=8)
            playerColorDropdown.place(x=top_left_x + 70, y=top_left_y + 15, anchor="w")

    def SetupPurchaseTiles(playerID, item):
        # building buttons
        itemOffset = {"Road": 0, "Settlement": 1, "City": 2, "Dev_Card": 3}
        colonizer.canvas.create_polygon(
            [
                PlayerBoraderTopLeftCoord(playerID)[0] + 110,
                PlayerBoraderTopLeftCoord(playerID)[1] + 35 + itemOffset[item] * 35,
                PlayerBoraderTopLeftCoord(playerID)[0] + 190,
                PlayerBoraderTopLeftCoord(playerID)[1] + 35 + itemOffset[item] * 35,
                PlayerBoraderTopLeftCoord(playerID)[0] + 190,
                PlayerBoraderTopLeftCoord(playerID)[1] + 65 + itemOffset[item] * 35,
                PlayerBoraderTopLeftCoord(playerID)[0] + 110,
                PlayerBoraderTopLeftCoord(playerID)[1] + 65 + itemOffset[item] * 35,
            ],
            outline="#000000",
            fill=playerColor[playerStats.loc[playerID, "color"]],
            tags="PlayerID" + str(playerID) + "Purchase" + item,
        )
        colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0] + (110 + 190) / 2,
            PlayerBoraderTopLeftCoord(playerID)[1]
            + (35 + 65) / 2
            + itemOffset[item] * 35,
            text=item if item != "Dev_Card" else "Dev Card",
            anchor="c",
            font=("Helvetica", 12),
            tags="PlayerID" + str(playerID) + "Purchase" + item,
        )
        colonizer.canvas.tag_bind(
            "PlayerID" + str(playerID) + "Purchase" + item,
            "<Button-1>",
            lambda event: PurchaseItem(playerID, item),
        )

    def SetupPlayerInit(playerID):
        if playerID != 0:
            for item in ["Road", "Settlement", "City", "Dev_Card"]:
                SetupPurchaseTiles(playerID, item)

            playerStats.at[
                playerID, "initPositionScoreObj"
            ] = colonizer.canvas.create_text(
                PlayerBoraderTopLeftCoord(playerID)[0] + (10 + 90) / 2,
                PlayerBoraderTopLeftCoord(playerID)[1] + 45,
                text="",
                anchor="c",
                font=("Helvetica", 12),
            )

        # resource tracker
        for resourceType in ["lumber", "brick", "sheep", "wheat", "rock"]:
            SetupCardButton(playerID, resourceType, True)

        # development cards tracker
        for devCardType in ["Knight", "VictoryPoint", "Monopoly", "RoadBuilding", "YearOfPlenty"]:
            SetupCardButton(playerID, devCardType, False)

        # total resource
        colonizer.canvas.create_polygon(
            [
                PlayerBoraderTopLeftCoord(playerID)[0] + 230 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 5,
                PlayerBoraderTopLeftCoord(playerID)[0] + 280 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 5,
                PlayerBoraderTopLeftCoord(playerID)[0] + 280 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 85,
                PlayerBoraderTopLeftCoord(playerID)[0] + 230 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 85,
            ],
            outline="#000000",
            fill="#4371FF", #blue
        )
        playerStats.at[playerID, "resourceTotalObj"] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0] + (230 + 280) / 2 + 5 * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 25,
            text="" if playerID == 0 else "0",
            anchor="c",
            font=("Helvetica", 24),
        )
        playerStats.at[playerID, "resourceTotalProdObj"] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0] + (230 + 280) / 2 + 5 * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 45,
            text="+0.000",
            anchor="c",
            font=("Helvetica", 12),
        )

        # total dev cards
        colonizer.canvas.create_polygon(
            [
                PlayerBoraderTopLeftCoord(playerID)[0] + 230 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 5 + 90,
                PlayerBoraderTopLeftCoord(playerID)[0] + 280 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 5 + 90,
                PlayerBoraderTopLeftCoord(playerID)[0] + 280 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 85 + 90,
                PlayerBoraderTopLeftCoord(playerID)[0] + 230 + 5 * 70,
                PlayerBoraderTopLeftCoord(playerID)[1] + 85 + 90,
            ],
            outline="#000000",
            fill=resourceColor["desert"],
        )
        playerStats.at[playerID, "acquiredDevCardTotalObj"] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0] + (230 + 280) / 2 + 5 * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 25 + 90,
            text=playerStats.loc[playerID, "acquiredDevCardTotal"],
            anchor="c",
            font=("Helvetica", 24),
        )
        playerStats.at[playerID, "resourceTotalProdObj"] = colonizer.canvas.create_text(
            PlayerBoraderTopLeftCoord(playerID)[0] + (230 + 280) / 2 + 5 * 70,
            PlayerBoraderTopLeftCoord(playerID)[1] + 45 + 90,
            text="Dev Cards",
            anchor="c",
            font=("Helvetica", 8),
        )

    for playerID in [0, 1, 2, 3, 4]:
        # build bank & players' borders
        colonizer.canvas.create_polygon(
            [
                PlayerBoraderTopLeftCoord(playerID)[0],
                PlayerBoraderTopLeftCoord(playerID)[1],
                gameWindowWidth,
                gameWindowHeight / 5 * playerID + 3,
                gameWindowWidth,
                gameWindowHeight / 5 * (playerID + 1) + 3,
                xBoardCenter + (radius + gapSize) * 7,
                gameWindowHeight / 5 * (playerID + 1) + 3,
            ],
            outline="#000000",
            fill="#FFFFFF",
            width=2,
        )

        SetupPlayerInit(0)
        SetupPlayerColor(playerID)


# %%
# init game
SetupBoard()
SetupPlayerStatsTracker()
colonizer.mainloop()
