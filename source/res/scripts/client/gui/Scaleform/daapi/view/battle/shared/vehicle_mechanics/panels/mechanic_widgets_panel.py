# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/panels/mechanic_widgets_panel.py
from __future__ import absolute_import
import typing
from gui.Scaleform.daapi.view.meta.WidgetsPanelMeta import WidgetsPanelMeta
from gui.Scaleform.genConsts.BATTLE_WIDGETS_CONSTS import BATTLE_WIDGETS_CONSTS
from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl, VehiclePassengerInfoWatcher
from items.vehicle_mechanics_types import VehicleMechanicKeys

class MechanicWidgetsPanel(WidgetsPanelMeta, VehiclePassengerInfoWatcher):
    _VEHICLE_MECHANIC_UI_COMPONENTS_MAP = {VehicleMechanicKeys.AUTORELOADER_SURGE: (BATTLE_WIDGETS_CONSTS.AUTORELOADER_SURGE,),
     VehicleMechanicKeys.AUXILIARY_ROCKET_LAUNCHER: (BATTLE_WIDGETS_CONSTS.AUXILIARY_ROCKET_LAUNCHER,),
     VehicleMechanicKeys.BUSTLE_FEED: (BATTLE_WIDGETS_CONSTS.BUSTLE_FEED,),
     VehicleMechanicKeys.CHARGE_SHOT: (BATTLE_WIDGETS_CONSTS.CHARGE_SHOT,),
     VehicleMechanicKeys.CHARGEABLE_BURST: (BATTLE_WIDGETS_CONSTS.CHARGEABLE_BURST,),
     VehicleMechanicKeys.CONCENTRATION_MODE: (BATTLE_WIDGETS_CONSTS.CONCENTRATION,),
     VehicleMechanicKeys.COMBAT_THROTTLE: (BATTLE_WIDGETS_CONSTS.SPEC_BOOST_MODE,),
     VehicleMechanicKeys.HEATING_ZONES_GUN: (BATTLE_WIDGETS_CONSTS.TEMPERATURE_GUN_HEAT_ZONES,),
     VehicleMechanicKeys.LOW_CHARGE_SHOT: (BATTLE_WIDGETS_CONSTS.LOW_CHARGE_SHOT,),
     VehicleMechanicKeys.OVERHEAT_GUN: (BATTLE_WIDGETS_CONSTS.TEMPERATURE_GUN_OVERHEAT,),
     VehicleMechanicKeys.PILLBOX_SIEGE_MODE: (BATTLE_WIDGETS_CONSTS.PILLBOX_SIEGE,),
     VehicleMechanicKeys.POWER_MODE: (BATTLE_WIDGETS_CONSTS.POWER,),
     VehicleMechanicKeys.PROPELLANT_GUN: (BATTLE_WIDGETS_CONSTS.PROPELLANT_GUN,),
     VehicleMechanicKeys.RECHARGEABLE_NITRO: (BATTLE_WIDGETS_CONSTS.RECHARGEABLE_NITRO,),
     VehicleMechanicKeys.ROCKET_ACCELERATION: (BATTLE_WIDGETS_CONSTS.ROCKET_ACCELERATOR,),
     VehicleMechanicKeys.SIGHT_POINTER: (BATTLE_WIDGETS_CONSTS.SIGHT_POINTER_WIDGET,),
     VehicleMechanicKeys.SHELL_PARAMS_SWITCHER: (BATTLE_WIDGETS_CONSTS.SHELL_PARAMS_SWITCHER,),
     VehicleMechanicKeys.SHELL_CALIBRATION: (BATTLE_WIDGETS_CONSTS.SHELL_CALIBRATION,),
     VehicleMechanicKeys.STAGED_JET_BOOSTERS: (BATTLE_WIDGETS_CONSTS.STAGED_JET_BOOSTERS,),
     VehicleMechanicKeys.STANCE_DANCE: (BATTLE_WIDGETS_CONSTS.STANCE_DANCE_FIGHT, BATTLE_WIDGETS_CONSTS.STANCE_DANCE_TURBO),
     VehicleMechanicKeys.STATIONARY_RELOAD: (BATTLE_WIDGETS_CONSTS.STATIONARY_RELOAD,),
     VehicleMechanicKeys.SUPPORT_WEAPON: (BATTLE_WIDGETS_CONSTS.SUPPORT_WEAPON,),
     VehicleMechanicKeys.TARGET_DESIGNATOR: (BATTLE_WIDGETS_CONSTS.TARGET_DESIGNATOR_WIDGET,),
     VehicleMechanicKeys.WHEELED_DASH: (BATTLE_WIDGETS_CONSTS.WHEELED_DASH,)}

    def _populate(self):
        super(MechanicWidgetsPanel, self)._populate()
        self.startVehiclePassengerLateListening(self.__onVehicleControlling)

    def _dispose(self):
        self.stopVehiclePassengerListening(self.__onVehicleControlling)
        super(MechanicWidgetsPanel, self)._dispose()

    def _setIsReplay(self, isReplay):
        self.as_isReplayS(isReplay)

    def _setIsVisible(self, isVisible):
        self.as_setVisibleS(isVisible)

    def _setCrosshairScaledPosition(self, position):
        self.as_updateLayoutS(*position)

    def _setCrosshairViewID(self, viewID):
        self.as_updateCrosshairTypeS(viewID)

    def _addMechanicUIComponents(self, mechanicComponents):
        for componentName in mechanicComponents:
            self.as_addWidgetS(componentName)

    @hasVehiclePassengerCtrl()
    def __onVehicleControlling(self, _, passengerCtrl=None):
        self.as_isPlayerS(passengerCtrl.isCurrentPlayerVehicle)
