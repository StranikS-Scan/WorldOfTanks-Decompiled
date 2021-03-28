# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async
from frameworks.wulf import ViewStatus
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import isIntroAmmunitionSetupShown, showIntroAmmunitionSetupWindow
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IUISpamController
_logger = logging.getLogger(__name__)

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)
    _uiSpamController = dependency.descriptor(IUISpamController)

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self).update(fullUpdate)
            if g_currentVehicle.isPresent():
                state, _ = g_currentVehicle.item.getState()
                self._ammunitionPanel.viewModel.setAmmoNotFull(state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL)

    def _onLoading(self, *args, **kwargs):
        super(HangarAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        serverSettings = self._settingsCore.serverSettings
        showAmmunitionHint = not serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.AMMUNITION_PANEL_HINT, default=False)
        if showAmmunitionHint and self._uiSpamController.shouldBeHidden(OnceOnlyHints.AMMUNITION_PANEL_HINT):
            serverSettings.setOnceOnlyHintsSettings({OnceOnlyHints.AMMUNITION_PANEL_HINT: True})
            serverSettings.saveInUIStorage({UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN: True})

    @async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        showIntro = selectedSection == TankSetupConstants.OPT_DEVICES and not isIntroAmmunitionSetupShown()
        if showIntro and self._uiSpamController.shouldBeHidden(OnceOnlyHints.AMMUNITION_PANEL_HINT):
            self._settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.OPTIONAL_DEVICE_SETUP_INTRO_SHOWN: True})
            showIntro = False
        if showIntro:
            yield showIntroAmmunitionSetupWindow()
        if self.viewStatus != ViewStatus.LOADED:
            return
        super(HangarAmmunitionPanelView, self)._onPanelSectionSelected(args)
