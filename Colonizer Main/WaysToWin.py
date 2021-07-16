import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.pyplot import figure
pd.set_option("display.max_rows", 20, "display.max_columns", 20)

#%%
# https://www.boardgameanalysis.com/the-102-ways-to-win-at-catan-part-i/

#%%
# Ways to win
waysToWin = 0
winScenario = []

for longestRoad in range(1 + 1):
    for largestArmy in range(1 + 1):
        for victoryPoint in range(5 + 1):
            for settlement in range(5 + 1):
                for city in range(min(settlement, 4) + 1):
                    for newSettlement in range(city + 1):
                        totalScore = settlement + city + newSettlement + victoryPoint + longestRoad * 2 + largestArmy * 2
                        if (totalScore == 10 or (longestRoad == 1 and totalScore == 11) or (largestArmy == 1 and totalScore == 11)):
                            waysToWin += 1
# #                             print('ways to win: #', waysToWin, 'score:', totalScore)
# #                             print(
# #                                 'victory point:', victoryPoint,
# #                                 'longest road:', longestRoad*2,
# #                                 'largest army:', largestArmy*2,
# #                                 'settlement:', settlement - city + newSettlement,
# #                                 'city:', city
# #                             )
                            winScenarioText = str(
                                    longestRoad*10000
                                    + largestArmy*1000
                                    + victoryPoint*100
                                    + (settlement - city + newSettlement)*10
                                    + city
                                ).zfill(5)
                            winScenario.append(winScenarioText)
# Remove duplicated scenarios
winScenario = list(dict.fromkeys(winScenario))
print(winScenario)

#%%
winScenario = pd.DataFrame(winScenario, columns = ['Scenario'])
print(winScenario)

#%%
winScenario['LongestRoad'] = winScenario['Scenario'].astype(str).str[0].astype(int)
winScenario['LargestArmy'] = winScenario['Scenario'].astype(str).str[1].astype(int)
winScenario['VictoryPoint'] = winScenario['Scenario'].astype(str).str[2].astype(int)
winScenario['Settlement'] = winScenario['Scenario'].astype(str).str[3].astype(int)
winScenario['City'] = winScenario['Scenario'].astype(str).str[4].astype(int)
winScenario['TotalScore'] = (
    winScenario['VictoryPoint']
    + winScenario['LongestRoad']*2
    + winScenario['LargestArmy']*2
    + winScenario['Settlement']
    + winScenario['City']*2
)
winScenario = winScenario[(winScenario['TotalScore'] == 10) | (winScenario['TotalScore'] == 11)]
print(winScenario)

#%%
# Checking to see if anything is impossible, such as having less than 2 buildings
print(winScenario[(winScenario['Settlement'] + winScenario['City']) < 2])

#%%
# Removing scenario 51101, this is not possible, as at game start we would always have
winScenario = winScenario[~winScenario['Scenario'].isin(['11401', '11510', '11501'])]
print(winScenario.shape)

#%%
# There is a special scenario, where the player has the 2nd longest road, and places the final
# settlement to cut off the longest road holder and gain a final settlement and longest road, winning with 12 points
# This can happen when winning longestRoad = False (we don't have longest road yet) and 1 settlement or more
twelvePtsWinScenario = winScenario[(winScenario['LongestRoad'] == 0) & (winScenario['Settlement'] >= 1) & (winScenario['TotalScore'] == 10)]
twelvePtsWinScenario['LongestRoad'] = 1
twelvePtsWinScenario['TotalScore'] = (
    twelvePtsWinScenario['VictoryPoint']
    + twelvePtsWinScenario['LongestRoad']*2
    + twelvePtsWinScenario['LargestArmy']*2
    + twelvePtsWinScenario['Settlement']
    + twelvePtsWinScenario['City']*2
)
twelvePtsWinScenario['Scenario'] = (
    twelvePtsWinScenario['LongestRoad']*10000
    + twelvePtsWinScenario['LargestArmy']*1000
    + twelvePtsWinScenario['VictoryPoint']*100
    + twelvePtsWinScenario['Settlement']*10
    + twelvePtsWinScenario['City']
)
twelvePtsWinScenario['Scenario'] = twelvePtsWinScenario['Scenario'].astype(str)
print(twelvePtsWinScenario)

#%%
# There's another impossible scenario in the 12 points scenario, the 1 settlement and 1 city, since the settlement has
# already been built since the beginning of the game
twelvePtsWinScenario = twelvePtsWinScenario[twelvePtsWinScenario['Scenario'] != '11511']
print(twelvePtsWinScenario)

#%%
allWinScenario = winScenario.append(twelvePtsWinScenario)
allWinScenario = allWinScenario.reset_index(drop = True)
print(allWinScenario.shape)

#%%
print(allWinScenario)

#%%
allWinScenario = winScenario
allWinScenario['MinDevCard'] = allWinScenario['LargestArmy']*3 + allWinScenario['VictoryPoint']
allWinScenario['NumOfBuilding'] = allWinScenario['Settlement'] + allWinScenario['City']
print(allWinScenario)

#%%
max(allWinScenario['NumOfBuilding'])

#%%
allWinScenario[allWinScenario['NumOfBuilding'] == 7]

#%%
optimalRoads = pd.DataFrame(
    data = np.array([
        [2, 2, 5],
        [3, 3, 5],
        [4, 4, 6],
        [5, 5, 7],
        [6, 6, 8],
        [7, 8, 9]
    ]),
    columns = ['NumOfBuilding', 'Plain', 'LongestRoad']
)
optimalRoads

#%%
temp = allWinScenario.merge(optimalRoads, on = 'NumOfBuilding', how = 'left')
temp

#%%
temp['OptimalRoad'] = np.where((temp['LongestRoad_x'] == 0), temp['Plain'], temp['LongestRoad_y'])
temp

#%%
allWinScenario = temp
allWinScenario = allWinScenario.drop(columns = ['Plain', 'LongestRoad_y'])
allWinScenario = allWinScenario.rename(columns = {'LongestRoad_x': 'LongestRoad', 'OptimalRoad': 'MinRoad'})
allWinScenario

#%%
allWinScenario['MinWood'] = allWinScenario['MinRoad'] + allWinScenario['Settlement'] + allWinScenario['City']
allWinScenario['MinBrick'] = allWinScenario['MinRoad'] + allWinScenario['Settlement'] + allWinScenario['City']
allWinScenario['MinSheep'] = allWinScenario['Settlement'] + allWinScenario['MinDevCard'] + allWinScenario['City']
allWinScenario['MinWheat'] = allWinScenario['Settlement'] + allWinScenario['MinDevCard'] + allWinScenario['City']*2 + allWinScenario['City']
allWinScenario['MinRock'] = allWinScenario['MinDevCard'] + allWinScenario['City']*3
allWinScenario['MinTotal'] = allWinScenario['MinWood'] + allWinScenario['MinBrick'] + allWinScenario['MinSheep'] + allWinScenario['MinWheat'] + allWinScenario['MinRock']
allWinScenario

#%%
allWinScenario = allWinScenario.sort_values('MinTotal')
allWinScenario

#%%
figure(num=None, figsize=(12, 9), dpi=120, facecolor='w', edgecolor='k')
scenarioNum = allWinScenario.shape[0]
plt.bar(np.arange(scenarioNum), allWinScenario['MinWood'], color = '#11933B')
plt.bar(np.arange(scenarioNum), allWinScenario['MinBrick'], color = '#DC5539', bottom = allWinScenario['MinWood'])
plt.bar(np.arange(scenarioNum), allWinScenario['MinSheep'], color = '#9CBD29', bottom = allWinScenario['MinWood'] + allWinScenario['MinBrick'])
plt.bar(np.arange(scenarioNum), allWinScenario['MinWheat'], color = '#F2BA24', bottom = allWinScenario['MinWood'] + allWinScenario['MinBrick'] + allWinScenario['MinSheep'])
plt.bar(np.arange(scenarioNum), allWinScenario['MinRock'], color = '#9FA5A1', bottom = allWinScenario['MinWood'] + allWinScenario['MinBrick'] + allWinScenario['MinSheep'] + allWinScenario['MinWheat'])
plt.ylabel("Number of Total Resource Needed for the Scenario")
plt.xlabel("Scenario (Sorted by the Number of Resource Needed)")

colors = {
    'Rock': '#9FA5A1',
    'Wheat': '#F2BA24',
    'Sheep': '#9CBD29',
    'Brick': '#DC5539',
    'Lumber': '#11933B',
}
labels = list(colors.keys())
handles = [plt.Rectangle((0,0),1,1, color=colors[label]) for label in labels]
plt.legend(handles, labels)

#%%
allWinScenario[allWinScenario['VictoryPoint'] == 0]
