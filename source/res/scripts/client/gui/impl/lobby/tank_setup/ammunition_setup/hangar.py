# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/ammunition_setup/hangar.py
from typing import TYPE_CHECKING
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.impl.lobby.tank_setup.ammunition_panel.hangar import HangarAmmunitionPanel
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.impl.lobby.tank_setup.main_tank_setup.hangar import HangarMainTankSetupView
from gui.impl.lobby.tank_setup.optional_devices_assistant.hangar import OptionalDevicesAssistantView
from gui.impl.lobby.tank_setup.tank_setup_builder import HangarTankSetupBuilder, EpicBattleTankSetupBuilder
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.game_control import IWotPlusController
from CurrentVehicle import g_currentVehicle
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

class HangarAmmunitionSetupView(BaseHangarAmmunitionSetupView, IGlobalListener):
    __slots__ = ()
    _wotPlusController = dependency.descriptor(IWotPlusController)

    def _canDisplayForVehicle(self):
        vehicle = g_currentVehicle.item if g_currentVehicle.isPresent() else None
        return bool(vehicle) and not (vehicle.isEvent or vehicle.isOnlyForComp7Battles or vehicle.isSecret or vehicle.isOnlyForClanWarsBattles or vehicle.isOnlyForEpicBattles)

    def _createOptionalDevicesAssistantPanel(self):
        return OptionalDevicesAssistantView(self.viewModel.optionalDevicesAssistant, self._vehItem.getItem()) if self._lobbyContext.getServerSettings().isOptionalDevicesAssistantEnabled() and self._wotPlusController.isEnabled() and self.prbEntity and self.prbEntity.getQueueType() == QUEUE_TYPE.RANDOMS and self._canDisplayForVehicle() else None

    def _createMainTankSetup(self):
        return HangarMainTankSetupView(self.viewModel.tankSetup, self.__getTankSetupBuilder()(self._vehItem))

    def _createAmmunitionPanel(self):
        ctx = {'specializationClickable': True}
        return HangarAmmunitionPanel(self.viewModel.ammunitionPanel, self._vehItem.getItem(), ctx=ctx)

    def __getTankSetupBuilder(self):
        return EpicBattleTankSetupBuilder if self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) else HangarTankSetupBuilder
