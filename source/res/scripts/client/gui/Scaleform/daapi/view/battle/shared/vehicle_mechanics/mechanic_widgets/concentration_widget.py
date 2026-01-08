# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/concentration_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from cache import last_cached_method
from constants import CONCENTRATION_MODE_STATE
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.ConcentrationWidgetMeta import ConcentrationWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from ConcentrationModeComponent import ConcentrationModeState
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class ConcentrationMechanicWidget(ConcentrationWidgetMeta, ContainersListener, IMechanicStatesListenerLogic):
    _CONCENTRATION_UI_STATES = {CONCENTRATION_MODE_STATE.IDLE: MECHANICS_WIDGET_CONST.IDLE,
     CONCENTRATION_MODE_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.PREPARING,
     CONCENTRATION_MODE_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     CONCENTRATION_MODE_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     CONCENTRATION_MODE_STATE.COOLDOWN: MECHANICS_WIDGET_CONST.PREPARING,
     CONCENTRATION_MODE_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, False)]}

    def __init__(self):
        super(ConcentrationMechanicWidget, self).__init__()
        self.__progressUpdaters = {}

    @eventHandler
    def onStatePrepared(self, state):
        self.__invalidateAll(state, isInstantly=True)

    @eventHandler
    def onStateObservation(self, state):
        self.__invalidateAll(state)

    @eventHandler
    def onStateTick(self, state):
        self.__invalidateProgress(self.__getDisplayState(state), state.progress, state.timeLeft)

    def _populate(self):
        self.__progressUpdaters = {MECHANICS_WIDGET_CONST.PREPARING: self.as_setPreparingProgressS,
         MECHANICS_WIDGET_CONST.ACTIVE: self.as_setActiveProgressS}
        super(ConcentrationMechanicWidget, self)._populate()

    def _dispose(self):
        self.__progressUpdaters.clear()
        super(ConcentrationMechanicWidget, self)._dispose()

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.CONCENTRATION_MODE, self), VehicleMechanicStatesUpdater(VehicleMechanic.CONCENTRATION_MODE, self), HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def __getDisplayState(self, state):
        return self._CONCENTRATION_UI_STATES[state.state]

    def __invalidateAll(self, state, isInstantly=False):
        uiState = self.__getDisplayState(state)
        self.__invalidateProgress.reset()
        self.__invalidateProgress(uiState, state.progress, state.timeLeft)
        self.as_setStateS(uiState, isInstantly)

    @last_cached_method()
    def __invalidateProgress(self, uiState, progress, timeLeft):
        if uiState in self.__progressUpdaters:
            self.__progressUpdaters[uiState](progress)
        self.as_setTimeS(timeLeft)
