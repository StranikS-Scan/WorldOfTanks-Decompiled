# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_main_view.py
import BigWorld
import GUI
import Math
from AvatarInputHandler.cameras import mathUtils
from frameworks.wulf import ViewFlags
from gui import g_guiResetters
from gui.impl.gen import R
from gui.impl.gen.view_models.new_year.components.new_year_side_bar_button_model import NewYearSideBarButtonModel
from gui.impl.gen.view_models.new_year.components.ny_widget_model import NyWidgetModel
from gui.impl.gen.view_models.new_year.views.new_year_main_view_model import NewYearMainViewModel
from gui.impl.gui_decorators import trackLifeCycle
from gui.impl.lobby.loot_box.loot_box_entry_point import LootboxesEntrancePointWidget
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates, NewYearSoundVars
from gui.impl.new_year.tooltips.atmosphere_content import AtmosphereContent
from gui.impl.new_year.tooltips.new_year_parts_tooltip_content import NewYearPartsTooltipContent
from gui.impl.new_year.views.ny_anchor_view import NyAnchorView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from new_year.ny_constants import CustomizationObjects, OBJECT_TO_ANCHOR, SyncDataKeys
from new_year.ny_level_helper import NewYearAtmospherePresenter
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
_SIDEBAR_OBJECTS_ORDER = (CustomizationObjects.FIR,
 CustomizationObjects.FIELD_KITCHEN,
 CustomizationObjects.PARKING,
 CustomizationObjects.ILLUMINATION)
_SOUNDS_MAP = {NewYearSoundConfigKeys.ENTRANCE_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE,
                                         CustomizationObjects.FIELD_KITCHEN: NewYearSoundEvents.KITCHEN,
                                         CustomizationObjects.PARKING: NewYearSoundEvents.SNOWTANK,
                                         CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE},
 NewYearSoundConfigKeys.EXIT_EVENT: {CustomizationObjects.FIR: NewYearSoundEvents.TREE_EXIT,
                                     CustomizationObjects.FIELD_KITCHEN: NewYearSoundEvents.KITCHEN_EXIT,
                                     CustomizationObjects.PARKING: NewYearSoundEvents.SNOWTANK_EXIT,
                                     CustomizationObjects.ILLUMINATION: NewYearSoundEvents.LIGHTE_EXIT},
 NewYearSoundConfigKeys.STATE_VALUE: {CustomizationObjects.FIR: NewYearSoundStates.TREE,
                                      CustomizationObjects.FIELD_KITCHEN: NewYearSoundStates.KITCHEN,
                                      CustomizationObjects.PARKING: NewYearSoundStates.SNOWTANK,
                                      CustomizationObjects.ILLUMINATION: NewYearSoundStates.LIGHTE}}
_ANCHORS_COUNT = 9

@trackLifeCycle('new_year.main_view')
class NewYearMainView(NewYearNavigation):
    __slots__ = ('__selectedObject', '__slotsCalc', '__anchors', '__slotsPositionController', '__changeResCallbackID', '__level')
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjectsMgr = dependency.descriptor(ICustomizableObjectsManager)

    def __init__(self, *args, **kwargs):
        super(NewYearMainView, self).__init__(R.views.newYearMainView, ViewFlags.LOBBY_SUB_VIEW, NewYearMainViewModel, *args, **kwargs)
        self.__anchors = None
        self.__slotsPositionController = GUI.WGNewYearSlotsController()
        self.__changeResCallbackID = None
        self.__level = NewYearAtmospherePresenter.getLevel()
        return

    @property
    def viewModel(self):
        return super(NewYearMainView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.newYearAtmosphereTooltipContent:
            return AtmosphereContent()
        return NewYearPartsTooltipContent() if contentID == R.views.newYearPartsTooltipContent else None

    def _initialize(self, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: self.__getEntranceSoundEvent,
         NewYearSoundConfigKeys.EXIT_EVENT: self.__getExitSoundEvent,
         NewYearSoundConfigKeys.STATE_VALUE: self.__getSoundStateValue}
        super(NewYearMainView, self)._initialize(soundConfig)
        self.viewModel.onCloseBtnClick += self.__onCloseBtnClick
        self.viewModel.onCraftBtnClick += self.__onCraftBtnClick
        self.viewModel.onAlbumBtnClick += self.__onAlbumBtnClick
        self.viewModel.onGetPartsBtnClick += self.__onGetPartsBtnClick
        self.viewModel.onSideBarBtnClick += self.__onSideBarBtnClick
        self.viewModel.onRewardsBtnClick += self.__onRewardsBtnClick
        g_guiResetters.add(self.__onChangeScreenResolution)
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_eventBus.addListener(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_LOADED, self.__hideUI, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_CLOSED, self.__showUI, scope=EVENT_BUS_SCOPE.LOBBY)
        BigWorld.callback(0.1, self.__registerDragging)
        self.viewModel.setLootBoxEntryPoint(LootboxesEntrancePointWidget())
        self.__readInterfaceScale()
        self.__initAnchors()
        self.__updateData(False)

    def _finalize(self):
        g_eventBus.removeListener(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_LOADED, self.__hideUI, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.NewYearEvent.ON_LEVEL_UP_WINDOW_CONTENT_CLOSED, self.__showUI, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__changeResCallbackID is not None:
            BigWorld.cancelCallback(self.__changeResCallbackID)
            self.__changeResCallbackID = None
        self.__slotsPositionController.clear()
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_OFF), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)
        if self.__anchors is not None:
            self.__anchors = None
        g_guiResetters.remove(self.__onChangeScreenResolution)
        self.viewModel.onCloseBtnClick -= self.__onCloseBtnClick
        self.viewModel.onCraftBtnClick -= self.__onCraftBtnClick
        self.viewModel.onAlbumBtnClick -= self.__onAlbumBtnClick
        self.viewModel.onGetPartsBtnClick -= self.__onGetPartsBtnClick
        self.viewModel.onSideBarBtnClick -= self.__onSideBarBtnClick
        self.viewModel.onRewardsBtnClick -= self.__onRewardsBtnClick
        self._nyController.onDataUpdated -= self.__onDataUpdated
        super(NewYearMainView, self)._finalize()
        return

    def __initAnchors(self):
        self.__anchors = []
        for _ in xrange(_ANCHORS_COUNT):
            self.__anchors.append(NyAnchorView())

        self.viewModel.setAnchor0(self.__anchors[0])
        self.viewModel.setAnchor1(self.__anchors[1])
        self.viewModel.setAnchor2(self.__anchors[2])
        self.viewModel.setAnchor3(self.__anchors[3])
        self.viewModel.setAnchor4(self.__anchors[4])
        self.viewModel.setAnchor5(self.__anchors[5])
        self.viewModel.setAnchor6(self.__anchors[6])
        self.viewModel.setAnchor7(self.__anchors[7])
        self.viewModel.setAnchor8(self.__anchors[8])

    def _afterObjectSwitch(self):
        self.__updateSideBar()
        self.__updateAnchors()
        self._newYearSounds.onEnterView()

    def __getCurrentObjectSlotsDescrs(self):
        return self._nyController.getSlotDescrs(self.getCurrentObject())

    def __deselectAnchors(self):
        slotDescrs = self.__getCurrentObjectSlotsDescrs()
        visibleCount = len(slotDescrs)
        for idx in xrange(visibleCount):
            anchor = self.__anchors[idx].viewModel
            anchor.setIsSelected(False)

    def __registerDragging(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.TURN_LOBBY_DRAGGING_ON), scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LobbySimpleEvent.NOTIFY_CURSOR_DRAGGING, self.__onNotifyCursorDragging)

    def __onNotifyCursorDragging(self, event):
        isDragging = event.ctx.get('isDragging', False)
        self.viewModel.setIsDragging(isDragging)

    def __onCloseBtnClick(self, *_):
        self.switchByObjectName(None)
        return

    def __onCraftBtnClick(self, *_):
        self._goToCraftView()

    def __onAlbumBtnClick(self, *_):
        self._goToAlbumView()

    def __onGetPartsBtnClick(self, *_):
        self._goToBreakView(blur3dScene=True)

    def __onSideBarBtnClick(self, args):
        objectName = args['objectName']
        if objectName != self.getCurrentObject():
            self._switchObject(objectName)
            self._newYearSounds.onExitView()
        self.__deselectAnchors()
        self.__slotsPositionController.clear()

    def __onRewardsBtnClick(self, _):
        self._goToRewardsView()

    def __onDataUpdated(self, keys):
        with self.viewModel.transaction() as tx:
            if SyncDataKeys.TOY_FRAGMENTS in keys:
                self.__updateShards(tx)
            if SyncDataKeys.SLOTS in keys:
                self.__updateAtmosphere(tx)
                self.__updateAnchors()
                self.__updateSideBar()
            if SyncDataKeys.INVENTORY_TOYS in keys:
                self.__updateSideBar()
                self.__updateAnchors()

    def __updateData(self, showAnim=True):
        with self.viewModel.transaction() as tx:
            self.__updateShards(tx)
            self.__updateAtmosphere(tx, showAnim)
            self.__updateSideBar()
            self.__updateAnchors()

    def __updateShards(self, tx):
        shardsNumber = self._itemsCache.items.festivity.getShardsCount()
        tx.setPartsCount(shardsNumber)

    def __updateAtmosphere(self, tx, showAnim=True):
        level = NewYearAtmospherePresenter.getLevel()
        if not showAnim:
            widgetAnim = NyWidgetModel.WIDGET_NO_ANIM
        elif self.__level < level:
            widgetAnim = NyWidgetModel.WIDGET_LVLUP_ANIM
            tx.widget.setPrevIconSrc(R.images.gui.maps.icons.new_year.widget.levels.c_80x80.dyn('level{}'.format(level - 1)))
        elif self.__level > level:
            widgetAnim = NyWidgetModel.WIDGET_LVLDOWN_ANIM
            tx.widget.setPrevIconSrc(R.images.gui.maps.icons.new_year.widget.levels.c_80x80.dyn('level{}'.format(level + 1)))
        else:
            widgetAnim = NyWidgetModel.WIDGET_NORMAL_ANIM
        self.__level = level
        tx.widget.setWidgetAnim(widgetAnim)
        tx.widget.setProgress(NewYearAtmospherePresenter.getFloatLevelProgress())
        tx.widget.setIconSrc(R.images.gui.maps.icons.new_year.widget.levels.c_80x80.dyn('level{}'.format(level)))
        self._newYearSounds.setRTPC(NewYearSoundVars.RTPC_LEVEL_ATMOSPHERE, self.__level)

    def __updateSideBar(self):
        sideBar = self.viewModel.sideBar.getItems()
        if not sideBar:
            for objectName in _SIDEBAR_OBJECTS_ORDER:
                btn = NewYearSideBarButtonModel()
                btn.setObjectName(objectName)
                btn.setTypeIcon(R.images.gui.maps.icons.new_year.main_view.side_bar.icons.dyn(objectName))
                btn.setLabel(R.strings.ny.mainView.sideBar.dyn(objectName + 'Btn').label)
                btn.setIsSelected(objectName == self.getCurrentObject())
                btn.setIsBetterAvailable(self._nyController.checkForNewToys(objectType=objectName))
                sideBar.addViewModel(btn)

        else:
            for btn in sideBar:
                btn.setIsBetterAvailable(self._nyController.checkForNewToys(objectType=btn.getObjectName()))
                btn.setIsSelected(btn.getObjectName() == self.getCurrentObject())

    def __updateAnchors(self):
        slotDescrs = self.__getCurrentObjectSlotsDescrs()
        visibleCount = len(slotDescrs)
        slotsData = self._itemsCache.items.festivity.getSlots()
        customizableObjectName = OBJECT_TO_ANCHOR[self.getCurrentObject()]
        worldAnchorsPositions = self.__getWorldAnchorsPositions(customizableObjectName)
        for idx in xrange(_ANCHORS_COUNT):
            anchorView = self.__anchors[idx]
            anchor = anchorView.viewModel
            visible = idx < visibleCount
            anchor.setIsVisible(visible)
            if visible:
                anchorIcon = R.images.gui.maps.icons.new_year.anchors.anchorPlus
                isMaxLevel = False
                isEmpty = True
                globalSlotID = slotDescrs[idx].id
                anchorView.setSlotID(globalSlotID)
                toyID = slotsData[globalSlotID]
                if toyID != -1:
                    toy = self._nyController.getToyDescr(toyID)
                    anchor.setTypeIcon(R.images.gui.maps.icons.new_year.decorationTypes.blue.dyn(toy.type))
                    anchorIcon = R.images.gui.maps.icons.new_year.anchors.dyn('level{}'.format(toy.rank))
                    isMaxLevel = int(toy.rank) >= 5
                    isEmpty = False
                anchor.setIcon(anchorIcon)
                anchor.setIsMaxLevel(isMaxLevel)
                anchor.setIsEmpty(isEmpty)
                anchor.setIsFir(visibleCount > 2)
                if worldAnchorsPositions is not None:
                    anchorWorldPos = worldAnchorsPositions[idx]
                    self.__slotsPositionController.addSlot(anchorView.uniqueID, anchorWorldPos)
                anchor.setIsBetterAvailable(self._nyController.checkForNewToys(slot=globalSlotID))

        return

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

    def __getWorldAnchorsPositions(self, custObjectName):
        entity = self._customizableObjectsMgr.getCustomizableEntity(custObjectName)
        if entity is None:
            return
        else:
            targetPos = entity.position
            slots = []
            for i in xrange(entity.slotCount):
                attrName = 'slot{}'.format(i)
                slot = getattr(entity, attrName, Math.Vector3())
                slots.append(Math.Vector3(slot))

            return self.__getWorldAnchorsPositionsByTargetPos(targetPos, slots)

    @staticmethod
    def __getWorldAnchorsPositionsByTargetPos(targetPos, slots):
        slotsWorldPositions = []
        for slot in slots:
            worldPos = targetPos + slot
            slotsWorldPositions.append(worldPos)

        return slotsWorldPositions

    @dependency.replace_none_kwargs(settingsCore=ISettingsCore)
    def __readInterfaceScale(self, settingsCore=None):
        interfaceScale = mathUtils.clamp(1.0, 2.0, round(settingsCore.interfaceScale.get()))
        self.__slotsPositionController.setInterfaceScale(interfaceScale)

    def __onChangeScreenResolution(self):
        self.__changeResCallbackID = BigWorld.callback(0.0, self.__afterChangeScreenResolution)

    def __afterChangeScreenResolution(self):
        self.__changeResCallbackID = None
        self.__readInterfaceScale()
        return
