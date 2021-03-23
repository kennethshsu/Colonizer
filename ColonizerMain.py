import numpy as np
import pandas as pd
import tkinter as tk

#%%
gameID = 6

gameWindowWidth = 1600
gameWindowHeight = 900
xBoardCenter = 450
yBoardCenter = 450
radius = 65
gapSize = 7

colonizer = tk.Tk()
colonizer.canvas = tk.Canvas(width = gameWindowWidth, height = gameWindowHeight)
colonizer.title('Colonizer - Game ' + str(gameID))
colonizer.canvas.pack()

#%%
# Some useful dictionaries
# Resrouce color
resourceColor = {
    'wood': '#11933B',
    'brick': '#DC5539',
    'sheep': '#9CBD29',
    'wheat': '#F2BA24',
    'rock': '#9FA5A1',
    'desert': '#EBE5B5'
}

# Dice probability
diceProb = {
    2: 1/36,
    3: 2/36,
    4: 3/36,
    5: 4/36,
    6: 5/36,
    7: 6/36,
    8: 5/36,
    9: 4/36,
    10: 3/36,
    11: 2/36,
    12: 1/36
}

#%%
gameBoards = pd.read_excel('./GameBoards.xlsx')

# Select which game board to load, gameID is selected above
selectedGameBoard = gameBoards[gameBoards['Game'] == gameID]
# We can add code here to make sure that the board is a valid board (e.g. 4 woods, 3 bricks, ..., 1 wood port, 1 brick port, etc)

#%%
# Load the board, hexes will get a default diceNumber of 0,
# it will be assigned next

# Load the hexes
hexTiles = pd.DataFrame(
    [
        # Row 1
        [selectedGameBoard.iloc[0, 1], -2, -4, 3, 0],
        [selectedGameBoard.iloc[0, 2], 0, -4, 3, 0],
        [selectedGameBoard.iloc[0, 3], 2, -4, 3, 0],
        # Row 2
        [selectedGameBoard.iloc[0, 4], -3, -2, 3, 0],
        [selectedGameBoard.iloc[0, 5], -1, -2, 2, 0],
        [selectedGameBoard.iloc[0, 6], 1, -2, 2, 0],
        [selectedGameBoard.iloc[0, 7], 3, -2, 3, 0],
        # Row 3
        [selectedGameBoard.iloc[0, 8], -4, 0, 3, 0],
        [selectedGameBoard.iloc[0, 9], -2, 0, 2, 0],
        [selectedGameBoard.iloc[0, 10], 0, 0, 1, 0],
        [selectedGameBoard.iloc[0, 11], 2, 0, 2, 0],
        [selectedGameBoard.iloc[0, 12], 4, 0, 3, 0],
        # Row 4
        [selectedGameBoard.iloc[0, 13], -3, 2, 3, 0],
        [selectedGameBoard.iloc[0, 14], -1, 2, 2, 0],
        [selectedGameBoard.iloc[0, 15], 1, 2, 2, 0],
        [selectedGameBoard.iloc[0, 16], 3, 2, 3, 0],
        # Row 5
        [selectedGameBoard.iloc[0, 17], -2, 4, 3, 0],
        [selectedGameBoard.iloc[0, 18], 0, 4, 3, 0],
        [selectedGameBoard.iloc[0, 19], 2, 4, 3, 0],
    ],
    columns = ['hexResource', 'xHexOffset', 'yHexOffset', 'ring', 'diceNumber']
)

# Load the ports
portTiles = pd.DataFrame(
    [
        [selectedGameBoard.iloc[0, 20], -2, -4, 'NW'],
        [selectedGameBoard.iloc[0, 21], 0, -4, 'NE'],
        [selectedGameBoard.iloc[0, 22], 3, -2, 'NE'],
        [selectedGameBoard.iloc[0, 23], 4, 0, 'E'],
        [selectedGameBoard.iloc[0, 24], 3, 2, 'SE'],
        [selectedGameBoard.iloc[0, 25], 0, 4, 'SE'],
        [selectedGameBoard.iloc[0, 26], -2, 4, 'SW'],
        [selectedGameBoard.iloc[0, 27], -3, 2, 'W'],
        [selectedGameBoard.iloc[0, 28], -3, -2, 'W']
    ],
    columns = ['portType', 'xHexOffset', 'yHexOffset', 'portDirection']
)


#%%
# Assigning dice numbers to the hexes
diceSetupHexOffset = selectedGameBoard.iloc[0, 29]
diceSetupClockwise = selectedGameBoard.iloc[0, 30]

# The order of hexes on the outer ring, followed by the first hex
diceOrderRing1 = pd.DataFrame(
    [
        [-2, -4], [0, -4], [2, -4], [3, -2], [4, 0], [3, 2], [2, 4], [0, 4],
        [-2, 4], [-3, 2], [-4, 0], [-3, -2]
    ]
)
diceOrderRing1 = pd.DataFrame.append(
    diceOrderRing1.iloc[diceSetupHexOffset:12],
    diceOrderRing1.iloc[0:diceSetupHexOffset]
)

# The order of hexes on the middle ring, followed by the first hex
diceOrderRing2 = pd.DataFrame(
    [
        [-1, -2], [1, -2], [2, 0], [1, 2], [-1, 2], [-2, 0]
    ]
)
diceOrderRing2 = pd.DataFrame.append(
    diceOrderRing2.iloc[int(diceSetupHexOffset/2):6],
    diceOrderRing2.iloc[0:int(diceSetupHexOffset/2)]
)

diceOrderRing3 = pd.DataFrame(
    [
        [0, 0]
    ]
)

# Setting up the order of hexes to get assigned dice numbers
if diceSetupClockwise:
    diceAssignmentOrder = diceOrderRing1
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing2)
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing3)

else:
    diceAssignmentOrder = diceOrderRing1.iloc[0:1].append(diceOrderRing1.iloc[1:18].iloc[::-1])
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing2.iloc[0:1].append(diceOrderRing2.iloc[1:18].iloc[::-1]))
    diceAssignmentOrder = diceAssignmentOrder.append(diceOrderRing3)


diceAssignmentOrder.columns = ['xHexOffset', 'yHexOffset']

diceSetupOrder = [5, 2, 6, 3, 8, 10, 9, 12, 11, 4, 8, 10, 9, 4, 5, 6, 3, 11]
diceCounter = 0

for index, row in diceAssignmentOrder.iterrows():

    if hexTiles.loc[
            (hexTiles['xHexOffset'] == row['xHexOffset'])
            & (hexTiles['yHexOffset'] == row['yHexOffset']), 'hexResource'
        ].all() != 'desert':
        hexTiles.loc[
            (hexTiles['xHexOffset'] == row['xHexOffset'])
            & (hexTiles['yHexOffset'] == row['yHexOffset']), 'diceNumber'
        ] = diceSetupOrder[diceCounter]
        diceCounter += 1
    else:
        hexTiles.loc[
            (hexTiles['xHexOffset'] == row['xHexOffset'])
            & (hexTiles['yHexOffset'] == row['yHexOffset']), 'diceNumber'
        ] = 0

#%% Hex coordinates by ring
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
        [4, -1, -6]
    ],
    columns = ['Ring', 'xHexOffset', 'yHexOffset']
)

#%% Init empty settlement/city spaces
buildingLocationArray = []
buildingNumber = 1
ringSize = [6, 18, 30] # The inner ring has 6 buildable locations, center ring has 18, outer ring has 30

for ring in range(3):
    for buildingInRing in range(ringSize[ring]):
        buildingLocationArray.append(
            [buildingNumber, ring + 1, buildingInRing + 1]
        )
        buildingNumber += 1

buildingLocation = pd.DataFrame(
    buildingLocationArray,
    columns = ['BuildingNum', 'Ring', 'RingBuildingNum'])

for index, row in buildingLocation.iterrows():

    if row['Ring'] == 1:
        buildingLocation.at[index, 'Hex1_X'] = HexOrder.iloc[0][1]
        buildingLocation.at[index, 'Hex1_Y'] = HexOrder.iloc[0][2]
        buildingLocation.at[index, 'Hex2_X'] = HexOrder[
            HexOrder['Ring'] == 2].iloc[
                (row['RingBuildingNum']-1)%6-1
            ]['xHexOffset']
        buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
            HexOrder['Ring'] == 2].iloc[
                (row['RingBuildingNum']-1)%6-1
            ]['yHexOffset']
        buildingLocation.at[index, 'Hex3_X'] = HexOrder[
            HexOrder['Ring'] == 2].iloc[
                (row['RingBuildingNum'])%6-1
            ]['xHexOffset']
        buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
            HexOrder['Ring'] == 2].iloc[
                (row['RingBuildingNum'])%6-1
            ]['yHexOffset']

    elif row['Ring'] == 2:
        # These buildings are adjacent to two hexes on ring 2
        if row['RingBuildingNum'] % 3 == 1:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3)-1)%6
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3)-1)%6
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3))%6
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3))%6
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round(row['RingBuildingNum']/3))*2
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round(row['RingBuildingNum']/3))*2
                ]['yHexOffset']

        # These buildings are adjacent to two hexes on ring 3
        else:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']+1)/3*2)-2)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']+1)/3*2)-2)%12
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3)-1)%6
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
                HexOrder['Ring'] == 2].iloc[
                    (round(row['RingBuildingNum']/3)-1)%6
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']+1)/3*2)-1)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']+1)/3*2)-1)%12
                ]['yHexOffset']

    elif row['Ring'] == 3:
        # These buildings are adjacent to one hex on ring 3 (i.e. outer coast)
        if row['RingBuildingNum'] % 5 != 2 & row['RingBuildingNum'] % 5 != 5:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']-1)/5*2))
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    (round((row['RingBuildingNum']-1)/5*2))
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    (round((row['RingBuildingNum']-1)/5*3-1)%18)
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    (round((row['RingBuildingNum']-1)/5*3-1)%18)
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    (round((row['RingBuildingNum']-1)/5*3)%18)
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    (round((row['RingBuildingNum']-1)/5*3)%18)
                ]['yHexOffset']

        # These buildings are adjacent to two hexes on ring 3 (i.e. inner coast)
        elif row['RingBuildingNum'] % 5 == 2:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2)%12
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2+1)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2+1)%12
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    round((row['RingBuildingNum']-2)/5*3)%18
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    round((row['RingBuildingNum']-2)/5*3)%18
                ]['yHexOffset']
        elif row['RingBuildingNum'] % 5 == 0:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2-1)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2-1)%12
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2)%12
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[
                HexOrder['Ring'] == 3].iloc[
                    round((row['RingBuildingNum']
                           -row['RingBuildingNum']%5)/5*2)%12
                ]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    round(row['RingBuildingNum']/5*3-1)%18
                ]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[
                HexOrder['Ring'] == 4].iloc[
                    round(row['RingBuildingNum']/5*3-1)%18
                ]['yHexOffset']

    buildingLocation.at[index, 'OccupiedPlayer'] = 0
    buildingLocation.at[index, 'isCity'] = False

buildingLocation['OccupiedPlayer'] = buildingLocation['OccupiedPlayer'].astype(int)

# Calculate the value of each building location
resourceEconValue = {
    'wood': 0,
    'brick': 0,
    'sheep': 0,
    'wheat': 0,
    'rock': 0
}

# Calcuate the scarcity of each resource
for index, row in hexTiles.iterrows():
    if row['hexResource'] == "wood":
        resourceEconValue['wood'] += diceProb[row['diceNumber']]
    elif row['hexResource'] == "brick":
        resourceEconValue['brick'] += diceProb[row['diceNumber']]
    elif row['hexResource'] == "sheep":
        resourceEconValue['sheep'] += diceProb[row['diceNumber']]
    elif row['hexResource'] == "wheat":
        resourceEconValue['wheat'] += diceProb[row['diceNumber']]
    elif row['hexResource'] == "rock":
        resourceEconValue['rock'] += diceProb[row['diceNumber']]

for index, row in buildingLocation.iterrows():
    buildingLocValue = 0

    for hexes in [1, 2, 3]:
        currentTile = hexTiles[
            (hexTiles['xHexOffset'] == row["Hex"+str(hexes)+"_X"])
            & (hexTiles['yHexOffset'] == row["Hex"+str(hexes)+"_Y"])
        ]

        if currentTile.empty:
            buildingLocValue += 0
        elif currentTile.iloc[0]['hexResource'] == 'desert':
            buildingLocValue += 0
        else:
            currentTileProb = diceProb[
                currentTile.iloc[0]['diceNumber']
            ]
            buildingLocValue += (
                1/resourceEconValue[currentTile.iloc[0]['hexResource']] * currentTileProb
            )
    buildingLocation.at[index, 'LocValue'] = buildingLocValue

#%% Setting up the Board
def printBuilding(buildingNumber, x, y, r, printText, color):
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    colonizer.canvas.create_oval(x0, y0, x1, y1, fill = color, tags = "Building"+str(buildingNumber))
    colonizer.canvas.create_text(
        (x0+x1)/2,
        (y0+y1)/2,
        text = printText,
        font = ('Helvetica', 11),
        tags = "Building"+str(buildingNumber)
    )
    colonizer.canvas.tag_bind("Building"+str(buildingNumber), "<Button-1>", lambda event: buildingClicked(buildingNumber))

def loadHex(hexResource, xHexOffset, yHexOffset, diceNumber):
    # Calculate the center of each hex tile
    xHexCenter = (
        xBoardCenter + np.sqrt(3)/2 * radius * xHexOffset
        + gapSize * xHexOffset
    )
    yHexCenter = (
        yBoardCenter + 3/4 * radius * yHexOffset
        + gapSize * yHexOffset
    )

    # Coordinates of the 6 points of the hex
    points = [
        xHexCenter + np.sqrt(3)/2 * radius, yHexCenter - radius/2,
        xHexCenter + 0, yHexCenter - radius,
        xHexCenter - np.sqrt(3)/2 * radius, yHexCenter - radius/2,
        xHexCenter - np.sqrt(3)/2 * radius, yHexCenter + radius/2,
        xHexCenter + 0, yHexCenter + radius,
        xHexCenter + np.sqrt(3)/2 * radius, yHexCenter + radius/2
    ]
    colonizer.canvas.create_polygon(points,
        outline = '#000000',
        fill = resourceColor[hexResource],
        width = 2
    )

    # This is the dice roll number
    if diceNumber > 1:
        colonizer.canvas.create_text(
            xHexCenter,
            yHexCenter,
            text = str(diceNumber),
            font = ('Helvetica', 32)
        )

    # This is the hex location coordinates
    colonizer.canvas.create_text(
        xHexCenter,
        yHexCenter + radius/4,
        text = "(" + str(xHexOffset) + ", " + str(yHexOffset) + ")",
        font = ('Helvetica', 10)
    )

def loadPort(portType, xHexOffset, yHexOffset, portDirection):
    # Calculate the center of each hex tile
    xHexCenter = (
        xBoardCenter + np.sqrt(3)/2 * radius * xHexOffset
        + gapSize * xHexOffset
    )
    yHexCenter = (
        yBoardCenter + 3/4 * radius * yHexOffset
        + gapSize * yHexOffset
    )

    if portDirection == 'E':
        points = [
            xHexCenter + np.sqrt(3)/2 * radius + gapSize*2,
            yHexCenter - radius/2 ,
            xHexCenter + np.sqrt(3)/2 * radius + gapSize*2,
            yHexCenter + radius/2,
            xHexCenter + np.sqrt(3)/2 * radius + np.sqrt(3)/2 * radius + gapSize*2,
            yHexCenter + 0
        ]
    elif portDirection == 'SE':
        points = [
            xHexCenter + 0 + gapSize,
            yHexCenter + radius + np.sqrt(3)*gapSize,
            xHexCenter + np.sqrt(3)/2 * radius + gapSize,
            yHexCenter + radius/2 + np.sqrt(3)*gapSize,
            xHexCenter + np.sqrt(3)/2 * radius + gapSize,
            yHexCenter + radius/2 + radius + np.sqrt(3)*gapSize
        ]
    elif portDirection == 'SW':
        points = [
            xHexCenter - 0 - gapSize,
            yHexCenter + radius + np.sqrt(3)*gapSize,
            xHexCenter - np.sqrt(3)/2 * radius - gapSize,
            yHexCenter + radius/2 + np.sqrt(3)*gapSize,
            xHexCenter - np.sqrt(3)/2 * radius - gapSize,
            yHexCenter + radius/2 + radius + np.sqrt(3)*gapSize
        ]
    elif portDirection == 'W':
        points = [
            xHexCenter - np.sqrt(3)/2 * radius - gapSize*2,
            yHexCenter - radius/2,
            xHexCenter - np.sqrt(3)/2 * radius - gapSize*2,
            yHexCenter + radius/2,
            xHexCenter - np.sqrt(3)/2 * radius - np.sqrt(3)/2 * radius - gapSize*2,
            yHexCenter + 0
        ]
    elif portDirection == 'NW':
        points = [
            xHexCenter - 0 - gapSize,
            yHexCenter - radius - np.sqrt(3)*gapSize,
            xHexCenter - np.sqrt(3)/2 * radius - gapSize,
            yHexCenter - radius/2 - np.sqrt(3)*gapSize,
            xHexCenter - np.sqrt(3)/2 * radius - gapSize,
            yHexCenter - radius/2 - radius - np.sqrt(3)*gapSize
        ]
    elif portDirection == "NE":
        points = [
            xHexCenter + 0 + gapSize,
            yHexCenter - radius - np.sqrt(3)*gapSize,
            xHexCenter + np.sqrt(3)/2 * radius + gapSize,
            yHexCenter - radius/2 - np.sqrt(3)*gapSize,
            xHexCenter + np.sqrt(3)/2 * radius + gapSize,
            yHexCenter - radius/2 - radius - np.sqrt(3)*gapSize
        ]
    colonizer.canvas.create_polygon(points,
        outline = '#000000',
        fill = resourceColor[portType],
        width = 2)

# Setting up hex by hex, row by row from upper left tile
for index, row in hexTiles.iterrows():
    loadHex(
        row['hexResource'],
        row['xHexOffset'],
        row['yHexOffset'],
        row['diceNumber']
    )

# Setting up ports
for index, row in portTiles.iterrows():
    loadPort(
        row['portType'],
        row['xHexOffset'],
        row['yHexOffset'],
        row['portDirection'],
    )

# Setting up buildings
def showBuildings():
    global showHexValue

    for index, row in buildingLocation.iterrows():
        # Calculate the center of each hex tile
        xOffset = (row['Hex1_X'] + row['Hex2_X'] + row['Hex3_X'])/3
        yOffset = (row['Hex1_Y'] + row['Hex2_Y'] + row['Hex3_Y'])/3
        xCenter = (
            xBoardCenter + np.sqrt(3)/2 * radius * xOffset
            + gapSize * xOffset
        )
        yCenter = (
            yBoardCenter + 3/4 * radius * yOffset + gapSize * yOffset
        )
        printBuilding(
            row['BuildingNum'],
            xCenter,
            yCenter,
            gapSize*2.5,
            "{0:0.2f}".format(row['LocValue']*10) if showHexValue else str(int(row['BuildingNum'])),
            "#e2e2e2" if showHexValue else "#ffffff"
        )

    if showHexValue:
        BuildingValueToggle.config(text = "    Show Building Number    ")
    else:
        BuildingValueToggle.config(text = "Show Building Location Value")

    # Toggle the value
    showHexValue = not showHexValue

def buildingClicked(buildingNumber):
    print('Building Clicked: ' + str(buildingNumber))

showHexValue = False
BuildingValueToggle = tk.Button(
    colonizer,
    text = "    Show Building Number    ",
    command = showBuildings
)
BuildingValueToggle.place(x = 20, y = 5)

showBuildings()

#%% Keep track of players
playerStats = pd.DataFrame(
    {
        'Player': [0, 1, 2, 3, 4],
        'color': ['white', 'white', 'white', 'white', 'white'],
        'inPlay': [True, False, False, False, False],
        'knownVictoryPoints': [0, 0, 0, 0, 0],
        'currentRoadLength': [0, 0, 0, 0, 0],
        'hasLongestRoad': [False, False, False, False, False],
        'currentArmySize': [0, 0, 0, 0, 0],
        'hasLargestArmy': [False, False, False, False, False],
        'road': [0, 15, 15, 15, 15],
        'settlement': [0, 5, 5, 5, 5],
        'city': [0, 4, 4, 4, 4],
        'hiddenDevCard': [25, 0, 0, 0, 0],
        'wood': [19, 0, 0, 0, 0],
        'brick': [19, 0, 0, 0, 0],
        'sheep': [19, 0, 0, 0, 0],
        'wheat': [19, 0, 0, 0, 0],
        'rock': [19, 0, 0, 0, 0]
    }
)
playerColors = ['red', 'blue', 'orange', 'green', 'black']

def printPlayerStats(playerID):
    #Build bank & players' borders
    top_left_x = xBoardCenter + (radius+gapSize) * 7
    top_left_y = gameWindowHeight/5 * playerID + 3
    top_right_x = gameWindowWidth
    top_right_y = gameWindowHeight/5 * playerID + 3
    bot_left_x = xBoardCenter + (radius+gapSize) * 7
    bot_left_y = gameWindowHeight/5 * (playerID+1) + 3
    bot_right_x = gameWindowWidth
    bot_right_y = gameWindowHeight/5 * (playerID+1) + 3

    colonizer.canvas.create_polygon(
        [top_left_x, top_left_y,
         top_right_x, top_right_y,
         bot_right_x, bot_right_y,
         bot_left_x, bot_left_y],
        outline = '#000000',
        fill = '#FFFFFF',
        width = 2
    )

    def printResource(resourceType):
        resourceOffset = {
            'wood': 0,
            'brick': 1,
            'sheep': 2,
            'wheat': 3,
            'rock': 4
        }

        #Building the resource box with button commands
        def resourceIncrement(playerID, resourceType):
            print("inc", playerID, resourceType)
        def resourceDecrement(playerID, resourceType):
            print("dec", playerID, resourceType)
        colonizer.canvas.create_polygon(
            [top_left_x + 200 + resourceOffset[resourceType] * 70, top_left_y + 5,
             top_left_x + 250 + resourceOffset[resourceType] * 70, top_left_y + 5,
             top_left_x + 250 + resourceOffset[resourceType] * 70, top_left_y + 85,
             top_left_x + 200 + resourceOffset[resourceType] * 70, top_left_y + 85],
            outline = '#000000',
            fill = resourceColor[resourceType],
            tags = "PlayerID"+str(playerID)+"Resource"+resourceType
        )
        colonizer.canvas.tag_bind("PlayerID"+str(playerID)+"Resource"+resourceType, "<Button-1>", lambda event: resourceIncrement(playerID, resourceType))
        colonizer.canvas.tag_bind("PlayerID"+str(playerID)+"Resource"+resourceType, "<Button-2>", lambda event: resourceDecrement(playerID, resourceType))

        #Player color selector
        if playerID == 0:
            #Show player ID and color
            colonizer.canvas.create_text(
                top_left_x + 10,
                top_left_y + 15,
                text = "Bank",
                anchor = 'w'
            )
        else:
            def playerColorChange(*args):
                playerStats.at[playerID, 'color'] = playerColor.get()
                playerStats.at[playerID, 'inPlay'] = True

            #Show player ID and color
            colonizer.canvas.create_text(
                top_left_x + 10,
                top_left_y + 15,
                text = "Player " + str(playerID) + ":",
                anchor = 'w'
            )

            #Assigns color to a player with a dropdown menu
            playerColor = tk.StringVar()
            playerColor.set("Select Color")
            playerColorDropdown = tk.OptionMenu(colonizer, playerColor, *playerColors, command = playerColorChange)
            playerColorDropdown.config(width = 8)
            playerColorDropdown.place(x = top_left_x + 70, y = top_left_y + 15, anchor = 'w')

    #Display bank's resources
    printResource('wood')
    printResource('brick')
    printResource('sheep')
    printResource('wheat')
    printResource('rock')

for playerID in [0, 1, 2, 3, 4]:
    printPlayerStats(playerID)






#%% Init game
colonizer.mainloop()






