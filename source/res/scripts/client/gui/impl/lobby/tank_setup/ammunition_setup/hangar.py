# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/hangar.py
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder, EpicBattleTankSetupBuilder
from helpers import dependency
from skeletons.new_year import INewYearController

class HangarAmmunitionSetupView(BaseHangarAmmunitionSetupView):
    _nyController = dependency.descriptor(INewYearController)

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def _addListeners(self):
        super(HangarAmmunitionSetupView, self)._addListeners()
        self._nyController.onStateChanged += self.__onStateChanged

    def _removeListeners(self):
        super(HangarAmmunitionSetupView, self)._removeListeners()
        self._nyController.onStateChanged -= self.__onStateChanged

    def __getTankSetupBuilder(self):
        return EpicBattleTankSetupBuilder if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else HangarTankSetupBuilder

    def __onStateChanged(self):
        self._ammunitionPanel.update(self._vehItem.getItem(), fullUpdate=True)
