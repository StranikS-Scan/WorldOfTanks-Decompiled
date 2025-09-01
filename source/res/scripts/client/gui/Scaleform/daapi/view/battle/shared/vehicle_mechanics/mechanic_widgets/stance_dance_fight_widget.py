# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/stance_dance_fight_widget.py
import typing
import CommandMapping
from constants import ARENA_PERIOD
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from helpers import dependency
from gui.Scaleform.daapi.view.meta.StanceDanceFightWidgetMeta import StanceDanceFightWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.crosshair_type_updater import CrosshairTypeUpdater
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanic_states_view_updater import VehicleMechanicStatesUpdater
from gui.veh_mechanics.battle.updaters.replay_paused_view_updater import ReplayPausedViewUpdater
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand, VehicleMechanic
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import List, Tuple
    from StanceDanceController import StanceDanceState
    from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeyCommand
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

def _getWidgetState(prev, state):
    if state.isActiveFightState:
        if state.isFightState:
            return (MECHANICS_WIDGET_CONST.ACTIVE, prev == MECHANICS_WIDGET_CONST.PASSIVE_ACTIVE)
        return (MECHANICS_WIDGET_CONST.PASSIVE_ACTIVE, False)
    if state.isFightState:
        if prev == MECHANICS_WIDGET_CONST.ACTIVE:
            return (MECHANICS_WIDGET_CONST.PRIME, False)
        if prev == MECHANICS_WIDGET_CONST.TRANSITION:
            return (MECHANICS_WIDGET_CONST.PREPARING, False)
        if state.energyFight == state.params.maxEnergy:
            return (MECHANICS_WIDGET_CONST.READY, prev != MECHANICS_WIDGET_CONST.PREPARING)
        return (MECHANICS_WIDGET_CONST.PREPARING, False)
    return (MECHANICS_WIDGET_CONST.TRANSITION, False) if state.isSwitchingState else (MECHANICS_WIDGET_CONST.IDLE, False)


class StanceDanceFightMechanicWidget(StanceDanceFightWidgetMeta, ComponentListener, IMechanicStatesListenerLogic):
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, False)],
     CommandMapping.CMD_CM_SPECIAL_ABILITY: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(StanceDanceFightMechanicWidget, self).__init__()
        self.__isPaused = False
        self.__progress = -1
        self.__uiState = None
        self.__defaultKey = None
        self.__activeKey = None
        return

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    @eventHandler
    def onStateTransition(self, oldState, newState):
        self.__invalidateAll(newState)

    @eventHandler
    def onStateTick(self, state):
        uiState, _ = _getWidgetState(self.__uiState, state)
        self.__invalidateProgress(state, uiState)

    def setHotkeys(self, hotKeyCommands):
        self.__defaultKey = hotKeyCommands[0]
        self.__activeKey = hotKeyCommands[1]
        self.__invalidateKey()

    def onReplayPaused(self, isPaused):
        self.__isPaused = isPaused
        self.as_pauseReplayS(self.__isPaused)

    def _getViewUpdaters(self):
        return [VehicleMechanicStatesUpdater(VehicleMechanic.STANCE_DANCE, self),
         VehicleMechanicPassengerUpdater(VehicleMechanic.STANCE_DANCE, self),
         HotKeysViewUpdater(self._HOT_KEY_MAP.keys(), self),
         CrosshairTypeUpdater(self),
         ReplayPausedViewUpdater(self)]

    def _populate(self):
        super(StanceDanceFightMechanicWidget, self)._populate()
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            self.__onArenaPeriodChange(arena.period)
        return

    def _dispose(self):
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(StanceDanceFightMechanicWidget, self)._dispose()
        return

    def __onArenaPeriodChange(self, arenaPeriod, *_):
        self.as_keysVisibleS(arenaPeriod == ARENA_PERIOD.BATTLE)

    def __invalidateKey(self):
        key = self.__defaultKey
        if self.__uiState == MECHANICS_WIDGET_CONST.READY:
            key = self.__activeKey
        if key:
            super(StanceDanceFightMechanicWidget, self).setHotkeys([key])

    def __invalidateAll(self, state, isInstantly=False):
        self.__uiState, forcInstantlyState = _getWidgetState(self.__uiState, state)
        self.__invalidateProgress(state, self.__uiState)
        self.as_setStateS(self.__uiState, isInstantly or forcInstantlyState)
        self.__invalidateKey()

    def __invalidateProgress(self, state, uiState):
        if uiState != self.__uiState:
            self.__uiState = uiState
            self.__invalidateKey()
        if state.getFightEnergyRatio != self.__progress:
            self.__progress = state.getFightEnergyRatio
            self.as_setProgressS(state.isSwitchingState, self.__progress)
        if state.isActiveFightState:
            self.as_setTimeS(state.timeLeftActiveFight)
        if state.isSwitchingState:
            self.as_switchTimerS(state.transitionTimeLeft)
