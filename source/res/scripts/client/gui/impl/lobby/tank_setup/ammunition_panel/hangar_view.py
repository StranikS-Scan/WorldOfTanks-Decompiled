# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from frameworks.wulf import ViewStatus
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import showIntro
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionPanelViewEvent
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from wg_async import wg_async
_logger = logging.getLogger(__name__)

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self).update(fullUpdate)
            self._updateViewModel()

    def _updateViewModel(self):
        if g_currentVehicle.isPresent():
            state, _ = g_currentVehicle.item.getState()
            self._ammunitionPanel.viewModel.setAmmoNotFull(state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL)

    def _addListeners(self):
        super(HangarAmmunitionPanelView, self)._addListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex += self._onChangeSetupIndex
        self.viewModel.onEscKeyDown += self.__onEscKeyDown

    def _removeListeners(self):
        super(HangarAmmunitionPanelView, self)._removeListeners()
        self.viewModel.ammunitionPanel.onChangeSetupIndex -= self._onChangeSetupIndex
        self.viewModel.onEscKeyDown -= self.__onEscKeyDown

    @wg_async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        if selectedSection == TankSetupConstants.SHELLS and self.vehItem and self.vehItem.gun.isDamageMutable():
            if not self._settingsCore.serverSettings.getUIStorage2().get(UI_STORAGE_KEYS.MUTABLE_DAMAGE_SHELL_MARK_IS_SHOWN):
                self._settingsCore.serverSettings.saveInUIStorage2({UI_STORAGE_KEYS.MUTABLE_DAMAGE_SHELL_MARK_IS_SHOWN: True})
        yield showIntro(selectedSection, self.getParentWindow())
        if self.viewStatus != ViewStatus.LOADED:
            return
        super(HangarAmmunitionPanelView, self)._onPanelSectionSelected(args)

    def _onChangeSetupIndex(self, args):
        groupID = int(args.get('groupId', None))
        newLayoutIdx = int(args.get('currentIndex', None))
        if groupID is None or newLayoutIdx is None:
            return
        else:
            self._ammunitionPanel.onChangeSetupLayoutIndex(groupID, newLayoutIdx)
            return

    def __onEscKeyDown(self):
        g_eventBus.handleEvent(AmmunitionPanelViewEvent(AmmunitionPanelViewEvent.CLOSE_VIEW), EVENT_BUS_SCOPE.LOBBY)

    def _updateView(self):
        isFullUpdate = not self._wasVehicleOnLoading and self.vehItem is not None
        self.update(fullUpdate=isFullUpdate)
        return
