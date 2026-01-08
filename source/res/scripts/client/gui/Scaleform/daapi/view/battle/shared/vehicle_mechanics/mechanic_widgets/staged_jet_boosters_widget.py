# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/staged_jet_boosters_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from constants import AcceleratorStatus, PHASED_MECHANIC_STATE
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.StagedJetBoostersWidgetMeta import StagedJetBoostersWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.Scaleform.genConsts.STAGED_JET_BOOSTERS_CONSTS import STAGED_JET_BOOSTERS_CONSTS
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from StagedJetBoostersController import StagedJetBoostersState

class StagedJetBoostersMechanicWidget(StagedJetBoostersWidgetMeta, ContainersListener, IMechanicStatesListenerLogic):
    _UI_STATES = {PHASED_MECHANIC_STATE.NOT_RUNNING: MECHANICS_WIDGET_CONST.IDLE,
     PHASED_MECHANIC_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.PREPARING,
     PHASED_MECHANIC_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     PHASED_MECHANIC_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     PHASED_MECHANIC_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     PHASED_MECHANIC_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE,
     PHASED_MECHANIC_STATE.EMPTY: MECHANICS_WIDGET_CONST.EMPTY}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_SPECIAL_ABILITY: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}
    _UI_MOVEMENT_INFO = {AcceleratorStatus.NONE: STAGED_JET_BOOSTERS_CONSTS.BACKWARD,
     AcceleratorStatus.LEFT: STAGED_JET_BOOSTERS_CONSTS.RIGHT,
     AcceleratorStatus.RIGHT: STAGED_JET_BOOSTERS_CONSTS.LEFT,
     AcceleratorStatus.BOTH: STAGED_JET_BOOSTERS_CONSTS.FORWARD}

    def __init__(self):
        super(StagedJetBoostersMechanicWidget, self).__init__()
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
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.STAGED_JET_BOOSTERS, self), VehicleMechanicStatesUpdater(VehicleMechanic.STAGED_JET_BOOSTERS, self), HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def __invalidateAll(self, state, isInstantly=False):
        self.as_setStateS(self._UI_STATES[state.state], isInstantly)
        self.as_setCountS(state.count)
        self.as_setMovementInfoS(self._UI_MOVEMENT_INFO[state.acceleratorStatus])
        self.__invalidateProgress(state=state, forced=True)

    def __invalidateProgress(self, state, forced=False):
        if forced or state.progress != self.__progress:
            self.__progress = state.progress
            self.as_setProgressS(self.__progress)
        if forced or state.timeLeft != self.__timeLeft:
            timeLeft = state.params.deployTime if state.state == PHASED_MECHANIC_STATE.NOT_RUNNING else state.timeLeft
            self.__timeLeft = timeLeft
            self.as_setTimeS(timeLeft)
