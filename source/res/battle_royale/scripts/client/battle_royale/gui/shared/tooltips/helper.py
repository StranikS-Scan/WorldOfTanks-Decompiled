# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/tooltips/helper.py
from functools import partial
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.reward_points_place_model import RewardPointsPlaceModel
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray, fillStringsArray
from gui.impl import backport
from gui.impl.gen import R
_string = R.strings.battle_royale.tooltip.progression.leaderboardReward

def fillProgressionPointsTableModel(viewModel, progressionPointsList, headerResource=_string):
    gameModes, gameModeLists = progressionPointsList
    fillStringsArray(map(partial(_getGameModeName, headerResource), gameModes), viewModel.getBattleTypes())
    gameModeColLists = list()
    for points in gameModeLists:
        prevLevel = 1
        gameModeCellList = list()
        for point in points:
            gameModeCellList.append(_getRowPointsCell(point, prevLevel, headerResource))
            prevLevel = point.lastInRange + 1

        gameModeColLists.append(gameModeCellList)

    battleModesArray = viewModel.getBattleModes()
    battleModesArray.clear()
    for colList in gameModeColLists:
        array = Array()
        fillViewModelsArray(colList, array)
        battleModesArray.addArray(array)

    battleModesArray.invalidate()


def _getGameModeName(headerResource, gameMode):
    return backport.text(headerResource.battleTypesHeader.num(gameMode)())


def _setRangeLabel(points, prevLevel, headerResource):
    numRange = (prevLevel, points.lastInRange)
    rangeTemplate = headerResource.text.places()
    if prevLevel == points.lastInRange:
        numRange = (points.lastInRange,)
        rangeTemplate = headerResource.text.place()
    return backport.text(rangeTemplate, place='-'.join(map(str, numRange)))


def _getRowPointsCell(points, prevLevel, headerResource):
    cell = RewardPointsPlaceModel()
    cell.setPlace(_setRangeLabel(points, prevLevel, headerResource))
    cell.setPoints(points.points)
    return cell
