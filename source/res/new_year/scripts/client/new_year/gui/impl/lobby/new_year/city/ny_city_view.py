# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/city/ny_city_view.py
import CGF
import typing
from adisp import adisp_process
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import ReturnPlace
from gui_lootboxes.gui.shared.event_dispatcher import showStorageView
from frameworks.wulf import WindowLayer
from gui.impl.pub import PopOverWindow
from new_year.gui.impl.lobby.new_year.popovers.env_switcher_popover import EnvSwitcherPopover
from gui.impl.gui_decorators import args2params
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui import SystemMessages
from new_year.cgf.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.gui.impl.gen.view_models.common.customization_zone_type_model import CustomizationZone
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_view_model import NyCityViewModel
from new_year.gui.impl.lobby.new_year.city.ny_object_view import NyObjectView
from new_year.gui.impl.lobby.new_year.city.ny_objects_overview import NyObjectsOverview
from new_year.gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo, HoverObject, destroyGUIHoveredObject
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from new_year.gui.impl.lobby.new_year.tooltips.customization_zone_tooltip import CustomizationZoneTooltip
from new_year.gui.impl.lobby.new_year.tooltips.level_up_widget_tooltip import LevelUpWidgetTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from new_year.gui.impl.lobby.new_year.tooltips.ny_common_tooltip import NyCommonTooltip, getCommonTooltipArgsFromEvent
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.skeletons.new_year import INewYearEnvironmentSwitchController, INewYearCurrencyController
from new_year.gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from new_year.gui.shared.events import NewYearEvent
from new_year.helpers.server_settings import getNewYearObjectsConfig
from new_year.helpers.ny_helpers import getCurrentObjectLevel
from new_year.ny_constants import CustomizationObjects, ANCHOR_TO_OBJECT, SyncDataKeys, NyWidgetTopMenu, TOY_TO_CAMERA
from new_year_common.items.components.ny_constants import TOY_TYPES_BY_OBJECT, NewYearObjects
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from new_year.gui.impl.new_year.sounds import NewYearSoundsManager, NewYearSoundEvents
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.view_helpers.blur_manager import CachedBlur
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from shared_utils import findFirst
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.slot_model import SlotModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.group_slots_model import GroupSlotsModel
from new_year_common.items.components.ny_constants import INVALID_TOY_ID
from new_year.gui.impl.lobby.new_year.popovers.ny_decorations_popover import NyDecorationsPopover
from new_year.skeletons.new_year import INewYearController
from new_year.gui.shared.gui_items.processors.ny_processor import UpgradeCustomizationObjectLevel
if typing.TYPE_CHECKING:
    from new_year.gui.shared.event_dispatcher import NYTabCtx
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.atmosphere_animation_model import AtmosphereAnimationModel
    from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.city.ny_city_marker_model import NyCityMarkerModel
MAP_RETURN_PLACE = {CustomizationObjects.FIR: ReturnPlace.TO_FIR,
 CustomizationObjects.TEREM: ReturnPlace.TO_TEREM,
 CustomizationObjects.INSTALLATIONS: ReturnPlace.TO_INSTALLATIONS,
 CustomizationObjects.FAIR: ReturnPlace.TO_FAIR,
 CustomizationObjects.SNOW_SLIDE: ReturnPlace.TO_SNOW_SLIDE,
 CustomizationObjects.FIREWORKS: ReturnPlace.TO_FIREWORKS,
 NewYearObjects.CITY_VIEW: ReturnPlace.TO_NY_CUSTOMIZATION}
_DEFAULT_SELECTED_TOY_SLOT_ID = -1

class NewYearHangarSelectableLogic(HangarSelectableLogic):

    def _onMouseDown(self):
        isCloseMainView = self.selected3DEntity is not None
        super(NewYearHangarSelectableLogic, self)._onMouseDown()
        if isCloseMainView:
            NewYearNavigation.closeMainView()
        return


class NyCityView(HistorySubModelPresenter):
    __slots__ = ('__presentersMap', '__currentTab', '__selectableLogic', '__currentObject', '__blur', '__objectConfig', '__hoveredObject', '__slotGroup', '__selectedSlotId', '__decorationPopover', '__levelUpCustomizationZones')
    _itemsCache = dependency.descriptor(IItemsCache)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __uiLoader = dependency.instance(IGuiLoader)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __nyEnvSwitcherController = dependency.descriptor(INewYearEnvironmentSwitchController)
    __nyCurrencyController = dependency.descriptor(INewYearCurrencyController)
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, cityModel, parentView):
        self.__selectableLogic = NewYearHangarSelectableLogic()
        self.__objectConfig = getNewYearObjectsConfig()
        self.__currentObject = None
        self.__slotGroup = None
        self.__blur = None
        self.__hoveredObject = HoverObject(None)
        self.__levelUpCustomizationZones = []
        self.__selectedSlotId = _DEFAULT_SELECTED_TOY_SLOT_ID
        self.__decorationPopover = NyDecorationsPopover(cityModel, parentView, _DEFAULT_SELECTED_TOY_SLOT_ID)
        super(NyCityView, self).__init__(cityModel, parentView)
        self.__presentersMap = {NyCityViewModel.OBJECTS_OVERVIEW: NyObjectsOverview(self.viewModel.objectsOverview, self),
         NyCityViewModel.OBJECT_VIEW: NyObjectView(self.viewModel.objectView, self)}
        self.__currentTab = None
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentTabInfo(self):
        return self.__presentersMap[self.__currentTab] if self.__currentTab is not None else None

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        if contentID == R.views.new_year.lobby.new_year.tooltips.CommonTooltip():
            return NyCommonTooltip(*getCommonTooltipArgsFromEvent(event))
        if contentID == R.views.new_year.lobby.new_year.tooltips.NyDecorationTooltip():
            return NyDecorationTooltip(event.getArgument('toyID'))
        if contentID == R.views.new_year.lobby.new_year.tooltips.CustomizationZoneTooltip():
            return CustomizationZoneTooltip(event.getArgument('customizationZone'))
        return LevelUpWidgetTooltip(event.getArgument('customizationZone')) if contentID == R.views.new_year.lobby.new_year.tooltips.LevelUpWidgetTooltip() else super(NyCityView, self).createToolTipContent(event, contentID)

    def createPopOver(self, event):
        if event.contentID == R.views.new_year.lobby.new_year.popovers.EnvSwitcherPopover():
            self.__nyEnvSwitcherController.notifyTipShouldClose()
            content = EnvSwitcherPopover(isInHangar=False)
            window = PopOverWindow(event, content, self.getParentWindow(), WindowLayer.TOP_WINDOW)
            window.load()
            return window
        return super(NyCityView, self).createPopOver(event)

    def setCameraState(self, cameraState):
        if self.__currentTab is not None:
            self.currentTabInfo.setCameraState(cameraState)
        return

    def setCameraSubState(self, subState, cameraState):
        if self.__currentTab is not None:
            self.currentTabInfo.setCameraSubState(subState, cameraState)
        return

    def initialize(self, *args, **kwargs):
        super(NyCityView, self).initialize(*args, **kwargs)
        self.__selectableLogic.init()
        self.__currentObject = NewYearNavigation.getCurrentObject()
        self.__updateTab()
        self.__updateMarkerInfo()
        self.__blur = CachedBlur(blurRadius=0.5)
        g_eventBus.addListener(NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(NewYearEvent.ON_TOY_INSTALLED, self.__onToyInstalled, scope=EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model, slotGroup=self.__slotGroup)
            model.atmosphereAnimation.setIsReady(False)
            model.lootBox.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
            model.setIsGuiLootBoxesVisible(self.__guiLootBoxes.isEnabled())
        self.__updateLootboxEntryPoint(self.__guiLootBoxes.getBoxesCount())
        self.__updateEnvironmentSwitcher()
        self.__decorationPopover.initialize(args, kwargs)

    def finalize(self):
        self.__levelUpAllSelectedCustomizationZones()
        self.viewModel.setCurrentSubModel(NyCityViewModel.OBJECTS_OVERVIEW)
        g_eventBus.removeListener(NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(NewYearEvent.ON_TOY_INSTALLED, self.__onToyInstalled, scope=EVENT_BUS_SCOPE.LOBBY)
        for slot in self._nyController.getSlotDescrs():
            self.__setSlotHighlight(slot.id, False)

        for tab in self.__presentersMap.itervalues():
            tab.finalize()

        self.__currentTab = None
        self.__slotGroup = None
        self.__currentObject = None
        self.__blur.fini()
        self.__selectableLogic.fini()
        self.__decorationPopover.finalize()
        self.__finalizeSoundEvents()
        if self.__hoveredObject.isHovered:
            self.__getMarkerModel(self.__hoveredObject.objectName).setIsZoneHovered(False)
        destroyGUIHoveredObject(self.__hoveredObject)
        super(NyCityView, self).finalize()
        return

    def clear(self):
        for presenter in self.__presentersMap.itervalues():
            presenter.clear()

        super(NyCityView, self).clear()

    def _getInfoForHistory(self):
        return {}

    def _getEvents(self):
        return ((self.viewModel.onHoverSlot, self.__onHoverSlot),
         (self.viewModel.onClickSlot, self.__onClickSlot),
         (self.viewModel.onHoverOutSlot, self.__onHoverOutSlot),
         (self.viewModel.onHoverMarker, self.__onHoverMarker),
         (self.viewModel.onHoverOutMarker, self.__onHoverOutMarker),
         (self.viewModel.atmosphereAnimation.onAnimationEnd, self.__onAnimationEnd),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdate),
         (self.__guiLootBoxes.onBoxesCountChange, self.__updateLootboxEntryPoint),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__guiLootBoxes.onStatusChange, self.__onLootBoxesStatusChange),
         (self.viewModel.lootBox.onLootBoxEntryPointClick, self.__onLootBoxEntryPointClick),
         (self.viewModel.onLevelUp, self.__onLevelUp),
         (self.viewModel.onLevelUpAnimationEnd, self.__onLevelUpAnimationEnd),
         (self._nyController.onCustomizationObjectUpdated, self.__onObjectUpdate),
         (self._nyController.onSpaceObjectHover, self.__onSpaceObjectHover),
         (self._nyController.onGUIObjectHover, self.__onGUIObjectHover),
         (self.__nyCurrencyController.onCurrencyUpdated, self.__onObjectUpdate),
         (self.viewModel.environmentSwitcher.onSwitch, self.__onSwitchPressed),
         (self.__nyEnvSwitcherController.onEnvironmentSwitched, self.__updateEnvironmentSwitcher),
         (self.viewModel.objectsOverview.panel.onClick, self.__onClick))

    def __showBlur(self):
        self.__blur.enable()

    def __onToyInstalled(self, event):
        ctx = event.ctx
        slotDescr = self._nyController.getSlotDescrs()[ctx['slotID']]
        slotsData = self._itemsCache.items.festivity.getSlots()
        if slotsData[ctx['slotID']] != ctx['toyID']:
            return
        with self.viewModel.atmosphereAnimation.transaction() as tx:
            tx.setIsReady(True)
            tx.setPoints(ctx['atmosphereBonus'])
            tx.setSlotId(slotDescr.id)

    def __onAnimationEnd(self):
        self.viewModel.atmosphereAnimation.setIsReady(False)

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.CITY:
            return
        tabName = ctx.tabName
        self.__updateTab()
        NewYearNavigation.switchTo(tabName)

    @args2params(str)
    def __onClick(self, customizationZone):
        NewYearNavigation.switchTo(customizationZone)

    def __onDataUpdated(self, keys):
        checkKeys = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS, SyncDataKeys.TOY_FRAGMENTS}
        with self.viewModel.transaction() as model:
            if set(keys) & checkKeys:
                self.__updateSlots(fullUpdate=False, model=model, slotGroup=self.__slotGroup)

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onClickSlot(self, args):
        name = args['name']
        if name in TOY_TO_CAMERA:
            self.setInternalViewState(TOY_TO_CAMERA[name])
        selectedSlot = int(args['slotId'])
        if selectedSlot == self.__selectedSlotId:
            if self.__selectedSlotId == _DEFAULT_SELECTED_TOY_SLOT_ID:
                return
            selectedSlot = _DEFAULT_SELECTED_TOY_SLOT_ID
        if self.__selectedSlotId == _DEFAULT_SELECTED_TOY_SLOT_ID:
            self.__levelUpAllSelectedCustomizationZones()
        self.__selectedSlotId = selectedSlot
        self.__decorationPopover.setSelectedSlotID(selectedSlot)
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=False, model=model, slotGroup=self.__slotGroup)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __onObjectUpdate(self, *args, **kwargs):
        self.__updateMarkerInfo()

    def __setSlotHighlight(self, slotId, isEnabled):
        if self.__hangarSpace.spaceInited:
            customizationManager = CGF.getManager(self.__hangarSpace.spaceID, LobbyCustomizableObjectsManager)
            if customizationManager:
                customizationManager.updateSlotHighlight(slotId, isEnabled)

    def __finalizeSoundEvents(self):
        if self.__currentObject in CustomizationObjects.ALL:
            NewYearSoundsManager.playGladeEvent(self.__currentObject, '_EXIT')
        if self.__currentObject == NewYearObjects.CITY_VIEW:
            NewYearSoundsManager.playEvent(NewYearSoundEvents.CITY_EXIT)

    def __onUpdate(self, *_, **__):
        if self._getNavigationAlias() != NewYearNavigation.getCurrentViewName():
            return
        newObject = NewYearNavigation.getCurrentObject()
        if self.__currentObject == newObject:
            return
        self.__levelUpAllSelectedCustomizationZones()
        self.__currentObject = newObject
        self.__updateTab()
        self.__slotGroup = TOY_TYPES_BY_OBJECT.get(self.__currentObject, {})
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model, slotGroup=self.__slotGroup)
        g_eventBus.handleEvent(NewYearEvent(NewYearEvent.SELECT_SIDEBAR_TAB_OUTSIDE, ctx={'menuName': NyWidgetTopMenu.CITY,
         'tabName': newObject}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateLootboxEntryPoint(self, count, *_):
        lastViewed = self.__guiLootBoxes.getSetting(LOOT_BOXES_VIEWED_COUNT)
        with self.viewModel.lootBox.transaction() as model:
            model.setBoxesCount(count)
            model.setHasNew(count > lastViewed)

    def __onAvailabilityChange(self, *_):
        self.viewModel.lootBox.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())

    def __onLootBoxesStatusChange(self):
        self.viewModel.setIsGuiLootBoxesVisible(self.__guiLootBoxes.isEnabled())

    @staticmethod
    def __onClickVideo():
        showInfoVideo()

    def __updateTab(self, **kwargs):
        tabName = NyCityViewModel.OBJECTS_OVERVIEW
        if self.__currentObject != NewYearObjects.CITY_VIEW:
            tabName = NyCityViewModel.OBJECT_VIEW
        if self.__currentTab == tabName:
            self.__presentersMap[self.__currentTab].update()
            return
        curTabInfo = self.currentTabInfo
        newTabInfo = self.__presentersMap[tabName]
        if curTabInfo and curTabInfo.isLoaded:
            curTabInfo.switchFinalize()
        self.__currentTab = tabName
        self.viewModel.setCurrentSubModel(tabName)
        if not newTabInfo.isLoaded:
            newTabInfo.initialize(**kwargs)

    def __onLootBoxEntryPointClick(self, *_):
        showStorageView(returnPlace=MAP_RETURN_PLACE.get(self.__currentObject, ReturnPlace.TO_NY_CUSTOMIZATION))

    def __updateMarkerInfo(self):
        self.__updateAtmosphere()
        with self.viewModel.transaction() as tx:
            for customizationZone in CustomizationObjects.ALL:
                currentLevel = getCurrentObjectLevel(customizationZone)
                modelMarker = self.__getMarkerModel(customizationZone, model=tx)
                modelMarker.customizationZone.setValue(CustomizationZone(customizationZone))
                modelMarker.setCurrentLevel(currentLevel)
                modelMarker.setCurrencyCount(self.__nyCurrencyController.getMandarinTokenCount)
                modelMarker.setLevelUpCurrencyNeed(self.__objectConfig.getNextLevelPrice(customizationZone, currentLevel))

    def __onLevelUp(self, args):
        customizationZone = str(args.get('customizationZone'))
        if customizationZone:
            self.__levelUpCustomizationZones.append(customizationZone)

    @adisp_process
    def __levelUpCustomizationZone(self, customizationZone):
        result = yield UpgradeCustomizationObjectLevel(customizationZone).request()
        SystemMessages.pushMessage(priority=result.msgPriority, text=result.userMsg, type=result.sysMsgType, messageData=result.msgData)

    def __levelUpAllSelectedCustomizationZones(self):
        for customizationZone in self.__levelUpCustomizationZones:
            self.__levelUpCustomizationZone(customizationZone)

        self.__levelUpCustomizationZones = []

    def __onLevelUpAnimationEnd(self, args):
        customizationZone = str(args.get('customizationZone'))
        if customizationZone:
            self.__levelUpCustomizationZone(customizationZone)
            self.__levelUpCustomizationZones.remove(customizationZone)

    @args2params(str)
    def __onHoverMarker(self, markerName):
        self._nyController.setGuiObjectHover(markerName, True)

    @args2params(str)
    def __onHoverOutMarker(self, markerName):
        self._nyController.setGuiObjectHover(markerName, False)

    def __onSpaceObjectHover(self, objectName, isHovered):
        objectName = ANCHOR_TO_OBJECT.get(objectName, '')
        if objectName in CustomizationObjects.ALL:
            self.__hoveredObject.setSpaceObjectHover(objectName, isHovered)
            self.__getMarkerModel(objectName).setIsZoneHovered(self.__hoveredObject.isHovered)

    def __onGUIObjectHover(self, objectName, isHovered):
        if objectName in CustomizationObjects.ALL:
            self.__hoveredObject.setGUIObjectHover(objectName, isHovered)

    @replaceNoneKwargsModel
    def __getMarkerModel(self, objectName, model=None):
        return getattr(model, objectName.lower() + 'Marker')

    def __onSwitchPressed(self, args):
        env = args.values()[0]
        self.__nyEnvSwitcherController.switchDayNightMode(env)
        self.__nyEnvSwitcherController.notifyTipShouldClose()

    def __updateEnvironmentSwitcher(self):
        with self.viewModel.environmentSwitcher.transaction() as tx:
            tx.setState(self.__nyEnvSwitcherController.userEnvState)
            tx.setMode(self.__nyEnvSwitcherController.currentDayNightMode)
            tx.setArrowDegree(self.__nyEnvSwitcherController.getTimeAngle())

    def __updateAtmosphere(self):
        lvl = self._itemsCache.items.festivity.getMaxLevel()
        isFirst = self._nyController.isFirstEntrance()
        with self.viewModel.transaction() as tx:
            tx.setCityLvl(lvl)
            tx.setIsFirstEntrance(isFirst)

    @staticmethod
    def __checkAndUpdateActualGroupSlotsLength(groupSlots, actualLength):
        currentLength = groupSlots.getItemsLength()
        if currentLength == actualLength:
            return False
        if actualLength > currentLength:
            for _ in range(actualLength - currentLength):
                groupSlots.addViewModel(GroupSlotsModel())

        else:
            for _ in range(currentLength - actualLength):
                groupSlots.removeItemByIndex(groupSlots.getItemsLength() - 1)

        return True

    def __updateSlots(self, fullUpdate, model, slotGroup):
        selectedSlotId = self.__selectedSlotId
        slotGroup = slotGroup or {}
        slotsData = self._itemsCache.items.festivity.getSlots()
        toys = self._itemsCache.items.festivity.getToys()
        nyStorage = self.__settingsCore.serverSettings.getNewYearStorage()
        needHint = not nyStorage.get(NewYearStorageKeys.HAS_TOYS_HINT_SHOWN, False) and bool(toys)
        actualLength = len(slotGroup)
        fullUpdate = self.__checkAndUpdateActualGroupSlotsLength(model.groupSlots, actualLength) or fullUpdate
        slots = self._nyController.getSlotDescrs()
        for groupIdx, groupName in enumerate(slotGroup):
            descrSlots = [ slot for slot in slots if slot.type == groupName ]
            groupModel = model.groupSlots.getItem(groupIdx)
            if fullUpdate:
                groupModel.slots.clear()
            for slotIdx, slotDescr in enumerate(descrSlots):
                toyID = slotsData[slotDescr.id]
                if toyID == INVALID_TOY_ID:
                    icon = R.invalid()
                    isEmpty = True
                    rank = 0
                else:
                    toy = toys.get(toyID)
                    icon = toy.getIcon()
                    rank = toy.getRank()
                    isEmpty = False
                slot = SlotModel() if fullUpdate else groupModel.slots.getItem(slotIdx)
                slotId = slotDescr.id
                slot.setType(slotDescr.type)
                slot.setSlotId(slotId)
                slot.setIsSelected(selectedSlotId == slotId)
                slot.setToyId(toyID)
                slot.setIcon(icon)
                slot.setRank(rank + 1)
                slot.setIsBetterAvailable(self._nyController.checkForNewToys(slot=slotDescr.id))
                slot.setIsEmpty(isEmpty)
                if needHint and findFirst(lambda t, sd=slotDescr: t.getToyType() == sd.type, toys.itervalues()):
                    needHint = False
                    groupModel.setHasToysHint(True)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.groupSlots.invalidate()
