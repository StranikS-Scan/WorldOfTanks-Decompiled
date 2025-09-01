# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/target_designator_widget.py
import typing
import CommandMapping
from constants import TARGET_DESIGNATOR_STATE as STATE
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.TargetDesignatorWidgetMeta import TargetDesignatorWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events.events_listener import ComponentListener
if typing.TYPE_CHECKING:
    from TargetDesignatorController import TargetDesignatorState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
_UI_STATE_MAP = {STATE.PRE_BATTLE: MECHANICS_WIDGET_CONST.IDLE,
 STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
 STATE.COOLDOWN: MECHANICS_WIDGET_CONST.PREPARING,
 STATE.READY: MECHANICS_WIDGET_CONST.READY}

class TargetDesignatorMechanicWidget(TargetDesignatorWidgetMeta, ComponentListener, IMechanicStatesListenerLogic):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, False)]}

    @eventHandler
    def onStatePrepared(self, state):
        self.onStateTransition(None, state, isInstantly=True)
        return

    @eventHandler
    def onStateTransition(self, _, state, isInstantly=False):
        self.onStateTick(state)
        self.as_setStateS(_UI_STATE_MAP[state.state], isInstantly)

    @eventHandler
    def onStateTick(self, state):
        if state.state == STATE.COOLDOWN:
            timeLeft = state.timeLeft()
            self.as_setTimeS(timeLeft)
            self.as_setPreparingProgressS(state.progress(timeLeft))
        elif state.state == STATE.PRE_BATTLE:
            self.as_setTimeS(state.timeLeft())

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.TARGET_DESIGNATOR, self), VehicleMechanicStatesUpdater(VehicleMechanic.TARGET_DESIGNATOR, self), HotKeysViewUpdater(self._HOT_KEY_MAP.keys(), self)]
