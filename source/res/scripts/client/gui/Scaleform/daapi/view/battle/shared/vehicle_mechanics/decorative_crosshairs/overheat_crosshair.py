# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/overheat_crosshair.py
import typing
import BattleReplay
from ReplayEvents import g_replayEvents
from constants import OVERHEAT_GAIN_STATE
from gui.veh_mechanics.battle.updaters.current_shell_damage_updater import CurrentShellDamageUpdater
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.OverheatDecorativeCrosshairMeta import OverheatDecorativeCrosshairMeta
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from vehicles.components.component_events.events_listener import ComponentListener
if typing.TYPE_CHECKING:
    from typing import List, Optional
    from OverheatStacksController import OverheatStacksState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class OverheatDecorativeCrosshair(OverheatDecorativeCrosshairMeta, ComponentListener, IMechanicStatesListenerLogic):

    def __init__(self):
        super(OverheatDecorativeCrosshair, self).__init__()
        self.__progress = 0
        self.__level = 0
        self.__baseDamage = 0
        self.__maxLevel = 0
        self.__speedThreshold = 0
        self.__dmgLevelBonus = 0.0
        self.__heatingTime = 0.0
        self.__coolingTime = 0.0
        self.__delayTimerProgress = 0
        self.__gainState = OVERHEAT_GAIN_STATE.NULL_STATE

    def _populate(self):
        super(OverheatDecorativeCrosshair, self)._populate()
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onPlaybackSpeedChanged += self._onPlaybackSpeedChanged
            g_replayEvents.onTimeWarpFinish += self._onReplayTimeWarpFinished

    def _dispose(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            g_replayEvents.onPlaybackSpeedChanged -= self._onPlaybackSpeedChanged
            g_replayEvents.onTimeWarpFinish -= self._onReplayTimeWarpFinished
        super(OverheatDecorativeCrosshair, self)._dispose()

    @eventHandler
    def onStatePrepared(self, state):
        self.__dmgLevelBonus = state.dmgLevelBonus
        self.__invalidateAll(state, force=True)
        self.__maxLevel = state.maxLevel
        self.__speedThreshold = state.speedThreshold
        self.__heatingTime = state.heatingTime
        self.__coolingTime = state.coolingTime
        self.__invalidateAll(state)
        self.as_setInitDataS(self.__speedThreshold, self.__maxLevel, self.__heatingTime, self.__coolingTime, False)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    def updateTimersData(self, speed):
        isSpeedChanged = speed != 1.0
        self.as_setInitDataS(self.__speedThreshold, self.__maxLevel, self.__heatingTime, self.__coolingTime, isSpeedChanged)

    def onCurrentShellDamageChanged(self, newDamage):
        self.__invalidateExpectedDamage(newDamage)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.OVERHEAT_STACKS, self), VehicleMechanicStatesUpdater(VehicleMechanic.OVERHEAT_STACKS, self), CurrentShellDamageUpdater(self)]

    def _onReplayTimeWarpFinished(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying:
            self.updateTimersData(BattleReplay.g_replayCtrl.playbackSpeed)
            self.__sendProgressToAS()

    def _onPlaybackSpeedChanged(self, speed):
        self.updateTimersData(speed)

    def __updateState(self, state):
        newProgress = state.progress
        newDelayTimerProgress = state.delayTimerProgress
        if self.__level != state.level or self.__gainState != state.gainState or self.__delayTimerProgress != newDelayTimerProgress:
            self.__progress = newProgress
            self.__level = state.level
            self.__delayTimerProgress = newDelayTimerProgress
            self.__gainState = state.gainState
            return True
        return False

    def __updateExpectedDamage(self, newBaseDamage=None):
        if newBaseDamage is None:
            newBaseDamage = self.__baseDamage
        self.__baseDamage = newBaseDamage
        maxDamage = round(newBaseDamage * (1.0 + self.__dmgLevelBonus * self.__maxLevel))
        self.as_setDamageDataS(self.__baseDamage, maxDamage)
        return

    def __invalidateState(self, state):
        if self.__updateState(state):
            self.__sendProgressToAS()

    def __invalidateExpectedDamage(self, newDamage):
        self.__updateExpectedDamage(newDamage)

    def __invalidateAll(self, state, force=False):
        self.__updateExpectedDamage()
        isUpdated = self.__updateState(state)
        if isUpdated or force:
            self.__sendProgressToAS()

    def __sendProgressToAS(self):
        self.as_setHeatProgresS(self.__delayTimerProgress)
        self.as_updateStateS(self.__gainState)
        self.as_setStacksProgresS(self.__progress, self.__level)
