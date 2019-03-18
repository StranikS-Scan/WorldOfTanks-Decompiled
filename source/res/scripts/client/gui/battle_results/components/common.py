# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/common.py
import BigWorld
from constants import ARENA_GUI_TYPE, FINISH_REASON
from account_helpers.AccountSettings import AccountSettings, ENABLE_RANKED_ANIMATIONS
from gui.Scaleform.locale.BATTLE_RESULTS import BATTLE_RESULTS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_results.components import base
from gui.battle_results.components import style
from gui.battle_results.settings import PLAYER_TEAM_RESULT as _TEAM_RESULT, UI_VISIBILITY
from gui.ranked_battles.ranked_models import RANK_CHANGE_STATES
from gui.battle_results.reusable import sort_keys
from gui.shared.formatters import text_styles
from gui.shared.utils import toUpper
from skeletons.gui.game_control import IRankedBattlesController
from helpers import i18n, dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import WinStatus
_ARENA_TYPE_FORMAT = '#arenas:type/{0}/name'
_ARENA_TYPE_EXT_FORMAT = '#menu:loading/battleTypes/{0}'
_ARENA_FULL_NAME_FORMAT = '#battle_results:common/arena/fullName'
_ARENA_ICON_PATH = '../maps/icons/map/stats/%s.png'
_FULL_RESULT_LABEL = '#menu:finalStatistic/commonStats/resultlabel/{0}'
_FINISH_REASON_LABEL = '#battle_results:finish/reason/{0}'
_FINISH_PLAYER_TANK_SEPARATOR = '#battle_results:finish/playerTank/separator'
_STEPS_EARNED = 2
_STEP_EARNED = 1
_STEP_NOT_CHANGED = 0
_STEP_LOST = -1

def makeArenaFullName(arenaTypeName, i18nKey):
    arenaFullName = i18n.makeString(_ARENA_FULL_NAME_FORMAT)
    return arenaFullName.format(i18n.makeString(arenaTypeName), i18n.makeString(i18nKey))


def makeRegularFinishResultLabel(finishReason, teamResult):
    return i18n.makeString(_FINISH_REASON_LABEL.format(''.join((str(finishReason), str(teamResult))))) if finishReason == FINISH_REASON.EXTERMINATION else i18n.makeString(_FINISH_REASON_LABEL.format(finishReason))


def makeEpicBattleFinishResultLabel(finishReason, teamResult):
    if finishReason is FINISH_REASON.TIMEOUT:
        finishReason = FINISH_REASON.DESTROYED_OBJECTS
        teamResult = _TEAM_RESULT.DEFEAT
    elif finishReason is FINISH_REASON.DESTROYED_OBJECTS:
        teamResult = _TEAM_RESULT.WIN
    return i18n.makeString(_FINISH_REASON_LABEL.format(''.join((str(finishReason), str(teamResult))))) if finishReason in {FINISH_REASON.EXTERMINATION, FINISH_REASON.TIMEOUT, FINISH_REASON.DESTROYED_OBJECTS} else i18n.makeString(_FINISH_REASON_LABEL.format(finishReason))


class RankInfoHelper(object):
    rankedController = dependency.descriptor(IRankedBattlesController)
    __TITLE_LABEL_MAP = {(RANK_CHANGE_STATES.RANK_EARNED, True): RANKED_BATTLES.BATTLERESULT_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_EARNED, False): RANKED_BATTLES.BATTLERESULT_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_LOST, True): RANKED_BATTLES.BATTLERESULT_RANKLOST,
     (RANK_CHANGE_STATES.RANK_LOST, False): RANKED_BATTLES.BATTLERESULT_RANKLOST,
     (RANK_CHANGE_STATES.STEP_EARNED, True): RANKED_BATTLES.BATTLERESULT_STAGEEARNED,
     (RANK_CHANGE_STATES.STEP_EARNED, False): RANKED_BATTLES.BATTLERESULT_STAGEEARNED,
     (RANK_CHANGE_STATES.STEPS_EARNED, True): RANKED_BATTLES.BATTLERESULT_STAGESEARNED,
     (RANK_CHANGE_STATES.STEPS_EARNED, False): RANKED_BATTLES.BATTLERESULT_STAGESEARNED,
     (RANK_CHANGE_STATES.STEP_LOST, True): RANKED_BATTLES.BATTLERESULT_STAGELOST,
     (RANK_CHANGE_STATES.STEP_LOST, False): RANKED_BATTLES.BATTLERESULT_STAGELOST,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, True): RANKED_BATTLES.BATTLERESULT_STAGENOTEARNED,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, False): RANKED_BATTLES.BATTLERESULT_STAGESAVED,
     (RANKEDBATTLES_ALIASES.SHIELD_LOSE, True): RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDLOSE,
     (RANKEDBATTLES_ALIASES.SHIELD_LOSE, False): RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDLOSE,
     (RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP, True): RANKED_BATTLES.BATTLERESULT_SHIELDLOSE,
     (RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP, False): RANKED_BATTLES.BATTLERESULT_SHIELDLOSE,
     (RANK_CHANGE_STATES.RANK_POINT, True): RANKED_BATTLES.BATTLERESULT_STATUS_RANKPOINT,
     (RANK_CHANGE_STATES.RANK_POINT, False): RANKED_BATTLES.BATTLERESULT_STATUS_RANKPOINT}
    __STATUS_LABEL_MAP = {(RANK_CHANGE_STATES.RANK_EARNED, True): RANKED_BATTLES.BATTLERESULT_STATUS_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_EARNED, False): RANKED_BATTLES.BATTLERESULT_STATUS_RANKEARNED,
     (RANK_CHANGE_STATES.RANK_LOST, True): RANKED_BATTLES.BATTLERESULT_STATUS_RANKLOST,
     (RANK_CHANGE_STATES.RANK_LOST, False): RANKED_BATTLES.BATTLERESULT_STATUS_RANKLOST,
     (RANK_CHANGE_STATES.STEP_EARNED, True): RANKED_BATTLES.BATTLERESULT_STATUS_STAGEEARNED,
     (RANK_CHANGE_STATES.STEP_EARNED, False): RANKED_BATTLES.BATTLERESULT_STATUS_STAGEEARNED,
     (RANK_CHANGE_STATES.STEPS_EARNED, True): RANKED_BATTLES.BATTLERESULT_STATUS_STAGESEARNED,
     (RANK_CHANGE_STATES.STEPS_EARNED, False): RANKED_BATTLES.BATTLERESULT_STATUS_STAGESEARNED,
     (RANK_CHANGE_STATES.STEP_LOST, True): RANKED_BATTLES.BATTLERESULT_STATUS_STAGELOST,
     (RANK_CHANGE_STATES.STEP_LOST, False): RANKED_BATTLES.BATTLERESULT_STATUS_STAGELOST,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, True): RANKED_BATTLES.BATTLERESULT_STATUS_STAGENOTEARNED,
     (RANK_CHANGE_STATES.NOTHING_CHANGED, False): RANKED_BATTLES.BATTLERESULT_STATUS_STAGESAVED,
     (RANK_CHANGE_STATES.RANK_POINT, True): RANKED_BATTLES.BATTLERESULT_STATUS_RANKPOINT,
     (RANK_CHANGE_STATES.RANK_POINT, False): RANKED_BATTLES.BATTLERESULT_STATUS_RANKPOINT}
    __SHIELD_STATES = (RANKEDBATTLES_ALIASES.SHIELD_LOSE, RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP)
    __WITH_SHIELD_STATES = {RANK_CHANGE_STATES.NOTHING_CHANGED, RANK_CHANGE_STATES.RANK_EARNED}
    __RESULTS_WITH_SHIELDS = {RANK_CHANGE_STATES.NOTHING_CHANGED,
     RANK_CHANGE_STATES.RANK_EARNED,
     RANK_CHANGE_STATES.STEP_EARNED,
     RANK_CHANGE_STATES.STEPS_EARNED}
    __TOP_ICON_MAP = {RANK_CHANGE_STATES.RANK_EARNED: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.RANK_POINT: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.RANK_LOST: RES_ICONS.getRankedPostBattleLoseIcon,
     RANK_CHANGE_STATES.STEP_EARNED: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.STEPS_EARNED: RES_ICONS.getRankedPostBattleTopIcon,
     RANK_CHANGE_STATES.STEP_LOST: RES_ICONS.getRankedPostBattleLoseIcon,
     RANK_CHANGE_STATES.NOTHING_CHANGED: RES_ICONS.getRankedPostBattleNotEffectiveIcon}
    __RANK_ICON_MAP = {RANK_CHANGE_STATES.RANK_EARNED: ('', RES_ICONS.getRankIcon),
     RANK_CHANGE_STATES.RANK_LOST: ('_grey', RES_ICONS.getRankIcon),
     RANK_CHANGE_STATES.STEPS_EARNED: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE2_GREEN_94X120),
     RANK_CHANGE_STATES.STEP_EARNED: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_GREEN_94X120),
     RANK_CHANGE_STATES.STEP_LOST: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_RED_94X120),
     RANK_CHANGE_STATES.NOTHING_CHANGED: (None, RES_ICONS.MAPS_ICONS_RANKEDBATTLES_RANKS_STAGE_STAGE_GREY_94X120),
     RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP: ('', RES_ICONS.getRankIcon),
     RANKEDBATTLES_ALIASES.SHIELD_LOSE: ('', RES_ICONS.getRankIcon),
     RANKEDBATTLES_ALIASES.SHIELD_ENABLED: ('', RES_ICONS.getRankIcon),
     RANK_CHANGE_STATES.RANK_POINT: ('', RES_ICONS.getRankIcon)}
    __RESOURCE_MAP = {_STEPS_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP2, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RES_ICONS.getRankedPostBattleTopIcon),
     _STEP_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RES_ICONS.getRankedPostBattleTopIcon),
     _STEP_NOT_CHANGED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, RES_ICONS.getRankedPostBattleNotEffectiveIcon),
     _STEP_LOST: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, RES_ICONS.getRankedPostBattleLoseIcon)}

    def __init__(self, reusable):
        self.__reusable = reusable

    def getState(self):
        return self.rankedController.getRankChangeStatus(self.__reusable.personal.getRankInfo())

    def makeSubTaskState(self):
        rankState = self.getState()
        rankedInfo = self.__reusable.personal.getRankInfo()
        shieldState = rankedInfo.shieldState
        if shieldState is not None:
            if shieldState in (RANKEDBATTLES_ALIASES.SHIELD_LOSE, RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP, RANKEDBATTLES_ALIASES.SHIELD_ENABLED):
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_ENABLED and rankState == RANK_CHANGE_STATES.STEP_LOST:
                    return RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE
                return RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK
        return RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK if rankState in (RANK_CHANGE_STATES.RANK_EARNED, RANK_CHANGE_STATES.RANK_LOST, RANK_CHANGE_STATES.RANK_POINT) else RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE

    def makeTitleLabel(self):
        isWin = self.__reusable.getPersonalTeam() == self.__reusable.common.winnerTeam
        rankState = self.getState()
        if rankState in self.__WITH_SHIELD_STATES:
            rankInfo = self.__reusable.personal.getRankInfo()
            shieldState = rankInfo.shieldState
            if shieldState is not None and shieldState in self.__SHIELD_STATES:
                return self.__TITLE_LABEL_MAP[shieldState, isWin]
            if rankState == RANK_CHANGE_STATES.RANK_EARNED:
                return i18n.makeString(self.__TITLE_LABEL_MAP[rankState, isWin], rank=rankInfo.accRank)
        return self.__TITLE_LABEL_MAP[rankState, isWin]

    def makeStatusLabel(self):
        isWin = self.__reusable.getPersonalTeam() == self.__reusable.common.winnerTeam
        rankState = self.getState()
        rankInfo = self.__reusable.personal.getRankInfo()
        if rankState in self.__RESULTS_WITH_SHIELDS:
            shieldState = rankInfo.shieldState
            if shieldState is not None:
                txt = '{}{}'
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
                    return txt.format(text_styles.highlightText(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDLOSE), text_styles.main(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDWARNING))
                if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP:
                    hpStr = text_styles.highTitle(rankInfo.shieldHP)
                    shieldCount = i18n.makeString(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDCOUNT, count=hpStr)
                    return txt.format(text_styles.highlightText(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDLOSESTEP), text_styles.main(shieldCount))
                if shieldState in RANKEDBATTLES_ALIASES.SHIELD_RENEW_STATES:
                    if rankState == RANK_CHANGE_STATES.STEP_EARNED:
                        return txt.format(text_styles.highlightText(RANKED_BATTLES.BATTLERESULT_STATUS_STAGEEARNED), text_styles.main(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDRENEW))
                    if rankState == RANK_CHANGE_STATES.STEPS_EARNED:
                        return txt.format(text_styles.highlightText(RANKED_BATTLES.BATTLERESULT_STATUS_STAGESEARNED), text_styles.main(RANKED_BATTLES.BATTLERESULT_STATUS_SHIELDRENEW))
            if rankState == RANK_CHANGE_STATES.RANK_EARNED:
                return text_styles.highlightText(i18n.makeString(self.__STATUS_LABEL_MAP[rankState, isWin], rank=rankInfo.accRank))
        return text_styles.highlightText(i18n.makeString(self.__STATUS_LABEL_MAP[rankState, isWin], rank=rankInfo.prevAccRank)) if rankState == RANK_CHANGE_STATES.RANK_LOST else text_styles.highlightText(self.__STATUS_LABEL_MAP[rankState, isWin])

    def makeDescriptionLabelAndTopIcon(self, allyVehicles):
        state = self.getState()
        isWin = self.__reusable.getPersonalTeam() == self.__reusable.common.winnerTeam
        accountDBID = self.__reusable.personal.avatar.accountDBID
        topNumber = self.__getTopBoundForPersonalTeam()
        earnedNumber = self.rankedController.getRanksTops(isLoser=not isWin, stepDiff=RANKEDBATTLES_ALIASES.STEP_VALUE_EARN)
        selfXp = None
        for item in allyVehicles:
            if item.player.dbID == accountDBID:
                selfXp = item.xp
                break

        if len(allyVehicles) <= topNumber or topNumber <= 0 or selfXp is None:
            isInTop = True
        else:
            isInTop = self.__isInTop(selfXp=selfXp, allyVehicles=allyVehicles, topNumber=topNumber)
            if not isInTop:
                topNumber = earnedNumber
                isInTop = self.__isInTop(selfXp=selfXp, allyVehicles=allyVehicles, topNumber=topNumber)
        if selfXp is not None and selfXp < self.getMinXp():
            resKey = RANKED_BATTLES.BATTLERESULT_NOTINTOP_MINXP
        elif not isWin and isInTop and state == RANK_CHANGE_STATES.NOTHING_CHANGED:
            resKey = RANKED_BATTLES.BATTLERESULT_NOTINTOP_STAGESAVED
        else:
            method = RANKED_BATTLES.getBattleResultsInTop if isInTop else RANKED_BATTLES.getBattleResultsNotInTop
            resKey = method('win') if isWin else method('lose')
        topIconMethod = self.__TOP_ICON_MAP[state]
        return (i18n.makeString(resKey).format(topNumber=topNumber), topIconMethod(topNumber))

    def makeRankAndShieldInfo(self):
        rankState = self.getState()
        shieldIcon = ''
        plateIcon = ''
        shieldCount = ''
        if rankState in self.__WITH_SHIELD_STATES:
            rankInfo = self.__reusable.personal.getRankInfo()
            shieldState = rankInfo.shieldState
            if shieldState is not None:
                if shieldState in (RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP, RANKEDBATTLES_ALIASES.SHIELD_LOSE, RANKEDBATTLES_ALIASES.SHIELD_ENABLED):
                    rankState = shieldState
                if rankInfo.shieldHP > 0:
                    shieldCount = str(rankInfo.shieldHP)
                    shieldIcon = RES_ICONS.getRankShieldIcon(size=RANKEDBATTLES_ALIASES.WIDGET_SMALL)
                    plateIcon = RES_ICONS.getRankShieldPlateIcon(size=RANKEDBATTLES_ALIASES.WIDGET_SMALL)
        suffix, resource = self.__RANK_ICON_MAP[rankState]
        if suffix is not None:
            rankAfterBattle, isMaster = self.__getRankAfterBattle()
            if self.getState() == RANK_CHANGE_STATES.RANK_LOST:
                rankAfterBattle += 1
            val = 'VehMaster{}'.format(suffix) if isMaster else '{}{}'.format(rankAfterBattle, suffix)
            resource = resource('58x80', val)
        return (resource,
         shieldCount,
         shieldIcon,
         plateIcon)

    def getTopBoundForTeam(self, team):
        return self.getWinnerBounds() if self.__reusable.common.winnerTeam == team else self.getLoserBounds()

    def getPlayerNumber(self):
        return len(self.rankedController.getRanksChanges(isLoser=False))

    def getWinnerBounds(self):
        winnerRankChanges = self.rankedController.getRanksChanges(isLoser=False)
        bounds, _ = self.__getRankTop(winnerRankChanges)
        return bounds

    def getLoserBounds(self):
        loserRankChanges = self.rankedController.getRanksChanges(isLoser=True)
        bounds, _ = self.__getRankTop(loserRankChanges)
        return bounds

    def getMinXp(self):
        return self.rankedController.getMinXp()

    def getPlayerStandoff(self, team, position, stepChanges):
        isLoser = self.__reusable.common.winnerTeam != team
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        configStepChanges = rankChanges[position]
        stepDiff = stepChanges - configStepChanges
        if stepDiff > 1:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_PLUS_2
        elif stepDiff < 0:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_MINUS
        elif stepDiff == 0:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE
        else:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_PLUS
        return (standoff, configStepChanges)

    def getStandoff(self, xp, xpToCompare, position, isLoser, isTop, lastStandoffInfo=None):
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        stepsDiff = rankChanges[position]
        minXP = self.rankedController.getMinXp()
        if isTop:
            if xp >= minXP:
                standoff = RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE
            else:
                standoff = RANKEDBATTLES_ALIASES.STANDOFF_MINUS
        elif xp < minXP:
            if stepsDiff >= 0:
                standoff = RANKEDBATTLES_ALIASES.STANDOFF_MINUS
            else:
                standoff = RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE
        elif xp == xpToCompare:
            if lastStandoffInfo is not None:
                lastStandoff, lastStepDiff = lastStandoffInfo
                diff = lastStepDiff - stepsDiff
                if diff == 0:
                    standoff = lastStandoff
                elif diff > 0:
                    standoff = self.__getNextStandoff(lastStandoff, diff)
                else:
                    standoff = RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE
            else:
                standoff = RANKEDBATTLES_ALIASES.STANDOFF_PLUS
        else:
            standoff = RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE
        return (standoff, stepsDiff)

    def getListsData(self, isLoser):
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        listsData = []
        steps = list(set(rankChanges))
        steps.sort(reverse=True)
        for step in steps:
            listsData.append(self.__getStepInfo(step, rankChanges))

        return listsData

    @staticmethod
    def __getStepTypeByDiff(stepDiff):
        if stepDiff == 0:
            return _STEP_NOT_CHANGED
        if stepDiff == 1:
            return _STEP_EARNED
        return _STEPS_EARNED if stepDiff > 0 else _STEP_LOST

    def __getStepInfo(self, stepElement, rankChanges):
        elementCount = rankChanges.count(stepElement)
        stepType = RankInfoHelper.__getStepTypeByDiff(stepElement)
        return (elementCount, self.__RESOURCE_MAP[stepType])

    def __getRankTop(self, rankChanges):
        topElement = rankChanges[0]
        return self.__getStepInfo(topElement, rankChanges)

    def __getTopBoundForPersonalTeam(self):
        return self.getTopBoundForTeam(self.__reusable.getPersonalTeam())

    def __getRankAfterBattle(self):
        rankInfo = self.__reusable.personal.getRankInfo()
        rankAfterBattle = rankInfo.accRank + rankInfo.vehRank
        return (rankAfterBattle, rankAfterBattle > self.rankedController.getAccRanksTotal())

    def __getNextStandoff(self, standoff, diff):
        count = len(RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS)
        standoffIndex = RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS.index(standoff)
        standoffIndex += diff
        if standoffIndex >= count:
            standoffIndex = count - 1
        return RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS[standoffIndex]

    def __isInTop(self, selfXp, allyVehicles, topNumber):
        topMinXp = min([ item.xp for item in allyVehicles[:topNumber] ])
        return selfXp >= topMinXp


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


class ObjectivesReachedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record and 'extCommon' in record:
            yes = i18n.makeString(BATTLE_RESULTS.DETAILS_TIME_VAL_YES)
            no = i18n.makeString(BATTLE_RESULTS.DETAILS_TIME_VAL_NO)
            reached = yes if record['extCommon']['destructibleEntity']['numStarted'] > 0 else no
        else:
            reached = ''
        return style.makeTimeStatsVO(self._field, reached)


class ObjectivesDestroyedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record and 'extCommon' in record:
            destroyed = str(record['extCommon']['destructibleEntity']['numDestroyed'])
        else:
            destroyed = '0'
        return style.makeTimeStatsVO(self._field, destroyed)


class BasesCapturedVO(base.StatsItem):
    __slots__ = ()

    def _convert(self, record, reusable):
        if record and 'extCommon' in record:
            captured = str(record['extCommon']['sector']['numCaptured'])
        else:
            captured = '0'
        return style.makeTimeStatsVO(self._field, captured)


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
        self.fullResultLabel = toUpper(i18n.makeString(_FULL_RESULT_LABEL.format(teamResult)))


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
        self.fullResultLabel = toUpper(i18n.makeString(_FULL_RESULT_LABEL.format(teamResult)))
        return


class EpicBattleBattleFinishResultBlock(RegularFinishResultBlock):
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
        self.finishReasonLabel = makeEpicBattleFinishResultLabel(reusable.common.finishReason, teamResult)
        self.shortResultLabel = teamResult
        self.fullResultLabel = toUpper(i18n.makeString(_FULL_RESULT_LABEL.format(teamResult)))
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
    __slots__ = ('state', 'linkage', 'title', 'description', 'topIcon', 'rankIcon', 'plateIcon', 'shieldIcon', 'shieldCount')

    def __init__(self, meta=None, field='', *path):
        super(RankChangesBlock, self).__init__(meta, field, *path)
        self.state = None
        self.linkage = None
        self.title = None
        self.description = None
        self.topIcon = None
        self.rankIcon = None
        self.shieldCount = ''
        self.shieldIcon = ''
        self.plateIcon = ''
        return

    def setRecord(self, result, reusable):
        helper = RankInfoHelper(reusable)
        self.state = helper.makeSubTaskState()
        self.rankIcon, self.shieldCount, self.shieldIcon, self.plateIcon = helper.makeRankAndShieldInfo()
        self.linkage = RANKEDBATTLES_ALIASES.BATTLE_RESULTS_SUB_TASK_UI
        self.title = helper.makeTitleLabel()
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sort_keys.VehicleXpSortKey)
        self.description, self.topIcon = helper.makeDescriptionLabelAndTopIcon(list(allies))


class RankedResultsStatusBlock(base.StatsItem):

    def _convert(self, value, reusable):
        helper = RankInfoHelper(reusable)
        return helper.makeStatusLabel()


class RankedResultsEnableAnimation(base.StatsItem):

    def _convert(self, value, reusable):
        return bool(AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS))


class RankedResultsShowWidgetAnimation(base.StatsItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def _convert(self, value, reusable):
        return not self.rankedController.awardWindowShouldBeShown(reusable.personal.getRankInfo())


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
