# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/post_battle_rewards_view.py
from collections import defaultdict
import SoundGroups
from epic_constants import EPIC_SELECT_BONUS_NAME, EPIC_SKILL_TOKEN_NAME
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from frontline.gui.bonus import FrontlineSkillBonus
from frontline.gui.frontline_bonus_packers import packBonusModelAndTooltipData
from frontline.gui.impl.gen.view_models.views.lobby.views.post_battle_rewards_view_model import PostBattleRewardsViewModel
from gui.impl.gen import R
from gui.impl.lobby.common.view_mixins import LobbyHeaderVisibility
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.pub import ViewImpl, WindowImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.server_events.bonuses import mergeBonuses
from gui.shared.event_dispatcher import showEpicRewardsSelectionWindow, showFrontlineAwards
from gui.sounds.epic_sound_constants import EPIC_METAGAME_WWISE_SOUND_EVENTS
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from PlayerEvents import g_playerEvents

class _PostBattleRewardsCtx(object):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('__ctx', '__currLevel', '__currFamePoints', '__currProgress', '__prevLevel', '__prevFamePoints', '__prevProgress')

    def __init__(self, ctx=None):
        self.__ctx = ctx or {}
        self.__currLevel, self.__currFamePoints = ctx.get('metaLevel', (1, 0))
        self.__prevLevel, self.__prevFamePoints = ctx.get('prevMetaLevel', (1, 0))
        self.__currProgress = self.__packLevel(self.currLevel, self.currFamePoints)
        self.__prevProgress = self.__packLevel(self.prevLevel, self.prevFamePoints)

    @property
    def currLevel(self):
        return self.__currLevel

    @property
    def currFamePoints(self):
        return self.__currFamePoints

    @property
    def currProgress(self):
        return self.__currProgress

    @property
    def prevLevel(self):
        return self.__prevLevel

    @property
    def prevFamePoints(self):
        return self.__prevFamePoints

    @property
    def prevProgress(self):
        return self.__prevProgress

    @property
    def boosterXP(self):
        return self.__ctx.get('boosterFlXP', 0)

    @property
    def achievedXP(self):
        return self.__ctx.get('originalFlXP', 0)

    @property
    def arenaUniqueID(self):
        return self.__ctx.get('arenaUniqueID')

    @property
    def playerRank(self):
        return max(self.__ctx.get('playerRank', 0), 1)

    @property
    def maxLevel(self):
        return self.__epicController.getMaxPlayerLevel()

    def isOnMaxLevel(self):
        return self.prevLevel == self.currLevel == self.maxLevel

    def isMaxLevelReached(self):
        return self.currLevel == self.maxLevel

    @property
    def newRewardsCount(self):
        return self.__epicController.getNotChosenRewardCount()

    @property
    def bonuses(self):
        return self.__getBonuses()

    def __packLevel(self, level, famePoints):
        getPointsProgressForLevel = self.__epicController.getPointsProgressForLevel
        return self.maxLevel if level == self.maxLevel else level + float(famePoints) / getPointsProgressForLevel(level)

    def __getBonuses(self):
        bonuses = []
        allLevelData = self.__epicController.getAllLevelRewards()
        for questLvl, rewardData in allLevelData.iteritems():
            if self.prevLevel < questLvl <= self.currLevel:
                rewards = rewardData.getBonuses()
                rewards.extend(self.__getAbilityPointsRewardBonus(questLvl))
                levelBonuses = self.__epicController.replaceOfferByReward(rewards)
                bonuses.extend(levelBonuses)

        return bonuses

    def __getAbilityPointsRewardBonus(self, level):
        abilityPts = self.__epicController.getAbilityPointsForLevel()
        return [FrontlineSkillBonus(abilityPts[level - 1])] if abilityPts and abilityPts[level - 1] and level <= len(abilityPts) else []


class PostBattleRewardsView(ViewImpl, LobbyHeaderVisibility, IGlobalListener):
    _MAX_VISIBLE_AWARDS = 6
    _BONUS_ORDER_PRIORITY = {'battlePassPoints': 1,
     EPIC_SKILL_TOKEN_NAME: 2,
     'crystal': 3,
     'goodies': 4,
     EPIC_SELECT_BONUS_NAME: 5,
     'crewBooks': 6}
    _MIDDLE_PRIORITY = 50
    __battleResultsService = dependency.descriptor(IBattleResultsService)
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, layoutID=R.views.frontline.mono.lobby.post_battle_rewards_view(), ctx=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.MAIN_VIEW
        settings.model = PostBattleRewardsViewModel()
        self.__ctx = _PostBattleRewardsCtx(ctx)
        self.__tooltipItems = {}
        self.__rewardsList = []
        self.__rewardsSelectionWindow = None
        self.__isProgressBarAnimating = False
        super(PostBattleRewardsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(PostBattleRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PostBattleRewardsView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return self.__tooltipItems.get(tooltipId) if tooltipId else None

    def createToolTipContent(self, event, contentID):
        showCount = int(event.getArgument('showCount')) - 1
        if contentID != R.views.lobby.tooltips.AdditionalRewardsTooltip() or len(self.__rewardsList) <= showCount:
            return super(PostBattleRewardsView, self).createToolTipContent(event, contentID)
        additionalRewards = [ reward for reward in self.__rewardsList[showCount:] ]
        return AdditionalRewardsTooltip(additionalRewards)

    def _getEvents(self):
        return [(self.viewModel.onClaimRewards, self.__onClaimRewards),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.onContinue, self.__onContinue),
         (self.viewModel.onIntroStartsPlaying, self.__onIntroStartsPlaying),
         (self.viewModel.onRibbonStartsPlaying, self.__onRibbonStartsPlaying),
         (self.viewModel.onProgressBarAnimationStart, self.__onProgressBarAnimationStart),
         (self.viewModel.onProgressBarAnimationComplete, self.__onProgressBarAnimationComplete),
         (g_playerEvents.onDisconnected, self.__onClose)]

    def _onLoading(self, *args, **kwargs):
        super(PostBattleRewardsView, self)._onLoading(*args, **kwargs)
        self._addListeners()
        self._fillModel()

    def _finalize(self):
        self.__onProgressBarAnimationComplete()
        super(PostBattleRewardsView, self)._finalize()
        self._removeListeners()

    def _fillModel(self):
        with self.getViewModel().transaction() as vm:
            vm.setRank(self.__ctx.playerRank)
            vm.setPrevProgress(self.__ctx.prevProgress)
            vm.setCurrProgress(self.__ctx.currProgress)
            vm.setAchievedPoints(self.__ctx.achievedXP)
            vm.setMaxLevel(self.__ctx.maxLevel)
            vm.setIsMaxLevel(self.__ctx.isOnMaxLevel())
            vm.setAmountRewardsToClaim(self.__ctx.newRewardsCount)
            self.__fillRewards(vm)

    def _addListeners(self):
        self.__eventsCache.onSyncCompleted += self.__onServerSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged

    def _removeListeners(self):
        self.__eventsCache.onSyncCompleted -= self.__onServerSettingsChanged
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged

    def __fillRewards(self, vm):
        tokenBonusesGroups = defaultdict(list)
        otherBonuses = []
        for sourceBonus in self.__ctx.bonuses:
            name = sourceBonus.getName()
            if name == EPIC_SELECT_BONUS_NAME:
                for key in sourceBonus.getValue():
                    splitKey = key.rsplit(':', 2)[0]
                    tokenBonusesGroups[splitKey].append(sourceBonus)

            otherBonuses.append(sourceBonus)

        tokenBonuses = []
        for tokenBonusesGroup in tokenBonusesGroups.values():
            tokenBonuses += mergeBonuses(tokenBonusesGroup)

        bonuses = sorted(mergeBonuses(otherBonuses) + tokenBonuses, key=lambda item: self._BONUS_ORDER_PRIORITY.get(item.getName(), self._MIDDLE_PRIORITY))
        rewardsList = vm.getRewards()
        self.__rewardsList = rewardsList
        packBonusModelAndTooltipData(bonuses, rewardsList, self.__tooltipItems)

    def __onClaimRewards(self):
        rewards = []

        def _onAwardsAnimationEnded():
            if self.__rewardsSelectionWindow:
                self.__rewardsSelectionWindow.destroy()

        def _onRewardReceived(rs):
            rewards.extend(rs)
            if rewards:
                showFrontlineAwards(bonuses=rewards, onAnimationEndedCallback=_onAwardsAnimationEnded)

        currLvl, _ = self.__epicController.getPlayerLevelInfo()
        self.__rewardsSelectionWindow = showEpicRewardsSelectionWindow(level=currLvl, onRewardsReceivedCallback=_onRewardReceived, onLoadedCallback=self.__onClose, isAutoDestroyWindowsOnReceivedRewards=False)

    def __onEpicUpdated(self, diff):
        if 'metaLevel' in diff:
            self._fillModel()

    def __onClose(self):
        self.destroyWindow()

    def __onContinue(self):
        arenaUniqueID = self.__ctx.arenaUniqueID
        if arenaUniqueID and self.__battleResultsService.areResultsPosted(arenaUniqueID):
            self.__battleResultsService.notifyBattleResultsPosted(arenaUniqueID, True)
        self.destroyWindow()

    def __onServerSettingsChanged(self, *_):
        if not self.__epicController.isEnabled():
            self.destroy()

    def __onIntroStartsPlaying(self):
        SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_ACHIEVED_RANK)

    def __onRibbonStartsPlaying(self):
        if self.__ctx.isMaxLevelReached():
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED_MAX)
        else:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_LEVEL_REACHED)

    def __onProgressBarAnimationStart(self):
        if not self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_START)
            self.__isProgressBarAnimating = True

    def __onProgressBarAnimationComplete(self):
        if self.__isProgressBarAnimating:
            SoundGroups.g_instance.playSound2D(EPIC_METAGAME_WWISE_SOUND_EVENTS.EB_PROGRESS_BAR_STOP)
            self.__isProgressBarAnimating = False


class PostBattleRewardsWindow(WindowImpl):

    def __init__(self, ctx=None, parent=None):
        super(PostBattleRewardsWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=PostBattleRewardsView(ctx=ctx), layer=WindowLayer.WINDOW, parent=parent)
