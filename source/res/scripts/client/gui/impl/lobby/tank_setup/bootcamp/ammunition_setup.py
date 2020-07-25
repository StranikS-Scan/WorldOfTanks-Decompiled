# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/bootcamp/ammunition_setup.py
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.lobby.tank_setup.ammunition_setup.hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.bootcamp.ammunition_panel import BootcampAmmunitionPanel
from gui.impl.lobby.tank_setup.bootcamp.setup_builder import BootcampTankSetupBuilder
from gui.impl.lobby.tank_setup.main_tank_setup.base import MainTankSetupView
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import AmmunitionSetupViewEvent

class BootcampAmmunitionSetupView(BaseHangarAmmunitionSetupView):

    def _onLoading(self, **kwargs):
        super(BootcampAmmunitionSetupView, self)._onLoading(**kwargs)
        self.viewModel.hints.addHintModel(TutorialHintConsts.SETUP_VIEW_SLOTS_OPT_DEVICE_MC)
        self.viewModel.setIsBootcamp(True)

    def _finalize(self):
        super(BootcampAmmunitionSetupView, self)._finalize()
        self.__hideHints()

    def _createMainTankSetup(self):
        return MainTankSetupView(self.viewModel.tankSetup, BootcampTankSetupBuilder(self._vehItem))

    def _createAmmunitionPanel(self):
        return BootcampAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem())

    @staticmethod
    def __hideHints():
        g_eventBus.handleEvent(AmmunitionSetupViewEvent(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, ctx={'hintName': TutorialHintConsts.SETUP_VIEW_SLOTS_OPT_DEVICE_MC}), EVENT_BUS_SCOPE.LOBBY)
