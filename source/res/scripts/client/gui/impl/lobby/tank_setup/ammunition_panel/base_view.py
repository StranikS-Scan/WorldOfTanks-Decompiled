# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/base_view.py
import logging
from CurrentVehicle import g_currentVehicle
from Event import Event
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_context_menu import BackportContextMenuContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_panel_view_model import AmmunitionPanelViewModel
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.backports.context_menu import getHangarContextMenuData
from gui.impl.lobby.tank_setup.backports.tooltips import getSlotTooltipData
from gui.impl.lobby.tank_setup.tank_setup_helper import setLastSlotAction, clearLastSlotAction
from gui.impl.lobby.tank_setup.tooltips.shells_info import ShellsInfo
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BaseAmmunitionPanelView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _gameEventController = dependency.descriptor(IGameEventController)
    __slots__ = ('_ammunitionPanel', 'onSizeChanged', 'onPanelSectionSelected', 'onPanelSectionResized', 'onSlotsWidthChanged')

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.tanksetup.AmmunitionPanel())
        settings.flags = flags
        settings.model = AmmunitionPanelViewModel()
        super(BaseAmmunitionPanelView, self).__init__(settings)
        self.onSizeChanged = Event()
        self.onPanelSectionSelected = Event()
        self.onPanelSectionResized = Event()
        self.onSlotsWidthChanged = Event()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = getSlotTooltipData(event, g_currentVehicle.item, self.viewModel.ammunitionPanel.getSelectedSlot())
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(BaseAmmunitionPanelView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return ShellsInfo(event.contentID, g_currentVehicle.item) if event.contentID == R.views.lobby.tanksetup.tooltips.ShellsInfo() else super(BaseAmmunitionPanelView, self).createToolTipContent(event, contentID)

    def createContextMenuContent(self, event):
        if event.contentID != R.views.common.BackportContextMenu():
            super(BaseAmmunitionPanelView, self).createContextMenuContent(event)
        contextMenuData = getHangarContextMenuData(event, self.uniqueID)
        return BackportContextMenuContent(contextMenuData) if contextMenuData is not None else super(BaseAmmunitionPanelView, self).createContextMenuContent(event)

    def setHangarSwitchAnimState(self, isComplete):
        self.viewModel.setIsReady(isComplete)

    @property
    def viewModel(self):
        return super(BaseAmmunitionPanelView, self).getViewModel()

    def setLastSlotAction(self, *args, **kwargs):
        setLastSlotAction(self.viewModel, g_currentVehicle.item, *args, **kwargs)

    def updateVisible(self):
        if self._gameEventController.isEventPrbActive():
            self.viewModel.setIsVisible(False)
        else:
            self.viewModel.setIsVisible(True)

    def update(self, fullUpdate=True):
        if fullUpdate:
            clearLastSlotAction(self.viewModel)
        self.viewModel.setIsMaintenanceEnabled(not g_currentVehicle.isLocked())
        self.viewModel.setIsDisabled(self._getIsDisabled())
        self._ammunitionPanel.update(g_currentVehicle.item, fullUpdate=fullUpdate)

    def destroy(self):
        self.onSizeChanged.clear()
        self.onPanelSectionSelected.clear()
        self.onPanelSectionResized.clear()
        self.onSlotsWidthChanged.clear()
        super(BaseAmmunitionPanelView, self).destroy()

    def _onLoading(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self._ammunitionPanel = self._createAmmunitionPanel()
        self._ammunitionPanel.onLoading()
        self.updateVisible()

    def _onLoaded(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        self.viewModel.setIsReady(True)

    def _initialize(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._initialize()
        self._addListeners()
        self._ammunitionPanel.initialize()
        self.update(fullUpdate=False)

    def _finalize(self):
        self._removeListeners()
        self._ammunitionPanel.finalize()
        super(BaseAmmunitionPanelView, self)._finalize()

    def _createAmmunitionPanel(self):
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, g_currentVehicle.item)

    def _addListeners(self):
        self.viewModel.onViewSizeInitialized += self.__onViewSizeInitialized
        self.viewModel.onSlotsWidthChanged += self.__onSlotWidthChanged
        self.viewModel.ammunitionPanel.onSectionSelect += self._onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSectionResized += self._onPanelSectionResized
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self._currentVehicleChanged
        self._itemsCache.onSyncCompleted += self.__itemCacheChanged

    def _removeListeners(self):
        self.viewModel.onViewSizeInitialized -= self.__onViewSizeInitialized
        self.viewModel.onSlotsWidthChanged -= self.__onSlotWidthChanged
        self.viewModel.ammunitionPanel.onSectionSelect -= self._onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSectionResized -= self._onPanelSectionResized
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self._currentVehicleChanged
        self._itemsCache.onSyncCompleted -= self.__itemCacheChanged

    def _onPanelSectionSelected(self, args):
        if not self._getIsDisabled():
            clearLastSlotAction(self.viewModel)
            self.onPanelSectionSelected(**args)

    def _onPanelSectionResized(self, kwargs):
        self.onPanelSectionResized(**kwargs)

    def _currentVehicleChanged(self):
        self.update()
        self.viewModel.setIsReady(self._getIsReady())

    def __onVehicleChangeStarted(self):
        self.viewModel.setIsReady(False)
        self.viewModel.setIsMaintenanceEnabled(False)
        self.viewModel.setIsDisabled(True)

    def __itemCacheChanged(self, *_):
        self.update(fullUpdate=False)

    @staticmethod
    def _getIsDisabled():
        return not g_currentVehicle.isInHangar() or g_currentVehicle.isLocked() or g_currentVehicle.isBroken()

    def _getIsReady(self):
        return self.viewStatus == ViewStatus.LOADED

    def __onViewSizeInitialized(self, args=None):
        self.onSizeChanged(args.get('width', 0), args.get('height', 0), args.get('offsetY', 0))

    def __onSlotWidthChanged(self, args=None):
        self.onSlotsWidthChanged(args.get('width', 0))
