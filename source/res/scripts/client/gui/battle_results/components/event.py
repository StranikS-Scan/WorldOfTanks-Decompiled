# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/event.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.EVENT import EVENT
from helpers import dependency
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_results.reusable import sort_keys
from gui.battle_results.components import base
from gui.battle_results.components import vehicles
from gui.server_events.awards_formatters import getEventAwardFormatter
from gui.battle_results.settings import PLAYER_TEAM_RESULT as _TEAM_RESULT
from skeletons.gui.game_event_controller import IGameEventController
from helpers.i18n import makeString as _ms

class EventStatsItem(base.StatsItem):
    gameEventController = dependency.descriptor(IGameEventController)

    def _getGeneral(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return self.gameEventController.getGeneral(info.generalID)

    def _getFront(self, result, reusable):
        general = self._getGeneral(result, reusable)
        return self.gameEventController.getFront(general.getFrontID())

    def _getBonusFormatted(self, result, reusable):
        general = self._getGeneral(result, reusable)
        front = self.gameEventController.getFronts().get(general.getFrontID())
        if front is None:
            return
        else:
            item = front.items[-1]
            return None if item is None else getEventAwardFormatter().format(item.getBonuses())[0]

    def _getMyPosition(self, result, reusable):
        isWin = reusable.getPersonalTeamResult() == _TEAM_RESULT.WIN
        battleResultsInfo = self.gameEventController.getBattleResultsInfo()
        rewardInfo = battleResultsInfo.getWinPoints() if isWin else battleResultsInfo.getLosePoints()
        info = reusable.getPersonalVehiclesInfo(result)
        return next((index for index, value in enumerate(rewardInfo) if value == info.generalPoints), 0)


class IsVictory(base.StatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        return reusable.getPersonalTeamResult() == _TEAM_RESULT.WIN


class EventVehicleStatsBlock(vehicles.RegularVehicleStatsBlock):
    gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ('generalIcon', 'levelIcon', 'tooltipData', 'status', 'inactive', 'background', 'position', 'reward')

    def _setTotalStats(self, result, noPenalties):
        super(EventVehicleStatsBlock, self)._setTotalStats(result, noPenalties)
        if result.avatar is None:
            return
        else:
            self.inactive = not noPenalties
            self.status = ''
            penaltyName = result.avatar.getPenaltyName()
            if not noPenalties and penaltyName:
                self.status = _ms({'afk': EVENT.BATTLE_RESULT_HASPENALTY_AFK,
                 'deserter': EVENT.BATTLE_RESULT_HASPENALTY_DESERTER}[penaltyName])
            return

    def setRecord(self, result, reusable):
        super(EventVehicleStatsBlock, self).setRecord(result, reusable)
        battleResultsInfo = self.gameEventController.getBattleResultsInfo()
        isWin = reusable.getPersonalTeamResult() == _TEAM_RESULT.WIN
        rewardInfo = battleResultsInfo.getWinPoints() if isWin else battleResultsInfo.getLosePoints()
        general = self.gameEventController.getGeneral(result.generalID)
        self.generalIcon = RES_ICONS.getGeneralIconInHangar(general.getID())
        self.levelIcon = RES_ICONS.getGeneralLevelIcon(result.generalLevel)
        self.background = RES_ICONS.getGeneralBackground(result.generalID)
        self.position = self.vehicleSort
        rewardValue = rewardInfo[self.position] if self.position < len(rewardInfo) else 0
        self.reward = '+{}'.format(rewardValue)
        self.tooltipData = {'tooltip': '',
         'specialArgs': [result.generalID,
                         rewardValue,
                         result.damageDealt,
                         isWin,
                         self.position + 1],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_FACTION_INFO_WIN_SCREEN,
         'isSpecial': True}


class PersonalFirstTeamItemSortKey(sort_keys.TeamItemSortKey):
    __slots__ = ('_sortKey',)

    def __init__(self, vehicleInfo, compareKey):
        super(PersonalFirstTeamItemSortKey, self).__init__(vehicleInfo)
        self._sortKey = compareKey

    def _cmp(self, other):
        sortKey = self._sortKey
        return cmp(getattr(other.info, sortKey), getattr(self.info, sortKey))


class EventBattlesTeamStatsBlock(vehicles.TeamStatsBlock):
    gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ()

    def __init__(self, meta=None, field='', *path):
        super(EventBattlesTeamStatsBlock, self).__init__(EventVehicleStatsBlock, meta, field, *path)

    def setRecord(self, result, reusable):
        sortKey = self.gameEventController.getBattleResultsInfo().getBattleResultsKey()
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sortKey=lambda info: PersonalFirstTeamItemSortKey(info, sortKey))
        super(EventBattlesTeamStatsBlock, self).setRecord(allies, reusable)


class EventPoints(base.StatsItem):

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.eventPoints


class GeneralPoints(EventStatsItem):

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return info.generalPoints


class FrontText(EventStatsItem):

    def _convert(self, result, reusable):
        general = self._getGeneral(result, reusable)
        return EVENT.getFrontName(general.getFrontID())


class GeneralText(EventStatsItem):

    def _convert(self, result, reusable):
        info = reusable.getPersonalVehiclesInfo(result)
        return EVENT.getGeneralProgressName(info.generalID)


class GeneralTooltip(EventStatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        isWin = reusable.getPersonalTeamResult() == _TEAM_RESULT.WIN
        info = reusable.getPersonalVehiclesInfo(result)
        position = self._getMyPosition(result, reusable)
        return {'tooltip': '',
         'specialArgs': [info.generalID,
                         info.generalPoints,
                         info.damageDealt,
                         isWin,
                         position + 1],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_FACTION_INFO_WIN_SCREEN,
         'isSpecial': True}


class FrontTooltip(EventStatsItem):
    __slots__ = ()

    def _convert(self, result, reusable):
        front = self._getFront(result, reusable)
        points = reusable.getPersonalVehiclesInfo(result).eventPoints
        return {'tooltip': '',
         'specialArgs': [front.getID(), points],
         'specialAlias': TOOLTIPS_CONSTANTS.EVENT_FRONT_INFO,
         'isSpecial': True}
