# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/ammunition_panel.py
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.ammunition_panel.base import BaseAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_blocks_controller import AmmunitionBlocksController
from gui.impl.lobby.tank_setup.ammunition_panel.base_view import BaseAmmunitionPanelView
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import AmmunitionSetupViewEvent
_BOOTCAMP_SECTIONS = (TankSetupConstants.OPT_DEVICES, TankSetupConstants.CONSUMABLES)

class _BootcampAmmunitionBlocksController(AmmunitionBlocksController):

    def _getTabs(self):
        return [] if self._vehicle is None else _BOOTCAMP_SECTIONS


class BootcampAmmunitionPanel(BaseAmmunitionPanel):

    def _createAmmunitionBlockController(self, vehicle):
        return _BootcampAmmunitionBlocksController(vehicle)


class BootcampAmmunitionPanelView(BaseAmmunitionPanelView):

    def _onLoading(self, *args, **kwargs):
        self.__hideHints()
        super(BootcampAmmunitionPanelView, self)._onLoading(*args, **kwargs)
        self.viewModel.hints.addHintModel(TutorialHintConsts.BOOTCAMP_PANEL_OPT_DEVICE_MC)
        self.viewModel.hints.addHintModel(TutorialHintConsts.BOOTCAMP_PANEL_EQUIPMENT_MC)
        self.viewModel.setIsBootcamp(True)

    def _finalize(self):
        super(BootcampAmmunitionPanelView, self)._finalize()
        self.__hideHints()

    def _createAmmunitionPanel(self):
        return BootcampAmmunitionPanel(self.viewModel.ammunitionPanel, g_currentVehicle.item)

    @staticmethod
    def __hideHints():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.BOOTCAMP_PANEL_OPT_DEVICE_MC}), EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.BOOTCAMP_PANEL_EQUIPMENT_MC}), EVENT_BUS_SCOPE.LOBBY)
