# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/hangar.py
from account_helpers.settings_core.settings_constants import OnceOnlyHints
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder, FrontlineTankSetupBuilder
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore

class HangarAmmunitionSetupView(BaseHangarAmmunitionSetupView):
    _settingsCore = dependency.descriptor(ISettingsCore)

    def _onLoading(self, **kwargs):
        with self.viewModel.transaction():
            super(HangarAmmunitionSetupView, self)._onLoading(**kwargs)
            if not self._settingsCore.serverSettings.getOnceOnlyHintsSetting(OnceOnlyHints.OPT_DEV_DRAG_AND_DROP_HINT, default=False):
                self.viewModel.hints.addHintModel(TutorialHintConsts.OPT_DEV_DRAG_AND_DROP_MC)

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem())

    def __getTankSetupBuilder(self):
        return FrontlineTankSetupBuilder if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else HangarTankSetupBuilder
