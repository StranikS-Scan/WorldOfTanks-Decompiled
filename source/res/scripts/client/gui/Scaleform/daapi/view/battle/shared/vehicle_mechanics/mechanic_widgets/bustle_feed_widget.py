# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/bustle_feed_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from constants import BUSTLE_FEED_STATE, BUSTLE_FEED_SWITCH_ACCESS
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.BustleFeedWidgetMeta import BustleFeedWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_commands_updater import VehicleMechanicCommandsUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_commands import IMechanicCommandsListenerLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.generic_mechanics.bustle_feed import BustleFeedState

class BustleFeedMechanicWidget(BustleFeedWidgetMeta, ContainersListener, IMechanicStatesListenerLogic, IMechanicCommandsListenerLogic):
    _BUSTLE_FEED_UI_STATES = {BUSTLE_FEED_STATE.INACTIVE: MECHANICS_WIDGET_CONST.IDLE,
     BUSTLE_FEED_STATE.ACTIVATION: MECHANICS_WIDGET_CONST.PREPARING,
     BUSTLE_FEED_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     BUSTLE_FEED_STATE.DEACTIVATION: MECHANICS_WIDGET_CONST.TRANSITION}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.SWITCH.value, False)]}

    def __init__(self):
        super(BustleFeedMechanicWidget, self).__init__()
        self.__switchAccessState = BUSTLE_FEED_SWITCH_ACCESS.ENABLED

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self.__invalidateState(newState)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAvailability(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(state)

    @eventHandler
    def onMechanicCommand(self, command):
        self.as_setCommandS(command.value)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.BUSTLE_FEED, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.BUSTLE_FEED, self),
         VehicleMechanicCommandsUpdater(VehicleMechanic.BUSTLE_FEED, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def __invalidateAll(self, state, isInstantly=False):
        self.__invalidateState(state, isInstantly=isInstantly)
        self.__invalidateAvailability(state)
        self.__invalidateProgress(state)

    def __invalidateState(self, state, isInstantly=False):
        uiState = self._BUSTLE_FEED_UI_STATES.get(state.state, MECHANICS_WIDGET_CONST.EMPTY)
        self.as_setStateS(uiState, isInstantly)

    def __invalidateAvailability(self, state):
        switchAccessState = state.switchAccessState
        if self.__switchAccessState != switchAccessState:
            self.as_setLockS(BUSTLE_FEED_SWITCH_ACCESS.isLocked(switchAccessState))
            self.as_setAvailabilityS(BUSTLE_FEED_SWITCH_ACCESS.isDisabled(switchAccessState))
            self.__switchAccessState = switchAccessState

    def __invalidateProgress(self, state):
        if state.isSwitchState():
            self.as_setProgressS(state.progress, state.timeLeft)
