# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/glade/ny_glade_view.py
import typing
import CGF
from account_helpers.AccountSettings import LOOT_BOXES_VIEWED_COUNT
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.group_slots_model import GroupSlotsModel
from gui.impl.gen.view_models.views.lobby.new_year.views.glade.slot_model import SlotModel
from gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.impl.lobby.new_year.popovers.ny_decorations_popover import NyDecorationsPopover
from gui.impl.lobby.new_year.popovers.ny_loot_box_popover import NyLootBoxPopoverView
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.new_year.navigation import NewYearTabCache, NewYearNavigation
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.impl.new_year.navigation import ViewAliases
from hangar_selectable_objects import HangarSelectableLogic
from helpers import dependency, getLanguageCode
from items.components.ny_constants import TOY_TYPES_BY_OBJECT, INVALID_TOY_ID
from new_year.cgf_components.lobby_customization_components import LobbyCustomizableObjectsManager
from new_year.ny_constants import SyncDataKeys, NyWidgetTopMenu
from realm import CURRENT_REALM
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
    from gui.impl.gen.view_models.views.lobby.new_year.views.glade.ny_glade_view_model import NyGladeViewModel
    from gui.impl.gen.view_models.views.lobby.new_year.views.glade.atmosphere_animation_model import AtmosphereAnimationModel

class NyGladeView(HistorySubModelPresenter):
    __slots__ = ('__selectableLogic', '__currentObject', '__blur')
    _itemsCache = dependency.descriptor(IItemsCache)
    __lobbyCtx = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __uiLoader = dependency.instance(IGuiLoader)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)

    def __init__(self, gladeModel, parentView):
        self.__selectableLogic = HangarSelectableLogic()
        self.__currentObject = None
        self.__blur = None
        super(NyGladeView, self).__init__(gladeModel, parentView)
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    @property
    def currentTab(self):
        return self.__currentObject

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.new_year_parts_tooltip_content.NewYearPartsTooltipContent():
            return NewYearPartsTooltipContent()
        return NyDecorationTooltip(event.getArgument('toyID')) if contentID == R.views.lobby.new_year.tooltips.NyDecorationTooltip() else super(NyGladeView, self).createToolTipContent(event, contentID)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.new_year.popovers.NyLootBoxPopover():
            from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.lootboxes_storage_view_model import ReturnPlace
            fromNyYear = ReturnPlace.TO_CUSTOM
            return NyLootBoxPopoverView(fromNyYear)
        slotId = int(event.getArgument('slotId'))
        return NyDecorationsPopover(slotId) if event.contentID == R.views.lobby.new_year.popovers.NyDecorationsPopover() else super(NyGladeView, self).createPopOverContent(event)

    def initialize(self, *args, **kwargs):
        super(NyGladeView, self).initialize(*args, **kwargs)
        self.__selectableLogic.init()
        self.__currentObject = NewYearNavigation.getCurrentObject()
        self.__blur = CachedBlur(blurRadius=0.5)
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.NewYearEvent.ON_TOY_INSTALLED, self.__onToyInstalled, scope=EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model)
            self.__updateIntro(force=kwargs.get('forceShowIntro', False), model=model)
            model.intro.region.setRealm(CURRENT_REALM)
            model.intro.region.setLanguage(getLanguageCode())
            model.atmosphereAnimation.setIsReady(False)
            model.lootBox.setIsLootBoxesEnabled(self.__guiLootBoxes.isLootBoxesAvailable())
            model.setIsGuiLootBoxesVisible(self.__guiLootBoxes.isEnabled())
        self.__updateLootboxEntryPoint(self.__guiLootBoxes.getBoxesCount())

    def finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.NewYearEvent.ON_TOY_INSTALLED, self.__onToyInstalled, scope=EVENT_BUS_SCOPE.LOBBY)
        for slot in self._nyController.getSlotDescrs():
            self.__setSlotHighlight(slot.id, False)

        self.__blur.fini()
        self.__selectableLogic.fini()
        self.__clearPopovers()
        super(NyGladeView, self).finalize()

    def _getInfoForHistory(self):
        return {}

    def _getEvents(self):
        return ((self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onHoverSlot, self.__onHoverSlot),
         (self.viewModel.onHoverOutSlot, self.__onHoverOutSlot),
         (self.viewModel.onMouseOver3dScene, self.__onMouseOver3dScene),
         (self.viewModel.intro.onClose, self.__onCloseIntro),
         (self.viewModel.intro.showBlur, self.__showBlur),
         (self.viewModel.intro.videoCover.onClick, self.__onClickVideo),
         (self.viewModel.atmosphereAnimation.onAnimationEnd, self.__onAnimationEnd),
         (self._nyController.onDataUpdated, self.__onDataUpdated),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdate),
         (self.__guiLootBoxes.onBoxesCountChange, self.__updateLootboxEntryPoint),
         (self.__guiLootBoxes.onAvailabilityChange, self.__onAvailabilityChange),
         (self.__guiLootBoxes.onStatusChange, self.__onLootBoxesStatusChange))

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
            tx.setPoints(ctx['atmoshereBonus'])
            tx.setSlotId(slotDescr.id)

    def __onAnimationEnd(self):
        self.viewModel.atmosphereAnimation.setIsReady(False)

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.GLADE:
            return
        tabName = ctx.tabName
        self.__currentObject = tabName
        NewYearNavigation.switchTo(tabName, True, withFade=True)
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model)
            self.__clearPopovers()

    def __onDataUpdated(self, keys):
        checkKeys = {SyncDataKeys.INVENTORY_TOYS, SyncDataKeys.SLOTS, SyncDataKeys.TOY_FRAGMENTS}
        with self.viewModel.transaction() as model:
            if set(keys) & checkKeys:
                self.__updateSlots(fullUpdate=False, model=model)

    def __updateSlots(self, fullUpdate, model):
        slotsData = self._itemsCache.items.festivity.getSlots()
        toys = self._itemsCache.items.festivity.getToys()
        nyStorage = self.__settingsCore.serverSettings.getNewYearStorage()
        needHint = not nyStorage.get(NewYearStorageKeys.HAS_TOYS_HINT_SHOWN, False) and bool(toys)
        groups = TOY_TYPES_BY_OBJECT.get(self.__currentObject, {})
        actualLength = len(groups)
        currentLength = model.groupSlots.getItemsLength()
        if currentLength != actualLength:
            fullUpdate = True
            if actualLength > currentLength:
                for _ in range(actualLength - currentLength):
                    model.groupSlots.addViewModel(GroupSlotsModel())

            else:
                for _ in range(currentLength - actualLength):
                    model.groupSlots.removeItemByIndex(model.groupSlots.getItemsLength() - 1)

        slots = self._nyController.getSlotDescrs()
        for groupIdx, groupName in enumerate(groups):
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
                slot.setType(slotDescr.type)
                slot.setSlotId(slotDescr.id)
                slot.setToyId(toyID)
                slot.setIcon(icon)
                slot.setRank(rank + 1)
                slot.setIsBetterAvailable(self._nyController.checkForNewToys(slot=slotDescr.id))
                slot.setIsEmpty(isEmpty)
                showHint = False
                if needHint and findFirst(lambda t, sd=slotDescr: t.getToyType() == sd.type, toys.itervalues()):
                    showHint = True
                    needHint = False
                slot.setHasToyHint(showHint)
                if fullUpdate:
                    groupModel.slots.addViewModel(slot)

        if fullUpdate:
            model.groupSlots.invalidate()

    def __updateIntro(self, model, force=False):
        showIntro = False
        settingKey = NewYearStorageKeys.GLADE_INTRO_VISITED
        if force:
            self.__settingsCore.serverSettings.saveInNewYearStorage({settingKey: False})
            showIntro = True
        elif not self.__settingsCore.serverSettings.getNewYearStorage().get(settingKey, False):
            showIntro = True
        self._tabCache.setIntroScreenState(NyWidgetTopMenu.GLADE, NewYearTabCache.OPENED_INTRO_STATE if showIntro else NewYearTabCache.VIEWED_INTRO_STATE)
        model.setIsIntroOpened(showIntro)

    def __onCloseIntro(self):
        self._tabCache.setIntroScreenState(NyWidgetTopMenu.GLADE, NewYearTabCache.VIEWED_INTRO_STATE)
        self.__settingsCore.serverSettings.saveInNewYearStorage({NewYearStorageKeys.GLADE_INTRO_VISITED: True})
        self.viewModel.setIsIntroOpened(False)
        self.__blur.disable()

    def __onHoverSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), True)

    def __onHoverOutSlot(self, args):
        self.__setSlotHighlight(int(args['slotId']), False)

    def __setSlotHighlight(self, slotId, isEnabled):
        if self.__hangarSpace.spaceInited:
            customizationManager = CGF.getManager(self.__hangarSpace.spaceID, LobbyCustomizableObjectsManager)
            if customizationManager:
                customizationManager.updateSlotHighlight(slotId, isEnabled)

    def __clearPopovers(self):
        for resId in (R.views.lobby.new_year.popovers.NyDecorationsPopover(),):
            popoverView = self.__uiLoader.windowsManager.getViewByLayoutID(resId)
            if popoverView is not None:
                popoverView.destroyWindow()

        return

    def __onUpdate(self, *_, **__):
        if self._getNavigationAlias() != NewYearNavigation.getCurrentViewName():
            return
        newObject = NewYearNavigation.getCurrentObject()
        if self.__currentObject == newObject:
            return
        self.__currentObject = newObject
        with self.viewModel.transaction() as model:
            self.__updateSlots(fullUpdate=True, model=model)
            self.__clearPopovers()
        g_eventBus.handleEvent(events.NewYearEvent(events.NewYearEvent.SELECT_SIDEBAR_TAB_OUTSIDE, ctx={'menuName': NyWidgetTopMenu.GLADE,
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

    @staticmethod
    def __onMoveSpace(args=None):
        if args is None:
            return
        else:
            dx = args.get('dx')
            dy = args.get('dy')
            dz = args.get('dz')
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_SPACE_MOVED, ctx={'dx': dx,
             'dy': dy,
             'dz': dz}), EVENT_BUS_SCOPE.GLOBAL)
            return

    @staticmethod
    def __onMouseOver3dScene(args):
        if NewYearNavigation.getCurrentViewName() == ViewAliases.GLADE_VIEW:
            g_eventBus.handleEvent(events.LobbySimpleEvent(events.LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': bool(args.get('isOver3dScene'))}))
