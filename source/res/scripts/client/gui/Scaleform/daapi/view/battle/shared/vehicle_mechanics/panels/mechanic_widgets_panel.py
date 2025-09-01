# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels/mechanic_widgets_panel.py
import typing
from gui.Scaleform.daapi.view.meta.WidgetsPanelMeta import WidgetsPanelMeta
from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl
from gui.Scaleform.genConsts.BATTLE_WIDGETS_CONSTS import BATTLE_WIDGETS_CONSTS
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class MechanicWidgetsPanel(WidgetsPanelMeta):
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {VehicleMechanic.ROCKET_ACCELERATION: (BATTLE_WIDGETS_CONSTS.ROCKET_ACCELERATOR,),
     VehicleMechanic.RECHARGEABLE_NITRO: (BATTLE_WIDGETS_CONSTS.RECHARGEABLE_NITRO,),
     VehicleMechanic.CONCENTRATION_MODE: (BATTLE_WIDGETS_CONSTS.CONCENTRATION,),
     VehicleMechanic.CHARGEABLE_BURST: (BATTLE_WIDGETS_CONSTS.CHARGEABLE_BURST,),
     VehicleMechanic.POWER_MODE: (BATTLE_WIDGETS_CONSTS.POWER,),
     VehicleMechanic.SUPPORT_WEAPON: (BATTLE_WIDGETS_CONSTS.SUPPORT_WEAPON,),
     VehicleMechanic.PILLBOX_SIEGE_MODE: (BATTLE_WIDGETS_CONSTS.PILLBOX_SIEGE,),
     VehicleMechanic.CHARGE_SHOT: (BATTLE_WIDGETS_CONSTS.CHARGE_SHOT,),
     VehicleMechanic.TARGET_DESIGNATOR: (BATTLE_WIDGETS_CONSTS.TARGET_DESIGNATOR_WIDGET,),
     VehicleMechanic.STANCE_DANCE: (BATTLE_WIDGETS_CONSTS.STANCE_DANCE_FIGHT, BATTLE_WIDGETS_CONSTS.STANCE_DANCE_TURBO),
     VehicleMechanic.STATIONARY_RELOAD: (BATTLE_WIDGETS_CONSTS.STATIONARY_RELOAD,)}

    def _setIsReplay(self, isReplay):
        self.as_isReplayS(isReplay)

    def _setIsVisible(self, isVisible):
        self.as_setVisibleS(isVisible)

    def _setCrosshairScaledPosition(self, position):
        self.as_updateLayoutS(*position)

    def _setCrosshairViewID(self, viewID):
        self.as_updateCrosshairTypeS(viewID)

    def _addMechanicUIComponent(self, mechanicComponents):
        for componentName in mechanicComponents:
            self.as_addWidgetS(componentName)

    @hasVehiclePassengerCtrl()
    def _onVehicleControlling(self, vehicle, passengerCtrl=None):
        self.as_isPlayerS(passengerCtrl.isCurrentPlayerVehicle)
        super(MechanicWidgetsPanel, self)._onVehicleControlling(vehicle)
