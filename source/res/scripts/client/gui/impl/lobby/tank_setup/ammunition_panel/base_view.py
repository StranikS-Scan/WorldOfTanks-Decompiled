# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/base_view.py
import logging
from CurrentVehicle import g_currentVehicle
from gui.prb_control import prbDispatcherProperty
from Event import Event
from frameworks.wulf import ViewFlags, ViewSettings, ViewStatus
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_context_menu import BackportContextMenuWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.ammunition_panel_view_model import AmmunitionPanelViewModel
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.backports.context_menu import getHangarContextMenuData
from gui.impl.lobby.tank_setup.backports.tooltips import getSlotTooltipData, getSlotSpecTooltipData
from gui.impl.lobby.tank_setup.tank_setup_helper import setLastSlotAction, clearLastSlotAction
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionPanelViewEvent
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)

class BaseAmmunitionPanelView(ViewImpl):
    _itemsCache = dependency.descriptor(IItemsCache)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __slots__ = ('_ammunitionPanel', '_wasVehicleOnLoading', 'onPanelSectionResized', 'onVehicleChanged')

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.tanksetup.AmmunitionPanel())
        settings.flags = flags
        settings.model = AmmunitionPanelViewModel()
        super(BaseAmmunitionPanelView, self).__init__(settings)
        self._ammunitionPanel = None
        self._wasVehicleOnLoading = False
        self.onPanelSectionResized = Event()
        self.onVehicleChanged = Event()
        return

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            if self._hangarSpace.spaceLoading():
                _logger.warning('Failed to get slotData. HangarSpace is currently loading.')
                return
            tooltipId = event.getArgument('tooltip')
            if tooltipId == TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC:
                tooltipData = getSlotSpecTooltipData(event, tooltipId)
            else:
                tooltipData = getSlotTooltipData(event, self.vehItem, self.viewModel.ammunitionPanel.getSelectedSlot())
            if tooltipData is not None:
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
                window.load()
                return window
        return super(BaseAmmunitionPanelView, self).createToolTip(event)

    def createContextMenu(self, event):
        if event.contentID == R.views.common.BackportContextMenu():
            contextMenuData = getHangarContextMenuData(event, self.uniqueID)
            if contextMenuData is not None:
                window = BackportContextMenuWindow(contextMenuData, self.getParentWindow())
                window.load()
                return window
        return super(BaseAmmunitionPanelView, self).createContextMenu(event)

    def setHangarSwitchAnimState(self, isComplete):
        self.viewModel.setIsReady(isComplete)

    def setPrbSwitching(self, value):
        self.viewModel.setIsDisabled(value)

    @property
    def viewModel(self):
        return super(BaseAmmunitionPanelView, self).getViewModel()

    @property
    def vehItem(self):
        return g_currentVehicle.item

    def setLastSlotAction(self, *args, **kwargs):
        setLastSlotAction(self.viewModel, self.vehItem, *args, **kwargs)

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def update(self, fullUpdate=True):
        if fullUpdate:
            clearLastSlotAction(self.viewModel)
        self.viewModel.setIsMaintenanceEnabled(not g_currentVehicle.isLocked())
        if not self.__canChangeVehicle():
            self.viewModel.setIsDisabled(True)
        else:
            self.viewModel.setIsDisabled(self._getIsDisabled())
        self._ammunitionPanel.update(self.vehItem, fullUpdate=fullUpdate)

    def destroy(self):
        self.onPanelSectionResized.clear()
        super(BaseAmmunitionPanelView, self).destroy()

    def _onLoading(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self._wasVehicleOnLoading = self.vehItem is not None
        self._ammunitionPanel = self._createAmmunitionPanel()
        self._ammunitionPanel.onLoading()
        return

    def _onLoaded(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._onLoaded(*args, **kwargs)
        self.viewModel.setIsReady(True)

    def _initialize(self, *args, **kwargs):
        super(BaseAmmunitionPanelView, self)._initialize()
        self._addListeners()
        self._ammunitionPanel.initialize()
        self._updateView()

    def _finalize(self):
        self._removeListeners()
        self._ammunitionPanel.finalize()
        super(BaseAmmunitionPanelView, self)._finalize()

    def _createAmmunitionPanel(self):
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self.vehItem)

    def _addListeners(self):
        self.viewModel.ammunitionPanel.onSectionSelect += self._onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSectionResized += self._onPanelSectionResized
        g_currentVehicle.onChangeStarted += self.__onVehicleChangeStarted
        g_currentVehicle.onChanged += self._currentVehicleChanged
        self._itemsCache.onSyncCompleted += self.__itemCacheChanged

    def _removeListeners(self):
        self.viewModel.ammunitionPanel.onSectionSelect -= self._onPanelSectionSelected
        self.viewModel.ammunitionPanel.onSectionResized -= self._onPanelSectionResized
        g_currentVehicle.onChangeStarted -= self.__onVehicleChangeStarted
        g_currentVehicle.onChanged -= self._currentVehicleChanged
        self._itemsCache.onSyncCompleted -= self.__itemCacheChanged

    def _onPanelSectionSelected(self, args):
        if not self._getIsDisabled() and self.__canChangeVehicle():
            clearLastSlotAction(self.viewModel)
            g_eventBus.handleEvent(AmmunitionPanelViewEvent(AmmunitionPanelViewEvent.SECTION_SELECTED, args), EVENT_BUS_SCOPE.LOBBY)

    def _onPanelSectionResized(self, kwargs):
        self.onPanelSectionResized(**kwargs)

    def _currentVehicleChanged(self):
        self.update()
        self.viewModel.setIsReady(self._getIsReady())

    def __onVehicleChangeStarted(self):
        self.viewModel.setIsReady(False)
        self.viewModel.setIsMaintenanceEnabled(False)
        self.viewModel.setIsDisabled(True)
        self.onVehicleChanged()

    def __itemCacheChanged(self, *_):
        self.update(fullUpdate=False)

    @staticmethod
    def _getIsDisabled():
        return not g_currentVehicle.isInHangar() or g_currentVehicle.isLocked() or g_currentVehicle.isBroken()

    def _getIsReady(self):
        return self.viewStatus == ViewStatus.LOADED

    def __canChangeVehicle(self):
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                return permission.canChangeVehicle()
        return True

    def _updateView(self):
        self.update(fullUpdate=False)
