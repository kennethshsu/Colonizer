import numpy as np
import os
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
        [selectedGameBoard.iloc[0, 1], -2, -4, 0],
        [selectedGameBoard.iloc[0, 2], 0, -4, 0],
        [selectedGameBoard.iloc[0, 3], 2, -4, 0],
        # Row 2
        [selectedGameBoard.iloc[0, 4], -3, -2, 0],
        [selectedGameBoard.iloc[0, 5], -1, -2, 0],
        [selectedGameBoard.iloc[0, 6], 1, -2, 0],
        [selectedGameBoard.iloc[0, 7], 3, -2, 0],
        # Row 3
        [selectedGameBoard.iloc[0, 8], -4, 0, 0],
        [selectedGameBoard.iloc[0, 9], -2, 0, 0],
        [selectedGameBoard.iloc[0, 10], 0, 0, 0],
        [selectedGameBoard.iloc[0, 11], 2, 0, 0],           
        [selectedGameBoard.iloc[0, 12], 4, 0, 0],
        # Row 4
        [selectedGameBoard.iloc[0, 13], -3, 2, 0],
        [selectedGameBoard.iloc[0, 14], -1, 2, 0],
        [selectedGameBoard.iloc[0, 15], 1, 2, 0],
        [selectedGameBoard.iloc[0, 16], 3, 2, 0],
        # Row 5
        [selectedGameBoard.iloc[0, 17], -2, 4, 0],
        [selectedGameBoard.iloc[0, 18], 0, 4, 0],
        [selectedGameBoard.iloc[0, 19], 2, 4, 0], 
    ],
    columns = ['hexResource', 'xHexOffset', 'yHexOffset', 'diceNumber']
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
        
        
#%%        
colonizer = Tk()
colonizer.title = 'Colonizer'
colonizer.canvas = Canvas(width = gameWindowWidth, height = gameWindowHeight)
colonizer.canvas.pack()

BoardModule()
colonizer.mainloop()






