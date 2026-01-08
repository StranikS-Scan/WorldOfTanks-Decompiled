# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/temperature_gun_overheat_crosshair.py
from __future__ import absolute_import
import typing
from constants import OVERHEAT_GUN_STATE
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.TemperatureGunOverheatDecorativeCrosshairMeta import TemperatureGunOverheatDecorativeCrosshairMeta
from gui.Scaleform.genConsts.DECORATIVE_CROSSHAIR_CONSTS import DECORATIVE_CROSSHAIR_CONSTS
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import IOverheatGunMechanicState
_MECHANIC_STATE_DECOR_MAP = {OVERHEAT_GUN_STATE.IDLE: DECORATIVE_CROSSHAIR_CONSTS.HIDE_STATE,
 OVERHEAT_GUN_STATE.WARNING: DECORATIVE_CROSSHAIR_CONSTS.WARNING_STATE,
 OVERHEAT_GUN_STATE.OVERHEATING: DECORATIVE_CROSSHAIR_CONSTS.SHOW_STATE}

class TemperatureGunOverheatDecorativeCrosshair(TemperatureGunOverheatDecorativeCrosshairMeta, ContainersListener, IMechanicStatesListenerLogic):

    @eventHandler
    def onStatePrepared(self, overheatState):
        self.__invalidateState(overheatState.overheatState, isInstantly=True)

    @eventHandler
    def onStateTransition(self, _, overheatState):
        self.__invalidateState(overheatState.overheatState)

    def _getViewUpdaters(self):
        return [VehicleMechanicStatesUpdater(VehicleMechanic.OVERHEAT_GUN, self), VehicleMechanicPassengerUpdater(VehicleMechanic.OVERHEAT_GUN, self)]

    def __invalidateState(self, overheatState, isInstantly=False):
        self.as_setStateS(_MECHANIC_STATE_DECOR_MAP[overheatState], isInstantly)
