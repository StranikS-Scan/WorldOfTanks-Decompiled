# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/hangar.py
import BigWorld
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder, EpicBattleTankSetupBuilder, HalloweenTankSetupBuilder

class HangarAmmunitionSetupView(BaseHangarAmmunitionSetupView):

    def __init__(self, *args, **kwargs):
        super(HangarAmmunitionSetupView, self).__init__(*args, **kwargs)
        self._isEventHangar = False

    def _onLoading(self, *args, **kwargs):
        super(HangarAmmunitionSetupView, self)._onLoading(*args, **kwargs)
        self._isEventHangar = self._eventBattlesController.isEventHangar()
        if self._isEventHangar:
            self._eventBattlesController.onEventDisabled += self._onEventDisabled
            self._eventBattlesController.onCompleteActivePhase += self._onCompleteActivePhase

    def _finalize(self):
        if self._isEventHangar:
            self._eventBattlesController.onEventDisabled -= self._onEventDisabled
            self._eventBattlesController.onCompleteActivePhase -= self._onCompleteActivePhase
        super(HangarAmmunitionSetupView, self)._finalize()

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def _onCompleteActivePhase(self):
        progressCtrl = self._eventBattlesController.getHWProgressCtrl()
        if not progressCtrl or progressCtrl.isPostPhase():
            self.__closeWindow()

    def _onEventDisabled(self):
        self.__closeWindow()

    def __closeWindow(self):
        if self.viewModel.getIsReady():
            self._forceCloseWindow()

    def __getTankSetupBuilder(self):
        if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
            return EpicBattleTankSetupBuilder
        else:
            hwEqCtrl = BigWorld.player().components.get('HWAccountEquipmentController', None)
            return HalloweenTankSetupBuilder if self.prbDispatcher is not None and hwEqCtrl is not None and (self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EVENT) or self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EVENT_BATTLES_2)) else HangarTankSetupBuilder
