# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/stationary_reloading_widget.py
import typing
from constants import STATIONARY_RELOAD_STATE, GUN_LOCK_REASONS
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.StationaryReloadWidgetMeta import StationaryReloadWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.Scaleform.genConsts.STATIONARY_RELOAD_WIDGET_CONSTS import STATIONARY_RELOAD_WIDGET_CONSTS as SR_CONSTS
from gui.battle_control.battle_constants import DEVICE_STATE_CRITICAL, DEVICE_STATE_NORMAL
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.vehicle_device_view_updater import VehicleDeviceStatusUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events import ComponentListener
if typing.TYPE_CHECKING:
    from StationaryReloadController import StationaryReloadState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class StationaryReloadingMechanicWidget(StationaryReloadWidgetMeta, ComponentListener, IMechanicStatesListenerLogic):
    _STATIONARY_RELOADING_UI_STATES = {STATIONARY_RELOAD_STATE.IDLE: MECHANICS_WIDGET_CONST.IDLE,
     STATIONARY_RELOAD_STATE.FIXING_GUN: MECHANICS_WIDGET_CONST.PREPARING,
     STATIONARY_RELOAD_STATE.PREPARING: MECHANICS_WIDGET_CONST.ACTIVE,
     STATIONARY_RELOAD_STATE.RELOADING: MECHANICS_WIDGET_CONST.IDLE,
     STATIONARY_RELOAD_STATE.FINISHING: MECHANICS_WIDGET_CONST.ACTIVE}

    def __init__(self):
        super(StationaryReloadingMechanicWidget, self).__init__()
        self.__isTurretDamaged = False
        self.__state = None
        return

    def vehicleDeviceStatusChanged(self, devicesStatuses):
        self.__isTurretDamaged = devicesStatuses.get('turretRotator') == DEVICE_STATE_CRITICAL
        self.__updateVehicleCondition()

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateState(newState)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateTimer()

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.STATIONARY_RELOAD, self), VehicleMechanicStatesUpdater(VehicleMechanic.STATIONARY_RELOAD, self), VehicleDeviceStatusUpdater({'turretRotator': (DEVICE_STATE_NORMAL, DEVICE_STATE_CRITICAL)}, self)]

    def __invalidateState(self, state, isInstantly=False):
        self.__state = state
        self.as_setStateS(self._STATIONARY_RELOADING_UI_STATES[state.state], isInstantly)
        self.__invalidateTimer()
        self.__updateVehicleCondition()

    def __invalidateTimer(self):
        if self.__state.state in {STATIONARY_RELOAD_STATE.PREPARING, STATIONARY_RELOAD_STATE.FINISHING}:
            self.as_setTimeS(self.__state.sequenceTimeLeft)

    def __updateVehicleCondition(self):
        if self.__state is None:
            return
        else:
            if self.__state.state != STATIONARY_RELOAD_STATE.FIXING_GUN:
                self.as_setConditionS(SR_CONSTS.NORMAL)
            elif self.__state.gunLockMask != GUN_LOCK_REASONS.NONE:
                self.as_setConditionS(SR_CONSTS.DESTROYED)
            elif self.__isTurretDamaged:
                self.as_setConditionS(SR_CONSTS.CRITICAL)
            else:
                self.as_setConditionS(SR_CONSTS.NORMAL)
            return
