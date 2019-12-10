# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_glade_view.py
import BigWorld
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_group_slots_model import NyGroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.ny_slot_model import NySlotModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.views.new_year_decorations_popover import NewYearDecorationsPopover
from gui.impl.new_year.views.ny_mega_decorations_popover import NYMegaDecorationsPopover
from gui.impl.new_year.views.tabs_controller import GladeTabsController
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_glade_view_model import NewYearGladeViewModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.lobby.loot_box.loot_box_entry_point import LootboxesEntrancePointWidget
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from items.components.ny_constants import ToyTypes, TOY_TYPES_BY_OBJECT, INVALID_TOY_ID, MAX_TOY_RANK
from new_year.ny_constants import CustomizationObjects, SyncDataKeys, AdditionalCameraObject
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager, ITalismanSceneController
_SIDEBAR_OBJECTS_ORDER = (CustomizationObjects.FIR,
 CustomizationObjects.TABLEFUL,
 CustomizationObjects.INSTALLATION,
 CustomizationObjects.ILLUMINATION)
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE,
                                         CustomizationObjects.TABLEFUL: NewYearSoundEvents.KITCHEN,
                                         CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK,
                                         CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE,
                                         AdditionalCameraObject.MASCOT: NewYearSoundEvents.TALISMAN},
 NewYearSoundConfigKeys.EXIT_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE_EXIT,
                                     CustomizationObjects.TABLEFUL: NewYearSoundEvents.KITCHEN_EXIT,
                                     CustomizationObjects.INSTALLATION: NewYearSoundEvents.SNOWTANK_EXIT,
                                     CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE_EXIT,
                                     AdditionalCameraObject.MASCOT: NewYearSoundEvents.TALISMAN_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {CustomizationObjects.FIR: NewYearSoundStates.TREE,
                                      CustomizationObjects.TABLEFUL: NewYearSoundStates.KITCHEN,
                                      CustomizationObjects.INSTALLATION: NewYearSoundStates.SNOWTANK,
                                      CustomizationObjects.ILLUMINATION: NewYearSoundStates.LIGHTE,
                                      AdditionalCameraObject.MASCOT: NewYearSoundStates.TALISMAN}}

@trackLifeCycle('new_year.main_view')
class NewYearGladeView(NewYearHistoryNavigation):
    __slots__ = ('__selectedObject', '__anchors', '__tabsController')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)
    _talismanController = dependency.descriptor(ITalismanSceneController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_glade_view.NewYearGladeView())
        settings.model = NewYearGladeViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearGladeView, self).__init__(settings)
        self.__tabsController = GladeTabsController()

    @property
    def viewModel(self):
        return super(NewYearGladeView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return NewYearPartsTooltipContent() if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent() else super(NewYearGladeView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        slotId = int(event.getArgument('slotId'))
        if event.contentID == R.views.lobby.new_year.views.new_year_decorations_popover.NewYearDecorationsPopover():
            return NewYearDecorationsPopover(slotId)
        return NYMegaDecorationsPopover(slotId) if event.contentID == R.views.lobby.new_year.views.ny_mega_decorations_popover.NyMegaDecorationsPopover() else super(NewYearGladeView, self).createPopOverContent(event)

    def _initialize(self, soundConfig=None, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        super(NewYearGladeView, self)._initialize(soundConfig)
        self._newYearSounds.playEvent(NewYearSoundEvents.GLADE)
        self.viewModel.onSideBarBtnClick += self.__onSideBarBtnClick
        self.viewModel.onHoverSlot += self.__onHoverSlot
        self.viewModel.onHoverOutSlot += self.__onHoverOutSlot
        self.viewModel.onSelectNewTalismanClick += self.__onSelectNewTalismanClick
        self._nyController.onDataUpdated += self.__onDataUpdated
        BigWorld.callback(0.1, self.__registerDragging)
        with self.viewModel.transaction() as model:
            self.__tabsController.updateTabModels(model.getItemsTabBar())
            self.__updateAnchors(fullUpdate=True, model=model)
            isMascotView = False
            for idx, itemModel in enumerate(self.viewModel.getItemsTabBar()):
                if itemModel.getName() == self.getCurrentObject():
                    model.setStartIndex(idx)
                    if itemModel.getName() == AdditionalCameraObject.MASCOT:
                        isMascotView = True

            model.setIsMascotTab(isMascotView)
        self.setChildView(R.dynamic_ids.lootBoxEntryPointHolder(), LootboxesEntrancePointWidget())
        self._talismanController.setTalismansInteractive(True)

    def _finalize(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_OFF), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        self.viewModel.onHoverSlot -= self.__onHoverSlot
        self.viewModel.onHoverOutSlot -= self.__onHoverOutSlot
        self.viewModel.onSideBarBtnClick -= self.__onSideBarBtnClick
        self.viewModel.onSelectNewTalismanClick -= self.__onSelectNewTalismanClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        self._talismanController.setTalismansInteractive(False)
        super(NewYearGladeView, self)._finalize()
        self._newYearSounds.playEvent(NewYearSoundEvents.GLADE_EXIT)

    def _afterObjectSwitch(self):
        self.__updateAnchors(fullUpdate=True)
        self._newYearSounds.onEnterView()

    def __getCurrentObjectSlotsDescrs(self):
        return self._nyController.getSlotDescrs(self.getCurrentObject())

    def __registerDragging(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_ON), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)

    def __onNotifyCursorDragging(self, event):
        isDragging = event.ctx.get('isDragging', False)
        self.viewModel.setIsDragging(isDragging)

    def __onSideBarBtnClick(self, args):
        objectName = args['objectName']
        if objectName != self.getCurrentObject():
            self._switchObject(objectName)
            self._newYearSounds.onExitView()

    def __onSelectNewTalismanClick(self):
        self._talismanController.switchToPreview()

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as model:
            checkKeys = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS, SyncDataKeys.TALISMAN_TOY_TAKEN}
            isNeedUpdate = len(checkKeys.intersection(keys)) > 0
            if isNeedUpdate:
                self.__updateAnchors(fullUpdate=False, model=model)
                self.__tabsController.updateTabModels(model.getItemsTabBar())

    @replaceNoneKwargsModel
    def __updateAnchors(self, fullUpdate, model=None):
        isMascotView = self.getCurrentObject() == AdditionalCameraObject.MASCOT
        model.setIsMascotTab(isMascotView)
        if isMascotView:
            model.groupSlots.clear()
            model.groupSlots.invalidate()
            talismanCount = len(self._nyController.getTalismans(True))
            talismanState = NewYearGladeViewModel.TALISMAN_DISABLED
            if self._nyController.getFreeTalisman() > 0:
                talismanState = NewYearGladeViewModel.TALISMAN_SELECT_NEW
            elif talismanCount > 0:
                if not self._nyController.isTalismanToyTaken():
                    talismanState = NewYearGladeViewModel.TALISMAN_GIFT_READY
                else:
                    talismanState = NewYearGladeViewModel.TALISMAN_GIFT_WAIT
            model.setTalismanGiftState(talismanState)
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
                toyType = ToyTypes.MEGA_COMMON if slotDescr.type in ToyTypes.MEGA else slotDescr.type
                icon = R.images.gui.maps.icons.new_year.decorationTypes.blue_48.dyn(toyType)()
                rankIcon = R.invalid()
                isEmpty = True
                if toyID != INVALID_TOY_ID:
                    toy = self._itemsCache.items.festivity.getToys().get(toyID)
                    isMaxLevel = toy.getRank() >= MAX_TOY_RANK
                    icon = toy.getIcon()
                    rankIcon = toy.getRankIcon()
                    isEmpty = False
                slot.setRankIcon(rankIcon)
                slot.setIsMega(slotDescr.type in ToyTypes.MEGA)
                slot.setSlotId(slotDescr.id)
                slot.setIcon(icon)
                slot.setIsMaxLevel(isMaxLevel)
                slot.setIsBetterAvailable(self._nyController.checkForNewToys(slot=slotDescr.id))
                slot.setIsEmpty(isEmpty)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

            if fullUpdate:
                model.groupSlots.addViewModel(groupModel)

        if fullUpdate:
            model.groupSlots.invalidate()

    def __hideUI(self, _):
        self.viewModel.setIsVisible(False)

    def __showUI(self, _):
        self.viewModel.setIsVisible(True)

    def __getEntranceSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.ENTRANCE_EVENT, {}).get(self.getCurrentObject())

    def __getExitSoundEvent(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.EXIT_EVENT, {}).get(self._navigationState.lastViewedObject)

    def __getSoundStateValue(self):
        return _SOUNDS_MAP.get(NewYearSoundConfigKeys.STATE_VALUE, {}).get(self.getCurrentObject())

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __setSlotHighlight(self, slotId, isEnabled):
        slot = self._nyController.getSlotDescrs()[slotId]
        self._customizableObjectsMgr.setSlotHighlight(slot, isEnabled)
