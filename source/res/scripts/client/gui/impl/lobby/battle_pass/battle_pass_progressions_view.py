# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/battle_pass_progressions_view.py
import logging
from functools import partial
from operator import itemgetter
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, IS_BATTLE_PASS_COLLECTION_SEEN, LAST_BATTLE_PASS_POINTS_SEEN
from account_helpers.settings_core.settings_constants import BattlePassStorageKeys
from battle_pass_common import BATTLE_PASS_RANDOM_QUEST_BONUS_NAME, BattlePassConsts, CurrencyBP, FinalReward
from frameworks.wulf import Array, ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.storage.storage_helpers import getVehicleCDForStyle
from gui.Scaleform.daapi.view.lobby.store.browser.shop_helpers import getBattlePassCoinProductsUrl, getBattlePassPointsProductsUrl
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.battle_pass.battle_pass_bonuses_packers import changeBonusTooltipData, packBonusModelAndTooltipData, packSpecialTooltipData
from gui.battle_pass.battle_pass_constants import ChapterState, MIN_LEVEL
from gui.battle_pass.battle_pass_decorators import createBackportTooltipDecorator, createTooltipContentDecorator
from gui.battle_pass.battle_pass_helpers import TANKMAN_BONUS_NAME, fillBattlePassCompoundPrice, getChapterType, getDataByTankman, getExtraInfoPageURL, getFormattedTimeLeft, getInfoPageURL, getIntroVideoURL, getRewardTypeBySource, getStyleForChapter, getTankmanInfo, getVehicleInfoForChapter, isCommonBattlePassChapter, isSeasonEndingSoon, updateBuyAnimationFlag
from gui.battle_pass.sounds import BattlePassSounds
from gui.collection.collections_helpers import getCollectionRes, loadBattlePassFromCollections
from gui.impl import backport
from gui.impl.auxiliary.collections_helper import fillCollectionModel
from gui.impl.auxiliary.rewards_helper import setRewards
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.battle_pass.battle_pass_progressions_view_model import BattlePassProgressionsViewModel, ButtonStates, ChapterStates, ChapterType
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_level_model import RewardLevelModel
from gui.impl.gen.view_models.views.lobby.vehicle_preview.top_panel.top_panel_tabs_model import TabID
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showMissionsBattlePass
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBattlePassBuyLevelWindow, showBattlePassBuyWindow, showBattlePassHowToEarnPointsView, showBattlePassStyleProgressionPreview, showBattlePassTankmenVoiceover, showBrowserOverlayView, showCollectionWindow, showHangar, showShop, showStylePreview
from gui.shared.formatters.time_formatters import formatDate
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier, SimpleNotifier
from helpers import dependency, int2roman, time_utils
from shared_utils import findFirst, first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IBattlePassController, ICollectionsSystemController, IWalletController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from tutorial.control.game_vars import getVehicleByIntCD
from web.web_client_api.common import ItemPackEntry, ItemPackType
_logger = logging.getLogger(__name__)
_bpRes = R.strings.battle_pass
_CHAPTER_STATES = {ChapterState.ACTIVE: ChapterStates.ACTIVE,
 ChapterState.COMPLETED: ChapterStates.COMPLETED,
 ChapterState.PAUSED: ChapterStates.PAUSED,
 ChapterState.NOT_STARTED: ChapterStates.NOTSTARTED}
_FREE_POINTS_INDEX = 0

class BattlePassProgressionsView(ViewImpl):
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battlePass = dependency.descriptor(IBattlePassController)
    __gui = dependency.descriptor(IGuiLoader)
    __itemsCache = dependency.descriptor(IItemsCache)
    __wallet = dependency.descriptor(IWalletController)
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)
    ANIMATION_PURCHASE_LEVELS = 'animPurchaseLevels'
    ANIMATIONS = {ANIMATION_PURCHASE_LEVELS: False}

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.battle_pass.BattlePassProgressionsView())
        settings.flags = ViewFlags.VIEW
        settings.model = BattlePassProgressionsViewModel()
        self.__tooltipItems = {}
        self.__specialTooltipItems = {}
        self.__viewActive = False
        self.__chapterID = kwargs.get('chapterID') or self.__getDefaultChapterID()
        self.__showReplaceRewardAnimations = False
        self.__notifier = None
        self.__exitSoundsIsPlayed = False
        super(BattlePassProgressionsView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(BattlePassProgressionsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattlePassProgressionsView, self).createToolTip(event)

    @createTooltipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(BattlePassProgressionsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            tooltipData = self.__tooltipItems.get(tooltipId)
            return tooltipData if tooltipData is not None else self.__specialTooltipItems.get(tooltipId)

    def activate(self):
        self._subscribe()
        self.__updateProgressData()
        self.__updateBuyButtonState()
        self.__startExtraSounds()

    def deactivate(self):
        if not self.__exitSoundsIsPlayed:
            self.__stopSounds()
        self._unsubscribe()

    def setChapter(self, chapterID):
        chapterChanged = chapterID != self.__chapterID
        self.__chapterID = chapterID or self.__getDefaultChapterID()
        with self.viewModel.transaction() as model:
            self.__updateProgressData(model=model)
        self.__updateBuyButtonState()
        if chapterChanged:
            self.__setShowBuyAnimations()

    def _getEvents(self):
        return ((self.viewModel.onActionClick, self.__onActionClick),
         (self.viewModel.onAboutClick, self.__onAboutClick),
         (self.viewModel.onClose, self.__onClose),
         (self.viewModel.widget3dStyle.onPreviewClick, self.__onPreviewClick),
         (self.viewModel.widgetFinalRewards.onRewardPreviewClick, self.__onFinalRewardPreviewClick),
         (self.viewModel.onTakeClick, self.__onTakeClick),
         (self.viewModel.onTakeAllClick, self.__onTakeAllClick),
         (self.viewModel.onOpenShopClick, self.__onOpenShopClick),
         (self.viewModel.onPointsInfoClick, self.__onPointsInfoClick),
         (self.viewModel.onFinishedAnimation, self.__resetReplaceRewardAnimations),
         (self.viewModel.onLevelsAnimationFinished, self.__resetLevelAnimations),
         (self.viewModel.showTankmen, self.__showTankmen),
         (self.viewModel.widgetFinalRewards.showTankmen, self.__showTankmen),
         (self.viewModel.onChapterChoice, self.__onChapterChoice),
         (self.viewModel.onBpcoinClick, self.__showCoinsShop),
         (self.viewModel.onBpbitClick, self.__showPointsShop),
         (self.viewModel.onTakeRewardsClick, self.__takeAllRewards),
         (self.viewModel.collectionEntryPoint.openCollection, self.__openCollection),
         (self.__battlePass.onPointsUpdated, self.__onPointsUpdated),
         (self.__battlePass.onBattlePassIsBought, self.__onBattlePassBought),
         (self.__battlePass.onBattlePassSettingsChange, self.__onBattlePassSettingsChange),
         (self.__battlePass.onRewardSelectChange, self.__onRewardSelectChange),
         (self.__battlePass.onOffersUpdated, self.__onOffersUpdated),
         (self.__battlePass.onSelectTokenUpdated, self.__onSelectTokenUpdated),
         (self.__battlePass.onChapterChanged, self.__onChapterChanged),
         (self.__battlePass.onExtraChapterExpired, self.__onExtraChapterExpired),
         (self.__collectionsSystem.onBalanceUpdated, self.__onCollectionsUpdated),
         (self.__collectionsSystem.onServerSettingsChanged, self.__onCollectionsUpdated),
         (self.__wallet.onWalletStatusChanged, self.__updateWalletAvailability),
         (g_playerEvents.onClientUpdated, self.__onBpBitUpdated))

    def _getListeners(self):
        return ((events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.AWARD_VIEW_CLOSE, self.__onAwardViewClose, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.ON_PURCHASE_LEVELS, self.__onPurchaseLevels, EVENT_BUS_SCOPE.LOBBY),
         (events.BattlePassEvent.BUYING_THINGS, self.__updateBuyButtonState, EVENT_BUS_SCOPE.LOBBY),
         (events.CollectionsEvent.NEW_ITEM_SHOWN, self.__onCollectionsUpdated, EVENT_BUS_SCOPE.LOBBY))

    def _getCallbacks(self):
        return (('stats.bpcoin', self.__updateBalance),)

    def _onLoading(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoading(*args, **kwargs)
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(PeriodicNotifier(self.__battlePass.getSeasonTimeLeft, self.__updateTimer))
        self.__notifier.addNotificator(SimpleNotifier(self.__battlePass.getFinalOfferTimeLeft, self.__updateTimer))
        self.__notifier.startNotification()
        self.__updateProgressData()
        self.__updateBuyButtonState()
        self.__startExtraSounds()

    def _onLoaded(self, *args, **kwargs):
        super(BattlePassProgressionsView, self)._onLoaded(*args, **kwargs)
        self.__setShowBuyAnimations()

    def _finalize(self):
        self.__tooltipItems = None
        self.__specialTooltipItems = None
        if self.__notifier is not None:
            self.__notifier.stopNotification()
            self.__notifier.clearNotification()
        if not self.__exitSoundsIsPlayed:
            self.__stopSounds()
        super(BattlePassProgressionsView, self)._finalize()
        return

    def __onActionClick(self):
        self.__resetBuyAnimation()
        ctrl = self.__battlePass
        if ctrl.isChapterActive(self.__chapterID):
            if ctrl.isBought(chapterID=self.__chapterID):
                self.__showBuyLevelsWindow()
            else:
                self.__showBuyWindow()
        elif not ctrl.isChapterCompleted(self.__chapterID):
            ctrl.activateChapter(self.__chapterID)
        elif not ctrl.isBought(chapterID=self.__chapterID):
            self.__showBuyWindow()

    def __onAboutClick(self):
        self.__loadUrl(getExtraInfoPageURL() if self.__battlePass.isExtraChapter(self.__chapterID) else getInfoPageURL())

    @staticmethod
    def __onClose():
        showHangar()

    @staticmethod
    def __loadUrl(url):
        showBrowserOverlayView(url, VIEW_ALIAS.BATTLE_PASS_BROWSER_VIEW)

    def __setBattlePassIntroShown(self):
        self.__settingsCore.serverSettings.saveInBPStorage({BattlePassStorageKeys.INTRO_SHOWN: True})

    @replaceNoneKwargsModel
    def __updateProgressData(self, model=None):
        self.__setAwards(model)
        self.__updateData(model=model)
        self.__updateBalance(model=model)
        self.__updateWalletAvailability(model=model)
        self.__updatePrice(model=model)

    def __setAwards(self, model):
        bpController = self.__battlePass
        self.__tooltipItems.clear()
        self.__specialTooltipItems.clear()
        if isCommonBattlePassChapter(self.__chapterID):
            self.__setStyleWidget(model)
        elif self.__battlePass.getPaidFinalRewardTypes(self.__chapterID):
            self.__setFinalRewardsWidget(model)
        else:
            _logger.error('Cannot find rewards for widget in progression for chapter=%s', self.__chapterID)
        model.levels.clearItems()
        minLevel, maxLevel = bpController.getChapterLevelInterval(self.__chapterID)
        freeBonuses = sorted(bpController.getAwardsInterval(self.__chapterID, minLevel, maxLevel, BattlePassConsts.REWARD_FREE).iteritems(), key=itemgetter(0))
        paidBonuses = sorted(bpController.getAwardsInterval(self.__chapterID, minLevel, maxLevel, BattlePassConsts.REWARD_PAID).iteritems(), key=itemgetter(0))
        for (level, freeBonus), (_, paidBonus) in zip(freeBonuses, paidBonuses):
            isNeedToTakeFree, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            isNeedToTakePaid, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            levelModel = RewardLevelModel()
            levelModel.setLevel(level)
            levelModel.setIsRare(bpController.isRareLevel(self.__chapterID, level))
            levelModel.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            levelModel.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)
            levelModel.setLevelPoints(bpController.getLevelPoints(self.__chapterID, level - 1))
            levelModel.setNeedTakeFree(isNeedToTakeFree)
            levelModel.setNeedTakePaid(isNeedToTakePaid)
            realFreeAwards = self.__battlePass.replaceOfferByReward(freeBonus)
            packBonusModelAndTooltipData(realFreeAwards, levelModel.freeRewardItems, self.__tooltipItems)
            realPaidAwards = self.__battlePass.replaceOfferByReward(paidBonus)
            packBonusModelAndTooltipData(realPaidAwards, levelModel.paidRewardItems, self.__tooltipItems)
            model.levels.addViewModel(levelModel)

    def __setStyleWidget(self, model):
        style = getStyleForChapter(self.__chapterID)
        if style is not None:
            vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
            vehicle = getVehicleByIntCD(vehicleCD)
            fillVehicleInfo(model.widget3dStyle.vehicleInfo, vehicle)
            model.widget3dStyle.setStyleName(style.userName)
            model.widget3dStyle.setStyleId(style.id)
        return

    def __setCharacterWidget(self, model, rewardSource=BattlePassConsts.REWARD_FREE):
        maxLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
        rewards = self.__battlePass.getSingleAward(self.__chapterID, maxLevel, awardType=rewardSource)
        characterBonus = findFirst(lambda b: b.getName() == TANKMAN_BONUS_NAME, rewards)
        if characterBonus is None:
            return
        else:
            character = getTankmanInfo(characterBonus)
            if character is None:
                return
            iconName, characterName, skills, groupName = getDataByTankman(character)
            skillsArray = Array()
            for skill in skills:
                skillsArray.addString(skill)

            model.setIcon(iconName)
            model.setTankman(characterName)
            model.setSkills(skillsArray)
            model.setTooltipId(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED)
            model.setGroupName(groupName)
            packSpecialTooltipData(TOOLTIPS_CONSTANTS.TANKMAN_NOT_RECRUITED, self.__specialTooltipItems, character.getRecruitID())
            return

    def __setFinalRewardsWidget(self, model):
        maxLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
        style = getStyleForChapter(self.__chapterID)
        if style is not None:
            model.widgetFinalRewards.styleInfo.setStyleName(style.userName)
            model.widgetFinalRewards.styleInfo.setStyleId(style.id)
        vehicleSource = getRewardTypeBySource(FinalReward.VEHICLE, self.__chapterID)
        if vehicleSource is not None:
            vehicle, _ = getVehicleInfoForChapter(self.__chapterID, awardSource=vehicleSource)
            if vehicle is not None:
                fillVehicleInfo(model.widgetFinalRewards.vehicleInfo, vehicle)
        tankmanSource = getRewardTypeBySource(FinalReward.TANKMAN, self.__chapterID)
        if tankmanSource is not None:
            self.__setCharacterWidget(model.widgetFinalRewards.tankmanInfo, rewardSource=tankmanSource)
        questSource = getRewardTypeBySource(FinalReward.BATTLE_QUEST, self.__chapterID)
        if questSource is not None:
            rewards = self.__battlePass.getSingleAward(self.__chapterID, maxLevel, questSource)
            battleQuestReward = findFirst(lambda b: b.getName() == BATTLE_PASS_RANDOM_QUEST_BONUS_NAME, rewards)
            if battleQuestReward is not None:
                model.widgetFinalRewards.setBattleQuest(battleQuestReward.tokenID)
        return

    def __resetRewardsInterval(self, model, fromLevel, toLevel, replaceRewards=False):
        startLevel, finalLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        if fromLevel == toLevel:
            return
        fromLevel += 1
        if toLevel > finalLevel:
            toLevel = finalLevel
        for level in range(fromLevel, toLevel + 1):
            levelData = model.levels.getItem(level - startLevel)
            isNeedToTakeFree, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            if replaceRewards and levelData.getNeedTakeFree() and not isNeedToTakeFree:
                levelData.freeRewardItems.clearItems()
                awards = self.__battlePass.getSingleAward(self.__chapterID, level, BattlePassConsts.REWARD_FREE)
                realAwards = self.__battlePass.replaceOfferByReward(awards)
                packBonusModelAndTooltipData(realAwards, levelData.freeRewardItems, self.__tooltipItems)
                self.__showReplaceRewardAnimations = True
            isNeedToTakePaid, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            if replaceRewards and levelData.getNeedTakePaid() and not isNeedToTakePaid:
                levelData.paidRewardItems.clearItems()
                awards = self.__battlePass.getSingleAward(self.__chapterID, level, BattlePassConsts.REWARD_PAID)
                realAwards = self.__battlePass.replaceOfferByReward(awards)
                packBonusModelAndTooltipData(realAwards, levelData.paidRewardItems, self.__tooltipItems)
                self.__showReplaceRewardAnimations = True
            levelData.setNeedTakeFree(isNeedToTakeFree)
            levelData.setNeedTakePaid(isNeedToTakePaid)
            levelData.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            levelData.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)

        model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)
        model.levels.invalidate()

    def __getRewardLevelState(self, awardType, level):
        bpController = self.__battlePass
        isNeedToTake = bpController.isNeedToTakeReward(self.__chapterID, awardType, level)
        isChooseRewardEnabled = isNeedToTake and bpController.isChooseRewardEnabled(awardType, self.__chapterID, level)
        return (isNeedToTake, isChooseRewardEnabled)

    @replaceNoneKwargsModel
    def __updateData(self, model=None):
        self.__updateLevelState(model)
        isBattlePassBought = self.__battlePass.isBought(chapterID=self.__chapterID)
        model.setIsBattlePassPurchased(isBattlePassBought)
        model.setIsPaused(self.__battlePass.isPaused())
        model.setChapterState(_CHAPTER_STATES.get(self.__battlePass.getChapterState(self.__chapterID)))
        setRewards(model, self.__chapterID)
        model.setChapterID(self.__chapterID)
        model.setSeasonNum(self.__battlePass.getSeasonNum())
        model.setBpbitCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0))
        model.setIsBattlePassCompleted(self.__battlePass.isCompleted())
        model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
        model.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())
        model.setChapterType(ChapterType(getChapterType(self.__chapterID)))
        model.setIsSeasonEndingSoon(isSeasonEndingSoon())
        model.setSeasonText(self.__makeSeasonTimeText())
        model.setHasExtra(self.__battlePass.hasExtra())
        model.setSpecialVoiceTankmenCount(len(self.__battlePass.getSpecialTankmen()))
        fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())
        self.__setExpirations(model)
        if isCommonBattlePassChapter(self.__chapterID):
            self.__setStyleTaken(model)
        elif self.__battlePass.getPaidFinalRewardTypes(self.__chapterID):
            self.__setFinalRewardsWidget(model)
        self.__updateRewardSelectButton(model=model)

    def __setExpirations(self, model):
        expireTimestamp = self.__battlePass.getChapterRemainingTime(self.__chapterID) if self.__battlePass.isExtraChapter(self.__chapterID) else self.__battlePass.getSeasonTimeLeft()
        model.setExpireTime(expireTimestamp)
        model.setExpireTimeStr(getFormattedTimeLeft(expireTimestamp))

    def __setStyleTaken(self, model):
        style = getStyleForChapter(self.__chapterID)
        vehicleCD = getVehicleCDForStyle(style, itemsCache=self.__itemsCache)
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        model.setIsStyleTaken(style.isInInventory or bool(style.installedCount(vehicle.intCD)))

    def __updateLevelState(self, model):
        previousBattlePassPointsSeen = AccountSettings.getSettings(LAST_BATTLE_PASS_POINTS_SEEN)
        previousChapterPoints = previousBattlePassPointsSeen.get(self.__chapterID, 0)
        previousFreePoints = previousBattlePassPointsSeen.get(_FREE_POINTS_INDEX, 0)
        currentChapterPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
        previousLevel = self.__battlePass.getLevelByPoints(self.__chapterID, previousChapterPoints)
        previousPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, previousChapterPoints, previousLevel)
        previousLevel += 1
        currentLevel = self.__battlePass.getLevelByPoints(self.__chapterID, currentChapterPoints)
        currentPoints, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, currentChapterPoints, currentLevel)
        currentLevel += 1
        finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
        currentLevel = currentLevel if currentLevel <= finalLevel else finalLevel
        freePointsInChapter = self.__battlePass.getFreePoints() + currentChapterPoints
        potentialLevel = self.__battlePass.getLevelByPoints(self.__chapterID, freePointsInChapter)
        freePointsInLevel, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, freePointsInChapter, potentialLevel)
        potentialLevel += 1
        previousPotentialLevel = self.__battlePass.getLevelByPoints(self.__chapterID, previousFreePoints)
        previousFreePointsInLevel, _ = self.__battlePass.getProgressionByPoints(self.__chapterID, previousFreePoints, previousPotentialLevel)
        previousPotentialLevel += 1
        if self.__battlePass.isExtraChapter(self.__chapterID):
            freePointsInChapter = 0
            freePointsInLevel = 0
            potentialLevel = 0
            previousFreePoints = 0
            previousFreePointsInLevel = 0
            previousPotentialLevel = 0
        model.setPreviousPointsInChapter(previousChapterPoints)
        model.setPreviousPointsInLevel(previousPoints)
        model.setPreviousLevel(previousLevel)
        model.setCurrentPointsInChapter(currentChapterPoints)
        model.setCurrentPointsInLevel(currentPoints)
        model.setCurrentLevel(currentLevel)
        model.setFreePointsInChapter(freePointsInChapter)
        model.setFreePointsInLevel(freePointsInLevel)
        model.setPreviousFreePointsInChapter(previousFreePoints)
        model.setPreviousFreePointsInLevel(previousFreePointsInLevel)
        model.setPreviousPotentialLevel(previousPotentialLevel)
        model.setPotentialLevel(potentialLevel)
        previousBattlePassPointsSeen[self.__chapterID] = currentChapterPoints
        previousBattlePassPointsSeen[_FREE_POINTS_INDEX] = freePointsInChapter
        AccountSettings.setSettings(LAST_BATTLE_PASS_POINTS_SEEN, previousBattlePassPointsSeen)

    def __updateBuyButtonState(self, *_):
        bpController = self.__battlePass
        isBattlePassBought = bpController.isBought(chapterID=self.__chapterID)
        isActiveChapter = bpController.isChapterActive(self.__chapterID)
        isCompleted = bpController.isChapterCompleted(self.__chapterID)
        state = ButtonStates.HIDE
        if isActiveChapter:
            if not isBattlePassBought:
                state = ButtonStates.BUY
            else:
                state = ButtonStates.LEVEL
        elif not isCompleted:
            state = ButtonStates.ACTIVATE
        elif not isBattlePassBought:
            state = ButtonStates.BUY
        with self.viewModel.transaction() as model:
            model.setButtonState(state)

    @replaceNoneKwargsModel
    def __updateRewardSelectButton(self, model=None):
        model.setIsChooseDeviceEnabled(False)
        notChosenRewardCount = self.__battlePass.getNotChosenRewardCount()
        model.setIsChooseDeviceEnabled(self.__battlePass.canChooseAnyReward())
        model.setNotChosenRewardCount(notChosenRewardCount)

    @replaceNoneKwargsModel
    def __updateRewardSelectButtons(self, model=None):
        self.__resetRewardSelectButtons(model, MIN_LEVEL)

    def __resetRewardSelectButtons(self, model, fromLevel):
        startLevel, finalLevel = self.__battlePass.getChapterLevelInterval(self.__chapterID)
        if fromLevel <= startLevel:
            fromLevel = startLevel + 1
        for level in range(fromLevel, finalLevel + 1):
            item = model.levels.getItem(level - startLevel)
            _, isChooseFreeRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_FREE, level)
            _, isChoosePaidRewardEnabled = self.__getRewardLevelState(BattlePassConsts.REWARD_PAID, level)
            item.setIsFreeRewardChoiceEnabled(isChooseFreeRewardEnabled)
            item.setIsPaidRewardChoiceEnabled(isChoosePaidRewardEnabled)

        model.levels.invalidate()

    def __updateTimer(self):
        self.viewModel.setExpireTimeStr(getFormattedTimeLeft(self.__battlePass.getSeasonTimeLeft()))
        self.__updateBuyButtonState()

    def __onMissionsTabChanged(self, event):
        viewActive = event.ctx.get('alias') == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS
        if self.__viewActive == viewActive and self.__viewActive:
            self.__clearSubViews()
        self.__viewActive = viewActive

    def __clearSubViews(self):

        def __isValidSubView(v):
            return v.viewFlags & ViewFlags.VIEW_TYPE_MASK == ViewFlags.LOBBY_TOP_SUB_VIEW and v.viewStatus in (ViewStatus.LOADED, ViewStatus.LOADING)

        for view in self.__gui.windowsManager.findViews(__isValidSubView):
            view.destroyWindow()

    def __onAwardViewClose(self, *_):
        self.__setShowBuyAnimations()

    def __onBattlePassSettingsChange(self, *_):
        if not self.__battlePass.isChapterExists(self.__chapterID):
            showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())
            return
        if self.__battlePass.isPaused():
            showMissionsBattlePass()
            return
        if not (self.__battlePass.isEnabled() and self.__battlePass.isActive()):
            showHangar()
            return
        self.__updateProgressData()
        self.__updateBuyButtonState()

    def __onGoToChapter(self, args):
        chapter = args.get('chapterNumber')
        if chapter is None:
            return
        else:
            self.__chapterID = int(chapter)
            self.__updateProgressData()
            self.__updateBuyButtonState()
            return

    def __onPreviewClick(self, args):
        level = args.get('level')
        if level is None:
            return
        else:
            styleInfo = getStyleForChapter(self.__chapterID, battlePass=self.__battlePass)
            vehicleCD = getVehicleCDForStyle(styleInfo, itemsCache=self.__itemsCache)
            showBattlePassStyleProgressionPreview(vehicleCD, styleInfo, styleInfo.getDescription(), self.__getPreviewCallback(), chapterId=self.__chapterID, styleLevel=int(level))
            return

    def __onFinalRewardPreviewClick(self):
        styleInfo = getStyleForChapter(self.__chapterID, battlePass=self.__battlePass)
        vehicleCD = getVehicleCDForStyle(styleInfo, itemsCache=self.__itemsCache)
        itemsPack = (ItemPackEntry(type=ItemPackType.CREW_100, groupID=1),)
        showStylePreview(vehicleCD, style=styleInfo, topPanelData={'linkage': VEHPREVIEW_CONSTANTS.TOP_PANEL_TABS_LINKAGE,
         'tabIDs': (TabID.VEHICLE, TabID.STYLE),
         'currentTabID': TabID.STYLE,
         'style': styleInfo}, itemsPack=itemsPack, backCallback=self.__getPreviewCallback())

    def __getPreviewCallback(self):
        return partial(showMissionsBattlePass, R.views.lobby.battle_pass.BattlePassProgressionsView(), self.__chapterID)

    def __onPointsUpdated(self):
        with self.viewModel.transaction() as model:
            newChapter = self.__battlePass.getCurrentChapterID()
            newPoints = self.__battlePass.getPointsInChapter(self.__chapterID)
            newFreePoints = self.__battlePass.getFreePoints() + newPoints
            oldFreePoints = model.getFreePointsInChapter()
            if model.getChapterID() != newChapter and newFreePoints == oldFreePoints:
                return
            oldPoints = model.getCurrentPointsInChapter()
            oldLevel = self.__battlePass.getLevelByPoints(self.__chapterID, oldPoints)
            newLevel = self.__battlePass.getLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, oldLevel, newLevel)
            self.__updateData(model=model)
        isDrawPoints = newLevel < oldLevel or newPoints < oldPoints or newFreePoints > oldFreePoints
        if isDrawPoints:
            model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.__updateBuyButtonState()

    def __updateTooltipsSingleCard(self, rewards, model):
        tooltipIds = [ item.getTooltipId() for item in model.rewardItems.getItems() ]
        tooltipIds = tooltipIds[:len(rewards)]
        changeBonusTooltipData(zip(rewards, tooltipIds), self.__tooltipItems)

    def __onBattlePassBought(self):
        with self.viewModel.transaction() as model:
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel)
            self.__updateData(model=model)
        self.__updateBuyButtonState()

    def __onRewardSelectChange(self):
        self.__updateRewardSelectButton()
        with self.viewModel.transaction() as model:
            if isCommonBattlePassChapter(self.__chapterID):
                self.__setStyleWidget(model)
            elif self.__battlePass.getPaidFinalRewardTypes(self.__chapterID):
                self.__setFinalRewardsWidget(model)
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel, replaceRewards=True)

    def __onSelectTokenUpdated(self):

        def __viewsPredicate(view):
            return view.layoutID in (R.views.lobby.battle_pass.BattlePassAwardsView(), R.views.lobby.battle_pass.RewardsSelectionView())

        if self.__gui.windowsManager.findViews(__viewsPredicate):
            return
        self.__updateRewardSelectButton()
        with self.viewModel.transaction() as model:
            if isCommonBattlePassChapter(self.__chapterID):
                self.__setStyleWidget(model)
            elif self.__battlePass.getPaidFinalRewardTypes(self.__chapterID):
                self.__setFinalRewardsWidget(model)
            model.setNotChosenRewardCount(self.__battlePass.getNotChosenRewardCount())
            model.setIsChooseRewardsEnabled(self.__battlePass.canChooseAnyReward())
            finalLevel = self.__battlePass.getMaxLevelInChapter(self.__chapterID)
            self.__resetRewardsInterval(model, MIN_LEVEL, finalLevel, replaceRewards=False)

    def __onChapterChanged(self):
        if self.__chapterID not in self.__battlePass.getChapterIDs():
            return
        self.__updateBuyButtonState()
        self.__updateProgressData()

    @staticmethod
    def __onExtraChapterExpired():
        showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())

    @replaceNoneKwargsModel
    def __onOffersUpdated(self, model=None):
        self.__updateRewardSelectButton(model=model)
        self.__updateRewardSelectButtons(model=model)

    def __onPurchaseLevels(self, _):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = True

    @replaceNoneKwargsModel
    def __setShowBuyAnimations(self, model=None):
        showAnimations = False
        isBattlePassBought = self.__battlePass.isBought(chapterID=self.__chapterID)
        if isBattlePassBought:
            showAnimations = updateBuyAnimationFlag(chapterID=self.__chapterID, settingsCore=self.__settingsCore, battlePass=self.__battlePass)
            model.setIsBattlePassPurchased(isBattlePassBought)
        model.setShowBuyAnimations(showAnimations)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False

    def __getDefaultChapterID(self):
        return self.__battlePass.getCurrentChapterID() or first(sorted(self.__battlePass.getChapterIDs()))

    def __showIntroVideo(self, onStart=False):
        settings = self.__settingsCore.serverSettings
        if onStart:
            if settings.getBPStorage().get(BattlePassStorageKeys.INTRO_VIDEO_SHOWN):
                return False
            settings.saveInBPStorage({BattlePassStorageKeys.INTRO_VIDEO_SHOWN: True})
        showBrowserOverlayView(getIntroVideoURL(), VIEW_ALIAS.BROWSER_OVERLAY)
        return True

    def __makeSeasonTimeText(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            endTimestamp = self.__battlePass.getChapterExpiration(self.__chapterID)
            endStringRes = _bpRes.progression.season.end.special
        elif self.__battlePass.isSeasonFinished():
            endTimestamp = 0
            endStringRes = _bpRes.commonProgression.body.ended
        else:
            endTimestamp = self.__battlePass.getSeasonFinishTime()
            endStringRes = _bpRes.progression.season.end.special if self.__battlePass.isHoliday() else _bpRes.progression.season.end.normal
        endTime = time_utils.getTimeStructInLocal(endTimestamp)
        return backport.text(endStringRes(), seasonNum=int2roman(self.__battlePass.getSeasonNum()), endDay=endTime.tm_mday, endMonth=backport.text(R.strings.menu.dateTime.months.num(endTime.tm_mon)()), endTime=formatDate('%H:%M', endTimestamp))

    def __showBuyWindow(self, backCallback=None):
        showBattlePassBuyWindow({'backCallback': backCallback})

    def __showBuyLevelsWindow(self, backCallback=None):
        showBattlePassBuyLevelWindow({'backCallback': backCallback,
         'chapterID': self.__chapterID})

    def __onTakeClick(self, args):
        level = args.get('level')
        if not level:
            return
        self.__battlePass.takeRewardForLevel(self.__chapterID, level)

    def __onTakeAllClick(self):
        self.__battlePass.takeAllRewards()

    @staticmethod
    def __onOpenShopClick():
        showShop(getBattlePassCoinProductsUrl())

    def __onPointsInfoClick(self):
        showBattlePassHowToEarnPointsView(parent=self.getParentWindow(), chapterID=self.__chapterID)

    @staticmethod
    def __onChapterChoice():
        showMissionsBattlePass(R.views.lobby.battle_pass.ChapterChoiceView())

    @replaceNoneKwargsModel
    def __updateWalletAvailability(self, status=None, model=None):
        model.setIsWalletAvailable(self.__wallet.isAvailable)

    @replaceNoneKwargsModel
    def __updateBalance(self, value=None, model=None):
        model.setBpcoinCount(self.__itemsCache.items.stats.bpcoin)

    @replaceNoneKwargsModel
    def __updatePrice(self, model=None):
        compoundPrice = self.__battlePass.getBattlePassCost(self.__chapterID)
        fillBattlePassCompoundPrice(model.price, compoundPrice)

    @replaceNoneKwargsModel
    def __resetReplaceRewardAnimations(self, model=None):
        self.__showReplaceRewardAnimations = False
        model.setShowReplaceRewardsAnimations(self.__showReplaceRewardAnimations)

    @replaceNoneKwargsModel
    def __resetLevelAnimations(self, model=None):
        self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS] = False
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])

    @replaceNoneKwargsModel
    def __resetBuyAnimation(self, model=None):
        model.setShowBuyAnimations(False)
        model.setShowLevelsAnimations(self.ANIMATIONS[self.ANIMATION_PURCHASE_LEVELS])

    def __onBpBitUpdated(self, *data):
        if data[0].get('cache', {}).get('dynamicCurrencies', {}).get(CurrencyBP.BIT.value, ''):
            with self.viewModel.transaction() as model:
                model.setBpbitCount(self.__itemsCache.items.stats.dynamicCurrencies.get(CurrencyBP.BIT.value, 0))

    def __takeAllRewards(self):
        self.__battlePass.takeAllRewards()

    def __openCollection(self):
        if not AccountSettings.getSettings(IS_BATTLE_PASS_COLLECTION_SEEN):
            AccountSettings.setSettings(IS_BATTLE_PASS_COLLECTION_SEEN, True)
            self.__onCollectionsUpdated()
        backText = backport.text(getCollectionRes(self.__battlePass.getCurrentCollectionId()).featureName())
        backCallback = partial(loadBattlePassFromCollections, R.views.lobby.battle_pass.BattlePassProgressionsView(), self.__chapterID)
        showCollectionWindow(collectionId=self.__battlePass.getCurrentCollectionId(), backCallback=backCallback, backBtnText=backText)

    @staticmethod
    def __showCoinsShop():
        showShop(getBattlePassCoinProductsUrl())

    @staticmethod
    def __showPointsShop():
        showShop(getBattlePassPointsProductsUrl())

    def __onCollectionsUpdated(self, *_):
        with self.viewModel.transaction() as model:
            fillCollectionModel(model.collectionEntryPoint, self.__battlePass.getCurrentCollectionId())

    @staticmethod
    def __showTankmen():
        showBattlePassTankmenVoiceover()

    def __stopSounds(self):
        if self.__battlePass.getSpecialTankmen():
            self.soundManager.playInstantSound(BattlePassSounds.HOLIDAY_VOICEOVER_STOP if self.__battlePass.isHoliday() else BattlePassSounds.VOICEOVER_STOP)
        self.__stopExtraSounds()
        self.__exitSoundsIsPlayed = True

    def __startExtraSounds(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            self.soundManager.playInstantSound(BattlePassSounds.SPECIAL_TASKS_ENTER)
            self.__exitSoundsIsPlayed = False

    def __stopExtraSounds(self):
        if self.__battlePass.isExtraChapter(self.__chapterID):
            self.soundManager.playInstantSound(BattlePassSounds.SPECIAL_TASKS_EXIT)
