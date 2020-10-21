# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_panel/hangar_view.py
import logging
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from async import async
from frameworks.wulf import ViewStatus
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.impl.lobby.tank_setup.intro_ammunition_setup_view import isIntroAmmunitionSetupShown, showIntroAmmunitionSetupWindow
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
from gui.shared.gui_items.Vehicle import Vehicle
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
_logger = logging.getLogger(__name__)

class HangarAmmunitionPanelView(BaseAmmunitionPanelView):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def update(self, fullUpdate=True):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self).update(fullUpdate)
            if g_currentVehicle.isPresent():
                state, _ = g_currentVehicle.item.getState()
                self._ammunitionPanel.viewModel.setAmmoNotFull(state == Vehicle.VEHICLE_STATE.AMMO_NOT_FULL)

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction():
            super(HangarAmmunitionPanelView, self)._onLoading(*args, **kwargs)
            if not self._settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.AMMUNITION_PANEL_HINT, default=False):
                self.viewModel.hints.addHintModel(TutorialHintConsts.AMMUNITION_PANEL_HINT_MC)
            else:
                self.viewModel.hints.addHintModel(TutorialHintConsts.HANGAR_PANEL_OPT_DEVICE_MC)
            self.viewModel.hints.addHintModel(TutorialHintConsts.HANGAR_PANEL_SHELLS_MC)

    @async
    def _onPanelSectionSelected(self, args):
        selectedSection = args['selectedSection']
        currentVehicle = g_currentVehicle.item or g_currentPreviewVehicle.item
        if currentVehicle is not None and currentVehicle.isOnlyForEventBattles and selectedSection == TankSetupConstants.SHELLS:
            return
        else:
            if self.viewModel.hints.hasHintModel(TutorialHintConsts.AMMUNITION_PANEL_HINT_MC):
                self.__hideHintModel()
            if selectedSection == TankSetupConstants.OPT_DEVICES and not isIntroAmmunitionSetupShown():
                yield showIntroAmmunitionSetupWindow()
            if self.viewStatus != ViewStatus.LOADED:
                return
            super(HangarAmmunitionPanelView, self)._onPanelSectionSelected(args)
            return

    @staticmethod
    def __hideHintModel():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.AMMUNITION_PANEL_HINT_MC}), EVENT_BUS_SCOPE.LOBBY)
