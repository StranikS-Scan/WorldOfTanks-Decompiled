# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/halloween/meta_view.py
import WWISE
from async import async, await
from frameworks.wulf import ViewSettings, ViewFlags
from adisp import process
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.dialogs.dialogs import showDecodeConfirmDialog
from gui.impl.gen.view_models.views.lobby.halloween.bonus_model import BonusModel
from gui.impl.gen.view_models.views.lobby.halloween.tank_model import TankModel
from gui.impl.gen.view_models.views.lobby.halloween.timeline_item_model import PrizeEnum, ItemStateEnum, TimelineItemModel
from gui.impl.gen.view_models.views.lobby.halloween.timeline_view_model import StateEnum, TimelineViewModel
from gui.impl.lobby.halloween.hangar_event_view import HangarEventView
from gui.shared.tooltips.event import InterrogationCtx, EventInterrogationTooltipData
from gui.shared.utils.functions import replaceHyphenToUnderscore
from helpers import dependency
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.halloween.event_keys_counter_panel_view_model import VisualTypeEnum
from gui.impl.gen.view_models.views.lobby.halloween.meta_view_model import MetaViewModel, PageTypeEnum
from gui.impl.lobby.halloween.event_keys_counter_panel_view import EventKeysCounterPanelView
from gui.impl.lobby.halloween.tooltips.shop_vehicle_tooltip import ShopVehicleTooltip
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.hangar.web_handlers import createHangarWebHandlers
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showBrowserOverlayView, showVideoRewardView, showInterrogationInfoWindow, showHangar, goToHalloweenKingRewardOnScene, selectVehicleInHangar, showShopView
from ids_generators import SequenceIDGenerator
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.game_control import ISoundEventChecker
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from skeletons.account_helpers.settings_core import ISettingsCore
from tutorial.hints_manager import HINT_SHOWN_STATUS
from account_helpers.settings_core.ServerSettingsManager import UIGameEventKeys
from gui.server_events.awards_formatters import AWARDS_SIZES, getHW21MetaAwardFormatter
from gui.Scaleform.daapi.view.lobby.missions.awards_formatters import EventShopBundleBonusesAwardsComposer
from gui.impl.lobby.halloween.sound_constants import EventHangarSound
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.impl.lobby.halloween.event_helpers import filterVehicleBonuses, getImgName
from gui.impl.gen.view_models.views.lobby.halloween.shop_view_model import PageTypeEnum as ShopPageTypeEnum
from uilogging.event.loggers import EventLogger
from uilogging.event.constants import EVENT_LOG_KEYS
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
_R_BACKPORT_TOOLTIP = R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent()
_NO_PRIZE_DIFFICULTY = 3
_EVENT_ALL_VIDEO = 'EventAllVideoURL'
_EVENT_INTRO_VIDEO = 'EventIntroVideoURL'

class MetaView(HangarEventView):
    gameEventController = dependency.descriptor(IGameEventController)
    settingsCore = dependency.descriptor(ISettingsCore)
    itemsCache = dependency.descriptor(IItemsCache)
    uiLogger = EventLogger(EVENT_LOG_KEYS.INTERROGATION_VIEW.value)
    soundEventChecker = dependency.descriptor(ISoundEventChecker)
    MAX_BONUSES_IN_VIEW = 4
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='eventMeta', entranceStates={}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='ev_halloween_2021_artefacts_enter', exitEvent='ev_halloween_2021_artefacts_exit')

    def __init__(self, layoutID, pageType):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = MetaViewModel()
        super(MetaView, self).__init__(settings)
        self.__keysCounterPanel = EventKeysCounterPanelView(VisualTypeEnum.META)
        self.__isMemoriesPageType = pageType == PageTypeEnum.MEMORIES.value
        self.__selectedBox = ''
        self.__eventRewards = self.gameEventController.getEventRewardController()
        self.__isFinalReward = pageType == PageTypeEnum.FINAL_REWARD.value
        self.__idGen = SequenceIDGenerator()
        self.__bonusCache = {}
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        self.__eventVehiclesInInventory = self.itemsCache.items.getVehicles(criteria=criteria).keys()
        self.__lastTankRecieved = None
        return

    @property
    def viewModel(self):
        return super(MetaView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == _R_BACKPORT_TOOLTIP:
            tooltipId = event.getArgument('tooltipId')
            if tooltipId == MetaViewModel.PRICE_TOOLTIP_ID:
                window = BackportTooltipWindow(createTooltipData(tooltip='', isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_COST, specialArgs=[]), self.getParentWindow())
                window.load()
                return window
            if tooltipId == MetaViewModel.INTERROGATION_TOOLTIP_ID:
                itemId = int(event.getArgument('itemId'))
                tokenID = self.__eventRewards.rewardBoxesIDsInOrder[itemId]
                rewardBox = self.__eventRewards.rewardBoxesConfig[tokenID]
                if self.__eventRewards.isRewardBoxOpened(tokenID):
                    status = EventInterrogationTooltipData.DECODED
                elif self.__eventRewards.isRewardBoxRecieved(tokenID):
                    status = EventInterrogationTooltipData.NOT_DECODED
                else:
                    status = EventInterrogationTooltipData.NOT_RECEIVED
                window = BackportTooltipWindow(createTooltipData(tooltip='', isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_INTERROGATION, specialArgs=[tokenID, InterrogationCtx(status=status, phase=int(rewardBox.questConditions.phaseNum), difficulty=int(rewardBox.questConditions.difficultyLevel))]), self.getParentWindow())
                window.load()
                return window
            if tooltipId == MetaViewModel.FINAL_INTERROGATION_TOOLTIP_ID:
                tokenID = self.__getFinalRewardBoxID()
                currMemories = self.__eventRewards.getCurrentRewardProgress()
                maxMemories = self.__eventRewards.getMaxRewardProgress()
                window = BackportTooltipWindow(createTooltipData(tooltip='', isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.EVENT_INTERROGATION, specialArgs=[tokenID, InterrogationCtx(status=EventInterrogationTooltipData.LAST, numberMemories=min(currMemories, maxMemories), totalMemories=maxMemories)]), self.getParentWindow())
                window.load()
                return window
            bonus = self.__bonusCache.get(tooltipId)
            if bonus:
                window = BackportTooltipWindow(createTooltipData(tooltip=bonus.tooltip, isSpecial=bonus.isSpecial, specialAlias=bonus.specialAlias, specialArgs=bonus.specialArgs), self.getParentWindow())
                window.load()
                return window
        super(MetaView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.halloween.tooltips.ShopVehicleTooltip():
            tankId = event.getArgument('tankId')
            return ShopVehicleTooltip(tankId)

    def _finalize(self):
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        self.viewModel.onClose -= self.__onClose
        self.viewModel.onPlayVideo -= self.__onPlayVideo
        self.viewModel.onDecodeVideo -= self.__onDecodeVideo
        self.viewModel.onSkipTasks -= self.__onSkipTasks
        self.viewModel.onShowInfoPage -= self.__onShowInfoPage
        self.viewModel.timeline.onClick -= self.__onTimelineItemClick
        self.viewModel.onTankPreview -= self.__onTankPreview
        self.gameEventController.onRewardBoxKeyUpdated -= self.__onUpdate
        self.gameEventController.onRewardBoxUpdated -= self.__onUpdate
        self.gameEventController.onIngameEventsUpdated -= self.__onIngameEventUpdate
        super(MetaView, self)._finalize()

    def _onLoading(self):
        super(MetaView, self)._onLoading()
        self.setChildView(self.__keysCounterPanel.layoutID, self.__keysCounterPanel)
        self.viewModel.onClose += self.__onClose
        self.viewModel.onPlayVideo += self.__onPlayVideo
        self.viewModel.onDecodeVideo += self.__onDecodeVideo
        self.viewModel.onSkipTasks += self.__onSkipTasks
        self.viewModel.onShowInfoPage += self.__onShowInfoPage
        self.viewModel.timeline.onClick += self.__onTimelineItemClick
        self.viewModel.onTankPreview += self.__onTankPreview
        self.gameEventController.onRewardBoxKeyUpdated += self.__onUpdate
        self.gameEventController.onRewardBoxUpdated += self.__onUpdate
        self.gameEventController.onIngameEventsUpdated += self.__onIngameEventUpdate
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        self.__onUpdate()

    def _initialize(self, *args, **kwargs):
        super(MetaView, self)._initialize(*args, **kwargs)
        if not self.__showOutroVideo():
            self.__showIntroVideo()

    def __fillModel(self):
        rewardBoxesConfig = self.__eventRewards.rewardBoxesConfig
        if self.__selectedBox in rewardBoxesConfig:
            ctx = self.__eventRewards.rewardBoxesConfig[self.__selectedBox].getCtx()
            ctx.update({'maxProgress': self.__eventRewards.getMaxRewardProgress(),
             'curProgress': self.__eventRewards.getCurrentRewardProgress(),
             'keyQuantity': self.__eventRewards.getRewardBoxKeyQuantity(),
             'isRewardOpened': self.__eventRewards.isRewardBoxOpened(self.__selectedBox),
             'isRewardRecieved': self.__eventRewards.isRewardBoxRecieved(self.__selectedBox)})
        else:
            ctx = {'boxIndex': MetaViewModel.INTRO_VIDEO_ITEM_ID,
             'isRewardOpened': True}
        self.__switchSoundState(ctx)
        with self.viewModel.transaction() as vm:
            self.__fillTimeline(vm, **ctx)
            if ctx['boxIndex'] == ctx.get('maxProgress'):
                if ctx['isRewardOpened']:
                    self.__fillFinalVideoPage(vm, **ctx)
                else:
                    self.__fillProgressPage(vm, **ctx)
            elif ctx['isRewardOpened']:
                self.__fillVideoPage(vm, **ctx)
            else:
                self.__fillTasksPage(vm, **ctx)
                self.__fillBonuses(vm, **ctx)

    @staticmethod
    def __switchSoundState(ctx):
        WWISE.WW_setState(EventHangarSound.ARTEFACTS_GROUP, EventHangarSound.ARTEFACTS_INTRO if ctx['boxIndex'] == MetaViewModel.INTRO_VIDEO_ITEM_ID else (EventHangarSound.ARTEFACTS_OPENED if ctx['isRewardOpened'] else (EventHangarSound.ARTEFACTS_ENCREPTED if ctx['isRewardRecieved'] else (EventHangarSound.ARTEFACTS_KING_TIGGER if ctx['boxIndex'] == ctx['maxProgress'] else EventHangarSound.ARTEFACTS_CLOSED))))

    @staticmethod
    def __fillVideoPage(vm, boxIndex=0, **kwargs):
        vm.setPageType(PageTypeEnum.VIDEO)
        vm.interrogation.setVideoIndex(boxIndex)

    @staticmethod
    def __fillFinalVideoPage(vm, **kwargs):
        vm.setPageType(PageTypeEnum.FINAL_VIDEO)
        vm.timeline.setState(StateEnum.ALL_RECEIVED)

    @staticmethod
    def __fillProgressPage(vm, curProgress=0, maxProgress=0, **kwargs):
        vm.setPageType(PageTypeEnum.PROGRESS)
        vm.setPrevUnlocked(min(curProgress, maxProgress))
        vm.setCurrentUnlocked(min(curProgress, maxProgress))
        vm.setTotal(maxProgress)

    @staticmethod
    def __fillTasksPage(vm, boxIndex=0, isRewardRecieved=False, keyQuantity=0, decodePrice=(None, 0), skipPrice=(None, 0), questConditions=(0, 0), **kwargs):
        vm.setPageType(PageTypeEnum.TASKS)
        vm.interrogation.setVideoIndex(boxIndex)
        vm.interrogation.setTaskPhase(questConditions.phaseNum)
        vm.interrogation.setTaskDifficulty(questConditions.difficultyLevel)
        vm.interrogation.setIsTaskDone(isRewardRecieved)
        vm.interrogation.setKeysAmount(keyQuantity)
        vm.interrogation.setDecodePrice(decodePrice.amount)
        vm.interrogation.setSkipPrice(skipPrice.amount)

    def __checkKeyCount(self, isDecodePrice):
        if self.__selectedBox is None:
            return False
        box = self.__eventRewards.rewardBoxesConfig.get(self.__selectedBox)
        if box is None:
            return False
        keyCount = self.__eventRewards.getRewardBoxKeyQuantity()
        amount = box.decodePrice.amount if isDecodePrice else box.skipPrice.amount
        if amount > keyCount:
            showShopView(ShopPageTypeEnum.KEYS)
            return False
        else:
            return True

    def __fillTimeline(self, vm, boxIndex=0, curProgress=0, maxProgress=0, **kwargs):
        with vm.timeline.transaction() as tlm:
            tlm.setSelectedItemId(boxIndex)
            if boxIndex != MetaViewModel.INTRO_VIDEO_ITEM_ID:
                tlm.setState(StateEnum.DEFAULT if curProgress < maxProgress else StateEnum.ALL_RECEIVED)
                tlm.setCurrentProgress(min(curProgress, maxProgress))
                self.__fillTimelineTank(tlm)
                items = tlm.getItems()
                self.__filltimelineItems(items, maxProgress)

    def __fillTimelineTank(self, tlm):
        finalBoxID = self.__getFinalRewardBoxID()
        vehicle = self.__getRewardVehicle(finalBoxID)
        if vehicle is None:
            return
        else:
            tlm.timelineTank.setId(vehicle.intCD)
            tlm.timelineTank.setType(vehicle.type)
            tlm.timelineTank.setName(vehicle.shortUserName)
            return

    def __filltimelineItems(self, items, maxProgress):
        items.clear()
        for rewardBoxID in self.__eventRewards.rewardBoxesIDsInOrder:
            rewardBox = self.__eventRewards.rewardBoxesConfig[rewardBoxID]
            isRewardBoxRecieved = self.__eventRewards.isRewardBoxRecieved(rewardBoxID)
            isRewardBoxOpened = self.__eventRewards.isRewardBoxOpened(rewardBoxID)
            if rewardBox.boxIndex < maxProgress:
                itemModel = self.__fillTimelineItem(isRewardBoxRecieved, isRewardBoxOpened, rewardBox)
                items.addViewModel(itemModel)

        items.invalidate()

    def __fillTimelineItem(self, isRewardBoxRecieved, isRewardBoxOpened, rewardBox):
        if isRewardBoxOpened:
            itemState = ItemStateEnum.DECODED
        elif isRewardBoxRecieved:
            itemState = ItemStateEnum.RECEIVED
        else:
            itemState = ItemStateEnum.DEFAULT
        if rewardBox.bonusVehicles:
            itemPrize = PrizeEnum.PRIZE_TANK if filterVehicleBonuses(rewardBox.bonusVehicles, self.__eventVehiclesInInventory) else PrizeEnum.PRIZE_GIFT
        elif int(rewardBox.questConditions.difficultyLevel) != _NO_PRIZE_DIFFICULTY:
            itemPrize = PrizeEnum.PRIZE_GIFT
        else:
            itemPrize = PrizeEnum.NO_PRIZE
        item = TimelineItemModel()
        item.setItemId(rewardBox.boxIndex)
        item.setCost(rewardBox.decodePrice.amount)
        item.setBackgroundImage('{}_{}'.format(itemState.value, rewardBox.boxIndex + 1))
        item.setPrize(itemPrize)
        item.setItemState(itemState)
        return item

    def __fillBonuses(self, vm, **kwargs):
        bonusesModel = vm.interrogation.getBonuses()
        bonusesModel.clear()
        self.__fillVehicleBonuses(bonusesModel, **kwargs)
        self.__fillRewardBonuses(bonusesModel, **kwargs)

    def __fillRewardBonuses(self, bonusesModel, bonusRewards=None, **kwargs):
        if bonusRewards is not None:
            formatter = EventShopBundleBonusesAwardsComposer(self.MAX_BONUSES_IN_VIEW, getHW21MetaAwardFormatter())
            bonusRewards = formatter.getFormattedBonuses(bonusRewards, AWARDS_SIZES.BIG)
            for bonus in bonusRewards:
                tooltipId = '{}'.format(self.__idGen.next())
                self.__bonusCache[tooltipId] = bonus
                bonusModel = BonusModel()
                bonusModel.setLabel(bonus.label)
                bonusModel.setBonusType(bonus.bonusName)
                bonusModel.setIcon(getImgName(bonus.getImage(AWARDS_SIZES.BIG)))
                bonusModel.setTooltipId(tooltipId)
                bonusesModel.addViewModel(bonusModel)

            bonusesModel.invalidate()
        return

    def __fillVehicleBonuses(self, bonusesModel, bonusVehicles=None, **kwargs):
        if bonusVehicles is not None:
            for bonus in bonusVehicles:
                for veh, _ in bonus.getVehicles():
                    vehicle = self.itemsCache.items.getItemByCD(veh.intCD)
                    if vehicle.isInInventory:
                        continue
                    tankModel = TankModel()
                    tankModel.setId(veh.intCD)
                    tankModel.setName(vehicle.userName)
                    tankModel.setType(vehicle.type)
                    tankModel.setIconName(replaceHyphenToUnderscore(vehicle.name.replace(':', '-')))
                    bonusesModel.addViewModel(tankModel)

            bonusesModel.invalidate()
        return

    @async
    def __onApply(self, rewardBoxID, isQuest):
        if rewardBoxID:
            finalRewardBoxID = self.__getFinalRewardBoxID()
            if rewardBoxID != finalRewardBoxID:
                rewardBox = self.__eventRewards.rewardBoxesConfig[rewardBoxID]
                isOk, _ = yield await(showDecodeConfirmDialog(rewardBox.decodePrice if isQuest else rewardBox.skipPrice))
                if not isOk:
                    return
            self.__processOpenBox(rewardBoxID, isQuest)

    @process
    def __processOpenBox(self, rewardBoxID, isQuest):
        success = yield self.__eventRewards.openRewardBox(rewardBoxID, not isQuest)
        if success:
            self.soundEventChecker.lockPlayingSounds()
            self.__playVideo(rewardBoxID, callbackOnUnload=lambda boxID=rewardBoxID: (self.soundEventChecker.unlockPlayingSounds(restore=False), self.__showReward(boxID)))

    def __showReward(self, rewardBoxID):
        if self.gameEventController.isEnabled():
            isFinalReward = rewardBoxID == self.__getFinalRewardBoxID()
            showVideoRewardView(ctx=dict(boxId=rewardBoxID, callback=lambda boxID=rewardBoxID: self.__onRewardRecieved(boxID), eventVehiclesInInventory=self.__eventVehiclesInInventory, isFinalReward=isFinalReward))

    def __onRewardRecieved(self, rewardBoxID):
        if not self.__eventRewards.isEnabled():
            return
        self.__lastTankRecieved = self.__getRewardVehicle(rewardBoxID)
        if self.__eventRewards.isRewardBoxOpened(rewardBoxID):
            self.__selectedBox = rewardBoxID
            g_eventBus.handleEvent(events.HalloweenEvent(events.HalloweenEvent.BOX_OPENED), scope=EVENT_BUS_SCOPE.LOBBY)
            self.__onInventoryChanged()
            finalRewardBoxID = self.__getFinalRewardBoxID()
            if rewardBoxID == finalRewardBoxID:
                self.__setRewardBoxesShown(finalRewardBoxID)
                self.__notifyOnBoxSelected()
            elif self.__eventRewards.isRewardBoxRecieved(finalRewardBoxID):
                self.__onApply(finalRewardBoxID, True)

    def __onInventoryChanged(self):
        if self.__lastTankRecieved is not None and self.__lastTankRecieved.isInInventory and self.__lastTankRecieved.isOnlyForEventBattles:
            g_currentVehicle.selectEventVehicle(self.__lastTankRecieved.invID)
            self.__lastTankRecieved = None
        return

    def __showFinalVideo(self, rewardBoxID):
        isFinalRewardRecieved = self.__eventRewards.isRewardBoxRecieved(rewardBoxID)
        if isFinalRewardRecieved:
            self.__onApply(rewardBoxID, True)

    def __onPlayVideo(self):
        self.__playVideo(self.__selectedBox)

    def __playVideo(self, box, callbackOnUnload=None):
        showBrowserOverlayView(GUI_SETTINGS.lookup(box), alias=VIEW_ALIAS.BROWSER_OVERLAY, webHandlers=createHangarWebHandlers(), forcedSkipEscape=True, callbackOnLoad=lambda : (self.uiLogger.videoStarted(), WWISE.WW_eventGlobal(EventHangarSound.PLAY_VIDEO if callbackOnUnload is None else EventHangarSound.DECODED_REWARD)), callbackOnUnload=lambda : (self.uiLogger.videoStopped(box), callbackOnUnload and callbackOnUnload()))

    def __playAllVideo(self):
        maxProgress = self.__eventRewards.getMaxRewardProgress()
        curProgress = self.__eventRewards.getCurrentRewardProgress()
        if curProgress > maxProgress:
            showBrowserOverlayView(GUI_SETTINGS.lookup(_EVENT_ALL_VIDEO), webHandlers=createHangarWebHandlers(), callbackOnLoad=lambda : WWISE.WW_eventGlobal(EventHangarSound.PLAY_VIDEO), forcedSkipEscape=True)

    def __onDecodeVideo(self):
        if self.__checkKeyCount(isDecodePrice=True):
            self.__onApply(self.__selectedBox, True)

    def __onSkipTasks(self):
        if self.__checkKeyCount(isDecodePrice=False):
            self.__onApply(self.__selectedBox, False)

    def __getFinalRewardBoxID(self):
        return next(reversed(self.__eventRewards.rewardBoxesIDsInOrder), '')

    def __getRewardVehicle(self, boxID):
        bonusVehicles = self.__eventRewards.rewardBoxesConfig[boxID].bonusVehicles
        if bonusVehicles is not None:
            for bonus in bonusVehicles:
                for veh, _ in bonus.getVehicles():
                    vehicle = self.itemsCache.items.getItemByCD(veh.intCD)
                    return vehicle

        return

    def __onTankPreview(self):
        finalBoxID = self.__getFinalRewardBoxID()
        vehicle = self.__getRewardVehicle(finalBoxID)
        if self.__eventRewards.isRewardBoxOpened(finalBoxID) and vehicle and vehicle.isInInventory:
            selectVehicleInHangar(vehicle.intCD, leaveEventMode=True)
        else:
            goToHalloweenKingRewardOnScene(previewAlias=VIEW_ALIAS.HALLOWEEN_META_REWARDS)

    def __onClose(self):
        showHangar()

    def __onShowInfoPage(self):
        showInterrogationInfoWindow()

    def __onUpdate(self):
        if not self.__selectedBox:
            self.__selectedBox = next(iter(self.__eventRewards.rewardBoxesIDsInOrder), '')
            if self.__isFinalReward:
                self.__selectedBox = self.__getFinalRewardBoxID()
            elif self.__isMemoriesPageType:
                rewardBoxes = self.__eventRewards.rewardBoxesConfig
                for park in self.__eventRewards.rewardBoxesIDsInOrder:
                    for bonus in rewardBoxes[park].bonusVehicles:
                        for vehicle, _ in bonus.getVehicles():
                            if g_currentPreviewVehicle.intCD == vehicle.intCD:
                                self.__selectedBox = park
                            break

            else:
                self.__selectedBox = next(self.__eventRewards.iterAvailbleRewardBoxIDsInOrder(), self.__selectedBox)
            self.__notifyOnBoxSelected()
        self.__fillModel()
        self.__setRewardBoxesShown()

    def __onIngameEventUpdate(self):
        if not self.__eventRewards.isEnabled():
            self.__onClose()

    def __getRewardBoxMask(self, rewardBoxID):
        return 1 << self.__eventRewards.rewardBoxesConfig[rewardBoxID].boxIndex

    def __setRewardBoxesShown(self, boxID=''):
        rewardBoxes = self.__eventRewards.rewardBoxesConfig
        value = self.settingsCore.serverSettings.getGameEventStorage().get(UIGameEventKeys.REWARD_BOXES_SHOWN)
        if value is not None:
            if boxID in rewardBoxes:
                value |= self.__getRewardBoxMask(boxID)
            else:
                for rewardBoxID in self.__eventRewards.iterAvailbleRewardBoxIDsInOrder():
                    if rewardBoxID != self.__getFinalRewardBoxID():
                        value |= self.__getRewardBoxMask(rewardBoxID)

        self.settingsCore.serverSettings.saveInGameEventStorage({UIGameEventKeys.REWARD_BOXES_SHOWN: value if value is not None else 0})
        return

    def __showIntroVideo(self):
        serverSettings = self.settingsCore.serverSettings
        if not bool(serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.EVENT_INTERROGATION_INFO)):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.EVENT_INTERROGATION_INFO: HINT_SHOWN_STATUS})
            self.__playVideo(_EVENT_INTRO_VIDEO, callbackOnUnload=showInterrogationInfoWindow)

    def __showOutroVideo(self):
        serverSettings = self.settingsCore.serverSettings
        finalBoxID = self.__getFinalRewardBoxID()
        finalBoxMask = self.__getRewardBoxMask(finalBoxID)
        wasShown = serverSettings.getGameEventStorage().get(UIGameEventKeys.REWARD_BOXES_SHOWN) & finalBoxMask
        if not wasShown:
            if self.__eventRewards.isRewardBoxRecieved(finalBoxID):
                self.__onApply(finalBoxID, True)
                return True
            if self.__eventRewards.isRewardBoxOpened(finalBoxID):
                self.__playVideo(finalBoxID, callbackOnUnload=lambda boxID=finalBoxID: self.__showReward(boxID))
                return True
        return False

    def __onTimelineItemClick(self, args):
        itemId = int(args.get('itemId', 0))
        if self.__eventRewards.getMaxRewardProgress() >= itemId >= 0:
            rewardBoxes = dict(((i, box) for i, box in enumerate(self.__eventRewards.rewardBoxesIDsInOrder)))
            if not self.__showOutroVideo():
                self.__selectedBox = rewardBoxes[itemId]
                self.__onUpdate()
                self.__notifyOnBoxSelected()
        elif itemId == MetaViewModel.INTRO_VIDEO_ITEM_ID:
            self.__selectedBox = _EVENT_INTRO_VIDEO
            self.__onUpdate()
        else:
            self.__playAllVideo()

    def __notifyOnBoxSelected(self):
        g_eventBus.handleEvent(events.HalloweenEvent(events.HalloweenEvent.BOX_SELECTED, ctx={'boxID': self.__selectedBox}), scope=EVENT_BUS_SCOPE.LOBBY)
