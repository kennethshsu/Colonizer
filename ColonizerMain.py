import numpy as np
import pandas as pd
import tkinter as tk

#%%
gameID = 2

gameWindowWidth = 1200
gameWindowHeight = 9000
xBoardCenter = 450
yBoardCenter = 450
radius = 60
gapSize = 5

colonizer = tk.Tk()
colonizer.title = 'Colonizer'
colonizer.canvas = tk.Canvas(width = gameWindowWidth, height = gameWindowHeight)
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
# Hexes, defaulting diceNumber to 0, it will be assigned next
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

# Ports
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

# Order of the hexs that will be assigned dice number from diceSetupOrder
diceAssignmentOrder = pd.DataFrame(
    [
        [-2, -4], [-3, -2], [-4, 0], [-3, 2], [-2, 4],
        [0, 4], [2, 4], [3, 2], [4, 0], [3, -2], 
        [2, -4], [0, -4], [-1, -2], [-2, 0], [-1, 2],
        [1, 2], [2, 0], [1, -2], [0, 0]
    ],
    columns = ['xHexOffset', 'yHexOffset']
)

# Loading in dice numbers, hex by hex
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

# print(buildingLocation)
## need to start the (up to) three buildings assgnment

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


#%%
def BoardModule():
    
    def createCircle(x, y, r, label, color):
        x0 = x - r
        y0 = y - r
        x1 = x + r
        y1 = y + r
        colonizer.canvas.create_oval(x0, y0, x1, y1, fill = color)
        colonizer.canvas.create_text(
            xCenter, 
            yCenter, 
            text = label,
            font = ('Helvetica', 12)
        )

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
                font = ('Helvetica', 30)
            )
        
        # This is the hex location coordinates
        colonizer.canvas.create_text(
            xHexCenter, 
            yHexCenter + radius/4, 
            text = "(" + str(xHexOffset) + ", " + str(yHexOffset) + ")",
            font = ('Helvetica', 8)
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
    
    # Print game ID
    colonizer.canvas.create_text(
            10, 
            10,  
            text = "Game ID: " + str(gameID),
            font = ('Helvetica', 20),
            anchor="nw"
        )
        
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
        createCircle(
            xCenter, 
            yCenter, 
            gapSize*2.5,
            str(int(row['BuildingNum'])),
            "white"
        )
    
    def create_button(x1, y1, x2, y2, buttonName, stringToPrint, actionName):
        colonizer.canvas.create_rectangle(x1, y1, x2, y2, fill = '#DCDCDC', tags = buttonName)
        colonizer.canvas.create_text((x1+x2)/2, (y1+y2)/2, text = stringToPrint, tags = buttonName)
        colonizer.canvas.tag_bind(buttonName,"<Button-1>", clicked)
    
    def clicked(*args):
        print("Button Clicked!")
        printHexValue()
    
    create_button(50, 50, 100, 100, "testButton", "Hex Value", clicked)
 
#%%
# Calculate each resource's value (total economic production)
def printHexValue():
    woodEconValue = 0
    brickEconValue = 0
    sheepEconValue = 0
    wheatEconValue = 0
    rockEconValue = 0
    
    
#%%        
BoardModule()
colonizer.mainloop()






