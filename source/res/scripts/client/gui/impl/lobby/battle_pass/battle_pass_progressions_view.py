# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_progressions_view.py
import logging
from operator import itemgetter
import typing
from account_helpers.AccountSettings import AccountSettings, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BattlePassConsts, BattlePassState
from frameworks.wulf import ViewSettings, ViewFlags, Array, ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl
from gui.Scaleform.daapi.view.meta.MissionsBattlePassViewMeta import MissionsBattlePassViewMeta
from gui.Scaleform.framework.entities.inject_component_adaptor import InjectComponentAdaptor
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData, changeBonusTooltipData
from gui.battle_pass.battle_pass_decorators import createTooltipContentDecorator, createBackportTooltipDecorator
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft, isSeasonEndingSoon, getInfoPageURL, getIntroVideoURL, BattlePassProgressionSubTabs, getSeasonHistory, getLevelFromStats, getDataByTankman, getStyleForChapter, getTankmanInfo, getNotChosen3DStylesCount
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_progressions_view_model import BattlePassProgressionsViewModel
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_lock_icon_tooltip_view import BattlePassLockIconTooltipView
from gui.impl.lobby.battle_pass.tooltips.battle_pass_points_view import BattlePassPointsTooltip
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePassCommonProgression
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView, showHangar, showShop, showBattlePassHowToEarnPointsView, showProgressionStylesStylePreview
from gui.shared.formatters import text_styles
from gui.shared.money import Currency
from gui.shared.utils.scheduled_notifications import PeriodicNotifier, Notifiable, SimpleNotifier
from helpers import dependency, time_utils, int2roman
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController, IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from soft_exception import SoftException
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel
_logger = logging.getLogger(__name__)
_rBattlePass = R.strings.battle_pass_2020

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
             'htmlText': text_styles.main(backport.text(_rBattlePass.progression.error())),
             'alignCenter': True,
             'btnVisible': True,
             'btnLabel': backport.text(_rBattlePass.progression.errorBtn()),
             'btnTooltip': '',
             'btnEvent': 'OpenHangar',
             'btnLinkage': BUTTON_LINKAGES.BUTTON_BLACK})
        else:
            self.as_setBackgroundS('')
            self.as_hideDummyS()


class BattlePassProgressionsView(ViewImpl):
    __slots__ = ('__tooltipItems', '__viewActive', '__tooltipContentCreator', '__showDummyCallback', '__showViewCallback', '__notifier', '__chosenChapter', '__showReplaceRewardAnimations')
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battlePassController = dependency.descriptor(IBattlePassController)
    __gui = dependency.descriptor(IGuiLoader)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
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
        self.__chosenChapter = self.__battlePassController.getCurrentChapter()
        self.__showReplaceRewardAnimations = False
        super(BattlePassProgressionsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattlePassProgressionsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassProgressionsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        tooltipContentCreator = self.__tooltipContentCreator.get(contentID)
        if tooltipContentCreator is None:
            raise SoftException('Incorrect tooltip type with contentID {}'.format(contentID))
        return tooltipContentCreator(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipItems.get(tooltipId)

    def setSubTab(self, subTab):
        self.__clearSubViews()
        if subTab == BattlePassProgressionSubTabs.BUY_TAB:
            self.__showBattlePassBuyWindow()
        elif subTab == BattlePassProgressionSubTabs.BUY_TAB_FOR_SHOP:
            self.__showBattlePassBuyWindow(backCallback=showShop)
        elif subTab == BattlePassProgressionSubTabs.BUY_LEVELS_TAB:
            self.__showBattlePassBuyLevelsWindow()
        elif subTab == BattlePassProgressionSubTabs.BUY_LEVELS_TAB_FROM_SHOP:
            self.__showBattlePassBuyLevelsWindow(backCallback=showShop)
        elif subTab == BattlePassProgressionSubTabs.SELECT_STYLE_TAB:
            self.__showStyleChoiceWindow()

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoading()
        self.__addListeners()
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(PeriodicNotifier(self.__battlePassController.getSeasonTimeLeft, self.__updateTimer))
        self.__notifier.addNotificator(SimpleNotifier(self.__battlePassController.getFinalOfferTimeLeft, self.__updateTimer))
        self.__notifier.startNotification()
        self.__updateProgressData()
        self.__updateBuyButtonState()

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
        self.__setBuyButtonHintShown()
        self.__updateBuyButtonState()
        with self.viewModel.transaction() as model:
            model.setShowBuyAnimations(False)
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        if self.__battlePassController.isBought(chapter=self.__chosenChapter):
            tab = BattlePassProgressionSubTabs.BUY_LEVELS_TAB
        else:
            tab = BattlePassProgressionSubTabs.BUY_TAB
        self.setSubTab(tab)

    def __onIntroCloseClick(self):
        if getNotChosen3DStylesCount() > 0:
            self.__onSelectStyle()
        self.viewModel.setShowIntro(False)
        self.__setBattlePassIntroShown()

    def __onAboutClick(self):
        self.__loadUrl(getInfoPageURL())

    @staticmethod
    def __onClose():
        showHangar()

    @staticmethod
    def __loadUrl(url):
        showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __showIntro(self):
        with self.viewModel.transaction() as tx:
            videoIsOpening = self.__showIntroVideo(onStart=True)
            tx.setShowIntro(self.__isFirstShowView())
            if not videoIsOpening:
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
                self.__updateBalance(model=model)
                self.__updateWalletAvailability(model=model)

    def __setAwards(self, model):
        self.__tooltipItems.clear()
        self.__setStyleWidget(model)
        self.__setRewardsList(BattlePassConsts.REWARD_FREE, model.freeRewards)
        self.__setRewardsList(BattlePassConsts.REWARD_PAID, model.paidRewards)
        self.__setChapterCharacter(model)
        self.__resetReplaceRewardAnimations(model=model)

    def __setStyleWidget(self, model):
        chosenItems = self.__itemsCache.items.battlePass.getChosenItems()
        if chosenItems is None or self.__chosenChapter not in chosenItems:
            style, level = (None, 0)
        else:
            intCD, level = chosenItems[self.__chosenChapter]
            style = self.__itemsCache.items.getItemByCD(intCD)
        isUnselectedPrevStyle = chosenItems is not None and self.__chosenChapter != BattlePassConsts.MINIMAL_CHAPTER_NUMBER and self.__chosenChapter - 1 not in chosenItems
        model.widget3dStyle.setStyleName(style.userName if style else '')
        model.widget3dStyle.setStyleId(style.id if style else 0)
        model.widget3dStyle.setLevel(level)
        model.widget3dStyle.setIsUnselectedPrevStyle(isUnselectedPrevStyle)
        return

    def __setChapterCharacter(self, model):
        _, maxLevel = self.__battlePassController.getChapterLevelInterval(self.__chosenChapter)
        freeModel = model.freeRewards.getItem(model.freeRewards.getItemsLength() - 1)
        tooltipId = self.__removeCharacter(freeModel)
        freeRewards = self.__battlePassController.getSingleAward(maxLevel)
        characterBonus = findFirst(lambda b: b.getName() == 'tmanToken', freeRewards)
        if characterBonus is None:
            self.__clearChapterCharacter(model)
            return
        else:
            character = getTankmanInfo(characterBonus)
            if character is None:
                self.__clearChapterCharacter(model)
                return
            iconName, characterName, skills = getDataByTankman(character)
            skillsArray = Array()
            for skill in skills:
                skillsArray.addString(skill)

            model.chapterCharacter.setIcon(iconName)
            model.chapterCharacter.setTankman(characterName)
            model.chapterCharacter.setSkills(skillsArray)
            if tooltipId is not None:
                model.chapterCharacter.setTooltipId(tooltipId)
            return

    @staticmethod
    def __clearChapterCharacter(model):
        model.chapterCharacter.setIcon('')
        model.chapterCharacter.setTankman('')
        model.chapterCharacter.setSkills(Array())

    @staticmethod
    def __removeCharacter(model):
        tooltipId = None
        freeItems = model.rewardItems.getItems()
        indexes = []
        for index, item in enumerate(freeItems):
            if item.getName() == 'tmanToken':
                indexes.append(index)
                tooltipId = item.getTooltipId()

        model.rewardItems.removeItemByIndexes(indexes)
        return tooltipId

    def __setRewardsList(self, awardType, model):
        model.clearItems()
        minLevel, maxLevel = self.__battlePassController.getChapterLevelInterval(self.__chosenChapter)
        curLevel = self.__battlePassController.getCurrentLevel()
        isBattlePassBought = self.__battlePassController.isBought(chapter=self.__chosenChapter)
        bonuses = sorted(self.__battlePassController.getAwardsInterval(minLevel, maxLevel, awardType).iteritems(), key=itemgetter(0))
        for level, awards in bonuses:
            item = RewardLevelModel()
            item.setLevel(level)
            item.setLevelPoints(self.__battlePassController.getLevelPoints(level - 1))
            item.setIsRare(self.__battlePassController.isRareLevel(level))
            levelState, isNeedToTake, isChooseRewardEnabled = self.__getRewardLevelState(awardType, curLevel, level, isBattlePassBought)
            item.setState(levelState)
            item.setNeedTake(isNeedToTake)
            item.setIsRewardChoiceEnabled(isChooseRewardEnabled)
            realAwards = self.__battlePassController.replaceOfferByReward(awards)
            packBonusModelAndTooltipData(realAwards, item.rewardItems, self.__tooltipItems)
            model.addViewModel(item)

        model.invalidate()

    def __resetRewardsInterval(self, awardType, model, fromLevel, toLevel, chapter, replaceRewards=False):
        curLevel = self.__battlePassController.getCurrentLevel()
        isBattlePassBought = self.__battlePassController.isBought()
        startLevel, finalLevel = self.__battlePassController.getChapterLevelInterval(chapter)
        if fromLevel <= startLevel:
            fromLevel = startLevel + 1
        if toLevel > finalLevel:
            toLevel = finalLevel
        for level in range(fromLevel, toLevel + 1):
            item = model.getItem(level - startLevel)
            levelState, isNeedToTake, isChooseRewardEnabled = self.__getRewardLevelState(awardType, curLevel, level, isBattlePassBought)
            if replaceRewards and item.getNeedTake() and not isNeedToTake:
                item.rewardItems.clearItems()
                awards = self.__battlePassController.getSingleAward(level, awardType)
                realAwards = self.__battlePassController.replaceOfferByReward(awards)
                packBonusModelAndTooltipData(realAwards, item.rewardItems, self.__tooltipItems)
                self.__showReplaceRewardAnimations = True
            item.setState(levelState)
            item.setNeedTake(isNeedToTake)
            item.setIsRewardChoiceEnabled(isChooseRewardEnabled)

        model.invalidate()

    def __getRewardLevelState(self, awardType, curLevel, level, isBattlePassBought):
        isReached = curLevel >= level or self.__battlePassController.getState() == BattlePassState.COMPLETED
        if awardType == BattlePassConsts.REWARD_PAID and not isBattlePassBought:
            levelState = RewardLevelModel.DISABLED
        else:
            levelState = RewardLevelModel.REACHED if isReached else RewardLevelModel.NOT_REACHED
        isNeedToTake = self.__battlePassController.isNeedToTakeReward(awardType, level)
        if isNeedToTake:
            isChooseRewardEnabled = self.__battlePassController.isChooseRewardEnabled(awardType, level)
        else:
            isChooseRewardEnabled = False
        return (levelState, isNeedToTake, isChooseRewardEnabled)

    @replaceNoneKwargsModel
    def __setCurrentLevelState(self, model=None):
        currentChapter = self.__battlePassController.getCurrentChapter()
        pointsBeforeChapterStart = self.__battlePassController.getFullChapterPoints(self.__chosenChapter, False)
        minLevel, maxLevel = self.__battlePassController.getChapterLevelInterval(self.__chosenChapter)
        if self.__chosenChapter == currentChapter:
            previousTotalPoints = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN)
            currentTotalPoints = self.__battlePassController.getCurrentPoints()
            AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, currentTotalPoints)
        elif self.__chosenChapter < currentChapter:
            previousTotalPoints = currentTotalPoints = self.__battlePassController.getFullChapterPoints(self.__chosenChapter, True)
        else:
            previousTotalPoints = currentTotalPoints = pointsBeforeChapterStart
        _, previousLevel = self.__battlePassController.getLevelByPoints(previousTotalPoints)
        previousPoints, _ = self.__battlePassController.getProgressionByPoints(previousTotalPoints, previousLevel)
        previousLevel += 1
        _, currentLevel = self.__battlePassController.getLevelByPoints(currentTotalPoints)
        currentLevel += 1
        if previousTotalPoints > currentTotalPoints or previousLevel > currentLevel:
            previousLevel = minLevel
            previousTotalPoints = pointsBeforeChapterStart
        previousLevel = min(max(previousLevel, minLevel - 1), maxLevel + 1)
        currentLevel = min(max(currentLevel, minLevel - 1), maxLevel + 1)
        previousTotalPoints = max(0, previousTotalPoints - pointsBeforeChapterStart)
        currentTotalPoints -= pointsBeforeChapterStart
        isBattlePassBought = self.__battlePassController.isBought(chapter=self.__chosenChapter)
        chapterConfig = self.__battlePassController.getChapterConfig()
        model.setChapterCount(len(chapterConfig))
        model.setChapterStep(first(chapterConfig, default=0))
        model.setChosenChapter(self.__chosenChapter)
        model.setCurrentChapter(currentChapter)
        model.setPointsBeforeStart(pointsBeforeChapterStart)
        chapterText = backport.text(_rBattlePass.progression.chapterText(), chapter=backport.text(_rBattlePass.chapter.name.num(self.__chosenChapter)()), chapterName=backport.text(_rBattlePass.chapter.fullName.num(self.__chosenChapter)()))
        model.setChapterText(chapterText)
        model.setPreviousAllPoints(previousTotalPoints)
        model.setPreviousPoints(previousPoints)
        model.setPreviousLevel(previousLevel)
        model.setCurrentAllPoints(currentTotalPoints)
        currentPoints, levelPoints = self.__battlePassController.getLevelProgression()
        if self.__chosenChapter != currentChapter:
            currentPoints = 0
            currentLevel = self.__battlePassController.getCurrentLevel() + 1
        currentLevel = min(currentLevel, self.__battlePassController.getMaxLevel())
        model.setCurrentPoints(currentPoints)
        model.setTotalPoints(levelPoints)
        model.setCurrentLevel(currentLevel)
        model.setIsBattlePassPurchased(isBattlePassBought)
        model.setIsPaused(self.__battlePassController.isPaused())
        model.setSeasonTimeLeft(getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft()))
        if self.__battlePassController.isSeasonFinished():
            model.setSeasonText(backport.text(_rBattlePass.commonProgression.body.ended()))
        else:
            seasonNum = self.__battlePassController.getSeasonNum()
            timeEnd = self.__battlePassController.getSeasonFinishTime()
            model.setSeasonText(self.__makeSeasonTimeText(timeEnd, seasonNum))
        self.__updateRewardSelectButton(model=model)

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
            seasonName = backport.text(_rBattlePass.offSeason.title(), season=int2roman(prevSeasonHistory.seasonNum))
            state, currentLevel = getLevelFromStats(prevOtherStats, prevSeasonHistory)
            with self.viewModel.transaction() as tx:
                tx.setShowOffSeason(True)
                offSeason = tx.offSeason
                offSeason.setLevel(currentLevel + 1)
                offSeason.setSeasonName(seasonName)
                offSeason.setHasBattlePass(self.__battlePassController.isBought(prevSeasonStats.seasonID))
                offSeason.setIsPostProgression(state != BattlePassState.BASE)
                offSeason.setIsPostProgressionCompleted(state == BattlePassState.COMPLETED)
                offSeason.setIsEnabled(sumPoints > 0)
            return

    def __updateBuyButtonState(self):
        currentLevel = self.__battlePassController.getCurrentLevel()
        isBattlePassBought = self.__battlePassController.isBought(chapter=self.__chosenChapter)
        minLevel, maxLevel = self.__battlePassController.getChapterLevelInterval(self.__chosenChapter)
        allLevelsComplete = maxLevel <= currentLevel or self.__battlePassController.getState() == BattlePassState.COMPLETED
        isVisible = not (isBattlePassBought and allLevelsComplete)
        if not isVisible:
            with self.viewModel.transaction() as model:
                model.setIsVisibleBuyButton(isVisible)
            return
        seasonTimeLeft = ''
        if minLevel > currentLevel + 1:
            if not isBattlePassBought:
                state = self.viewModel.buyButton.DISABLE_BP
            else:
                state = self.viewModel.buyButton.DISABLE_LEVELS
        elif not isBattlePassBought:
            state = self.viewModel.buyButton.BUY_BP
        else:
            state = self.viewModel.buyButton.BUY_LEVELS
        showBubble = not self.__isBuyButtonHintShown()
        isHighlightOn = isSeasonEndingSoon()
        if isHighlightOn:
            seasonTimeLeft = getFormattedTimeLeft(self.__battlePassController.getSeasonTimeLeft())
        with self.viewModel.transaction() as model:
            model.setIsVisibleBuyButton(isVisible)
            buyButtonModel = model.buyButton
            buyButtonModel.setState(state)
            buyButtonModel.setIsHighlightOn(isHighlightOn)
            buyButtonModel.setSeasonTimeLeft(seasonTimeLeft)
            buyButtonModel.setShowBuyButtonBubble(showBubble)

    @replaceNoneKwargsModel
    def __updateRewardSelectButton(self, model=None):
        model.setIsChooseDeviceEnabled(False)
        model.setIsTakeAllButtonVisible(False)
        notChosenRewardCount = self.__battlePassController.getNotChosenRewardCount()
        if notChosenRewardCount:
            model.setIsTakeAllButtonVisible(True)
            notChosenStylesCount = getNotChosen3DStylesCount(battlePass=self.__battlePassController, itemsCache=self.__itemsCache)
            model.setIsChooseDeviceEnabled(self.__battlePassController.isChooseRewardsEnabled() or notChosenStylesCount > 0)
            notChosenRewardCount += notChosenStylesCount
            model.setNotChosenRewardCount(notChosenRewardCount)

    @replaceNoneKwargsModel
    def __updateRewardSelectButtons(self, model=None):
        startLevel = 1
        finalLevel = self.__battlePassController.getMaxLevel()
        self.__resetRewardSelectButtons(BattlePassConsts.REWARD_FREE, model.freeRewards, startLevel, finalLevel, self.__chosenChapter)
        self.__resetRewardSelectButtons(BattlePassConsts.REWARD_PAID, model.paidRewards, startLevel, finalLevel, self.__chosenChapter)

    def __resetRewardSelectButtons(self, awardType, model, fromLevel, toLevel, chapter):
        startLevel, finalLevel = self.__battlePassController.getChapterLevelInterval(chapter)
        if fromLevel <= startLevel:
            fromLevel = startLevel + 1
        if toLevel > finalLevel:
            toLevel = finalLevel
        for level in range(fromLevel, toLevel + 1):
            item = model.getItem(level - startLevel)
            isChooseRewardEnabled = self.__battlePassController.isChooseRewardEnabled(awardType, level)
            item.setIsRewardChoiceEnabled(isChooseRewardEnabled)

        model.invalidate()

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
        model.onAboutClick += self.__onAboutClick
        model.onViewLoaded += self.__showViewCallback
        model.onClose += self.__onClose
        model.intro.onClose += self.__onIntroCloseClick
        model.intro.onVideo += self.__showIntroVideo
        model.onGoToChapter += self.__onGoToChapter
        model.widget3dStyle.onPreviewClick += self.__onPreviewClick
        model.widget3dStyle.onSelectStyle += self.__onSelectStyle
        model.onTakeClick += self.__onTakeClick
        model.onTakeAllClick += self.__onTakeAllClick
        model.onOpenShopClick += self.__onOpenShopClick
        model.onPointsInfoClick += self.__onPointsInfoClick
        model.onFinishedAnimation += self.__resetReplaceRewardAnimations
        self.__battlePassController.onPointsUpdated += self.__onPointsUpdated
        self.__battlePassController.onBattlePassIsBought += self.__onBattlePassBought
        self.__battlePassController.onBattlePassSettingsChange += self.__onBattlePassSettingsChange
        self.__battlePassController.onRewardSelectChange += self.__onRewardSelectChange
        self.__battlePassController.onOffersUpdated += self.__onOffersUpdated
        self.__battlePassController.onSeasonStateChange += self.__updateProgressData
        self.__wallet.onWalletStatusChanged += self.__updateWalletAvailability
        g_clientUpdateManager.addCurrencyCallback(Currency.BPCOIN, self.__updateBalance)
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.FocusEvent.COMPONENT_FOCUSED, self.__onFocus)
        g_eventBus.addListener(events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY)

    def __removeListeners(self):
        model = self.viewModel
        model.onBuyClick -= self.__onBuyClick
        model.onAboutClick -= self.__onAboutClick
        model.onViewLoaded -= self.__showViewCallback
        model.onClose -= self.__onClose
        model.intro.onClose -= self.__onIntroCloseClick
        model.intro.onVideo -= self.__showIntroVideo
        model.onGoToChapter -= self.__onGoToChapter
        model.widget3dStyle.onPreviewClick -= self.__onPreviewClick
        model.widget3dStyle.onSelectStyle -= self.__onSelectStyle
        model.onTakeClick -= self.__onTakeClick
        model.onOpenShopClick -= self.__onOpenShopClick
        model.onTakeAllClick -= self.__onTakeAllClick
        model.onPointsInfoClick -= self.__onPointsInfoClick
        model.onFinishedAnimation -= self.__resetReplaceRewardAnimations
        self.__battlePassController.onPointsUpdated -= self.__onPointsUpdated
        self.__battlePassController.onBattlePassIsBought -= self.__onBattlePassBought
        self.__battlePassController.onBattlePassSettingsChange -= self.__onBattlePassSettingsChange
        self.__battlePassController.onRewardSelectChange -= self.__onRewardSelectChange
        self.__battlePassController.onOffersUpdated -= self.__onOffersUpdated
        self.__battlePassController.onSeasonStateChange -= self.__updateProgressData
        self.__wallet.onWalletStatusChanged -= self.__updateWalletAvailability
        g_clientUpdateManager.removeCurrencyCallback(Currency.BPCOIN, self.__updateBalance)
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

        def __lobbyTopSubViewPredicate(view):
            return view.viewFlags & ViewFlags.VIEW_TYPE_MASK == ViewFlags.LOBBY_TOP_SUB_VIEW and view.viewStatus in (ViewStatus.LOADED, ViewStatus.LOADING)

        views = self.__gui.windowsManager.findViews(__lobbyTopSubViewPredicate)
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
            return
        self.__updateProgressData()
        self.__updateBuyButtonState()

    def __onGoToChapter(self, args):
        chapter = args.get('chapterNumber')
        if chapter is None:
            return
        else:
            self.__chosenChapter = int(chapter)
            self.__updateProgressData()
            self.__updateBuyButtonState()
            return

    def __onPreviewClick(self):
        styleInfo = getStyleForChapter(self.__chosenChapter, itemsCache=self.__itemsCache)
        vehicleCD = getVehicleCDForStyle(styleInfo, itemsCache=self.__itemsCache)
        showProgressionStylesStylePreview(vehicleCD, styleInfo, styleInfo.getDescription(), showMissionsBattlePassCommonProgression)

    def __onSelectStyle(self):
        self.setSubTab(BattlePassProgressionSubTabs.SELECT_STYLE_TAB)

    def __onPointsUpdated(self):
        with self.viewModel.transaction() as model:
            newChapter = self.__battlePassController.getCurrentChapter()
            if model.getCurrentChapter() != newChapter:
                self.__onGoToChapter({'chapterNumber': newChapter})
                return
            oldPoints = model.getCurrentAllPoints()
            pointsBeforeStart = model.getPointsBeforeStart()
            oldPoints += pointsBeforeStart
            oldChapter, oldLevel = self.__battlePassController.getLevelByPoints(oldPoints)
            newPoints = self.__battlePassController.getCurrentPoints()
            newLevel = self.__battlePassController.getCurrentLevel()
            self.__resetRewardsInterval(BattlePassConsts.REWARD_FREE, model.freeRewards, oldLevel, newLevel, oldChapter)
            self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, oldLevel, newLevel, oldChapter)
            self.__setCurrentLevelState(model=model)
        isDrawPoints = newLevel < oldLevel or newPoints < oldPoints
        if isDrawPoints:
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.__updateBuyButtonState()

    def __updateTooltipsSingleCard(self, rewards, model):
        tooltipIds = [ item.getTooltipId() for item in model.rewardItems.getItems() ]
        tooltipIds = tooltipIds[:len(rewards)]
        changeBonusTooltipData(zip(rewards, tooltipIds), self.__tooltipItems)

    def __onBattlePassBought(self):
        with self.viewModel.transaction() as model:
            startLevel = 1
            finalLevel = self.__battlePassController.getMaxLevel()
            self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, startLevel, finalLevel, self.__chosenChapter)
            self.__setCurrentLevelState(model=model)
        self.__updateBuyButtonState()

    def __onRewardSelectChange(self):
        self.__updateRewardSelectButton()
        with self.viewModel.transaction() as model:
            self.__setStyleWidget(model)
            startLevel = 1
            finalLevel = self.__battlePassController.getMaxLevel()
            self.__resetRewardsInterval(BattlePassConsts.REWARD_FREE, model.freeRewards, startLevel, finalLevel, self.__chosenChapter, True)
            self.__resetRewardsInterval(BattlePassConsts.REWARD_PAID, model.paidRewards, startLevel, finalLevel, self.__chosenChapter, True)
            model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)

    @replaceNoneKwargsModel
    def __onOffersUpdated(self, model=None):
        self.__updateRewardSelectButton(model=model)
        self.__updateRewardSelectButtons(model=model)

    def __onPurchaseLevels(self, _):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = True

    def __getTooltipContentCreator(self):
        return {R.views.lobby.battle_pass.tooltips.BattlePassPointsView(): self.__getBattlePassPointsTooltipContent,
         R.views.lobby.battle_pass.tooltips.BattlePassLockIconTooltipView(): self.__getBattlePassLockIconTooltipContent}

    @replaceNoneKwargsModel
    def __setShowBuyAnimations(self, model=None):
        showAnimations = False
        if self.__battlePassController.isBought():
            settings = self.__settingsCore.serverSettings
            shownChapters = settings.getBPStorage().get(BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN)
            chapter = 1 << self.__chosenChapter - 1
            if shownChapters & chapter == 0:
                showAnimations = True
                settings.saveInBPStorage({BattlePassStorageKeys.BUY_ANIMATION_WAS_SHOWN: shownChapters | chapter})
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

    def __showIntroVideo(self, onStart=False):
        settings = self.__settingsCore.serverSettings
        if onStart:
            if settings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN):
                return False
            settings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)
        return True

    def __makeSeasonTimeText(self, timeStamp, seasonNum):
        day, month = self.__getDayMonth(timeStamp)
        return backport.text(_rBattlePass.progression.seasonText(), seasonNum=int2roman(seasonNum), endDay=str(day), endMonth=backport.text(R.strings.menu.dateTime.months.num(month)()))

    def __showBattlePassBuyWindow(self, backCallback=None):
        from gui.impl.lobby.battle_pass.battle_pass_buy_view import BattlePassBuyWindow
        ctx = {'backCallback': backCallback}
        view = self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassBuyView())
        if view is None:
            self.viewModel.setAreSoundsAllowed(False)
            window = BattlePassBuyWindow(ctx, self.getParentWindow())
            window.load()
        return

    def __showBattlePassBuyLevelsWindow(self, backCallback=None):
        from gui.impl.lobby.battle_pass.battle_pass_buy_levels_view import BattlePassBuyLevelWindow
        ctx = {'backCallback': backCallback}
        view = self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePassBuyView())
        if view is None:
            self.viewModel.setAreSoundsAllowed(False)
            window = BattlePassBuyLevelWindow(ctx, self.getParentWindow())
            window.load()
        return

    def __showStyleChoiceWindow(self):
        from gui.impl.lobby.battle_pass.battle_pass_3d_style_choice_view import BattlePass3dStyleChoiceWindow
        view = self.__gui.windowsManager.getViewByLayoutID(R.views.lobby.battle_pass.BattlePass3dStyleChoiceView())
        if view is None:
            self.viewModel.setAreSoundsAllowed(False)
            window = BattlePass3dStyleChoiceWindow(self.getParentWindow())
            window.load()
        return

    def __onTakeClick(self, args):
        level = args.get('level')
        if not level:
            return
        self.__battlePassController.takeRewardForLevel(level)

    def __onTakeAllClick(self):
        self.__battlePassController.takeAllRewards()

    def __onOpenShopClick(self):
        showShop(getBattlePassCoinProductsUrl())

    def __onPointsInfoClick(self):
        showBattlePassHowToEarnPointsView(parent=self.getParentWindow())

    @replaceNoneKwargsModel
    def __updateWalletAvailability(self, status=None, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __resetReplaceRewardAnimations(self, model=None):
        self.__showReplaceRewardAnimations = False
        model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)
