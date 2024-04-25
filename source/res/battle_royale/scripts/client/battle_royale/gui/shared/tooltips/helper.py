# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/shared/tooltips/helper.py
import typing
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.leaderboard_reward_tooltip_model import LeaderboardRewardTooltipModel
from battle_royale.gui.impl.gen.view_models.views.lobby.tooltips.reward_points_place_model import RewardPointsPlaceModel
from frameworks.wulf import Array
from frameworks.wulf.view.array import fillViewModelsArray, fillStringsArray
from gui.impl import backport
from gui.impl.gen import R
if typing.TYPE_CHECKING:
    from typing import List
    from battle_royale.gui.game_control.battle_royale_controller import BattleRoyaleProgressionPoints

def fillProgressionPointsTableModel(viewModel, progressionPointsList):
    gameModes, gameModeLists = progressionPointsList
    fillStringsArray(map(_getGameModeName, gameModes), viewModel.getBattleTypes())
    gameModeColLists = list()
    for points in gameModeLists:
        prevLevel = 1
        gameModeCellList = list()
        for point in points:
            gameModeCellList.append(_getRowPointsCell(point, prevLevel))
            prevLevel = point.lastInRange + 1

        gameModeColLists.append(gameModeCellList)

    battleModesArray = viewModel.getBattleModes()
    battleModesArray.clear()
    for colList in gameModeColLists:
        array = Array()
        fillViewModelsArray(colList, array)
        battleModesArray.addArray(array)

    battleModesArray.invalidate()


_brProgressionTooltip = R.strings.battle_royale.tooltip.progression.leaderboardReward

def _getGameModeName(gameMode):
    return backport.text(_brProgressionTooltip.battleTypesHeader.num(gameMode)())


def _setRangeLabel(points, prevLevel):
    numRange = (prevLevel, points.lastInRange)
    rangeTemplate = _brProgressionTooltip.text.places()
    if prevLevel == points.lastInRange:
        numRange = (points.lastInRange,)
        rangeTemplate = _brProgressionTooltip.text.place()
    return backport.text(rangeTemplate, place='-'.join(map(str, numRange)))


def _getRowPointsCell(points, prevLevel):
    cell = RewardPointsPlaceModel()
    cell.setPlace(_setRangeLabel(points, prevLevel))
    cell.setPoints(points.points)
    return cell
