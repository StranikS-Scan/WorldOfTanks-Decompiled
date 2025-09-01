# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/rechargeable_nitro_widget.py
import typing
import CommandMapping
from constants import RECHARGEABLE_NITRO_STATE
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.RocketAcceleratorIndicatorMeta import RocketAcceleratorIndicatorMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from RechargeableNitroController import RechargeableNitroState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class RechargeableNitroMechanicWidget(RocketAcceleratorIndicatorMeta, ComponentListener, IMechanicStatesListenerLogic):
    _UI_STATES = {RECHARGEABLE_NITRO_STATE.NOT_RUNNING: MECHANICS_WIDGET_CONST.IDLE,
     RECHARGEABLE_NITRO_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.PREPARING,
     RECHARGEABLE_NITRO_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     RECHARGEABLE_NITRO_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     RECHARGEABLE_NITRO_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     RECHARGEABLE_NITRO_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE,
     RECHARGEABLE_NITRO_STATE.PRIMED: MECHANICS_WIDGET_CONST.PRIME,
     RECHARGEABLE_NITRO_STATE.DEPLETING: MECHANICS_WIDGET_CONST.ACTIVE}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    def __init__(self):
        super(RechargeableNitroMechanicWidget, self).__init__()
        self.__progress = 0.0
        self.__timeLeft = 0.0

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, newState):
        self.__invalidateAll(newState)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(state)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.RECHARGEABLE_NITRO, self), VehicleMechanicStatesUpdater(VehicleMechanic.RECHARGEABLE_NITRO, self), HotKeysViewUpdater(self._HOT_KEY_MAP.keys(), self)]

    def __invalidateAll(self, state, isInstantly=False):
        self.as_setStateS(self._UI_STATES[state.state], isInstantly)
        self.__invalidateProgress(state=state, forced=True)

    def __invalidateProgress(self, state, forced=False):
        if forced or state.progress != self.__progress:
            self.__progress = state.progress
            self.as_setProgressS(self.__progress)
        if forced or state.timeLeft != self.__timeLeft:
            self.__timeLeft = state.timeLeft
            self.as_setTimeS(state.timeLeft)
