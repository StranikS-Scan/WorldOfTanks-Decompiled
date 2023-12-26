# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/glade/ny_glade_view.py
import logging
import typing
import CGF
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NY_MAX_LEVEL_MESSAGE_CLOSE, NY_REWARD_KIT_OPEN
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import adisp_process
from ny_common.settings import NYLootBoxConsts
from constants import CURRENT_REALM
from cgf_components.hangar_camera_manager import HangarCameraManager
from gui import SystemMessages
from gui.SystemMessages import SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.ny_constants import TutorialStates
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_resource_collector_tooltip_model import CollectorTooltipType
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.levelup_price_model import LevelupPriceModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_resource_collector_model import CollectState
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import AnimationLevelUpStates
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.slot_model import SlotModel
from gui.impl.lobby.new_year.glade.ny_toys_list import NyToysList
from gui.impl.lobby.new_year.ny_selectable_logic_presenter import SelectableLogicPresenter
from gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.impl.lobby.new_year.scene_rotatable_view import SceneRotatableView
from gui.impl.lobby.new_year.tooltips.ny_customization_object_tooltip import NyCustomizationObjectTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_decoration_unavailable_tooltip import NyDecorationUnavailableTooltip
from gui.impl.lobby.new_year.tooltips.ny_resource_collector_tooltip import NyResourceCollectorTooltip
from gui.impl.lobby.new_year.tooltips.ny_reward_kits_unavailable_tooltip import NyRewardKitsUnavailableTooltip
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.new_year_helper import getRewardKitsCount, formatRomanNumber
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import NYTabCtx, showLootBoxEntry, showLootBoxBuyWindow, showResourcesIntroWindow
from gui.shared.events import ObjectHoverEvent
from gui.shared.lock_overlays import lockNotificationManager
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.scheduled_notifications import PeriodicNotifier
from gui.shared.view_helpers.blur_manager import CachedBlur
from helpers import dependency, time_utils
from items.components.ny_constants import INVALID_TOY_ID, TOY_TYPES_BY_OBJECT, CurrentNYConstants, CustomizationObjects, NYFriendServiceDataTokens
from messenger.proto.events import g_messengerEvents
from new_year.newyear_cgf_components.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.ny_constants import SyncDataKeys, NyWidgetTopMenu, NYObjects, NY_LEVEL_UP_NOTIFICATION_LOCK_KEY, MegaDecorationsObjects
from new_year.ny_helper import getNYGeneralConfig
from new_year.ny_level_helper import NewYearAtmospherePresenter
from new_year.ny_notifications_helpers import checkAndNotifyAllDecorationReceived
from new_year.ny_processor import BuyObjectLevel
from new_year.ny_resource_collecting_helper import getCollectingCooldownTime, getAvgResourcesByCollecting, isCollectingAvailable, isExtraCollectingAvailable, getSkippedDays
from new_year.ny_toy_info import NewYearCurrentToyInfo
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IWalletController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.new_year import INewYearController
from wg_async import wg_async, await_callback
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import NyGladeViewModel
    from ny_common.ObjectsConfig import ObjectsConfig
_logger = logging.getLogger(__name__)
_MEGA_DECORATION_CAMERA_BY_OBJECT = {CustomizationObjects.FIR: MegaDecorationsObjects.BRIDGE,
 CustomizationObjects.FAIR: MegaDecorationsObjects.WHEEL,
 CustomizationObjects.INSTALLATION: MegaDecorationsObjects.CASTLE}

class NyGladeView(SceneRotatableView, SelectableLogicPresenter):
    __slots__ = ('__currentObject', '__toysList', '__notifier', '__blur', '__hoveredObjectName', '__levelUpInProgress', '__resourceCollectingLock', '__cameraManager', '__totalAtmPoints')
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __nyController = dependency.descriptor(INewYearController)
    __wallet = dependency.instance(IWalletController)

    def __init__(self, gladeModel, parentView):
        self.__currentObject = None
        self.__toysList = NyToysList()
        self.__notifier = None
        self.__blur = None
        self.__hoveredObjectName = None
        self.__levelUpInProgress = False
        self.__resourceCollectingLock = False
        self.__cameraManager = None
        self.__totalAtmPoints = None
        super(NyGladeView, self).__init__(gladeModel, parentView)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentTab(self):
        return self.__currentObject

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyCustomizationObjectTooltip() and self.__hoveredObjectName:
            return NyCustomizationObjectTooltip(self.__hoveredObjectName)
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationTooltip(toyID)
        if contentID == R.views.lobby.new_year.tooltips.NyDecorationUnavailableTooltip():
            toyID = event.getArgument('toyID')
            return NyDecorationUnavailableTooltip(toyID)
        if event.contentID == R.views.lobby.new_year.tooltips.NyRewardKitsUnavailableTooltip():
            return NyRewardKitsUnavailableTooltip()
        if contentID == R.views.lobby.new_year.tooltips.NyResourceCollectorTooltip():
            collectorTooltipType = CollectorTooltipType(event.getArgument('type'))
            return NyResourceCollectorTooltip(collectorTooltipType)
        return super(NyGladeView, self).createToolTipContent(event, contentID)

    def initialize(self, *args, **kwargs):
        super(NyGladeView, self).initialize(*args, **kwargs)
        self.__blur = CachedBlur(blurRadius=0.1)
        self.__toysList.initialize(self.viewModel.toySlotsBar)
        self.__currentObject = NewYearNavigation.getCurrentObject()
        self.__notifier = PeriodicNotifier(lambda : time_utils.ONE_SECOND, self.__updateResourceCollectingByNotifier, periods=(time_utils.ONE_SECOND,))
        self.__cameraManager = CGF.getManager(self.__hangarSpace.spaceID, HangarCameraManager)
        self.__cameraManager.onCameraSwitched += self.__onCameraSwitched
        self._itemsCache.onSyncCompleted += self.__onSyncCompleted
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        NewYearNavigation.onSidebarSelected += self.__onSideBarSelected
        self.__totalAtmPoints = NewYearAtmospherePresenter.getTotalAtmospherePoints()
        currentState = self.__getCurrentState()
        if currentState <= TutorialStates.INTRO:
            self.__startTutorial()
        if self.__getCurrentState() < TutorialStates.FINISHED and self.currentTab == NYObjects.RESOURCES:
            showResourcesIntroWindow()
        with self.viewModel.transaction() as model:
            model.setTabName(self.__currentObject)
            model.toySlotsBar.setHasNewToysAnimation(False)
            model.setHasChangedViewAnimation(False)
            model.setAnimationLevelUpState(AnimationLevelUpStates.IDLE)
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateResourceCollecting(model=model)
            self.__updateRewardKitEntryPoint()
            self.__updateUpgradeInfo(model=model)

    def finalize(self):
        self._itemsCache.onSyncCompleted -= self.__onSyncCompleted
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        NewYearNavigation.onSidebarSelected -= self.__onSideBarSelected
        self.__cameraManager.onCameraSwitched -= self.__onCameraSwitched
        self.__toysList.finalize()
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__totalAtmPoints = None
        for slot in self._nyController.getSlotDescrs():
            self.__setSlotHighlight(slot.id, False)

        self.__clearPopovers()
        if self.__blur is not None:
            self.__blur.fini()
            self.__blur = None
        self.__checkAndStopAnimation()
        super(NyGladeView, self).finalize()
        return

    def _getInfoForHistory(self):
        return {}

    def _getEvents(self):
        return super(NyGladeView, self)._getEvents() + ((self.viewModel.toySlotsBar.onHoverSlot, self.__onHoverSlot),
         (self.viewModel.toySlotsBar.onHoverOutSlot, self.__onHoverOutSlot),
         (self.viewModel.toySlotsBar.onSelectSlot, self.__onSelectSlot),
         (self.viewModel.toySlotsBar.onAnimationEnd, self.__onUpdateToysAnimationEnd),
         (self.viewModel.resourceCollector.onCollect, self.__onCollect),
         (self.viewModel.resourceCollector.onHideFinishedStatus, self.__onHideFinishedStatus),
         (self.viewModel.customizationLevelUp.onLevelUp, self.__onLevelUp),
         (self.viewModel.rewardKit.onOpenKit, self.__onOpenKit),
         (self.viewModel.maxLevelReward.onAccept, self.__onMaxLevelRewardAccept),
         (self.viewModel.onNextTutorialState, self.__onNextTutorialState),
         (self.viewModel.onSetTutorialState, self.__onSetTutorialState),
         (self.viewModel.onMaxLevelMessageClosed, self.__onMaxLevelMessageClosed),
         (self.viewModel.onUpdateContentModel, self.__onUpdateContentModel),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (self._nyController.currencies.onBalanceUpdated, self.__onBalanceUpdated),
         (self._nyController.onWidgetLevelUpAnimationEnd, self.__setAnimationEnd),
         (self._nyController.resourceCollecting.onCollectingUpdateLock, self.__onCollectingLock),
         (self._nyController.resourceCollecting.onStartCollectingAvailableAnim, self.__onCollectigAvailable),
         (self.__wallet.onWalletStatusChanged, self.__onWalletStatusChanged),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdate),
         (NewYearNavigation.onPreSwitchView, self.__onPreSwitchView))

    def __lockNotifications(self):
        g_messengerEvents.onLockPopUpMessages(key=self.__class__.__name__, lockHigh=True)
        lockNotificationManager(lock=True, postponeActive=True, source=NY_LEVEL_UP_NOTIFICATION_LOCK_KEY)

    def __unlockNotifications(self):
        g_messengerEvents.onUnlockPopUpMessages(key=self.__class__.__name__)
        lockNotificationManager(lock=False, releasePostponed=True, source=NY_LEVEL_UP_NOTIFICATION_LOCK_KEY)

    def __onConverterOpen(self, event):
        with self.viewModel.transaction() as model:
            model.setIsConverterOpened(True)

    def __onConverterClose(self, event):
        with self.viewModel.transaction() as model:
            model.setIsConverterOpened(False)

    def _getListeners(self):
        return ((ObjectHoverEvent.HOVER_IN, self.__customizationObjectHoverIn, EVENT_BUS_SCOPE.DEFAULT),
         (ObjectHoverEvent.HOVER_OUT, self.__customizationObjectHoverOut, EVENT_BUS_SCOPE.DEFAULT),
         (events.NyResourcesConverterPopup.SHOW, self.__onConverterOpen, EVENT_BUS_SCOPE.DEFAULT),
         (events.NyResourcesConverterPopup.HIDE, self.__onConverterClose, EVENT_BUS_SCOPE.DEFAULT))

    def __onPreSwitchView(self, ctx):
        self.__hideMaxLevelReward()

    def __onSideBarSelected(self, ctx):
        if ctx.menuName != NyWidgetTopMenu.GLADE:
            return
        instantly = False
        self.__hideMaxLevelReward()
        tabName = ctx.tabName
        if self.__getCurrentState() < TutorialStates.FINISHED and tabName == NYObjects.RESOURCES:
            instantly = True
            showResourcesIntroWindow()
        self.__currentObject = tabName
        NewYearNavigation.switchTo(tabName, instantly=instantly)
        self.viewModel.setIsTabSwitching(True)
        self.__clearPopovers()

    def __onUpdateContentModel(self):
        with self.viewModel.transaction() as model:
            model.setIsTabSwitching(False)
            model.setTabName(self.__currentObject)
            self.__hoveredObjectName = None
            model.setShowCustomizationObjectTooltip(False)
            model.setHasChangedViewAnimation(False)
            model.toySlotsBar.setHasNewToysAnimation(False)
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateResourceCollecting(model=model)
            self.__updateUpgradeInfo(model=model)
            model.setIsMaxLevelMessageClosed(AccountSettings.getUIFlag(NY_MAX_LEVEL_MESSAGE_CLOSE))
        return

    def __onUpdate(self, *_, **__):
        if self.getNavigationAlias() != NewYearNavigation.getCurrentViewName():
            return
        newObject = NewYearNavigation.getCurrentObject()
        if self.__currentObject == newObject:
            return
        self.__currentObject = newObject
        if self.__getCurrentState() < TutorialStates.FINISHED and self.currentTab == NYObjects.RESOURCES:
            showResourcesIntroWindow()
        self.__checkAndStopAnimation()
        self.viewModel.setIsTabSwitching(True)
        self.__clearPopovers()
        NewYearNavigation.selectSidebarTabOutside(menuName=NyWidgetTopMenu.GLADE, tabName=newObject)

    def __onDataUpdated(self, keys, diff):
        checkKeys = {SyncDataKeys.INVENTORY_TOYS,
         SyncDataKeys.SLOTS,
         SyncDataKeys.OBJECTS_LEVELS,
         SyncDataKeys.RESOURCE_COLLECTING}
        if checkKeys.intersection(set(keys)):
            with self.viewModel.transaction() as model:
                self.__updateResourceCollecting(model=model)
                if self.__currentObject not in NYObjects.UPGRADABLE_GROUP or self._nyController.customizationObjects.getLevel(self.__currentObject) == 0:
                    return
                self.__updateSlots(fullUpdate=False, model=model)
                self.__updateUpgradeInfo(model=model)
                if SyncDataKeys.INVENTORY_TOYS in keys:
                    if SyncDataKeys.INVENTORY_TOYS not in diff[CurrentNYConstants.PDATA_KEY]:
                        return
                    slots = diff[CurrentNYConstants.PDATA_KEY][SyncDataKeys.INVENTORY_TOYS]
                    if self.__hasNewToysInDiff(slots) and not AccountSettings.getUIFlag(NY_REWARD_KIT_OPEN):
                        self.__updateNewToys(model=model, diff=slots)

    @staticmethod
    def __hasNewToysInDiff(diff):
        for toys in diff.values():
            for toyInfo in toys.values():
                _, isUnseen, _ = toyInfo
                return isUnseen > 0

    def __updateSlots(self, fullUpdate, model):
        slotsData = self._itemsCache.items.festivity.getSlotsData()
        groups = TOY_TYPES_BY_OBJECT.get(self.__currentObject, {})
        toys = self._itemsCache.items.festivity.getToys()
        actualLength = len(groups)
        currentLength = model.toySlotsBar.groupSlots.getItemsLength()
        if currentLength != actualLength:
            fullUpdate = True
            if actualLength > currentLength:
                for _ in range(actualLength - currentLength):
                    model.toySlotsBar.groupSlots.addViewModel(GroupSlotsModel())

            else:
                for _ in range(currentLength - actualLength):
                    model.toySlotsBar.groupSlots.removeItemByIndex(model.toySlotsBar.groupSlots.getItemsLength() - 1)

        slots = self._nyController.getSlotDescrs()
        for groupIdx, groupName in enumerate(groups):
            descrSlots = [ slot for slot in slots if slot.type == groupName ]
            groupModel = model.toySlotsBar.groupSlots.getItem(groupIdx)
            if fullUpdate:
                groupModel.slots.clear()
            for slotIdx, slotDescr in enumerate(descrSlots):
                toyID = slotsData[slotDescr.id]
                slotType = slotDescr.type
                if toyID == INVALID_TOY_ID:
                    icon = R.images.gui.maps.icons.newYear.decoration_types.craft.dyn(slotType)()
                    isEmpty = True
                else:
                    toy = toys[slotDescr.id][toyID]
                    icon = toy.getIcon()
                    isEmpty = False
                slot = SlotModel() if fullUpdate else groupModel.slots.getItem(slotIdx)
                slot.setSlotId(slotDescr.id)
                slot.setIsEmpty(isEmpty)
                slot.setToyId(toyID)
                slot.setIcon(icon)
                slot.setIsNew(self._nyController.checkForNewToysInSlot(slotDescr.id))
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.toySlotsBar.groupSlots.invalidate()

    def __getCurrentState(self):
        tutorialState = self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STATE)
        return tutorialState if tutorialState is not None else TutorialStates.INTRO

    def __onNextTutorialState(self):
        state = self.__getCurrentState() + 1
        if state < len(TutorialStates):
            self.__updateTutorialState(state)

    def __onSetTutorialState(self, args):
        self.__updateTutorialState(int(args['state']))

    def __updateTutorialState(self, state):
        serverSettings = self.__settingsCore.serverSettings
        if state >= len(TutorialStates):
            _logger.error('State %d is incorrect', state)
        else:
            if state == TutorialStates.INTRO:
                self.__blur.enable()
            if state == TutorialStates.WIDGET:
                self.__blur.disable()
                self._activateSelectableLogic()
            if state >= TutorialStates.UI:
                if not self.__settingsCore.serverSettings.getNewYearStorage().get(NewYearStorageKeys.TUTORIAL_STAGE_3_SEEN):
                    serverSettings.saveInNewYearStorage({NewYearStorageKeys.TUTORIAL_STAGE_3_SEEN: True})
            if state == TutorialStates.FINISHED:
                showResourcesIntroWindow()
                return
            serverSettings.saveInNewYearStorage({NewYearStorageKeys.TUTORIAL_STATE: state})

    def __startTutorial(self):
        self.__blur.enable()
        self._deactivateSelectableLogic()

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __onSelectSlot(self, args):
        with self.viewModel.transaction() as model:
            selectedSlotId = int(args['slotId'])
            model.toySlotsBar.setSelectedSlot(selectedSlotId)
            self.__toysList.open(selectedSlotId)

    def __onUpdateToysAnimationEnd(self):
        with self.viewModel.transaction() as model:
            model.toySlotsBar.setHasNewToysAnimation(False)
            currentLevel = self._nyController.customizationObjects.getLevel(self.__currentObject)
            object = self.__currentObject
            if self.__totalAtmPoints == NewYearAtmospherePresenter.getTotalAtmospherePoints():
                return
            self.__totalAtmPoints = NewYearAtmospherePresenter.getTotalAtmospherePoints()
            if self._nyController.customizationObjects.isMaxLevel(object, currentLevel):
                self.__showMaxLevelReward()
            else:
                model.setAnimationLevelUpState(AnimationLevelUpStates.WIDGET)

    def __setSlotHighlight(self, slotId, isEnabled):
        if self.__hangarSpace.space is None:
            return
        else:
            customizationManager = CGF.getManager(self.__hangarSpace.spaceID, LobbyCustomizableObjectsManager)
            if customizationManager:
                customizationManager.updateSlotHighlight(slotId, isEnabled)
            return

    def __onConverterOpened(self, isOpened):
        self.viewModel.setIsOpenConverter(isOpened)

    def __customizationObjectHoverIn(self, event):
        if self.currentTab == NYObjects.TOWN:
            self.viewModel.setShowCustomizationObjectTooltip(True)
            self.__hoveredObjectName = event.ctx.get('customizationObjectName')

    def __customizationObjectHoverOut(self, _):
        if self.currentTab == NYObjects.TOWN:
            self.viewModel.setShowCustomizationObjectTooltip(False)
            self.__hoveredObjectName = None
        return

    @replaceNoneKwargsModel
    def __updateResourceCollecting(self, model=None):
        cooldownTime = getCollectingCooldownTime()
        state = self.__getState(cooldownTime)
        model = model.resourceCollector
        model.setCollectState(state)
        model.setCooldown(cooldownTime)
        oneDayCollects = getAvgResourcesByCollecting(forceExtraCollect=False)
        manyDayCollects = getAvgResourcesByCollecting(forceExtraCollect=True)
        model.setBaseCollectAmount(oneDayCollects)
        model.setExtraCollectAmount(manyDayCollects - oneDayCollects)
        model.setSkippedDays(getSkippedDays())
        if cooldownTime > 0:
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()

    def __updateResourceCollectingByNotifier(self):
        if self.__resourceCollectingLock:
            return
        self.__updateResourceCollecting()

    def __onCollectingLock(self, lock):
        if lock:
            self.__notifier.stopNotification()
        self.__resourceCollectingLock = True

    def __onCollectigAvailable(self):
        self.__resourceCollectingLock = False
        self.__updateResourceCollecting()

    def __getState(self, cooldownTime):
        isAvailable = isCollectingAvailable()
        isExtraAvailable = isExtraCollectingAvailable()
        eventEndTimeTill = getNYGeneralConfig().getEventEndTime() - time_utils.getServerUTCTime()
        isFinishVisited = self.__nyController.getIsResourcesFinishVisited()
        if isAvailable:
            if not self.__wallet.isAvailable:
                if isExtraAvailable:
                    state = CollectState.UNAVAILABLEEXTRA
                else:
                    state = CollectState.UNAVAILABLE
            elif isExtraAvailable:
                state = CollectState.AVAILABLEEXTRA
            else:
                state = CollectState.AVAILABLE
        elif isFinishVisited:
            state = CollectState.FINISHEDHIDDEN
        elif cooldownTime > eventEndTimeTill:
            state = CollectState.FINISHED
        else:
            state = CollectState.COLLECTED
        return state

    @wg_async
    def __onCollect(self):
        result = yield await_callback(self._nyController.resourceCollecting.collect)()
        if result:
            self.__updateResourceCollecting()

    def __onHideFinishedStatus(self):
        self.__nyController.setIsResourcesFinishVisited(True)
        self.viewModel.resourceCollector.setCollectState(CollectState.FINISHEDHIDDEN)

    @adisp_process
    def __onLevelUp(self):
        if self.__levelUpInProgress:
            return
        self.__levelUpInProgress = True
        self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.PENDING)
        result = yield BuyObjectLevel(self.__currentObject).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType, priority=result.msgPriority)
        if result.success and result.auxData:
            data = result.auxData
            tokens = data.get('tokens')
            objectName = data.get('objectName')
            level = data.get('level', 0)
            self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.CUSTOMIZATION)
            self.__lockNotifications()
            decorationTokens = []
            if tokens:
                tokenIDs = tokens.keys()
                decorationTokens = [ tID for tID in NYFriendServiceDataTokens.HANGAR_DECORATIONS if tID in tokenIDs ]
            toysCount = 0
            if decorationTokens and objectName in CustomizationObjects.ALL and self._nyController.customizationObjects.isMaxLevel(objectName, level):
                slotTypes = TOY_TYPES_BY_OBJECT[objectName]
                objectsConfig = self._nyController.customizationObjects.getConfig()
                levelsDescr = objectsConfig.getObjectByID(objectName).getLevels()
                for levelDescr in levelsDescr:
                    for slotType in slotTypes:
                        slotCount = self._nyController.getNumberOfSlotsByType(slotType)
                        toysCount += levelDescr.getToyCountBySlotType(slotType) * slotCount

                SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.objectMaxLevel.dyn(objectName)()), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.LOW, messageData={'header': backport.text(R.strings.system_messages.newYear.objectLevelUp.header())})
                self.__updateMaxLevelReward(objectName, level, toysCount)
                checkAndNotifyAllDecorationReceived()
            else:
                for group in data.get(CurrentNYConstants.TOYS, {}).values():
                    toysCount += sum((count for count in group.values()))

                SystemMessages.pushMessage(backport.text(R.strings.system_messages.newYear.objectLevelUp.dyn(objectName)(), level=formatRomanNumber(level), items=toysCount), type=SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.LOW, messageData={'header': backport.text(R.strings.system_messages.newYear.objectLevelUp.header())})
        else:
            self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.IDLE)
            self.__levelUpInProgress = False

    def __setAnimationEnd(self):
        self.__levelUpInProgress = False
        self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.IDLE)
        self.__unlockNotifications()

    def __checkAndStopAnimation(self):
        self.viewModel.toySlotsBar.setHasNewToysAnimation(False)
        if self.viewModel.getAnimationLevelUpState() is not AnimationLevelUpStates.IDLE:
            self.viewModel.setHasChangedViewAnimation(True)
            self.__setAnimationEnd()

    def __updateMaxLevelReward(self, objectID, level, toysCount):
        with self.viewModel.transaction() as model:
            maxLevelReward = model.maxLevelReward
            maxLevelReward.setObjectType(objectID)
            maxLevelReward.setLevel(level)
            maxLevelReward.setToysCount(toysCount)

    def __showMaxLevelReward(self):
        self.viewModel.maxLevelReward.setIsVisible(True)
        cameraName = _MEGA_DECORATION_CAMERA_BY_OBJECT[NewYearNavigation.getCurrentObject()]
        self.__cameraManager.switchByCameraName(cameraName, instantly=False)

    def __onCameraSwitched(self, cameraName):
        if cameraName not in MegaDecorationsObjects.ALL():
            return
        self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.MAXLEVEL)

    def __hideMaxLevelReward(self):
        if self.viewModel.maxLevelReward.getIsVisible():
            self.viewModel.setAnimationLevelUpState(AnimationLevelUpStates.WIDGET)
            self.viewModel.maxLevelReward.setIsVisible(False)
            self.__cameraManager.switchByCameraName(NewYearNavigation.getCurrentObject(), instantly=False)

    def __onMaxLevelRewardAccept(self):
        self.__hideMaxLevelReward()

    def __onMaxLevelMessageClosed(self):
        AccountSettings.setUIFlag(NY_MAX_LEVEL_MESSAGE_CLOSE, True)
        self.viewModel.setIsMaxLevelMessageClosed(True)

    @staticmethod
    def __onOpenKit():
        if getRewardKitsCount() > 0:
            showLootBoxEntry()
        else:
            showLootBoxBuyWindow()

    def __clearPopovers(self):
        with self.viewModel.transaction() as model:
            model.toySlotsBar.setSelectedSlot(-1)

    def __onSyncCompleted(self, *_):
        self.__updateRewardKitEntryPoint()
        self.__updateResourceCollecting()

    def __onSettingsChanged(self, *_):
        self.__updateRewardKitEntryPoint()

    def __updateRewardKitEntryPoint(self):
        kitsCount = getRewardKitsCount()
        kitViewed = self.__settingsCore.serverSettings.getSectionSettings(SETTINGS_SECTIONS.LOOT_BOX_VIEWED, 'count', 0)
        shopConfig = self.__lobbyCtx.getServerSettings().getLootBoxShop()
        source = shopConfig.get(NYLootBoxConsts.SOURCE, NYLootBoxConsts.EXTERNAL)
        with self.viewModel.rewardKit.transaction() as model:
            model.setKitsCount(kitsCount)
            model.setHasNew(kitsCount > kitViewed)
            model.setIsDisabled(not self.__lobbyCtx.getServerSettings().isLootBoxesEnabled())
            model.setRealm(CURRENT_REALM)
            model.setIsExternal(source == NYLootBoxConsts.EXTERNAL)

    @staticmethod
    def __onClickVideo():
        showInfoVideo()

    def __updateUpgradeInfo(self, model):
        if self.__currentObject not in NYObjects.UPGRADABLE_GROUP:
            model.setIsShowLevelUp(False)
            return
        else:
            currentLevel = self._nyController.customizationObjects.getLevel(self.__currentObject)
            objectsConfig = self._nyController.customizationObjects.getConfig()
            nextLevelDescr = objectsConfig.getObjectByID(self.__currentObject).getNextLevel(currentLevel)
            model.customizationLevelUp.setTargetLevel(currentLevel + 1)
            if nextLevelDescr is None:
                model.setIsShowLevelUp(False)
                return
            model.customizationLevelUp.setObject(self.__currentObject)
            model.setIsShowLevelUp(True)
            isEnoughToBuy = True
            pricesModel = model.customizationLevelUp.price
            pricesModel.clear()
            for currency, count in nextLevelDescr.getLevelPrice().iteritems():
                priceItem = LevelupPriceModel()
                priceItem.setCurrency(currency)
                priceItem.setValue(count)
                enoughCurrency = self._nyController.currencies.getResouceBalance(currency) >= count
                priceItem.setIsEnough(enoughCurrency)
                pricesModel.addViewModel(priceItem)
                if not enoughCurrency:
                    isEnoughToBuy = False

            model.customizationLevelUp.setIsEnoughToBuy(isEnoughToBuy)
            pricesModel.invalidate()
            return

    def __onBalanceUpdated(self):
        with self.viewModel.transaction() as model:
            self.__updateUpgradeInfo(model=model)

    def __updateNewToys(self, model, diff):
        groups = TOY_TYPES_BY_OBJECT.get(self.__currentObject, {})
        slots = self._nyController.getSlotDescrs()
        newToysCount = 0
        for groupIdx, groupName in enumerate(groups):
            descrSlots = [ slot for slot in slots if slot.type == groupName ]
            groupModel = model.toySlotsBar.groupSlots.getItem(groupIdx)
            for slotIdx, slotDescr in enumerate(descrSlots):
                slot = groupModel.slots.getItem(slotIdx)
                newToys = slot.getNewToys()
                newToys.clear()
                for toyId in diff.get(slotDescr.id, []):
                    newToysCount += 1
                    newToys.addString(NewYearCurrentToyInfo(toyId).getIconName())

        if newToysCount > 0:
            model.toySlotsBar.setHasNewToysAnimation(True)

    def __onWalletStatusChanged(self, *args):
        self.__updateResourceCollecting()
