# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/components/ranked.py
import typing
from collections import namedtuple
from account_helpers import AccountSettings
from account_helpers.AccountSettings import ENABLE_RANKED_ANIMATIONS
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.battle_results.components import base
from gui.battle_results.reusable import sort_keys
from gui.impl import backport
from gui.impl.gen import R
from gui.ranked_battles.ranked_models import RankChangeStates as _RCS
from gui.ranked_battles.ranked_helpers import getBonusBattlesIncome
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.account_helpers.settings_core import ISettingsCore
from shared_utils import CONST_CONTAINER
TitleAndDescription = namedtuple('TitleAndDescription', 'title, description, descriptionIcon')
Shield = namedtuple('Shield', 'shieldCount, shieldIcon, plateIcon')
IconsAndShield = namedtuple('IconsAndShield', 'icon, shield')

def _getTopsLoseIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.lose.c_106x98.dyn('top{}'.format(topNumber))())


def _getTopsTopIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.top.c_106x98.dyn('top{}'.format(topNumber))())


def _getTopsNotEffectiveIcon(topNumber):
    return backport.image(R.images.gui.maps.icons.rankedBattles.tops.notEffective.c_106x98.dyn('top{}'.format(topNumber))())


class MiniSteps(CONST_CONTAINER):
    STEPS_EARNED_BONUS = 4
    STEP_EARNED_BONUS = 3
    STEPS_EARNED = 2
    STEP_EARNED = 1
    STEP_NOT_CHANGED = 0
    STEP_LOST = -1


class RankedInfoHelper(object):
    rankedController = dependency.descriptor(IRankedBattlesController)
    __slots__ = ('_reusable',)
    _RESOURCE_MAP = {MiniSteps.STEPS_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP2, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, _getTopsTopIcon),
     MiniSteps.STEP_EARNED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_TOP, _getTopsTopIcon),
     MiniSteps.STEP_NOT_CHANGED: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_NOTEFFECTIVE, _getTopsNotEffectiveIcon),
     MiniSteps.STEP_LOST: (RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, RANKEDBATTLES_ALIASES.BACKGROUND_STATE_LOSE, _getTopsLoseIcon)}

    def __init__(self, reusable):
        self._reusable = reusable

    def getRankChangeStatus(self):
        return self.rankedController.getRankChangeStatus(self._reusable.personal.getRankInfo())


class RankedResultsInfoHelper(RankedInfoHelper):
    __slots__ = ()
    _CHANGE_TO_ALIAS_STATE = {_RCS.LEAGUE_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.DIVISION_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.QUAL_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.QUAL_UNBURN_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.RANK_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.RANK_SHIELD_PROTECTED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE,
     _RCS.RANK_UNBURN_PROTECTED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NORMAL_STATE,
     _RCS.RANK_LOST: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE,
     _RCS.STEP_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.STEPS_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.BONUS_STEP_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.BONUS_STEPS_EARNED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_POSITIVE_STATE,
     _RCS.NOTHING_CHANGED: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NORMAL_STATE,
     _RCS.STEP_LOST: RANKEDBATTLES_ALIASES.BATTLE_RESULTS_NEGATIVE_STATE}
    _STATUS_LABEL_MAP = {_RCS.LEAGUE_EARNED: None,
     _RCS.DIVISION_EARNED: None,
     _RCS.QUAL_EARNED: None,
     _RCS.QUAL_UNBURN_EARNED: None,
     _RCS.RANK_EARNED: R.strings.ranked_battles.battleresult.status.rankEarned(),
     _RCS.RANK_SHIELD_PROTECTED: R.strings.ranked_battles.battleresult.status.shieldLoseStep(),
     _RCS.RANK_UNBURN_PROTECTED: R.strings.ranked_battles.battleresult.status.rankUnburnable(),
     _RCS.RANK_LOST: R.strings.ranked_battles.battleresult.status.rankLost(),
     _RCS.STEP_EARNED: R.strings.ranked_battles.battleresult.status.stageEarned(),
     _RCS.BONUS_STEP_EARNED: R.strings.ranked_battles.battleresult.status.stageEarned(),
     _RCS.STEPS_EARNED: R.strings.ranked_battles.battleresult.status.stagesEarned(),
     _RCS.BONUS_STEPS_EARNED: R.strings.ranked_battles.battleresult.status.stagesEarned(),
     _RCS.STEP_LOST: R.strings.ranked_battles.battleresult.status.stageLost(),
     _RCS.NOTHING_CHANGED: R.strings.ranked_battles.battleresult.status.stageSaved()}

    def makeState(self):
        return self._CHANGE_TO_ALIAS_STATE.get(self.getRankChangeStatus())

    def makeStatusLabel(self):
        isWin = self._reusable.getPersonalTeam() == self._reusable.common.winnerTeam
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        shieldState = rankInfo.shieldState
        resultLabel = backport.text(self._STATUS_LABEL_MAP[rankState])
        resultSubLabel = ''
        if rankState in (_RCS.LEAGUE_EARNED,
         _RCS.DIVISION_EARNED,
         _RCS.QUAL_EARNED,
         _RCS.QUAL_UNBURN_EARNED):
            return ''
        if rankState == _RCS.NOTHING_CHANGED and isWin:
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
            return MiniSteps.STEP_NOT_CHANGED
        if stepDiff == 1:
            return MiniSteps.STEP_EARNED
        return MiniSteps.STEPS_EARNED if stepDiff > 0 else MiniSteps.STEP_LOST

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
    _STEPS_ICONS = {_RCS.BONUS_STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage4_bonus(),
     _RCS.STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage2_green(),
     _RCS.BONUS_STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage2_bonus(),
     _RCS.STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_green(),
     _RCS.STEP_LOST: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_red(),
     _RCS.NOTHING_CHANGED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_grey(),
     _RCS.RANK_UNBURN_PROTECTED: R.images.gui.maps.icons.rankedBattles.ranks.stage.c_140x120.stage_grey()}
    _MINI_STEPS_ICONS = {MiniSteps.STEPS_EARNED_BONUS: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus2Bonus(),
     MiniSteps.STEP_EARNED_BONUS: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus1Bonus(),
     MiniSteps.STEPS_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus2(),
     MiniSteps.STEP_EARNED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.plus1(),
     MiniSteps.STEP_NOT_CHANGED: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.nothing(),
     MiniSteps.STEP_LOST: R.images.gui.maps.icons.rankedBattles.ranks.miniStage.minus1()}
    _STATE_TO_SUBTASK = {_RCS.LEAGUE_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE,
     _RCS.DIVISION_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION,
     _RCS.QUAL_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION,
     _RCS.QUAL_UNBURN_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION,
     _RCS.RANK_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK,
     _RCS.RANK_SHIELD_PROTECTED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK,
     _RCS.RANK_UNBURN_PROTECTED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.RANK_LOST: RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST,
     _RCS.STEP_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.BONUS_STEP_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.STEPS_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.BONUS_STEPS_EARNED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.STEP_LOST: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE,
     _RCS.NOTHING_CHANGED: RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE}
    _TITLE_LABEL_MAP = {_RCS.LEAGUE_EARNED: R.strings.ranked_battles.battleresult.leagueEarned(),
     _RCS.DIVISION_EARNED: R.strings.ranked_battles.battleresult.divisionEarned(),
     _RCS.QUAL_EARNED: R.strings.ranked_battles.battleresult.divisionEarned(),
     _RCS.QUAL_UNBURN_EARNED: R.strings.ranked_battles.battleresult.divisionEarned(),
     _RCS.RANK_EARNED: R.strings.ranked_battles.battleresult.rankEarned(),
     _RCS.RANK_SHIELD_PROTECTED: R.strings.ranked_battles.battleresult.shieldLoseStep(),
     _RCS.RANK_UNBURN_PROTECTED: R.strings.ranked_battles.battleresult.rankUnburnable(),
     _RCS.RANK_LOST: R.strings.ranked_battles.battleresult.rankLost(),
     _RCS.BONUS_STEP_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     _RCS.BONUS_STEPS_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     _RCS.STEP_EARNED: R.strings.ranked_battles.battleresult.stageEarned(),
     _RCS.STEPS_EARNED: R.strings.ranked_battles.battleresult.stagesEarned(),
     _RCS.STEP_LOST: R.strings.ranked_battles.battleresult.stageLost(),
     _RCS.NOTHING_CHANGED: R.strings.ranked_battles.battleresult.stageSaved()}

    def makeTitleAndDescription(self, allyVehicles):
        isWin = self._reusable.getPersonalTeam() == self._reusable.common.winnerTeam
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        shieldState = rankInfo.shieldState
        title = backport.text(self._TITLE_LABEL_MAP[rankState])
        if rankState == _RCS.NOTHING_CHANGED and isWin:
            title = backport.text(R.strings.ranked_battles.battleresult.stageNotEarned())
        if shieldState == RANKEDBATTLES_ALIASES.SHIELD_LOSE:
            title = backport.text(R.strings.ranked_battles.battleresult.shieldLose())
        position = self._getPlayerPosition(allyVehicles)
        descriptionIcon = self._getDescriptionIcon(rankState, rankInfo.stepChanges, rankInfo.updatedStepChanges)
        topNumber = self._getWinnerBounds(position) if isWin else self._getLoserBounds(position)
        position = position + 1 if position is not None else topNumber
        winKey = 'win' if isWin else 'lose'
        topKey = 'inTop' if topNumber >= position else 'notInTop'
        description = backport.text(R.strings.ranked_battles.battleresult.dyn(topKey).dyn(winKey)(), topNumber=topNumber)
        if topNumber == 1:
            description = backport.text(R.strings.ranked_battles.battleresult.first.dyn(topKey).dyn(winKey)())
        if rankState in (_RCS.RANK_UNBURN_PROTECTED, _RCS.QUAL_UNBURN_EARNED):
            description = backport.text(R.strings.ranked_battles.battleresult.notInTop.stageSaved())
        if rankInfo.isBonusBattle:
            description = text_styles.concatStylesToSingleLine(description, backport.text(R.strings.ranked_battles.battleresult.bonusBattlesUsed()))
        if rankState in (_RCS.DIVISION_EARNED,
         _RCS.LEAGUE_EARNED,
         _RCS.QUAL_EARNED,
         _RCS.QUAL_UNBURN_EARNED):
            if rankState == _RCS.LEAGUE_EARNED:
                description = backport.text(R.strings.ranked_battles.battleresult.leagueUnavailable())
            bonusBattlesIncome = getBonusBattlesIncome(R.strings.ranked_battles.battleresult.bonusBattlesEarned, rankInfo.stepsBonusBattles, rankInfo.efficiencyBonusBattles, rankState == _RCS.LEAGUE_EARNED)
            description = text_styles.concatStylesToSingleLine(description, backport.text(R.strings.ranked_battles.battleresult.bonusBattlesEarned()), bonusBattlesIncome)
        return TitleAndDescription(title, description, descriptionIcon)

    def makeIcons(self):
        shieldIcon = plateIcon = shieldCount = None
        state = self.makeSubTaskState()
        rankState = self.getRankChangeStatus()
        rankInfo = self._reusable.personal.getRankInfo()
        if state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE:
            icon = backport.image(R.images.gui.maps.icons.rankedBattles.league.c_70x70.c_0())
        elif state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_DIVISION:
            icon = backport.image(R.images.gui.maps.icons.rankedBattles.divisions.c_58x80.dyn('c_{}'.format(self.rankedController.getDivision(rankInfo.accRank + 1).getID()))())
        elif state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK_LOST:
            icon = self.__getRankIcon(rankInfo.prevAccRank)
        elif state == RANKEDBATTLES_ALIASES.SUBTASK_STATE_RANK:
            icon = self.__getRankIcon(rankInfo.accRank)
            if self.rankedController.getRank(rankInfo.accRank).isVisualUnburnable():
                shieldIcon = backport.image(R.images.gui.maps.icons.rankedBattles.ranks.unburnable.small())
            if rankInfo.shieldHP > 0:
                shieldCount = str(rankInfo.shieldHP)
                shortcut = R.images.gui.maps.icons.rankedBattles
                shieldIcon = backport.image(shortcut.ranks.shields.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL)())
                plateIcon = backport.image(shortcut.ranks.shields.plate.empty.dyn(RANKEDBATTLES_ALIASES.WIDGET_SMALL)())
        else:
            icon = backport.image(self._STEPS_ICONS[rankState])
        return IconsAndShield(icon, Shield(shieldCount, shieldIcon, plateIcon))

    def makeSubTaskState(self):
        return self._STATE_TO_SUBTASK[self.getRankChangeStatus()]

    def _getDescriptionIcon(self, state, stepChanges, updatedStepChanges):
        if stepChanges is None:
            return
        if state in (_RCS.RANK_UNBURN_PROTECTED, _RCS.RANK_SHIELD_PROTECTED, _RCS.QUAL_UNBURN_EARNED):
            if stepChanges == MiniSteps.STEP_LOST:
                return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.miniStage.protected())
        subTaskState = self.makeSubTaskState()
        if subTaskState not in (RANKEDBATTLES_ALIASES.SUBTASK_STATE_STAGE, RANKEDBATTLES_ALIASES.SUBTASK_STATE_LEAGUE):
            if stepChanges == MiniSteps.STEP_LOST and self.settingsCore.getSetting('isColorBlind'):
                return backport.image(R.images.gui.maps.icons.rankedBattles.ranks.miniStage.blindMinus1())
            if stepChanges == MiniSteps.STEP_EARNED and updatedStepChanges > stepChanges:
                stepChanges = MiniSteps.STEP_EARNED_BONUS
            elif stepChanges == MiniSteps.STEPS_EARNED and updatedStepChanges > stepChanges:
                stepChanges = MiniSteps.STEPS_EARNED_BONUS
            return backport.image(self._MINI_STEPS_ICONS[stepChanges])
        else:
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
