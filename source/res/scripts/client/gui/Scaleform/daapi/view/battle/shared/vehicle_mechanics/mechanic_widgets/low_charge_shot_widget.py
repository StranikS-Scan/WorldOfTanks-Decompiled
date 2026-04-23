# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/low_charge_shot_widget.py
from __future__ import absolute_import
import typing
import BattleReplay
from constants import LowChargeShotReloadingState
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.LowChargeShotWidgetMeta import LowChargeShotWidgetMeta
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.mechanics.low_charge_shot_updater import LowChargeShotUpdater
from vehicles.mechanics.gun_mechanics.low_charge_shot.private import LowChargeShotMechanicState, DEFAULT_MECHANIC_STATE
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class LowChargeShotMechanicWidget(LowChargeShotWidgetMeta, ContainersListener, IMechanicStatesListenerLogic):

    def __init__(self):
        super(LowChargeShotMechanicWidget, self).__init__()
        self.__mechanicState = DEFAULT_MECHANIC_STATE
        self.__shellChangeTime = 0.0

    @eventHandler
    def onStatePrepared(self, state):
        self.__updateState(state)
        self.__updateInitialTime()
        timeLeft = state.calculateTimeLeft()
        self.__updateTimeLeft(timeLeft, state)

    @eventHandler
    def onStateObservation(self, state):
        self.__updateState(state)
        self.__updateInitialTime()
        if not BattleReplay.g_replayCtrl.isPlaying:
            if state.reloadingState in (LowChargeShotReloadingState.EMPTY, LowChargeShotReloadingState.FULL_CHARGE):
                timeLeft = state.timeLeft
            else:
                timeLeft = state.calculateTimeLeft()
            self.__updateTimeLeft(timeLeft, state)

    @eventHandler
    def onStateTick(self, state):
        if BattleReplay.g_replayCtrl.isPlaying and state.reloadingState not in (LowChargeShotReloadingState.NONE, LowChargeShotReloadingState.EMPTY):
            timeLeft = state.calculateTimeLeft()
            self.as_setTimeLeftS(timeLeft, state.reloadingState, True)

    def setShellChangeTime(self, isVisible, shellChangeTime):
        if self.__mechanicState.reloadingState not in (LowChargeShotReloadingState.NONE, LowChargeShotReloadingState.EMPTY, LowChargeShotReloadingState.QUICK_RELOAD):
            self.__updateShellChangeTime(shellChangeTime if isVisible else 0.0)
            self.__updateInitialTime()

    def setBaseTimeBeforeBattleOrEmpty(self, baseTimeSet):
        if self.__mechanicState.reloadingState in (LowChargeShotReloadingState.NONE, LowChargeShotReloadingState.EMPTY):
            if baseTimeSet > 0:
                baseTime = baseTimeSet
                lowChargeTime = baseTime * self.__mechanicState.reloadTimeCoefficient
            else:
                baseTime = 0.0
                lowChargeTime = 0.0
            self.as_setInitialTimeS(baseTime, lowChargeTime, self.__mechanicState.almostFinishedTime, self.__mechanicState.reloadTimeCoefficient, self.__shellChangeTime)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.LOW_CHARGE_SHOT, self), VehicleMechanicStatesUpdater(VehicleMechanic.LOW_CHARGE_SHOT, self), LowChargeShotUpdater(self)]

    def __updateState(self, state):
        self.__mechanicState = state

    def __updateShellChangeTime(self, shellChangeTime):
        self.__shellChangeTime = shellChangeTime

    def __updateTimeLeft(self, timeLeft, state):
        if state.reloadingState == LowChargeShotReloadingState.NONE:
            return
        if timeLeft >= -1 or state.reloadingState == LowChargeShotReloadingState.EMPTY:
            self.as_setTimeLeftS(timeLeft, state.reloadingState, False)

    def __updateInitialTime(self):
        self.as_setInitialTimeS(self.__mechanicState.baseTime, self.__mechanicState.lowChargeTime, self.__mechanicState.almostFinishedTime, self.__mechanicState.reloadTimeCoefficient, self.__shellChangeTime)
