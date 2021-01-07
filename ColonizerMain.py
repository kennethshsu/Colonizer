import numpy as np
import pandas as pd
from tkinter import *

#%%
gameID = 2

gameWindowWidth = 1200
gameWindowHeight = 9000
xBoardCenter = 450
yBoardCenter = 450
radius = 60
gapSize = 5

colonizer = Tk()
colonizer.title = 'Colonizer'
colonizer.canvas = Canvas(width = gameWindowWidth, height = gameWindowHeight)
colonizer.canvas.pack()

#%%
# Resrouce color dictionary
resourceColor = {
    'wood': '#11933B',
    'brick': '#DC5539',
    'sheep': '#9CBD29',
    'wheat': '#F2BA24',
    'rock': '#9FA5A1',
    'desert': '#EBE5B5'
}

#%%
gameBoards = pd.read_excel('./GameBoards.xlsx')

# Select which game board to load, gameID is selected above
selectedGameBoard = gameBoards[gameBoards['Game'] == gameID]
print(selectedGameBoard)

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

    if hexTiles.loc[(hexTiles['xHexOffset'] == row['xHexOffset']) & (hexTiles['yHexOffset'] == row['yHexOffset']), 'hexResource'].all() != 'desert':
        hexTiles.loc[(hexTiles['xHexOffset'] == row['xHexOffset']) & (hexTiles['yHexOffset'] == row['yHexOffset']), 'diceNumber'] = diceSetupOrder[diceCounter]
        diceCounter += 1
    else:
        hexTiles.loc[(hexTiles['xHexOffset'] == row['xHexOffset']) & (hexTiles['yHexOffset'] == row['yHexOffset']), 'diceNumber'] = 0

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
        [3, -2, -4]
    ],
    columns = ['Ring', 'xHexOffset', 'yHexOffset']
)
print(HexOrder.iloc[0][1])

#%% Init empty settlement/city spaces
buildingLocationArray = []
buildingNumber = 1
ringSize = [6, 18, 30] # The inner ring has 6 buildable locations, center ring has 18, outer ring has 30

for ring in range(3):
    for buildingInRing in range(ringSize[ring]):
        buildingLocationArray.append([buildingNumber, ring + 1, buildingInRing + 1])
        buildingNumber += 1

buildingLocation = pd.DataFrame(buildingLocationArray, columns = ['BuildingNum', 'Ring', 'RingBuildingNum'])

# print(buildingLocation)
## need to start the (up to) three buildings assgnment

# Inner ring buildings
print(ringSize[1])
for index, row in buildingLocation.iterrows():
    if row['Ring'] == 1:
        buildingLocation.at[index, 'Hex1_X'] = HexOrder.iloc[0][1]
        buildingLocation.at[index, 'Hex1_Y'] = HexOrder.iloc[0][2]
        buildingLocation.at[index, 'Hex2_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(row['RingBuildingNum']-1)%6-1]['xHexOffset']
        buildingLocation.at[index, 'Hex2_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(row['RingBuildingNum']-1)%6-1]['yHexOffset']
        buildingLocation.at[index, 'Hex3_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(row['RingBuildingNum'])%6-1]['xHexOffset']
        buildingLocation.at[index, 'Hex3_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(row['RingBuildingNum'])%6-1]['yHexOffset']
        
    if row['Ring'] == 2:
        # These buildings have 2 hexes from the center ring, and 1 from the outer ring
        if row['RingBuildingNum'] % 3 == 1:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round(row['RingBuildingNum']/3)-1)%6]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round(row['RingBuildingNum']/3)-1)%6]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round(row['RingBuildingNum']/3))%6]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round(row['RingBuildingNum']/3))%6]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round(row['RingBuildingNum']/3))*2]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round(row['RingBuildingNum']/3))*2]['yHexOffset']
        elif row['RingBuildingNum'] % 3 == 2:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum']-1)/3))*2]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum']-1)/3))*2]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round((row['RingBuildingNum']-1)/3))%6]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round((row['RingBuildingNum']-1)/3))%6]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum']-1)/3))*2+1]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum']-1)/3))*2+1]['yHexOffset']
        elif row['RingBuildingNum'] % 3 == 0:
            buildingLocation.at[index, 'Hex1_X'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum'])/3*2)-1)]['xHexOffset']
            buildingLocation.at[index, 'Hex1_Y'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum'])/3*2)-1)]['yHexOffset']
            buildingLocation.at[index, 'Hex2_X'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round((row['RingBuildingNum']-1)/3))%6-1]['xHexOffset']
            buildingLocation.at[index, 'Hex2_Y'] = HexOrder[HexOrder['Ring'] == 2].iloc[(round((row['RingBuildingNum']-1)/3))%6-1]['yHexOffset']
            buildingLocation.at[index, 'Hex3_X'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum'])/3*2)%12)]['xHexOffset']
            buildingLocation.at[index, 'Hex3_Y'] = HexOrder[HexOrder['Ring'] == 3].iloc[(round((row['RingBuildingNum'])/3*2)%12)]['yHexOffset']    

print(buildingLocation[['RingBuildingNum', 'Hex1_X', 'Hex1_Y', 'Hex2_X', 'Hex2_Y', 'Hex3_X', 'Hex3_Y']])
# print(buildingLocation)

#%%
def BoardModule():
    def loadHex(hexResource, xHexOffset, yHexOffset, diceNumber):
        # Calculate the center of each hex tile
        xHexCenter = xBoardCenter + np.sqrt(3)/2 * radius * xHexOffset + gapSize * xHexOffset
        yHexCenter = yBoardCenter + 3/4 * radius * yHexOffset + gapSize * yHexOffset
    
        # Coordinates of the 6 points of the hex
        points = [
            xHexCenter + np.sqrt(3)/2 * radius, yHexCenter - radius/2,
            xHexCenter + 0, yHexCenter - radius,
            xHexCenter - np.sqrt(3)/2 * radius, yHexCenter - radius/2,
            xHexCenter - np.sqrt(3)/2 * radius, yHexCenter + radius/2,
            xHexCenter + 0, yHexCenter + radius,
            xHexCenter + np.sqrt(3)/2 * radius, yHexCenter + radius/2]
        colonizer.canvas.create_polygon(points,
            outline = '#000000',
            fill = resourceColor[hexResource],
            width = 2)
        
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
        xHexCenter = xBoardCenter + np.sqrt(3)/2 * radius * xHexOffset + gapSize * xHexOffset
        yHexCenter = yBoardCenter + 3/4 * radius * yHexOffset + gapSize * yHexOffset
        
        if portDirection == 'E':
            points = [
                xHexCenter + np.sqrt(3)/2 * radius + gapSize*2, yHexCenter - radius/2 ,
                xHexCenter + np.sqrt(3)/2 * radius + gapSize*2, yHexCenter + radius/2,
                xHexCenter + np.sqrt(3)/2 * radius + np.sqrt(3)/2 * radius + gapSize*2, yHexCenter + 0
            ]
        elif portDirection == 'SE':
            points = [
                xHexCenter + 0 + gapSize, yHexCenter + radius + np.sqrt(3)*gapSize,
                xHexCenter + np.sqrt(3)/2 * radius + gapSize, yHexCenter + radius/2 + np.sqrt(3)*gapSize,
                xHexCenter + np.sqrt(3)/2 * radius + gapSize, yHexCenter + radius/2 + radius + np.sqrt(3)*gapSize
            ]
        elif portDirection == 'SW':
            points = [
                xHexCenter - 0 - gapSize, yHexCenter + radius + np.sqrt(3)*gapSize,
                xHexCenter - np.sqrt(3)/2 * radius - gapSize, yHexCenter + radius/2 + np.sqrt(3)*gapSize,
                xHexCenter - np.sqrt(3)/2 * radius - gapSize, yHexCenter + radius/2 + radius + np.sqrt(3)*gapSize
            ]
        elif portDirection == 'W':
            points = [
                xHexCenter - np.sqrt(3)/2 * radius - gapSize*2, yHexCenter - radius/2,
                xHexCenter - np.sqrt(3)/2 * radius - gapSize*2, yHexCenter + radius/2,
                xHexCenter - np.sqrt(3)/2 * radius - np.sqrt(3)/2 * radius - gapSize*2, yHexCenter + 0
            ]
        elif portDirection == 'NW':
            points = [
                xHexCenter - 0 - gapSize, yHexCenter - radius - np.sqrt(3)*gapSize,
                xHexCenter - np.sqrt(3)/2 * radius - gapSize, yHexCenter - radius/2 - np.sqrt(3)*gapSize,
                xHexCenter - np.sqrt(3)/2 * radius - gapSize, yHexCenter - radius/2 - radius - np.sqrt(3)*gapSize
            ]
        elif portDirection == "NE":
            points = [
                xHexCenter + 0 + gapSize, yHexCenter - radius - np.sqrt(3)*gapSize,
                xHexCenter + np.sqrt(3)/2 * radius + gapSize, yHexCenter - radius/2 - np.sqrt(3)*gapSize,
                xHexCenter + np.sqrt(3)/2 * radius + gapSize, yHexCenter - radius/2 - radius - np.sqrt(3)*gapSize
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
        loadHex(row['hexResource'], row['xHexOffset'], row['yHexOffset'], row['diceNumber'])
    
    # Setting up ports
    for index, row in portTiles.iterrows():
        loadPort(row['portType'], row['xHexOffset'], row['yHexOffset'], row['portDirection'],)
        
    # Setting up buildings
    for index, row in buildingLocation.iterrows():
        # Calculate the center of each hex tile
        xOffset = (row['Hex1_X'] + row['Hex2_X'] + row['Hex3_X'])/3
        yOffset = (row['Hex1_Y'] + row['Hex2_Y'] + row['Hex3_Y'])/3
        xCenter = xBoardCenter + np.sqrt(3)/2 * radius * xOffset + gapSize * xOffset
        yCenter = yBoardCenter + 3/4 * radius * yOffset + gapSize * yOffset
        colonizer.canvas.create_text(
            xCenter, 
            yCenter, 
            text = "B:" + str(int(row['BuildingNum'])),
            font = ('Helvetica', 8)
        )
        
        
#%%        
BoardModule()
colonizer.mainloop()






