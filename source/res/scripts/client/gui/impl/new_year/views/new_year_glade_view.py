# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_glade_view.py
import typing
import BigWorld
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from adisp import process
from async import async, await
from frameworks.wulf import ViewSettings
from gui import SystemMessages
from gui.impl.dialogs import dialogs
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_glade_view_model import NewYearGladeViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_group_slots_model import NyGroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_slot_model import NySlotModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_talisman_consts import NyTalismanConsts
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_talisman_progress_level_model import NyTalismanProgressLevelModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.lobby.loot_box.loot_box_entry_point import LootboxesEntrancePointWidget
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.mega_toy_bubble import MegaToyBubble
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.new_year_helper import TalismanGiftNotifier, IS_ROMAN_NUMBERS_ALLOWED, getLastObservedGiftStage, setLastObservedGiftStage
from gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.tooltips.new_year_talisman_progression_tooltip_content import NewYearTalismanProgressionTooltipContent
from gui.impl.new_year.views.new_year_decorations_popover import NewYearDecorationsPopover
from gui.impl.new_year.views.ny_mega_decorations_popover import NYMegaDecorationsPopover
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import LobbySimpleEvent
from helpers import dependency, uniprof
from helpers.func_utils import oncePerPeriod
from items.components.ny_constants import ToyTypes, TOY_TYPES_BY_OBJECT, INVALID_TOY_ID, MAX_TOY_RANK, MAX_TALISMAN_STAGE
from new_year.ny_constants import CustomizationObjects, SyncDataKeys, AdditionalCameraObject, NyWidgetTopMenu, NyTabBarMainView
from new_year.ny_processor import ChangeTalismanBonusStageProcessor
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager, ITalismanSceneController
from uilogging.decorators import loggerEntry, loggerTarget, simpleLog
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
_OBJECT_TO_TAB_TYPE = {CustomizationObjects.FIR: NyTalismanConsts.TAB_TOY_TYPE,
 CustomizationObjects.TABLEFUL: NyTalismanConsts.TAB_TOY_TYPE,
 CustomizationObjects.INSTALLATION: NyTalismanConsts.TAB_TOY_TYPE,
 CustomizationObjects.ILLUMINATION: NyTalismanConsts.TAB_TOY_TYPE,
 AdditionalCameraObject.MASCOT: NyTalismanConsts.TAB_MASCOT_TYPE,
 AdditionalCameraObject.CELEBRITY: NyTalismanConsts.TAB_CELEBRITY_TYPE}

@loggerTarget(logKey=NY_LOG_KEYS.NY_TALISMANS, loggerCls=NYLogger)
@trackLifeCycle('new_year.main_view')
class NewYearGladeView(NewYearHistoryNavigation):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _talismanController = dependency.descriptor(ITalismanSceneController)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_glade_view.NewYearGladeView())
        settings.model = NewYearGladeViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearGladeView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearGladeView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        return NewYearTalismanProgressionTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_talisman_progression_tooltip_content.NewYearTalismanProgressionTooltipContent() else super(NewYearGladeView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        slotId = int(event.getArgument('slotId'))
        if event.contentID == R.views.lobby.new_year.views.new_year_decorations_popover.NewYearDecorationsPopover():
            return NewYearDecorationsPopover(slotId)
        return NYMegaDecorationsPopover(slotId) if event.contentID == R.views.lobby.new_year.views.ny_mega_decorations_popover.NyMegaDecorationsPopover() else super(NewYearGladeView, self).createPopOverContent(event)

    @loggerEntry
    @uniprof.regionDecorator(label='ny.glade', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(NewYearGladeView, self)._initialize()
        self.viewModel.onHoverSlot += self.__onHoverSlot
        self.viewModel.onHoverOutSlot += self.__onHoverOutSlot
        self.viewModel.onSelectNewTalismanClick += self.__onSelectNewTalismanClick
        self.viewModel.onMouseEnterProgress += self.__onMouseEnterProgress
        self.viewModel.onIncreaseLevel += self.__onIncreaseGiftLevel
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._nyController.onDataUpdated += self.__onDataUpdated
        self.__talismanGiftNotifier = TalismanGiftNotifier(self.__updateTalismanGiftCooldown)
        BigWorld.callback(0.1, self.__registerDragging)
        with self.viewModel.transaction() as model:
            model.setPrevTotalReceivedToys(getLastObservedGiftStage())
            self.__updateAnchors(fullUpdate=True, model=model)
            self.__updateShards()
            model.setTabType(_OBJECT_TO_TAB_TYPE.get(self.getCurrentObject()))
        self.setChildView(R.dynamic_ids.lootBoxEntryPointHolder(), LootboxesEntrancePointWidget())
        self._talismanController.setTalismansInteractive(True)
        self._talismanController.onTalismanGiftProgressChanged += self.__updateTalismanProgress

    @uniprof.regionDecorator(label='ny.glade', scope='exit')
    def _finalize(self):
        self.__unregisterDragging()
        self.viewModel.onHoverSlot -= self.__onHoverSlot
        self.viewModel.onHoverOutSlot -= self.__onHoverOutSlot
        self.viewModel.onSelectNewTalismanClick -= self.__onSelectNewTalismanClick
        self.viewModel.onIncreaseLevel -= self.__onIncreaseGiftLevel
        self.viewModel.onMouseEnterProgress -= self.__onMouseEnterProgress
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._talismanController.onTalismanGiftProgressChanged -= self.__updateTalismanProgress
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__talismanGiftNotifier.stopNotification()
        self.__talismanGiftNotifier.clear()
        self._talismanController.setTalismansInteractive(False)
        super(NewYearGladeView, self)._finalize()

    def _afterObjectSwitch(self):
        self.__updateAnchors(fullUpdate=True)

    def __getCurrentObjectSlotsDescrs(self):
        return self._nyController.getSlotDescrs(self.getCurrentObject())

    def __registerDragging(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_ON), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)

    def __unregisterDragging(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_OFF), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)

    def __onNotifyCursorDragging(self, event):
        isDragging = event.ctx.get('isDragging', False)
        self.viewModel.setIsDragging(isDragging)

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.GLADE:
            return
        tabName = ctx.tabName
        if tabName != self.getCurrentObject():
            if tabName == NyTabBarMainView.CELEBRITY:
                self.switchByObjectName(tabName)
            else:
                self._switchObject(tabName)

    @simpleLog(action=NY_LOG_ACTIONS.NY_TALISMAN_SELECT_FROM_SCREEN)
    def __onSelectNewTalismanClick(self):
        self._talismanController.switchToPreview()

    @simpleLog(action=NY_LOG_ACTIONS.NY_TALISMAN_PROGRESS_CLICK)
    @oncePerPeriod(0.2)
    @async
    def __onIncreaseGiftLevel(self, args):
        levelIndex = int(args.get('level'))
        cost, shardsShortage, _ = self.__calcGiftUpgradeCost(levelIndex)
        talismanCount = len(self._nyController.getTalismans(isInInventory=True))
        level = levelIndex + 1
        self.viewModel.setExpectedTalismanLevel(level)
        confirm = yield await(dialogs.showNYGiftUpgradeDialog(self.getParentWindow(), level, cost, shardsShortage, talismanCount))
        if confirm:
            if shardsShortage:
                self._goToByViewAlias(ViewAliases.BREAK_VIEW, giftUpgradeCost=cost)
            else:
                self.__requestGiftUpgrade(levelIndex)
        else:
            self.viewModel.setExpectedTalismanLevel(self.viewModel.getTalismanLevel())

    @process
    def __requestGiftUpgrade(self, levelIndex):
        result = yield ChangeTalismanBonusStageProcessor(levelIndex).request()
        if result.userMsg:
            SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        if result.success:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.TALISMAN_GIFT_LVL_UP)

    def __calcGiftUpgradeCost(self, level):
        shardsCount = self._itemsCache.items.festivity.getShardsCount()
        talismanConfig = self.__lobbyCtx.getServerSettings().getNewYearTalismansConfig()
        receivedToys, currentStage = self._itemsCache.items.festivity.getTalismansStage()
        validUpgrade, cost, _ = talismanConfig.validateAndGetLevelUp(currentStage, receivedToys, level)
        shardsShortage = max(0, cost - shardsCount)
        return (cost, shardsShortage, validUpgrade)

    def __onMouseEnterProgress(self, _):
        self.viewModel.setShowTalismanHint(False)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.IS_TALISMAN_PROGRESS_HOVERED: True})

    def __updateShowTalismanHint(self, model):
        settings = self.__settingsCore.serverSettings.getNewYearStorage()
        if settings.get(NewYearStorageKeys.IS_TALISMAN_PROGRESS_HOVERED, False):
            return
        model.setShowTalismanHint(self._itemsCache.items.festivity.getShardsCount() > 100)

    def __onDataUpdated(self, keys):
        checkKeys = {SyncDataKeys.INVENTORY_TOYS,
         SyncDataKeys.SLOTS,
         SyncDataKeys.TALISMAN_TOY_TAKEN,
         SyncDataKeys.TALISMANS}
        isTalismanSequenceChanged = _OBJECT_TO_TAB_TYPE.get(self.getCurrentObject()) == NyTalismanConsts.TAB_MASCOT_TYPE and SyncDataKeys.TALISMANS_SEQUENCE_STAGE in keys
        with self.viewModel.transaction() as model:
            if set(keys) & checkKeys or isTalismanSequenceChanged:
                self.__updateAnchors(fullUpdate=False, model=model)
            if SyncDataKeys.TOY_FRAGMENTS in keys:
                self.__updateShards()

    @replaceNoneKwargsModel
    def __updateAnchors(self, fullUpdate, model=None):
        tabType = _OBJECT_TO_TAB_TYPE.get(self.getCurrentObject())
        model.setTabType(tabType)
        if tabType == NyTalismanConsts.TAB_MASCOT_TYPE:
            model.groupSlots.clear()
            model.groupSlots.invalidate()
            talismanCount = len(self._nyController.getTalismans(isInInventory=True))
            lastDayOfEvent = self._nyController.isLastDayOfEvent()
            hasFreeTalisman = self._nyController.getFreeTalisman() > 0
            model.setHasTalismanToSelect(hasFreeTalisman)
            talismanState = NyTalismanConsts.TALISMAN_DISABLED
            if hasFreeTalisman and talismanCount == 0:
                talismanState = NyTalismanConsts.TALISMAN_SELECT_FIRST
            elif talismanCount > 0:
                self.__updateShowTalismanHint(model)
                if self._nyController.isTalismanToyTaken():
                    if lastDayOfEvent:
                        talismanState = NyTalismanConsts.TALISMAN_FINISHED
                    else:
                        talismanState = NyTalismanConsts.TALISMAN_GIFT_WAIT
                    self.__talismanGiftNotifier.startNotification()
                else:
                    talismanState = NyTalismanConsts.TALISMAN_GIFT_READY
                    self.__talismanGiftNotifier.stopNotification()
            model.setTalismanGiftState(talismanState)
            if fullUpdate:
                self.__updateTalismanProgress()
            return
        self.__talismanGiftNotifier.stopNotification()
        if tabType == NyTalismanConsts.TAB_CELEBRITY_TYPE:
            model.groupSlots.clear()
            model.groupSlots.invalidate()
            return
        slotsData = self._itemsCache.items.festivity.getSlots()
        if fullUpdate:
            model.groupSlots.clear()
        groups = TOY_TYPES_BY_OBJECT[self.getCurrentObject()]
        for groupIdx, groupName in enumerate(groups):
            descrSlots = [ descr for descr in self.__getCurrentObjectSlotsDescrs() if descr.type == groupName ]
            groupModel = NyGroupSlotsModel() if fullUpdate else model.groupSlots.getItem(groupIdx)
            for slotIdx, slotDescr in enumerate(descrSlots):
                slot = NySlotModel() if fullUpdate else groupModel.slots.getItem(slotIdx)
                isMaxLevel = False
                toyID = slotsData[slotDescr.id]
                isMegaToy = slotDescr.type in ToyTypes.MEGA
                toyType = ToyTypes.MEGA_COMMON if isMegaToy else slotDescr.type
                icon = R.invalid()
                rank = 0
                isEmpty = True
                if toyID != INVALID_TOY_ID:
                    toy = self._itemsCache.items.festivity.getToys().get(toyID)
                    isMaxLevel = toy.getRank() >= MAX_TOY_RANK
                    icon = toy.getIcon()
                    rank = toy.getRank()
                    isEmpty = False
                slot.setType(toyType)
                slot.setRank(rank)
                slot.setIsRomanNumbersAllowed(IS_ROMAN_NUMBERS_ALLOWED)
                slot.setIsMega(isMegaToy)
                slot.setSlotId(slotDescr.id)
                slot.setIcon(icon)
                slot.setIsMaxLevel(isMaxLevel)
                if isMegaToy:
                    isBetterAvailable = MegaToyBubble.mustBeShown(slotDescr.type, not isEmpty)
                else:
                    isBetterAvailable = self._nyController.checkForNewToys(slot=slotDescr.id)
                slot.setIsBetterAvailable(isBetterAvailable)
                slot.setIsEmpty(isEmpty)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

            if fullUpdate:
                model.groupSlots.addViewModel(groupModel)

        if fullUpdate:
            model.groupSlots.invalidate()

    def __updateTalismanProgress(self):
        talismanConfig = self.__lobbyCtx.getServerSettings().getNewYearTalismansConfig()
        receivedToys, currentStage = self._itemsCache.items.festivity.getTalismansStage()
        with self.viewModel.transaction() as model:
            model.setTotalReceivedToys(talismanConfig.getTotalReceivedToys(currentStage, receivedToys))
            model.setMaxReceivedToys(talismanConfig.getReceivedToysForMaxLevel())
            model.setExpectedTalismanLevel(currentStage)
            model.setTalismanLevel(currentStage)
        setLastObservedGiftStage(self.viewModel.getTotalReceivedToys())
        talismanLevelsInfo = self.viewModel.getTalismanLevelsInfo()
        talismanLevelsInfo.clear()
        for stage in xrange(1, MAX_TALISMAN_STAGE + 1):
            levelProgressModel = NyTalismanProgressLevelModel()
            levelProgressModel.setLevel(stage + 1)
            if stage > currentStage:
                result, cost, _ = talismanConfig.validateAndGetLevelUp(currentStage, receivedToys, stage)
                levelProgressModel.setCost(cost if result else 0)
            else:
                levelProgressModel.setCost(0)
            talismanLevelsInfo.addViewModel(levelProgressModel)

        talismanLevelsInfo.invalidate()

    def __updateShards(self):
        self.viewModel.setCurrentShards(self._itemsCache.items.festivity.getShardsCount())

    def __updateTalismanGiftCooldown(self, talismanGiftCooldown):
        self.viewModel.setTalismanGiftCooldown(talismanGiftCooldown)

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __setSlotHighlight(self, slotId, isEnabled):
        slot = self._nyController.getSlotDescrs()[slotId]
        self._customizableObjectsMgr.setSlotHighlight(slot, isEnabled)
