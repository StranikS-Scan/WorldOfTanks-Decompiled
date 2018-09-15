# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/common.py
import BigWorld
from constants import ARENA_GUI_TYPE, FINISH_REASON
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_results.components import base
from gui.battle_results.components import style
from gui.battle_results.settings import PLAYER_TEAM_RESULT as _TEAM_RESULT, UI_VISIBILITY
from gui.ranked_battles.ranked_models import RANK_CHANGE_STATES
from gui.battle_results.reusable import sort_keys
from skeletons.gui.game_control import IRankedBattlesController
from helpers import i18n, dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import WinStatus
_ARENA_TYPE_FORMAT = '#arenas:type/{0}/name'
_ARENA_TYPE_EXT_FORMAT = '#menu:loading/battleTypes/{0}'
_ARENA_FULL_NAME_FORMAT = '{0} - {1}'
_ARENA_ICON_PATH = '../maps/icons/map/stats/%s.png'
_FULL_RESULT_LABEL = '#menu:finalStatistic/commonStats/resultlabel/{0}'
_FINISH_REASON_LABEL = '#battle_results:finish/reason/{0}'
_FALLOUT_RESULT_LABEL = '#battle_results:fallout/{submode}/{status}'
_STEP_EARNED = 1
_STEP_NOT_CHANGED = 0
_STEP_LOST = -1

def makeArenaFullName(arenaTypeName, i18nKey):
    """Returns i18n string containing full name of arena.
    :param arenaTypeName: string containing name of arena.
    :param i18nKey: string containing i18n key.
    :return: i18n string.
    """
    return _ARENA_FULL_NAME_FORMAT.format(i18n.makeString(arenaTypeName), i18n.makeString(i18nKey))


def makeRegularFinishResultLabel(finishReason, teamResult):
    """Returns i18n string describing finish reason of regular battle.
    :param finishReason: integer containing one of FINISH_REASON.*.
    :param teamResult: string containing one of PLAYER_TEAM_RESULT.*.
    :return: i18n string.
    """
    return i18n.makeString(_FINISH_REASON_LABEL.format(''.join((str(finishReason), str(teamResult))))) if finishReason == FINISH_REASON.EXTERMINATION else i18n.makeString(_FINISH_REASON_LABEL.format(finishReason))


class RankInfoHelper(object):
    """
    Helper class for filling RankChangesBlock.
    """
    rankedController = dependency.descriptor(IRankedBattlesController)
    __TITLE_LABEL_MAP = {(RANK_CHANGE_STATES.RANK_EARNED, True): RANKED_BATTLES.BATTLERESULT_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_EARNED, False): RANKED_BATTLES.BATTLERESULT_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_LOST, True): RANKED_BATTLES.BATTLERESULT_RANKLOST,
     (RANK_CHANGE_STATES.RANK_LOST, False): RANKED_BATTLES.BATTLERESULT_RANKLOST,
     (RANK_CHANGE_STATES.STEP_EARNED, True): RANKED_BATTLES.BATTLERESULT_STAGEEARNED,
     (RANK_CHANGE_STATES.STEP_EARNED, False): RANKED_BATTLES.BATTLERESULT_STAGEEARNED,
     (RANK_CHANGE_STATES.STEP_LOST, True): RANKED_BATTLES.BATTLERESULT_STAGELOST,
     (RANK_CHANGE_STATES.STEP_LOST, False): RANKED_BATTLES.BATTLERESULT_STAGELOST,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, True): RANKED_BATTLES.BATTLERESULT_STAGENOTEARNED,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, False): RANKED_BATTLES.BATTLERESULT_STAGESAVED}
    __TOP_ICON_MAP = {RANK_CHANGE_STATES.RANK_EARNED: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.RANK_LOST: RES_ICONS.getRankedPostBattleLoseIcon,
     RANK_CHANGE_STATES.STEP_EARNED: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.STEP_LOST: RES_ICONS.getRankedPostBattleLoseIcon,
     RANK_CHANGE_STATES.NOTHING_CHANGED: RES_ICONS.getRankedPostBattleNotEffectiveIcon}
    __RANK_ICON_MAP = {RANK_CHANGE_STATES.RANK_EARNED: ('', RES_ICONS.getRankIcon),
     RANK_CHANGE_STATES.RANK_LOST: ('_grey', RES_ICONS.getRankIcon),
     RANK_CHANGE_STATES.STEP_EARNED: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_GREEN_94X120),
     RANK_CHANGE_STATES.STEP_LOST: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_RED_94X120),
     RANK_CHANGE_STATES.NOTHING_CHANGED: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_GREY_94X120)}
    __RESOURCE_MAP = {_STEP_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RES_ICONS.getRankedPostBattleTopIcon),
     _STEP_NOT_CHANGED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, RES_ICONS.getRankedPostBattleNotEffectiveIcon),
     _STEP_LOST: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, RES_ICONS.getRankedPostBattleLoseIcon)}
    _STANDOFF_INVISIBLE = 0
    _STANDOFF_PLUS = 1
    _STANDOFF_MINUS = 2
    _STANDOFF_CROSS = 3

    def __init__(self, reusable):
        self.__reusable = reusable

    def getState(self):
        """
        Return a state, describing changes: is it rank or step changes.
        :return: one from self.STATES
        """
        return self.rankedController.getRankChangeStatus(self.__reusable.personal.getRankInfo())

    def makeSubTaskState(self):
        """
        Returns 'state' field for RankChangesBlock
        :return: string, one from RANKED_BATTLES constants
        """
        if self.getState() in (RANK_CHANGE_STATES.RANK_EARNED, RANK_CHANGE_STATES.RANK_LOST):
            isMaster = self.__getRankAfterBattle() > self.rankedController.getAccRanksTotal()
            if isMaster:
                return RANKEDBATTLES_ALIASES.SUBTASK_STATE_MASTER
            return RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK
        return RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE

    def makeTitleLabel(self):
        """
        Returns 'title' field for RankChangesBlock
        :return: string, one from RANKED_BATTLES constants
        """
        isWin = self.__reusable.getPersonalTeam() == self.__reusable.common.winnerTeam
        return self.__TITLE_LABEL_MAP[self.getState(), isWin]

    def makeDescriptionLabel(self, allyVehicles):
        """
        Returns 'description' field for RankChangesBlock
        :return: string, one from RANKED_BATTLES constants
        """
        state = self.getState()
        isWin = self.__reusable.getPersonalTeam() == self.__reusable.common.winnerTeam
        accountDBID = self.__reusable.personal.avatar.accountDBID
        topNumber = self.__getTopBoundForPersonalTeam()
        selfXp = None
        for item in allyVehicles:
            if item.player.dbID == accountDBID:
                selfXp = item.xp
                break

        if len(allyVehicles) <= topNumber or topNumber <= 0 or selfXp is None:
            isInTop = True
        else:
            topMinXp = min([ item.xp for item in allyVehicles[:topNumber] ])
            isInTop = selfXp >= topMinXp
        if selfXp is not None and selfXp < self.getMinXp():
            resKey = RANKED_BATTLES.BATTLERESULT_NOTINTOP_MINXP
        elif not isWin and isInTop and state == RANK_CHANGE_STATES.NOTHING_CHANGED:
            resKey = RANKED_BATTLES.BATTLERESULT_NOTINTOP_STAGESAVED
        else:
            method = RANKED_BATTLES.getBattleResultsInTop if isInTop else RANKED_BATTLES.getBattleResultsNotInTop
            resKey = method('win') if isWin else method('lose')
        return i18n.makeString(resKey).format(topNumber=topNumber)

    def makeTopIcon(self):
        """
        Returns 'topIcon' field for RankChangesBlock
        :return: string, one from RES_ICONS constants
        """
        topIconMethod = self.__TOP_ICON_MAP[self.getState()]
        return topIconMethod(self.__getTopBoundForPersonalTeam())

    def makeRankIcon(self):
        """
        Returns 'rankIcon' field for RankChangesBlock
        :return: string, one from RES_ICONS constants
        """
        suffix, resource = self.__RANK_ICON_MAP[self.getState()]
        if suffix is not None:
            rankAfterBattle = self.__getRankAfterBattle()
            isMaster = rankAfterBattle > self.rankedController.getAccRanksTotal()
            val = 'VehMaster{}'.format(suffix) if isMaster else '{}{}'.format(rankAfterBattle, suffix)
            return resource('58x80', val)
        else:
            return resource

    def getTopBoundForTeam(self, team):
        """
        Returns a top bound for the team(integer value) depending on battle result.
        For example: Win - TOP_12, Lose - TOP_3
        :param team: team index
        """
        return self.getWinnerBounds(isTop=True) if self.__reusable.common.winnerTeam == team else self.getLoserBounds(isTop=True)

    def getPlayerNumber(self):
        return len(self.rankedController.getRanksChanges(isLoser=False))

    def getWinnerBounds(self, isTop):
        winnerRankChanges = self.rankedController.getRanksChanges(isLoser=False)
        bounds, _ = self.__getRankBounds(winnerRankChanges, isTop)
        return bounds

    def getLoserBounds(self, isTop):
        loserRankChanges = self.rankedController.getRanksChanges(isLoser=True)
        bounds, _ = self.__getRankBounds(loserRankChanges, isTop)
        return bounds

    def getMinXp(self):
        return self.rankedController.getMinXp()

    def getStandoff(self, isTop, xp, xpToCompare, team):
        if isTop:
            standoff = self._STANDOFF_INVISIBLE if xp >= xpToCompare else self._STANDOFF_MINUS
        else:
            isLoser = self.__reusable.common.winnerTeam != team
            rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
            if rankChanges and rankChanges[0] == 0 and xp == xpToCompare:
                standoff = self._STANDOFF_CROSS
            elif xp == xpToCompare and xp >= self.getMinXp():
                standoff = self._STANDOFF_PLUS
            else:
                standoff = self._STANDOFF_INVISIBLE
        return standoff

    def getCapacityWithResources(self, isLoser, isTopList):
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        capacity, resources = self.__getRankBounds(rankChanges, isTopList)
        backgroundType, iconMethod = resources
        icon = iconMethod(capacity) if isTopList else ''
        return (capacity, icon, backgroundType)

    def __getRankBounds(self, rankChanges, isTop):
        earned = rankChanges.count(_STEP_EARNED)
        notChanged = rankChanges.count(_STEP_NOT_CHANGED)
        lost = rankChanges.count(_STEP_LOST)
        if not earned:
            top, bottom = notChanged, lost
            resources = (self.__RESOURCE_MAP[_STEP_NOT_CHANGED], self.__RESOURCE_MAP[_STEP_LOST])
        elif not notChanged:
            top, bottom = earned, lost
            resources = (self.__RESOURCE_MAP[_STEP_EARNED], self.__RESOURCE_MAP[_STEP_LOST])
        else:
            top, bottom = earned, notChanged
            resources = (self.__RESOURCE_MAP[_STEP_EARNED], self.__RESOURCE_MAP[_STEP_NOT_CHANGED])
        return (top, resources[0]) if isTop else (bottom, resources[1])

    def __getTopBoundForPersonalTeam(self):
        """
        Returns a top bound for self team(integer value) depending on battle result.
        """
        return self.getTopBoundForTeam(self.__reusable.getPersonalTeam())

    def __getRankAfterBattle(self):
        """
        Computes the rank after battle,
        considering losing rank (show the previous as this rank + 1) and 'Master' rank
        :return: int, containing the rank number,
                 the value > rankedController.getAccRanksTotal() means 'Master' rank
        """
        rankInfo = self.__reusable.personal.getRankInfo()
        rankAfterBattle = rankInfo.accRank
        if rankAfterBattle == self.rankedController.getAccRanksTotal() and rankInfo.vehRank > 0:
            rankAfterBattle += 1
        if self.getState() == RANK_CHANGE_STATES.RANK_LOST:
            rankAfterBattle += 1
        return rankAfterBattle


class ArenaShortTimeVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return style.makeTimeStatsVO(self._field, BigWorld.wg_getShortTimeFormat(record))


class ArenaDateTimeItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return ' '.join((BigWorld.wg_getShortDateFormat(record), BigWorld.wg_getShortTimeFormat(record)))


class RegularArenaFullNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        arenaGuiType = reusable.common.arenaGuiType
        arenaType = reusable.common.arenaType
        if arenaGuiType in (ARENA_GUI_TYPE.RANDOM, ARENA_GUI_TYPE.EPIC_RANDOM):
            i18nKey = _ARENA_TYPE_FORMAT.format(arenaType.getGamePlayName())
        else:
            i18nKey = _ARENA_TYPE_EXT_FORMAT.format(arenaGuiType)
        return makeArenaFullName(arenaType.getName(), i18nKey)


class FalloutArenaFullNameItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        common = reusable.common
        arenaType = common.arenaType
        i18nKey = _ARENA_TYPE_EXT_FORMAT.format(common.arenaGuiType)
        if common.hasResourcePoints:
            i18nKey += '/resource'
        elif common.isMultiTeamMode:
            i18nKey += '/multiteam'
        return makeArenaFullName(arenaType.getName(), i18nKey)


class ArenaIconItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return reusable.common.getArenaIcon(_ARENA_ICON_PATH)


class ArenaDurationItem(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record:
            converted = i18n.makeString(BATTLE_RESULTS.DETAILS_TIME_VALUE, int(record / 60), int(record % 60))
        else:
            converted = None
        return converted


class ArenaDurationVO(ArenaDurationItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        return style.makeTimeStatsVO(self._field, super(ArenaDurationVO, self)._convert(record, reusable))


class PlayerKillingTimeVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        info = reusable.personal.getLifeTimeInfo()
        if info.isKilled:
            minutes = int(info.lifeTime / 60)
            seconds = int(info.lifeTime % 60)
            converted = i18n.makeString(BATTLE_RESULTS.DETAILS_TIME_VALUE, minutes, seconds)
        else:
            converted = '-'
        return style.makeTimeStatsVO(self._field, converted)


class FinishResultMeta(base.DictMeta):
    __slots__ = ()

    def __init__(self, finishReasonLabel, shortResultLabel, fullResultLabel):
        meta = {finishReasonLabel: '',
         shortResultLabel: '',
         fullResultLabel: ''}
        auto = ((0, base.StatsItem(finishReasonLabel, 'finishReasonLabel')), (1, base.StatsItem(shortResultLabel, 'shortResultLabel')), (2, base.StatsItem(fullResultLabel, 'fullResultLabel')))
        super(FinishResultMeta, self).__init__(meta, auto)


class RegularFinishResultBlock(base.StatsBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')

    def __init__(self, meta=None, field='', *path):
        super(RegularFinishResultBlock, self).__init__(meta, field, *path)
        self.finishReasonLabel = None
        self.shortResultLabel = None
        self.fullResultLabel = None
        return

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        self.finishReasonLabel = makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = _FULL_RESULT_LABEL.format(teamResult)


class FalloutFinishResultBlock(RegularFinishResultBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        finishReason = reusable.common.finishReason
        if reusable.common.isMultiTeamMode:
            if teamResult in (_TEAM_RESULT.DEFEAT, _TEAM_RESULT.DRAW):
                teamResult = _TEAM_RESULT.ENDED
            falloutSubMode = 'multiteam'
        else:
            falloutSubMode = 'classic'
        resultTemplate = _FALLOUT_RESULT_LABEL.format(submode=falloutSubMode, status=teamResult)
        if teamResult not in (_TEAM_RESULT.DRAW, _TEAM_RESULT.ENDED):
            finishReasonStr = 'points'
            if finishReason == FINISH_REASON.WIN_POINTS_CAP:
                finishReasonStr = 'cap'
            elif finishReason == FINISH_REASON.EXTERMINATION:
                finishReasonStr = 'extermination'
            resultTemplate += '/' + finishReasonStr
        self.finishReasonLabel = i18n.makeString(resultTemplate)
        self.shortResultLabel = teamResult
        self.fullResultLabel = _FULL_RESULT_LABEL.format(teamResult)


class StrongholdBattleFinishResultBlock(RegularFinishResultBlock):
    __slots__ = ('finishReasonLabel', 'shortResultLabel', 'fullResultLabel')
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def setRecord(self, result, reusable):
        teamResult = reusable.getPersonalTeamResult()
        team = reusable.getPersonalTeam()
        winnerIfDraw = reusable.personal.avatar.winnerIfDraw
        if teamResult == _TEAM_RESULT.DRAW and winnerIfDraw:
            if team == winnerIfDraw:
                teamResult = _TEAM_RESULT.WIN
                winStatus = WinStatus.WIN
            else:
                teamResult = _TEAM_RESULT.DEFEAT
                winStatus = WinStatus.LOSE
            sessionCtx = self.sessionProvider.getCtx()
            if sessionCtx.extractLastArenaWinStatus() is not None:
                sessionCtx.setLastArenaWinStatus(WinStatus(winStatus))
        self.finishReasonLabel = makeRegularFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = _FULL_RESULT_LABEL.format(teamResult)
        return


class AllyTeamClanTitle(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return '{} [{}]'.format(BATTLE_RESULTS.TEAM_STATS_OWNTEAM, reusable.players.getFirstAllyClan(reusable.getPersonalTeam()).clanAbbrev)


class EnemyTeamClanTitle(base.StatsItem):
    __slots__ = ()

    def _convert(self, value, reusable):
        return '{} [{}]'.format(BATTLE_RESULTS.TEAM_STATS_ENEMYTEAM, reusable.players.getFirstEnemyClan(reusable.getPersonalTeam()).clanAbbrev)


class ClanInfoBlock(base.StatsBlock):
    __slots__ = ('clanDBID', 'clanAbbrev')

    def __init__(self, meta=None, field='', *path):
        super(ClanInfoBlock, self).__init__(meta, field, *path)
        self.clanDBID = None
        self.clanAbbrev = None
        return

    def setRecord(self, record, reusable):
        if record is not None:
            self.clanDBID = record.clanDBID
            self.clanAbbrev = '[{}]'.format(record.clanAbbrev)
        return


class ClansInfoBlock(base.StatsBlock):
    __slots__ = ('allies', 'enemies')

    def __init__(self, meta=None, field='', *path):
        super(ClansInfoBlock, self).__init__(meta, field, *path)
        self.allies = None
        self.enemies = None
        return

    def setRecord(self, record, reusable):
        team = reusable.getPersonalTeam()
        players = reusable.players
        self.allies = players.getFirstAllyClan(team)
        self.enemies = players.getFirstEnemyClan(team)


class RankChangesBlock(base.StatsBlock):
    __slots__ = ('state', 'linkage', 'title', 'description', 'topIcon', 'rankIcon')

    def __init__(self, meta=None, field='', *path):
        super(RankChangesBlock, self).__init__(meta, field, *path)
        self.state = None
        self.linkage = None
        self.title = None
        self.description = None
        self.topIcon = None
        self.rankIcon = None
        return

    def setRecord(self, result, reusable):
        helper = RankInfoHelper(reusable)
        self.state = helper.makeSubTaskState()
        self.topIcon = helper.makeTopIcon()
        self.rankIcon = helper.makeRankIcon()
        self.linkage = RANKEDBATTLES_ALIASES.BATTLE_RESULTS_SUB_TASK_UI
        self.title = helper.makeTitleLabel()
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sort_keys.VehicleXpSortKey)
        self.description = helper.makeDescriptionLabel(list(allies))


class RankedResultsBlockTitle(base.StatsItem):

    def _convert(self, value, reusable):
        helper = RankInfoHelper(reusable)
        return style.makeRankedResultsTitle(helper.makeTitleLabel())


class TeamsUiVisibility(base.StatsItem):

    def _convert(self, value, reusable):
        ui_visibility = 0
        if reusable.isSquadSupported:
            ui_visibility |= UI_VISIBILITY.SHOW_SQUAD
        return ui_visibility


class EligibleForCrystalRewards(base.StatsItem):

    def _convert(self, value, reusable):
        return reusable.personal.avatar.eligibleForCrystalRewards


class SortieTeamsUiVisibility(TeamsUiVisibility):

    def _convert(self, value, reusable):
        ui_visibility = super(SortieTeamsUiVisibility, self)._convert(value, reusable)
        ui_visibility |= UI_VISIBILITY.SHOW_RESOURCES
        return ui_visibility
