# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/wheeled_dash_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from cache import last_cached_method
from WheeledDashController import WheeledDashState
from constants import PHASED_MECHANIC_STATE
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.WheeledDashWidgetMeta import WheeledDashWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from helpers import dependency
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_commands_updater import VehicleMechanicCommandsUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class WheeledDashMechanicWidget(WheeledDashWidgetMeta, ContainersListener, IMechanicStatesListenerLogic):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _WHEELED_DASH_UI_STATES = {PHASED_MECHANIC_STATE.NOT_RUNNING: MECHANICS_WIDGET_CONST.IDLE,
     PHASED_MECHANIC_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.DEPLOYING,
     PHASED_MECHANIC_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     PHASED_MECHANIC_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     PHASED_MECHANIC_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     PHASED_MECHANIC_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE,
     PHASED_MECHANIC_STATE.EMPTY: MECHANICS_WIDGET_CONST.DISABLE}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ACTIVATE.value, False)]}

    def __init__(self):
        super(WheeledDashMechanicWidget, self).__init__()
        self.__progressUpdaters = {}
        self.__isReducedCooldown = False

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateState(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateState(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(self.__getDisplayState(state), state.progress, state.timeLeft, state.baseTime, state.isReducedCooldown)

    def _populate(self):
        self.__progressUpdaters = {MECHANICS_WIDGET_CONST.PREPARING: self.as_setPreparingProgressS,
         MECHANICS_WIDGET_CONST.DEPLOYING: self.as_setPreparingProgressS,
         MECHANICS_WIDGET_CONST.ACTIVE: self.as_setActiveProgressS}
        super(WheeledDashMechanicWidget, self)._populate()

    def _dispose(self):
        self.__progressUpdaters.clear()
        super(WheeledDashMechanicWidget, self)._dispose()

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.WHEELED_DASH, self),
         VehicleMechanicStatesUpdater(VehicleMechanic.WHEELED_DASH, self),
         VehicleMechanicCommandsUpdater(VehicleMechanic.WHEELED_DASH, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def __getDisplayState(self, state):
        return self._WHEELED_DASH_UI_STATES.get(state.state, MECHANICS_WIDGET_CONST.IDLE)

    def __invalidateState(self, state, isInstantly=False):
        uiState = self.__getDisplayState(state)
        self.__invalidateProgress.reset()
        self.__invalidateProgress(uiState, state.progress, state.timeLeft, state.baseTime, state.isReducedCooldown)
        self.as_setStateS(uiState, isInstantly)

    @last_cached_method()
    def __invalidateProgress(self, uiState, progress, timeLeft, baseTime, isReducedCooldown):
        self.as_setTimeS(baseTime if uiState == MECHANICS_WIDGET_CONST.IDLE else timeLeft)
        if uiState in self.__progressUpdaters:
            self.__progressUpdaters[uiState](progress)
        if self.__isReducedCooldown != isReducedCooldown:
            self.__isReducedCooldown = isReducedCooldown
            self.as_isReducedCooldownS(isReducedCooldown)
