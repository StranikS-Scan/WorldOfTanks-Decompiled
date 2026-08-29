# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/sight_pointer_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD, SIGHT_POINTER_STATE, SIGHT_POINTER_COMMON_CONSTANTS
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.SightPointerWidgetMeta import SightPointerWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_life_cycle_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from items.components.shared_components import SightPointerParams
    from SightPointerComponent import SightPointerState

class SightPointerMechanicWidget(SightPointerWidgetMeta, ContainersListener, IComponentLifeCycleListenerLogic, IMechanicStatesListenerLogic):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _UI_STATE_MAP = {SIGHT_POINTER_STATE.DISABLED: MECHANICS_WIDGET_CONST.PREPARING,
     SIGHT_POINTER_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     SIGHT_POINTER_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     SIGHT_POINTER_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     SIGHT_POINTER_STATE.COOLDOWN: MECHANICS_WIDGET_CONST.PREPARING}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_SPECIAL_ABILITY: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    def __init__(self):
        super(SightPointerMechanicWidget, self).__init__()
        self.__uiState = MECHANICS_WIDGET_CONST.IDLE
        self.__progress = -1.0
        self.__tankIconState = 'hide'
        self.__initialDeployTime = 0.0
        self.__isPrebattle = False

    @eventHandler
    def onComponentParamsCollected(self, params):
        self.__initialDeployTime = params.initialDeployTime + SIGHT_POINTER_COMMON_CONSTANTS.ANIMATION_DELAY
        if self.__isPrebattle:
            self.as_setTimeS(self.__initialDeployTime)

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(state)
        self.__invalidateTankIcon(state)

    def _populate(self):
        super(SightPointerMechanicWidget, self)._populate()
        g_playerEvents.onSightPointerEnemySpotted += self._onSightPointerEnemySpotted
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
            self.__onArenaPeriodChange(arena.period)
        return

    def _dispose(self):
        g_playerEvents.onSightPointerEnemySpotted -= self._onSightPointerEnemySpotted
        arena = self.__sessionProvider.arenaVisitor.getArenaSubscription()
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        super(SightPointerMechanicWidget, self)._dispose()
        return

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanic.SIGHT_POINTER, self),
         VehicleMechanicPassengerUpdater(VehicleMechanic.SIGHT_POINTER, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.SIGHT_POINTER, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def _onSightPointerEnemySpotted(self):
        self.as_triggerHighlightLampS()

    def __onArenaPeriodChange(self, arenaPeriod, *_):
        isPrebattle = arenaPeriod < ARENA_PERIOD.BATTLE
        if self.__isPrebattle and not isPrebattle:
            self.as_setTimeS(0)
        elif isPrebattle and self.__initialDeployTime > 0:
            self.as_setTimeS(self.__initialDeployTime)
        self.__isPrebattle = isPrebattle

    def __invalidateState(self, state, isInstantly=False):
        if state.state not in self._UI_STATE_MAP:
            return
        newState = self._UI_STATE_MAP[state.state]
        if self.__uiState != newState:
            self.__uiState = newState
            self.as_setStateS(newState, isInstantly)
            self.__invalidateProgress(state, forced=True)
            self.__invalidateTankIcon(state)

    def __invalidateTankIcon(self, state):
        isAbilityActive = state.state == SIGHT_POINTER_STATE.ACTIVE
        hasTanksInScope = state.vehiclesUnderScan
        if not isAbilityActive:
            if self.__tankIconState == 'found':
                newState = 'hide'
            else:
                newState = 'hide_instantly'
        elif hasTanksInScope:
            newState = 'found'
        else:
            newState = 'active'
        if self.__tankIconState != newState:
            self.__tankIconState = newState
            self.as_setTankIconStateS(newState)

    def __invalidateProgress(self, state, forced=False):
        if not self.__isPrebattle:
            self.as_setTimeS(state.timeLeft)
        if forced or state.progress != self.__progress:
            self.__progress = state.progress
            self.as_setProgressS(self.__progress, state.timeLeft)
