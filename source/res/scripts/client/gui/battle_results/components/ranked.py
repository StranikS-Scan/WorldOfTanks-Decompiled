# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/ranked.py
from collections import namedtuple
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ENABLE_RANKED_ANIMATIONS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.battle_results.components import base
from gui.battle_results.reusable import sort_keys
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_models import RankChangeStates
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.account_helpers.settings_core import ISettingsCore
TitleAndDescription = namedtuple('TitleAndDescription', 'title, description, descriptionIcon')
Shield = namedtuple('Shield', 'shieldCount, shieldIcon, plateIcon')
IconAndShield = namedtuple('IconAndShield', 'icon, shield')

def _getTopsLoseIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.lose.c_106x98.dyn('top{}'.format(topNumber))())


def _getTopsTopIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.top.c_106x98.dyn('top{}'.format(topNumber))())


def _getTopsNotEffectiveIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.notEffective.c_106x98.dyn('top{}'.format(topNumber))())


_STEPS_EARNED = 2
_STEP_EARNED = 1
_STEP_NOT_CHANGED = 0
_STEP_LOST = -1

class RankedInfoHelper(object):
    rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('_reusable',)
    _RESOURCE_MAP = {_STEPS_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP2, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, _getTopsTopIcon),
     _STEP_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, _getTopsTopIcon),
     _STEP_NOT_CHANGED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, _getTopsNotEffectiveIcon),
     _STEP_LOST: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, _getTopsLoseIcon)}

    def __init__(self, reusable):
        self._reusable = reusable

    def getRankChangeStatus(self):
        return self.rankedController.getRankChangeStatus(self._reusable.personal.getRankInfo())


class RankedResultsInfoHelper(RankedInfoHelper):
    __slots__ = ()
    _CHANGE_TO_ALIAS_STATE = {RankChangeStates.LEAGUE_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.DIVISION_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.RANK_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.RANK_SHIELD_PROTECTED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE,
     RankChangeStates.RANK_UNBURN_PROTECTED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NORMAL_STATE,
     RankChangeStates.RANK_LOST: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE,
     RankChangeStates.STEP_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.STEPS_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.BONUS_STEP_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.BONUS_STEPS_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     RankChangeStates.NOTHING_CHANGED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NORMAL_STATE,
     RankChangeStates.STEP_LOST: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE}
    _STATUS_LABEL_MAP = {RankChangeStates.LEAGUE_EARNED: None,
     RankChangeStates.DIVISION_EARNED: None,
     RankChangeStates.RANK_EARNED: R.strings.ranked_battles.battleresult.status.rankEarned(),
     RankChangeStates.RANK_SHIELD_PROTECTED: R.strings.ranked_battles.battleresult.status.shieldLoseStep(),
     RankChangeStates.RANK_UNBURN_PROTECTED: R.strings.ranked_battles.battleresult.status.rankUnburnable(),
     RankChangeStates.RANK_LOST: R.strings.ranked_battles.battleresult.status.rankLost(),
     RankChangeStates.STEP_EARNED: R.strings.ranked_battles.battleresult.status.stageEarned(),
     RankChangeStates.BONUS_STEP_EARNED: R.strings.ranked_battles.battleresult.status.stageEarned(),
     RankChangeStates.STEPS_EARNED: R.strings.ranked_battles.battleresult.status.stagesEarned(),
     RankChangeStates.BONUS_STEPS_EARNED: R.strings.ranked_battles.battleresult.status.stagesEarned(),
     RankChangeStates.STEP_LOST: R.strings.ranked_battles.battleresult.status.stageLost(),
     RankChangeStates.NOTHING_CHANGED: R.strings.ranked_battles.battleresult.status.stageSaved()}

    def makeState(self):
        return self._CHANGE_TO_ALIAS_STATE.get(self.getRankChangeStatus())

    def makeStatusLabel(self):
        isWin = self._reusable.getPersonalTeam() == self._reusable.common.winnerTeam
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        shieldState = rankInfo.shieldState
        resultLabel = backport.text(self._STATUS_LABEL_MAP[rankState])
        resultSubLabel = ''
        if rankState == RankChangeStates.LEAGUE_EARNED or rankState == RankChangeStates.DIVISION_EARNED:
            return ''
        if rankState == RankChangeStates.NOTHING_CHANGED and isWin:
            resultLabel = backport.text(R.strings.ranked_battles.battleresult.status.stageNotEarned())
        if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
            resultLabel = backport.text(R.strings.ranked_battles.battleresult.status.shieldLose())
            resultSubLabel = backport.text(R.strings.ranked_battles.battleresult.status.shieldWarning())
        if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP:
            resultSubLabel = backport.text(R.strings.ranked_battles.battleresult.status.shieldCount(), count=text_styles.highTitle(rankInfo.shieldHP))
        if shieldState in RANKEDBATTLES_ALIASES.SHIELD_RENEW_STATES:
            resultSubLabel = backport.text(R.strings.ranked_battles.battleresult.status.shieldRenew())
        return text_styles.concatStylesToMultiLine(text_styles.heroTitle(resultLabel), text_styles.promoSubTitle(resultSubLabel))

    def getListsData(self, isLoser):
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        listsData = []
        steps = list(set(rankChanges))
        steps.sort(reverse=True)
        for step in steps:
            listsData.append(self.__getStepInfo(step, rankChanges))

        return listsData

    def getPlayersNumber(self):
        return len(self.rankedController.getRanksChanges(isLoser=False))

    def getPlayerStandoff(self, team, position, stepChanges, updatedStepChanges):
        isLoser = self._reusable.common.winnerTeam != team
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        configStepChanges = rankChanges[position]
        stepDiff = stepChanges - configStepChanges
        if stepDiff > 1:
            return (RANKEDBATTLES_ALIASES.STANDOFF_PLUS_2, configStepChanges)
        if stepDiff == 1:
            return (RANKEDBATTLES_ALIASES.STANDOFF_PLUS, configStepChanges)
        if stepChanges < 0 and updatedStepChanges == 0:
            return (RANKEDBATTLES_ALIASES.STANDOFF_RPOTECTED, configStepChanges)
        return (RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE, configStepChanges) if stepDiff == 0 else (RANKEDBATTLES_ALIASES.STANDOFF_MINUS, configStepChanges)

    def getStandoff(self, xp, xpToCompare, position, isLoser, isTop, lastStandoffInfo=None):
        rankChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
        stepsDiff = rankChanges[position]
        if isTop:
            return (RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE, stepsDiff)
        elif xp == xpToCompare:
            if lastStandoffInfo is not None:
                lastStandoff, lastStepDiff = lastStandoffInfo
                diff = lastStepDiff - stepsDiff
                if diff == 0:
                    return (lastStandoff, stepsDiff)
                if diff > 0:
                    return (self.__getNextStandoff(lastStandoff, diff), stepsDiff)
                return (RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE, stepsDiff)
            return (RANKEDBATTLES_ALIASES.STANDOFF_PLUS, stepsDiff)
        else:
            return (RANKEDBATTLES_ALIASES.STANDOFF_INVISIBLE, stepsDiff)

    @classmethod
    def __getStepTypeByDiff(cls, stepDiff):
        if stepDiff == 0:
            return _STEP_NOT_CHANGED
        if stepDiff == 1:
            return _STEP_EARNED
        return _STEPS_EARNED if stepDiff > 0 else _STEP_LOST

    @classmethod
    def __getStepInfo(cls, stepElement, rankChanges):
        elementCount = rankChanges.count(stepElement)
        stepType = cls.__getStepTypeByDiff(stepElement)
        return (elementCount, cls._RESOURCE_MAP[stepType])

    @classmethod
    def __getNextStandoff(cls, standoff, diff):
        count = len(RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS)
        standoffIndex = RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS.index(standoff)
        standoffIndex += diff
        if standoffIndex >= count:
            standoffIndex = count - 1
        return RANKEDBATTLES_ALIASES.NON_NEGATIVE_STANDOFFS[standoffIndex]


class RankedChangesInfoHelper(RankedInfoHelper):
    settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ()
    _STEPS_ICONS = {RankChangeStates.BONUS_STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage4_bonus(),
     RankChangeStates.STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage2_green(),
     RankChangeStates.BONUS_STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage2_bonus(),
     RankChangeStates.STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_green(),
     RankChangeStates.STEP_LOST: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_red(),
     RankChangeStates.NOTHING_CHANGED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_grey(),
     RankChangeStates.RANK_UNBURN_PROTECTED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_grey()}
    _MINI_STEPS_ICONS = {_STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus2(),
     _STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus1(),
     _STEP_NOT_CHANGED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.nothing(),
     _STEP_LOST: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.minus1()}
    _STATE_TO_SUBTASK = {RankChangeStates.LEAGUE_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE,
     RankChangeStates.DIVISION_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION,
     RankChangeStates.RANK_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK,
     RankChangeStates.RANK_SHIELD_PROTECTED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK,
     RankChangeStates.RANK_UNBURN_PROTECTED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.RANK_LOST: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST,
     RankChangeStates.STEP_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.BONUS_STEP_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.STEPS_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.BONUS_STEPS_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.STEP_LOST: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     RankChangeStates.NOTHING_CHANGED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE}
    _TITLE_LABEL_MAP = {RankChangeStates.LEAGUE_EARNED: R.strings.ranked_battles.battleresult.leagueEarned(),
     RankChangeStates.DIVISION_EARNED: R.strings.ranked_battles.battleresult.divisionEarned(),
     RankChangeStates.RANK_EARNED: R.strings.ranked_battles.battleresult.rankEarned(),
     RankChangeStates.RANK_SHIELD_PROTECTED: R.strings.ranked_battles.battleresult.shieldLoseStep(),
     RankChangeStates.RANK_UNBURN_PROTECTED: R.strings.ranked_battles.battleresult.rankUnburnable(),
     RankChangeStates.RANK_LOST: R.strings.ranked_battles.battleresult.rankLost(),
     RankChangeStates.BONUS_STEP_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     RankChangeStates.BONUS_STEPS_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     RankChangeStates.STEP_EARNED: R.strings.ranked_battles.battleresult.stageEarned(),
     RankChangeStates.STEPS_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     RankChangeStates.STEP_LOST: R.strings.ranked_battles.battleresult.stageLost(),
     RankChangeStates.NOTHING_CHANGED: R.strings.ranked_battles.battleresult.stageSaved()}

    def makeTitleAndDescription(self, allyVehicles):
        isWin = self._reusable.getPersonalTeam() == self._reusable.common.winnerTeam
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        shieldState = rankInfo.shieldState
        title = backport.text(self._TITLE_LABEL_MAP[rankState])
        if rankState == RankChangeStates.NOTHING_CHANGED and isWin:
            title = backport.text(R.strings.ranked_battles.battleresult.stageNotEarned())
        if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
            title = backport.text(R.strings.ranked_battles.battleresult.shieldLose())
        position = self._getPlayerPosition(allyVehicles)
        descriptionIcon = self._getDescriptionIcon(position)
        topNumber = self._getWinnerBounds(position) if isWin else self._getLoserBounds(position)
        position = position + 1 if position is not None else topNumber
        winKey = 'win' if isWin else 'lose'
        topKey = 'inTop' if topNumber >= position else 'notInTop'
        description = backport.text(R.strings.ranked_battles.battleresult.dyn(topKey).dyn(winKey)(), topNumber=topNumber)
        if rankState in (RankChangeStates.DIVISION_EARNED, RankChangeStates.LEAGUE_EARNED):
            description = backport.text(R.strings.ranked_battles.battleresult.bonusBattlesEarned(), count=text_styles.neutral(rankInfo.additionalBonusBattles))
            if rankState == RankChangeStates.LEAGUE_EARNED:
                description = text_styles.concatStylesToMultiLine(backport.text(R.strings.ranked_battles.battleresult.leagueUnavailable()), description)
            return TitleAndDescription(title, description, descriptionIcon)
        elif rankState == RankChangeStates.RANK_UNBURN_PROTECTED:
            title = backport.text(R.strings.ranked_battles.battleresult.rankUnburnable())
            description = backport.text(R.strings.ranked_battles.battleresult.notInTop.stageSaved())
            return TitleAndDescription(title, description, descriptionIcon)
        else:
            return TitleAndDescription(title, description, descriptionIcon)

    def makeIcons(self):
        icon = None
        shieldIcon = None
        plateIcon = None
        shieldCount = None
        state = self.makeSubTaskState()
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE:
            icon = backport.image(R.images.gui.maps.icons.rankedBattles.league.c_70x70.c_0())
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION:
            icon = backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_58x80.dyn('c_{}'.format(self.rankedController.getDivision(rankInfo.accRank + 1).getID()))())
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST:
            icon = self.__getRankIcon(rankInfo.prevAccRank)
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK:
            icon = self.__getRankIcon(rankInfo.accRank)
            if rankInfo.shieldHP > 0:
                shieldCount = str(rankInfo.shieldHP)
                shortcut = R.images.gui.maps.icons.rankedBattles
                shieldIcon = backport.image(shortcut.ranks.shields.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL)())
                plateIcon = backport.image(shortcut.ranks.shields.plate.empty.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL)())
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE:
            icon = backport.image(self._STEPS_ICONS[rankState])
        return IconAndShield(icon, Shield(shieldCount, shieldIcon, plateIcon))

    def makeSubTaskState(self):
        return self._STATE_TO_SUBTASK[self.getRankChangeStatus()]

    def _getDescriptionIcon(self, position):
        if position is None:
            return
        else:
            subTaskState = self.makeSubTaskState()
            if subTaskState in (RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK, RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST):
                state = self.getRankChangeStatus()
                isLoser = self._reusable.getPersonalTeam() != self._reusable.common.winnerTeam
                stepsChanges = self.rankedController.getRanksChanges(isLoser=isLoser)
                stepsChange = stepsChanges[position] if position is not None else _STEP_NOT_CHANGED
                if stepsChange == _STEP_LOST:
                    if state in (RankChangeStates.RANK_UNBURN_PROTECTED, RankChangeStates.RANK_SHIELD_PROTECTED):
                        return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.miniStage.protected())
                    if self.settingsCore.getSetting('isColorBlind'):
                        return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.miniStage.blindMinus1())
                return backport.image(self._MINI_STEPS_ICONS[stepsChange])
            return

    def _getLoserBounds(self, position):
        loserRankChanges = self.rankedController.getRanksChanges(isLoser=True)
        if position is None:
            return sum([ 1 for item in loserRankChanges if item >= 0 ])
        elif loserRankChanges[position] >= 0:
            for idx, stepChange in enumerate(loserRankChanges[position:]):
                if stepChange != loserRankChanges[position]:
                    return position + idx

            return len(loserRankChanges)
        else:
            for idx, stepChange in enumerate(loserRankChanges[position::-1]):
                if stepChange >= 0:
                    return position - idx + 1

            return 0

    def _getPlayerPosition(self, allyVehicles):
        accountDBID = self._reusable.personal.avatar.accountDBID
        tmpXp = -1
        position = 0
        for item in allyVehicles:
            if item.player.dbID == accountDBID:
                return position
            if tmpXp != item.xp:
                tmpXp = item.xp
                position += 1

        return None

    def _getWinnerBounds(self, position):
        winnerRankChanges = self.rankedController.getRanksChanges(isLoser=False)
        if position is None:
            return sum([ 1 for item in winnerRankChanges if item > 0 ])
        elif winnerRankChanges[position] > 0:
            for idx, stepChange in enumerate(winnerRankChanges[position:]):
                if stepChange != winnerRankChanges[position]:
                    return position + idx

            return len(winnerRankChanges)
        else:
            for idx, stepChange in enumerate(winnerRankChanges[position::-1]):
                if stepChange > 0:
                    return position - idx + 1

            return 0

    def __getRankIcon(self, rankID):
        division = self.rankedController.getDivision(rankID)
        return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.c_58x80.dyn('rank%s_%s' % (division.getID(), division.getRankUserName(rankID)))())


class RankedResultsShowWidgetAnimation(base.StatsItem):
    rankedController = dependency.descriptor(IRankedBattlesController)

    def _convert(self, value, reusable):
        return not self.rankedController.awardWindowShouldBeShown(reusable.personal.getRankInfo())


class RankedResultsStatusBlock(base.StatsItem):

    def _convert(self, value, reusable):
        helper = RankedResultsInfoHelper(reusable)
        return helper.makeStatusLabel()


class RankedResultsStateBlock(base.StatsItem):

    def _convert(self, value, reusable):
        helper = RankedResultsInfoHelper(reusable)
        return helper.makeState()


class RankedResultsEnableAnimation(base.StatsItem):

    def _convert(self, value, reusable):
        return bool(AccountSettings.getSettings(ENABLE_RANKED_ANIMATIONS))


class RankChangesBlock(base.StatsBlock):
    __slots__ = ('state', 'linkage', 'title', 'description', 'descriptionIcon', 'icon', 'plateIcon', 'shieldIcon', 'shieldCount')

    def __init__(self, meta=None, field='', *path):
        super(RankChangesBlock, self).__init__(meta, field, *path)
        self.state = None
        self.linkage = None
        self.title = None
        self.description = None
        self.descriptionIcon = None
        self.icon = None
        self.shieldCount = None
        self.shieldIcon = None
        self.plateIcon = None
        return

    def setRecord(self, result, reusable):
        helper = RankedChangesInfoHelper(reusable)
        self.linkage = RANKEDBATTLES_ALIASES.BATTLE_RESULTS_SUB_TASK_UI
        self.state = helper.makeSubTaskState()
        self.icon, shieldIcon = helper.makeIcons()
        self.shieldCount, self.shieldIcon, self.plateIcon = shieldIcon
        allies, _ = reusable.getBiDirectionTeamsIterator(result, sort_keys.VehicleXpSortKey)
        self.title, self.description, self.descriptionIcon = helper.makeTitleAndDescription(allies)
