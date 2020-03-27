# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_progressions_view.py
import typing
from operator import itemgetter
from battle_pass_common import BattlePassConsts, BattlePassState
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.managers.UtilsManager import ONE_SECOND
from helpers.func_utils import oncePerPeriod
from soft_exception import SoftException
from account_helpers.AccountSettings import AccountSettings, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, changeBonusTooltipData
from gui.battle_pass.undefined_bonuses import isUndefinedBonusTooltipData, createUndefinedBonusTooltipWindow
from gui.battle_pass.battle_pass_helpers import getExtrasVideoPageURL, getFormattedTimeLeft, isSeasonEndingSoon, isCurrentBattlePassStateBase, isNeededToVote, getInfoPageURL, getIntroVideoURL
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_progressions_view_model import BattlePassProgressionsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_lock_icon_tooltip_view import BattlePassLockIconTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_points_view import BattlePassPointsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.MissionsBattlePassViewMeta import MissionsBattlePassViewMeta
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePassBuyWindow, showBattleVotingResultWindow, showBrowserOverlayView, showHangar
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class BattlePassProgressionsComponent(InjectComponentAdaptor, MissionsBattlePassViewMeta, LobbySubView):
    __slots__ = ()

    def as_showViewS(self):
        super(BattlePassProgressionsComponent, self).as_showViewS()
        self.as_setWaitingVisibleS(False)

    def dummyClicked(self, eventType):
        if eventType == 'OpenHangar':
            showHangar()

    def _makeInjectView(self):
        self.as_setWaitingVisibleS(True)
        return BattlePassProgressionsView(self.__showDummy, self.as_showViewS, flags=ViewFlags.COMPONENT)

    def __showDummy(self, show):
        if show:
            self.as_setBackgroundS(backport.image(R.images.gui.maps.icons.battlePass2020.progression.bg()))
            self.as_showDummyS({'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ICON_ALERT_32X32,
             'htmlText': text_styles.main(backport.text(R.strings.battle_pass_2020.progression.error())),
             'alignCenter': True,
             'btnVisible': True,
             'btnLabel': backport.text(R.strings.battle_pass_2020.progression.errorBtn()),
             'btnTooltip': '',
             'btnEvent': 'OpenHangar',
             'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK})
        else:
            self.as_setBackgroundS('')
            self.as_hideDummyS()


class BattlePassProgressionsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__viewActive', '__tooltipContentCreator', '__showDummyCallback', '__showViewCallback', '__notifier')
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __gui = dependency.descriptor(IGuiLoader)
    ANIMATION_PURCHASE_LEVELS = 'animPurchaseLevels'
    ANIMATIONS = {ANIMATION_PURCHASE_LEVELS: False}

    def __init__(self, showDummyCallback, showViewCallback, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassProgressionsView())
        settings.flags = flags
        settings.model = BattlePassProgressionsViewModel()
        self.__showDummyCallback = showDummyCallback
        self.__showViewCallback = showViewCallback
        self.__tooltipItems = {}
        self.__viewActive = False
        self.__tooltipContentCreator = self.__getTooltipContentCreator()
        super(BattlePassProgressionsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassProgressionsView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getTooltipData(event)
            if tooltipData is None:
                return
            isGFTooltip = isUndefinedBonusTooltipData(tooltipData)
            if isGFTooltip:
                window = createUndefinedBonusTooltipWindow(tooltipData, self.getParentWindow())
            else:
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            if isGFTooltip:
                window.move(event.mouse.positionX, event.mouse.positionY)
            return window
        else:
            return super(BattlePassProgressionsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipContentCreator = self.__tooltipContentCreator.get(contentID)
        if tooltipContentCreator is None:
            raise SoftException('Incorrect tooltip type with contentID {}'.format(contentID))
        return tooltipContentCreator(event)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoading()
        with self.viewModel.transaction() as tx:
            self.__showIntroVideo(onStart=True)
            tx.setShowIntro(self.__isFirstShowView())
            self.__setShowBuyAnimations(model=tx)
        self.__addListeners()
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(PeriodicNotifier(self.__battlePassController.getSeasonTimeLeft, self.__updateTimer))
        self.__notifier.addNotificator(PeriodicNotifier(self.__battlePassController.getSellAnyLevelsUnlockTimeLeft, self.__updateTimer))
        self.__notifier.addNotificator(SimpleNotifier(self.__battlePassController.getFinalOfferTimeLeft, self.__updateTimer))
        self.__notifier.startNotification()
        self.__updateProgressData()
        self.__updateBuyButtonState()
        self.__updateExtrasAndVotingButtons()

    def _finalize(self):
        super(BattlePassProgressionsView, self)._finalize()
        self.__removeListeners()
        self.__showDummyCallback = None
        self.__showViewCallback = None
        self.__tooltipItems = None
        if self.viewModel.getShowIntro():
            self.__setBattlePassIntroShown()
        self.__notifier.stopNotification()
        self.__notifier.clearNotification()
        return

    def __showDummy(self):
        if self.__showDummyCallback is not None:
            self.__showDummyCallback(True)
        return

    def __hideDummy(self):
        if self.__showDummyCallback is not None:
            self.__showDummyCallback(False)
        return

    def __onBuyClick(self):
        if self.__battlePassController.isSellAnyLevelsUnlocked():
            self.__setBuyButtonHintShown()
            self.__updateBuyButtonState()
        with self.viewModel.transaction() as model:
            model.setShowBuyAnimations(False)
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        showBattlePassBuyWindow()

    @staticmethod
    @oncePerPeriod(ONE_SECOND)
    def __onVotingResultClick():
        showBattleVotingResultWindow()

    def __onIntroCloseClick(self):
        self.viewModel.setShowIntro(False)
        self.__setBattlePassIntroShown()

    def __onExtrasClick(self):
        self.__loadUrl(getExtrasVideoPageURL())

    def __onAboutClick(self):
        self.__loadUrl(getInfoPageURL())

    @staticmethod
    def __onClose():
        showHangar()

    @staticmethod
    def __loadUrl(url):
        showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __isFirstShowView(self):
        return not self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_SHOWN)

    def __setBattlePassIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})

    def __updateProgressData(self):
        isPaused = self.__battlePassController.isPaused()
        if isPaused:
            self.__showDummy()
            with self.viewModel.transaction() as model:
                self.__setIsPaused(isPaused, model)
        else:
            self.__hideDummy()
            with self.viewModel.transaction() as model:
                self.__setAwards(model)
                self.__setCurrentLevelState(model=model)

    def __getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def __setAwards(self, model):
        self.__tooltipItems.clear()
        self.__setRewardsList(BattlePassConsts.REWARD_FREE, model.freeRewards)
        self.__setRewardsList(BattlePassConsts.REWARD_PAID, model.paidRewards)
        self.__setRewardsList(BattlePassConsts.REWARD_POST, model.postRewards)
        self.__setFinalReward(model)

    def __setFinalReward(self, model):
        finalLevel = self.__battlePassController.getMaxLevel()
        freeReward, paidReward = self.__battlePassController.getSplitFinalAwards()
        freeModel = model.freeRewards.getItem(finalLevel - 1)
        paidModel = model.paidRewards.getItem(finalLevel - 1)
        self.__removeMedals(freeModel)
        packBonusModelAndTooltipData(freeReward, freeModel.rewardItems, self.__tooltipItems)
        packBonusModelAndTooltipData(paidReward, paidModel.rewardItems, self.__tooltipItems)

    def __removeMedals(self, model):
        freeItems = model.rewardItems.getItems()
        indexies = []
        for index, item in enumerate(freeItems):
            if item.getName() == 'dossier_achievement':
                indexies.append(index)

        model.rewardItems.removeItemByIndexes(indexies)

    def __setRewardsList(self, awardType, model):
        model.clearItems()
        bonuses = sorted(self.__battlePassController.getAwardsList(awardType).iteritems(), key=itemgetter(0))
        curLevel = self.__battlePassController.getCurrentLevel()
        curState = self.__battlePassController.getState()
        isBattlePassBought = self.__battlePassController.isBought()
        state = BattlePassState.POST if awardType == BattlePassConsts.REWARD_POST else BattlePassState.BASE
        isBase = state == BattlePassState.BASE
        for level, award in bonuses:
            item = RewardLevelModel()
            item.setLevel(level)
            item.setLevelPoints(self.__battlePassController.getLevelPoints(level - 1, isBase))
            item.setIsRare(self.__battlePassController.isRareLevel(level, isBase))
            isReached = curLevel >= level and state == curState or curState > state
            if awardType == BattlePassConsts.REWARD_PAID and not isBattlePassBought:
                levelState = RewardLevelModel.DISABLED
            else:
                levelState = RewardLevelModel.REACHED if isReached else RewardLevelModel.NOT_REACHED
            item.setState(levelState)
            packBonusModelAndTooltipData(award, item.rewardItems, self.__tooltipItems)
            model.addViewModel(item)

        model.invalidate()

    def __resetRewardsInterval(self, awardType, model, fromLevel, toLevel):
        curLevel = self.__battlePassController.getCurrentLevel()
        curState = self.__battlePassController.getState()
        isBattlePassBought = self.__battlePassController.isBought()
        state = BattlePassState.POST if awardType == BattlePassConsts.REWARD_POST else BattlePassState.BASE
        maxPostLevel = self.__battlePassController.getMaxLevel(False)
        if toLevel >= maxPostLevel and state == BattlePassState.POST:
            toLevel = maxPostLevel - 1
        for level in range(fromLevel, toLevel + 1):
            item = model.getItem(level)
            isReached = curLevel >= level and state == curState or curState > state
            if awardType == BattlePassConsts.REWARD_PAID and not isBattlePassBought:
                levelState = RewardLevelModel.DISABLED
            else:
                levelState = RewardLevelModel.REACHED if isReached else RewardLevelModel.NOT_REACHED
            item.setState(levelState)

        model.invalidate()

    @replaceNoneKwargsModel
    def __setCurrentLevelState(self, model=None):
        previousTotalPoints = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN)
        previousState, previousLevel = self.__battlePassController.getLevelByPoints(previousTotalPoints)
        previousPoints, _ = self.__battlePassController.getProgressionByPoints(previousTotalPoints, previousState, previousLevel)
        previousLevel += 1
        currentTotalPoints = self.__battlePassController.getCurrentPoints()
        currentState = self.__battlePassController.getState()
        currentLevel = self.__battlePassController.getCurrentLevel() + 1
        AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, currentTotalPoints)
        if previousState != currentState:
            if not (previousState == BattlePassState.POST and currentState == BattlePassState.COMPLETED):
                previousLevel = 1
                previousTotalPoints = 0
        if previousTotalPoints > currentTotalPoints or previousLevel > currentLevel:
            previousState = BattlePassState.BASE
            previousLevel = 1
            previousTotalPoints = 0
        previousLevel = min(previousLevel, self.__battlePassController.getMaxLevel(previousState == BattlePassState.BASE))
        currentLevel = min(currentLevel, self.__battlePassController.getMaxLevel(currentState == BattlePassState.BASE))
        if previousTotalPoints > 0:
            if previousState == BattlePassState.POST:
                previousTotalPoints -= self.__battlePassController.getMaxPoints()
            elif previousState == BattlePassState.COMPLETED:
                previousTotalPoints = self.__battlePassController.getMaxPoints(False)
        if currentState == BattlePassState.POST:
            currentTotalPoints -= self.__battlePassController.getMaxPoints()
        elif currentState == BattlePassState.COMPLETED:
            currentTotalPoints = self.__battlePassController.getMaxPoints(False)
        currentPoints, levelPoints = self.__battlePassController.getLevelProgression()
        isBattlePassBought = self.__battlePassController.isBought()
        model.setTitle(backport.text(R.strings.battle_pass_2020.progression.title()))
        model.setPreviousAllPoints(previousTotalPoints)
        model.setPreviousPoints(previousPoints)
        model.setPreviousLevel(previousLevel)
        model.setCurrentAllPoints(currentTotalPoints)
        model.setCurrentPoints(currentPoints)
        model.setTotalPoints(levelPoints)
        model.setCurrentLevel(currentLevel)
        model.setMaxLevelBase(self.__battlePassController.getMaxLevel())
        model.setMaxLevelPost(self.__battlePassController.getMaxLevel(False))
        model.setIsPostProgression(currentState != BattlePassState.BASE)
        model.setIsBattlePassPurchased(isBattlePassBought)
        isPaused = self.__battlePassController.isPaused()
        canBuy = self.__battlePassController.isActive() or currentLevel > 0 and not isPaused
        model.setIsPaused(isPaused)
        model.setCanBuy(canBuy)
        model.setSeasonTimeLeft(getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft()))
        if self.__battlePassController.isSeasonFinished():
            model.setSeasonTime(backport.text(R.strings.battle_pass_2020.commonProgression.body.ended()))
        else:
            timeStart = self.__battlePassController.getSeasonStartTime()
            timeEnd = self.__battlePassController.getSeasonFinishTime()
            timePeriod = '{} - {}'.format(self.__makeSeasonTimeText(timeStart), self.__makeSeasonTimeText(timeEnd))
            model.setSeasonTime(timePeriod)

    def __updateBuyButtonState(self):
        sellAnyLevelsUnlocked = self.__battlePassController.isSellAnyLevelsUnlocked()
        disableBuyButton = not sellAnyLevelsUnlocked and self.__battlePassController.getBoughtLevels() > 0
        showBubble = sellAnyLevelsUnlocked and not self.__isBuyButtonHintShown() and isCurrentBattlePassStateBase()
        isVisible = isCurrentBattlePassStateBase() or not self.__battlePassController.isBought()
        sellAnyLevelsUnlockTimeLeft = ''
        if disableBuyButton:
            sellAnyLevelsUnlockTimeLeft = getFormattedTimeLeft(self.__battlePassController.getSellAnyLevelsUnlockTimeLeft())
        with self.viewModel.transaction() as model:
            model.setIsFinalOfferTime(isSeasonEndingSoon())
            model.setSeasonTimeLeft(getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft()))
            model.setSellAnyLevelsUnlockTimeLeft(sellAnyLevelsUnlockTimeLeft)
            model.setShowBuyButtonBubble(showBubble)
            model.setIsVisibleBuyButton(isVisible)

    def __updateExtrasAndVotingButtons(self):
        with self.viewModel.transaction() as tx:
            tx.setHighlightVoting(isNeededToVote())
            tx.setIsPlayerVoted(self.__battlePassController.isPlayerVoted())

    def __updateTimer(self):
        self.viewModel.setSeasonTimeLeft(getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft()))
        self.__updateBuyButtonState()

    def __isBuyButtonHintShown(self):
        return self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.BUY_BUTTON_HINT_IS_SHOWN)

    def __setBuyButtonHintShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.BUY_BUTTON_HINT_IS_SHOWN: True})

    def __addListeners(self):
        model = self.viewModel
        model.onBuyClick += self.__onBuyClick
        model.onVotingResultClick += self.__onVotingResultClick
        model.onExtrasClick += self.__onExtrasClick
        model.onAboutClick += self.__onAboutClick
        model.onViewLoaded += self.__showViewCallback
        model.onClose += self.__onClose
        model.intro.onClose += self.__onIntroCloseClick
        model.intro.onVideo += self.__showIntroVideo
        self.__battlePassController.onPointsUpdated += self.__onPointsUpdated
        self.__battlePassController.onVoted += self.__onVoted
        self.__battlePassController.onBattlePassIsBought += self.__onBattlePassBought
        self.__battlePassController.onUnlimitedPurchaseUnlocked += self.__updateBuyButtonState
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.FocusEvent.COMPONENT_FOCUSED, self.__onFocus)
        g_eventBus.addListener(events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        model = self.viewModel
        model.onBuyClick -= self.__onBuyClick
        model.onVotingResultClick -= self.__onVotingResultClick
        model.onExtrasClick -= self.__onExtrasClick
        model.onAboutClick -= self.__onAboutClick
        model.onViewLoaded -= self.__showViewCallback
        model.onClose -= self.__onClose
        model.intro.onClose -= self.__onIntroCloseClick
        model.intro.onVideo -= self.__showIntroVideo
        self.__battlePassController.onPointsUpdated -= self.__onPointsUpdated
        self.__battlePassController.onVoted -= self.__onVoted
        self.__battlePassController.onBattlePassIsBought -= self.__onBattlePassBought
        self.__battlePassController.onUnlimitedPurchaseUnlocked -= self.__updateBuyButtonState
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.FocusEvent.COMPONENT_FOCUSED, self.__onFocus)
        g_eventBus.removeListener(events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getDayMonth(timeStamp):
        timeStruct = time_utils.getTimeStructInUTC(timeStamp)
        return (timeStruct.tm_mday, timeStruct.tm_mon)

    def __onMissionsTabChanged(self, event):

        def _predicateLobbyTopSubViews(view):
            return view.viewFlags & ViewFlags.VIEW_TYPE_MASK == ViewFlags.LOBBY_TOP_SUB_VIEW

        viewActive = event.ctx == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS
        if self.__viewActive == viewActive and self.__viewActive:
            views = self.__gui.windowsManager.findViews(_predicateLobbyTopSubViews)
            for view in views:
                view.destroyWindow()

        self.__viewActive = viewActive

    def __onFocus(self, event):
        context = event.ctx
        if context.get('alias') == VIEW_ALIAS.LOBBY_MISSIONS:
            if self.__viewActive:
                self.__setShowBuyAnimations()

    def __onBattlePassSettingsChange(self, *_):
        if not self.__battlePassController.isVisible() or self.__battlePassController.isPaused():
            showHangar()
        self.__updateProgressData()
        self.__updateBuyButtonState()

    def __onPointsUpdated(self):
        with self.viewModel.transaction() as model:
            oldPoints = model.getCurrentAllPoints()
            if model.getIsPostProgression():
                oldPoints += self.__battlePassController.getMaxPoints()
            newPoints = self.__battlePassController.getCurrentPoints()
            oldState, oldLevel = self.__battlePassController.getLevelByPoints(oldPoints)
            newState, newLevel = self.__battlePassController.getLevelByPoints(newPoints)
            if oldState == BattlePassState.BASE:
                if newState == oldState:
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_FREE, model.freeRewards, oldLevel, newLevel)
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, oldLevel, newLevel)
                else:
                    maxLevel = self.__battlePassController.getMaxLevel() - 1
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_FREE, model.freeRewards, oldLevel, maxLevel)
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, oldLevel, maxLevel)
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_POST, model.postRewards, 1, newLevel)
            elif oldState == BattlePassState.POST:
                if newState == oldState:
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_POST, model.postRewards, oldLevel, newLevel)
                else:
                    maxLevel = self.__battlePassController.getMaxLevel(False) - 1
                    self.__resetRewardsInterval(BattlePassConsts.REWARD_POST, model.postRewards, oldLevel, maxLevel)
            self.__setCurrentLevelState(model=model)
        isDrawPoints = newLevel < oldLevel or newPoints < oldPoints
        if isDrawPoints:
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.__updateBuyButtonState()
        self.__updateExtrasAndVotingButtons()

    def __onVoted(self):
        self.__updateFinalRewardTooltips()
        self.__updateExtrasAndVotingButtons()

    def __updateFinalRewardTooltips(self):
        maxLevel = self.__battlePassController.getMaxLevel()
        freeRewards, paidRewards = self.__battlePassController.getSplitFinalAwards()
        self.__updateTooltipsSingleCard(freeRewards, self.viewModel.freeRewards.getItem(maxLevel - 1))
        self.__updateTooltipsSingleCard(paidRewards, self.viewModel.paidRewards.getItem(maxLevel - 1))

    def __updateTooltipsSingleCard(self, rewards, model):
        tooltipIds = [ item.getTooltipId() for item in model.rewardItems.getItems() ]
        tooltipIds = tooltipIds[:len(rewards)]
        changeBonusTooltipData(zip(rewards, tooltipIds), self.__tooltipItems)

    def __onBattlePassBought(self):
        with self.viewModel.transaction() as model:
            maxLevel = self.__battlePassController.getMaxLevel() - 1
            self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, 1, maxLevel)
            self.__setCurrentLevelState(model=model)
        self.__updateBuyButtonState()

    def __onPurchaseLevels(self, _):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = True

    def __getTooltipContentCreator(self):
        return {R.views.lobby.battle_pass.tooltips.BattlePassPointsView(): self.__getBattlePassPointsTooltipContent,
         R.views.lobby.battle_pass.tooltips.BattlePassLockIconTooltipView(): self.__getBattlePassLockIconTooltipContent}

    def __setIsPaused(self, value, model=None):
        model.setIsPaused(value)

    @replaceNoneKwargsModel
    def __setShowBuyAnimations(self, model=None):
        showAnimations = False
        if self.__battlePassController.isBought():
            settings = self.__settingsCore.serverSettings
            if not settings.getBPStorage().get(BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN):
                showAnimations = True
                settings.saveInBPStorage({BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN: True})
        model.setShowBuyAnimations(showAnimations)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False

    @staticmethod
    def __getBattlePassPointsTooltipContent(_=None):
        return BattlePassPointsTooltip()

    @staticmethod
    def __getBattlePassLockIconTooltipContent(_=None):
        return BattlePassLockIconTooltipView()

    def __showIntroVideo(self, onStart=False):
        settings = self.__settingsCore.serverSettings
        if onStart:
            if settings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN):
                return
            settings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __makeSeasonTimeText(self, timeStamp):
        day, month = self.__getDayMonth(timeStamp)
        return backport.text(R.strings.battle_pass_2020.progression.seasonTime(), day=str(day), month=backport.text(R.strings.menu.dateTime.months.num(month)()))
