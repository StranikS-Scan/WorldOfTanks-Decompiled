# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_progressions_view.py
import logging
from operator import itemgetter
import typing
import SoundGroups
from account_helpers.AccountSettings import AccountSettings, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.offers.cache import CachePrefetchResult
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from adisp import process, async
from battle_pass_common import BattlePassConsts, BattlePassState, getBattlePassVoteToken
from frameworks.wulf import ViewSettings, ViewFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.store.browser import shop_helpers
from gui.Scaleform.daapi.view.meta.MissionsBattlePassViewMeta import MissionsBattlePassViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_pass.battle_pass_bonuses_helper import TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, changeBonusTooltipData
from gui.battle_pass.battle_pass_helpers import getExtrasVideoPageURL, getFormattedTimeLeft, isSeasonEndingSoon, isCurrentBattlePassStateBase, isNeededToVote, getInfoPageURL, getIntroVideoURL, BattlePassProgressionSubTabs, getSeasonHistory, BackgroundPositions, showOfferTrophyDevices, showOfferNewDevices
from gui.battle_pass.battle_pass_award import BattlePassAwardsManager
from gui.battle_pass.undefined_bonuses import isUndefinedBonusTooltipData, createUndefinedBonusTooltipWindow
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_progressions_view_model import BattlePassProgressionsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_lock_icon_tooltip_view import BattlePassLockIconTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_points_view import BattlePassPointsTooltip
from gui.impl.lobby.battle_pass.tooltips.battle_pass_progress_warning_tooltip_view import BattlePassProgressWarningTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattleVotingResultWindow, showBrowserOverlayView, showHangar, showShop, showBattlePassOnboardingWindow
from gui.shared.formatters import text_styles
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable, SimpleNotifier
from helpers import dependency, time_utils
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.offers import IOffersDataProvider
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
_logger = logging.getLogger(__name__)

class BattlePassProgressionsComponent(InjectComponentAdaptor, MissionsBattlePassViewMeta, LobbySubView):
    __slots__ = ()

    def as_showViewS(self):
        super(BattlePassProgressionsComponent, self).as_showViewS()
        self.as_setWaitingVisibleS(False)

    def markVisited(self):
        pass

    def dummyClicked(self, eventType):
        if eventType == 'OpenHangar':
            showHangar()

    def _makeInjectView(self):
        self.as_setWaitingVisibleS(True)
        return BattlePassProgressionsView(self.__showDummy, self.as_showViewS, flags=ViewFlags.COMPONENT)

    def setSubTab(self, subTab):
        if self._injectView is not None:
            self._injectView.setSubTab(subTab)
        return

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
    __itemsCache = dependency.descriptor(IItemsCache)
    __offersProvider = dependency.descriptor(IOffersDataProvider)
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

    def setSubTab(self, subTab):
        self.__clearSubViews()
        if subTab == BattlePassProgressionSubTabs.VOTING_TAB:
            showBattleVotingResultWindow(parent=self.getParentWindow())
            if isNeededToVote():
                self.__battlePassController.getFinalRewardLogic().postVotingOpened(isVotingOpen=True)
        elif subTab == BattlePassProgressionSubTabs.BUY_TAB:
            self.__showBattlePassBuyWindow()
        elif subTab == BattlePassProgressionSubTabs.BUY_TAB_FOR_SHOP:
            self.__showBattlePassBuyWindow(backCallback=showShop)
        elif subTab == BattlePassProgressionSubTabs.ONBOARDING_TAB:
            showBattlePassOnboardingWindow(parent=self.getParentWindow())

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoading()
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
        SoundGroups.g_instance.playSound2D(backport.sound(R.sounds.bp_progress_bar_stop()))
        self.__removeListeners()
        self.__showDummyCallback = None
        self.__showViewCallback = None
        self.__tooltipItems = None
        self.__battlePassController.getVotingRequester().stopGetting()
        if self.viewModel.getShowIntro():
            self.__setBattlePassIntroShown()
        self.__notifier.stopNotification()
        self.__notifier.clearNotification()
        return

    def __showDummy(self):
        if self.__showDummyCallback is not None:
            self.__showDummyCallback(True)
            with self.viewModel.transaction() as model:
                model.setIsPaused(True)
        return

    def __hideDummy(self):
        if self.__showDummyCallback is not None:
            self.__showDummyCallback(False)
            with self.viewModel.transaction() as model:
                model.setIsPaused(False)
        return

    def __onBuyClick(self):
        if self.__battlePassController.isSellAnyLevelsUnlocked():
            self.__setBuyButtonHintShown()
            self.__updateBuyButtonState()
        with self.viewModel.transaction() as model:
            model.setShowBuyAnimations(False)
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        if self.viewModel.buyButton.getState() == self.viewModel.buyButton.ONBOARDING:
            self.setSubTab(BattlePassProgressionSubTabs.ONBOARDING_TAB)
        else:
            self.setSubTab(BattlePassProgressionSubTabs.BUY_TAB)

    def __onVotingResultClick(self):
        self.setSubTab(BattlePassProgressionSubTabs.VOTING_TAB)

    def __onIntroCloseClick(self):
        self.viewModel.setShowIntro(False)
        self.__setBattlePassIntroShown()

    def __onExtrasClick(self):
        self.__loadUrl(getExtrasVideoPageURL())

    def __onAboutClick(self):
        self.__loadUrl(getInfoPageURL())

    @staticmethod
    def __onBuyVehicleClick():
        showShop(shop_helpers.getBuyVehiclesUrl())

    @staticmethod
    def __onTrophySelectClick():
        showOfferTrophyDevices()

    @staticmethod
    def __onNewDeviceSelectClick():
        showOfferNewDevices()

    @staticmethod
    def __onClose():
        showHangar()

    @staticmethod
    def __loadUrl(url):
        showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __showIntro(self):
        with self.viewModel.transaction() as tx:
            self.__showIntroVideo(onStart=True)
            tx.setShowIntro(self.__isFirstShowView())
            self.__setShowBuyAnimations(model=tx)

    def __isFirstShowView(self):
        return not self.__settingsCore.serverSettings.getBPStorage().get(BattlePassStorageKeys.INTRO_SHOWN)

    def __setBattlePassIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})

    def __updateProgressData(self):
        isPaused = self.__battlePassController.isPaused()
        if isPaused:
            self.__showDummy()
        elif self.__battlePassController.isOffSeasonEnable():
            self.__hideDummy()
            self.__updateOffSeason()
        else:
            self.__hideDummy()
            self.__showIntro()
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
        self.__setMedalReward(model)

    def __setMedalReward(self, model):
        maxLevel = self.__battlePassController.getMaxLevel()
        freeRewards = self.__battlePassController.getSingleAward(maxLevel)
        dossierBonus = findFirst(lambda b: b.getName() == 'dossier', freeRewards)
        if dossierBonus is None:
            return
        else:
            randomStats = self.__itemsCache.items.getAccountDossier().getRandomStats()
            achievements = dossierBonus.getAchievementsFromDossier(randomStats)
            if not achievements:
                return
            model.setHaveMedalReward(achievements[-1].isInDossier())
            model.medalReward.clearItems()
            packBonusModelAndTooltipData([dossierBonus], model.medalReward, self.__tooltipItems)
            return

    def __setFinalReward(self, model):
        finalLevel = self.__battlePassController.getMaxLevel()
        freeReward, paidReward = self.__battlePassController.getSplitFinalAwards()
        freeModel = model.freeRewards.getItem(finalLevel - 1)
        paidModel = model.paidRewards.getItem(finalLevel - 1)
        self.__removeMedals(freeModel)
        packBonusModelAndTooltipData(freeReward, freeModel.rewardItems, self.__tooltipItems)
        packBonusModelAndTooltipData(paidReward, paidModel.rewardItems, self.__tooltipItems)

    @staticmethod
    def __removeMedals(model):
        freeItems = model.rewardItems.getItems()
        indexes = []
        for index, item in enumerate(freeItems):
            if item.getName() == 'dossier_achievement':
                indexes.append(index)

        model.rewardItems.removeItemByIndexes(indexes)

    def __setRewardsList(self, awardType, model):
        model.clearItems()
        curLevel = self.__battlePassController.getCurrentLevel()
        curState = self.__battlePassController.getState()
        isBattlePassBought = self.__battlePassController.isBought()
        bonuses = sorted(self.__battlePassController.getAwardsList(awardType).iteritems(), key=itemgetter(0))
        state = BattlePassState.POST if awardType == BattlePassConsts.REWARD_POST else BattlePassState.BASE
        isBase = state == BattlePassState.BASE
        for level, award in bonuses:
            item = RewardLevelModel()
            item.setLevelPoints(self.__battlePassController.getLevelPoints(level - 1, isBase))
            item.setIsRare(self.__battlePassController.isRareLevel(level, isBase))
            levelState = self.__getRewardLevelState(awardType, curLevel, level, curState, state, isBattlePassBought)
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
            if level == 0:
                continue
            item = model.getItem(level - 1)
            levelState = self.__getRewardLevelState(awardType, curLevel, level, curState, state, isBattlePassBought)
            item.setState(levelState)

        model.invalidate()

    def __getRewardLevelState(self, awardType, curLevel, level, curState, state, isBattlePassBought):
        isReached = curLevel >= level and state == curState or curState > state
        if awardType == BattlePassConsts.REWARD_PAID and not isBattlePassBought:
            levelState = RewardLevelModel.DISABLED
        else:
            levelState = RewardLevelModel.REACHED if isReached else RewardLevelModel.NOT_REACHED
        for bonusName in (TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME):
            container = self.__battlePassController.getDeviceTokensContainer(bonusName)
            hasFreeToken = level in container.freeTokenPositions and awardType == BattlePassConsts.REWARD_FREE
            hasPaidToken = level in container.paidTokenPositions and awardType == BattlePassConsts.REWARD_PAID
            if (hasFreeToken or hasPaidToken) and not container.isTokenUsed(level, awardType):
                levelState = RewardLevelModel.NOT_CHOSEN

        return levelState

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
                previousTotalPoints = self.__battlePassController.getMaxPoints(isBase=False)
        if currentState == BattlePassState.POST:
            currentTotalPoints -= self.__battlePassController.getMaxPoints()
        elif currentState == BattlePassState.COMPLETED:
            currentTotalPoints = self.__battlePassController.getMaxPoints(isBase=False)
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
        canPlayerParticipate = self.__battlePassController.canPlayerParticipate()
        if self.__battlePassController.isOnboardingActive() and not canPlayerParticipate:
            model.setProgressionState(model.ONBOARDING)
        elif not canPlayerParticipate:
            model.setProgressionState(model.LACK_OF_VEHICLES)
        else:
            model.setProgressionState(model.NORMAL)
        if self.__battlePassController.isSeasonFinished():
            model.setSeasonTime(backport.text(R.strings.battle_pass_2020.commonProgression.body.ended()))
        else:
            timeStart = self.__battlePassController.getSeasonStartTime()
            timeEnd = self.__battlePassController.getSeasonFinishTime()
            timePeriod = '{} - {}'.format(self.__makeSeasonTimeText(timeStart), self.__makeSeasonTimeText(timeEnd))
            model.setSeasonTime(timePeriod)
        self.__updateDeviceSelectButtons(model=model)

    def __updateOffSeason(self):
        prevSeasonStats = self.__battlePassController.getLastFinishedSeasonStats()
        if prevSeasonStats is None:
            self.__showDummy()
            _logger.warning('There is not previous season stats')
            return
        else:
            prevOtherStats = prevSeasonStats.otherStats
            prevSeasonHistory = getSeasonHistory(prevSeasonStats.seasonID)
            if prevSeasonHistory is None:
                self.__showDummy()
                _logger.warning('There is not previous season %r history', prevSeasonStats.seasonID)
                return
            sumPoints = sum(prevSeasonStats.vehPoints)
            if prevOtherStats.maxBase == prevSeasonHistory.maxBaseLevel:
                currentLevel = prevOtherStats.maxPost
                state = BattlePassState.POST
            else:
                currentLevel = prevOtherStats.maxBase
                state = BattlePassState.BASE
            if prevOtherStats.maxPost >= prevSeasonHistory.maxPostLevel:
                state = BattlePassState.COMPLETED
            with self.viewModel.transaction() as tx:
                tx.setShowOffSeason(True)
                offSeason = tx.offSeason
                offSeason.setLevel(currentLevel + 1)
                offSeason.setSeasonName(backport.text(R.strings.battle_pass_2020.offSeason.title()))
                offSeason.setHasBattlePass(self.__battlePassController.isBought(prevSeasonStats.seasonID))
                offSeason.setIsPostProgression(state != BattlePassState.BASE)
                offSeason.setIsPostProgressionCompleted(state == BattlePassState.COMPLETED)
                offSeason.setIsEnabled(sumPoints > 0)
                for vehCD in prevSeasonHistory.rewardVehicles:
                    vehicle = self.__itemsCache.items.getItemByCD(vehCD)
                    vehicleBackgroundPosition = BattlePassAwardsManager.getVehicleBackgroundPosition(vehCD)
                    if vehicleBackgroundPosition == BackgroundPositions.LEFT:
                        offSeason.setLeftVehicle(vehicle.userName)
                    if vehicleBackgroundPosition == BackgroundPositions.RIGHT:
                        offSeason.setRightVehicle(vehicle.userName)

                self.__updateVotingResult(model=tx)
            return

    @replaceNoneKwargsModel
    def __updateVotingResult(self, model=None):
        votingRequester = self.__battlePassController.getVotingRequester()
        prevSeasonStats = self.__battlePassController.getLastFinishedSeasonStats()
        if prevSeasonStats is None:
            return
        else:
            availableService, votingResult = votingRequester.startGettingResults(prevSeasonStats.seasonID)
            isFailedService = not availableService or not votingResult
            offSeason = model.offSeason
            offSeason.setIsFailedService(isFailedService)
            if len(votingResult) != 2:
                _logger.error('Incorrect voting results - %s', votingResult)
                if len(votingResult) > 2:
                    return
                _logger.error('Trying to build results from history')
                prevSeasonHistory = getSeasonHistory(prevSeasonStats.seasonID)
                for vehCD in prevSeasonHistory.rewardVehicles:
                    if vehCD not in votingResult:
                        votingResult[vehCD] = 0

            selectedVehCD = self.__getSelectedVoteOptionFromTokens(prevSeasonStats.seasonID, votingResult.keys())
            winVehCD, _ = max(votingResult.iteritems(), key=itemgetter(1))
            if not selectedVehCD:
                offSeason.setVoteStatus(offSeason.NOT_VOTE)
            elif winVehCD == selectedVehCD:
                offSeason.setVoteStatus(offSeason.WIN_VOTE)
            else:
                offSeason.setVoteStatus(offSeason.LOSE_VOTE)
            for vehCD, voices in votingResult.iteritems():
                vehiclePosition = BattlePassAwardsManager.getVehicleBackgroundPosition(vehCD)
                if vehiclePosition == BackgroundPositions.LEFT:
                    offSeason.setLeftPoints(voices)
                if vehiclePosition == BackgroundPositions.RIGHT:
                    offSeason.setRightPoints(voices)

            return

    def __onVotingResultsUpdated(self):
        if self.viewModel.getShowOffSeason():
            self.__updateVotingResult()

    def __updateBuyButtonState(self):
        isOnboardingActive = self.__battlePassController.isOnboardingActive()
        isBattlePassBought = self.__battlePassController.isBought()
        isVisible = isCurrentBattlePassStateBase() or not isBattlePassBought or isOnboardingActive
        if not isVisible:
            with self.viewModel.transaction() as model:
                model.setIsVisibleBuyButton(isVisible)
            return
        sellAnyLevelsUnlocked = self.__battlePassController.isSellAnyLevelsUnlocked()
        disableBuyButton = not sellAnyLevelsUnlocked and self.__battlePassController.getBoughtLevels() > 0
        isHighlightOn = False
        showBubble = False
        sellAnyLevelsUnlockTimeLeft = ''
        seasonTimeLeft = ''
        if self.__battlePassController.isPlayerNewcomer():
            state = self.viewModel.buyButton.ONBOARDING
            isHighlightOn = not self.__battlePassController.canPlayerParticipate()
        elif disableBuyButton:
            state = self.viewModel.buyButton.DISABLE
            sellAnyLevelsUnlockTimeLeft = getFormattedTimeLeft(self.__battlePassController.getSellAnyLevelsUnlockTimeLeft())
        else:
            if not isBattlePassBought:
                state = self.viewModel.buyButton.BUY_BP
            else:
                state = self.viewModel.buyButton.BUY_LEVELS
            showBubble = sellAnyLevelsUnlocked and not self.__isBuyButtonHintShown() and isCurrentBattlePassStateBase()
            isHighlightOn = isSeasonEndingSoon()
            if isHighlightOn:
                seasonTimeLeft = getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft())
        with self.viewModel.transaction() as model:
            model.setIsVisibleBuyButton(isVisible)
            buyButtonModel = model.buyButton
            buyButtonModel.setState(state)
            buyButtonModel.setIsHighlightOn(isHighlightOn)
            buyButtonModel.setSeasonTimeLeft(seasonTimeLeft)
            buyButtonModel.setSellAnyLevelsUnlockTimeLeft(sellAnyLevelsUnlockTimeLeft)
            buyButtonModel.setShowBuyButtonBubble(showBubble)

    def __updateExtrasAndVotingButtons(self):
        with self.viewModel.transaction() as tx:
            tx.setHighlightVoting(isNeededToVote())
            tx.setIsPlayerVoted(self.__battlePassController.isPlayerVoted())

    @process
    @replaceNoneKwargsModel
    def __updateDeviceSelectButtons(self, model=None):
        newDeviceTokensCount = self.__battlePassController.getNewDeviceSelectTokensCount()
        trophyTokensCount = self.__battlePassController.getTrophySelectTokensCount()
        model.setTrophySelectCount(trophyTokensCount)
        model.setNewDeviceSelectCount(newDeviceTokensCount)
        model.setIsChooseDeviceEnabled(False)
        if any((newDeviceTokensCount, trophyTokensCount)):
            result = yield self.__syncOfferResources()
            model.setIsChooseDeviceEnabled(self.__battlePassController.isChooseDeviceEnabled() and result == CachePrefetchResult.SUCCESS)

    @async
    @process
    def __syncOfferResources(self, callback=None):
        Waiting.show('loadContent')
        result = yield self.__offersProvider.isCdnResourcesReady()
        Waiting.hide('loadContent')
        callback(result)

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
        model.onBuyVehicleClick += self.__onBuyVehicleClick
        model.onTrophySelectClick += self.__onTrophySelectClick
        model.onNewDeviceSelectClick += self.__onNewDeviceSelectClick
        self.__battlePassController.onPointsUpdated += self.__onPointsUpdated
        self.__battlePassController.onVoted += self.__onVoted
        self.__battlePassController.onBattlePassIsBought += self.__onBattlePassBought
        self.__battlePassController.onUnlimitedPurchaseUnlocked += self.__updateBuyButtonState
        self.__battlePassController.getVotingRequester().onVotingResultsUpdated += self.__onVotingResultsUpdated
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__battlePassController.onOnboardingChange += self.__onOnboardingChange
        self.__battlePassController.onDeviceSelectChange += self.__onDeviceSelectChange
        self.__battlePassController.onSeasonStateChange += self.__updateProgressData
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
        model.onBuyVehicleClick -= self.__onBuyVehicleClick
        model.onTrophySelectClick -= self.__onTrophySelectClick
        model.onNewDeviceSelectClick -= self.__onNewDeviceSelectClick
        self.__battlePassController.onPointsUpdated -= self.__onPointsUpdated
        self.__battlePassController.onVoted -= self.__onVoted
        self.__battlePassController.onBattlePassIsBought -= self.__onBattlePassBought
        self.__battlePassController.onUnlimitedPurchaseUnlocked -= self.__updateBuyButtonState
        self.__battlePassController.getVotingRequester().onVotingResultsUpdated -= self.__onVotingResultsUpdated
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__battlePassController.onOnboardingChange -= self.__onOnboardingChange
        self.__battlePassController.onDeviceSelectChange -= self.__onDeviceSelectChange
        self.__battlePassController.onSeasonStateChange -= self.__updateProgressData
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.FocusEvent.COMPONENT_FOCUSED, self.__onFocus)
        g_eventBus.removeListener(events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getDayMonth(timeStamp):
        timeStruct = time_utils.getTimeStructInUTC(timeStamp)
        return (timeStruct.tm_mday, timeStruct.tm_mon)

    def __onMissionsTabChanged(self, event):
        viewActive = event.ctx == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS
        if self.__viewActive == viewActive and self.__viewActive:
            self.__clearSubViews()
        self.__viewActive = viewActive

    def __clearSubViews(self):
        views = self.__gui.windowsManager.findViews(lambda view: view.viewFlags & ViewFlags.VIEW_TYPE_MASK == ViewFlags.LOBBY_TOP_SUB_VIEW)
        for view in views:
            view.destroyWindow()

    def __onFocus(self, event):
        context = event.ctx
        if context.get('alias') == VIEW_ALIAS.LOBBY_MISSIONS:
            if self.__viewActive:
                self.__setShowBuyAnimations()

    def __onBattlePassSettingsChange(self, *_):
        if not self.__battlePassController.isEnabled():
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

    def __onDeviceSelectChange(self):
        self.__updateDeviceSelectButtons()
        for bonusName in (TROPHY_GIFT_TOKEN_BONUS_NAME, NEW_DEVICE_GIFT_TOKEN_BONUS_NAME):
            tokensContainer = self.__battlePassController.getDeviceTokensContainer(bonusName)
            curLevel = self.__battlePassController.getCurrentLevel()
            with self.viewModel.transaction() as model:
                for pos in tokensContainer.freeTokenPositions:
                    if 0 < pos < curLevel:
                        self.__resetRewardsInterval(BattlePassConsts.REWARD_FREE, model.freeRewards, pos, pos)

                for pos in tokensContainer.paidTokenPositions:
                    if 0 < pos < curLevel:
                        self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, pos, pos)

    def __onPurchaseLevels(self, _):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = True

    def __onOnboardingChange(self):
        self.__updateBuyButtonState()
        self.__updateProgressData()

    def __getTooltipContentCreator(self):
        return {R.views.lobby.battle_pass.tooltips.BattlePassPointsView(): self.__getBattlePassPointsTooltipContent,
         R.views.lobby.battle_pass.tooltips.BattlePassLockIconTooltipView(): self.__getBattlePassLockIconTooltipContent,
         R.views.lobby.battle_pass.tooltips.BattlePassProgressWarningTooltipView(): self.__getBattlePassProgressWarningTooltipContent}

    @replaceNoneKwargsModel
    def __setShowBuyAnimations(self, model=None):
        showAnimations = False
        if self.__battlePassController.isBought():
            settings = self.__settingsCore.serverSettings
            if not settings.getBPStorage().get(BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN):
                showAnimations = True
                settings.saveInBPStorage({BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN: True})
        model.setShowBuyAnimations(showAnimations)
        model.setAreSoundsAllowed(True)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False

    @staticmethod
    def __getBattlePassPointsTooltipContent(_=None):
        return BattlePassPointsTooltip()

    @staticmethod
    def __getBattlePassLockIconTooltipContent(_=None):
        return BattlePassLockIconTooltipView()

    @staticmethod
    def __getBattlePassProgressWarningTooltipContent(_=None):
        return BattlePassProgressWarningTooltipView()

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

    def __getSelectedVoteOptionFromTokens(self, seasonID, vehicleCDs):
        for vehCD in vehicleCDs:
            token = self.__itemsCache.items.tokens.getTokens().get(getBattlePassVoteToken(seasonID, vehCD))
            if token is not None:
                return vehCD

        return

    def __showBattlePassBuyWindow(self, backCallback=None):
        from gui.impl.lobby.battle_pass.battle_pass_buy_view import BattlePassBuyWindow
        ctx = {'backCallback': backCallback}
        view = self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassBuyView())
        if view is None:
            self.viewModel.setAreSoundsAllowed(False)
            window = BattlePassBuyWindow(ctx, self.getParentWindow())
            window.load()
        return
