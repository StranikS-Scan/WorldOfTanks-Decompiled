# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/spec_boost_mode_widget.py
from __future__ import absolute_import
import typing
import CommandMapping
from cache import last_cached_method
from constants import PHASED_MECHANIC_STATE
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import HotKeyData
from gui.Scaleform.daapi.view.meta.SpecBoostModeWidgetMeta import SpecBoostModeWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST
from gui.veh_mechanics.battle.updaters.hotkey_updaters import HotKeysViewUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_life_cycle_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_states_updater import VehicleMechanicStatesUpdater
from items.vehicle_mechanics_types import VehicleMechanicKeys
from vehicles.mechanics.mechanic_constants import VehicleMechanicCommand
from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.generic_mechanics.spec_boost_mode import ISpecBoostModeMechanicParams, ISpecBoostModeMechanicState

class SpecBoostModeWidget(SpecBoostModeWidgetMeta, ContainersListener, IComponentLifeCycleListenerLogic, IMechanicStatesListenerLogic):
    __SPEC_BOOST_MODE_UI_STATES = {PHASED_MECHANIC_STATE.NOT_RUNNING: MECHANICS_WIDGET_CONST.IDLE,
     PHASED_MECHANIC_STATE.DEPLOYING: MECHANICS_WIDGET_CONST.PREPARING,
     PHASED_MECHANIC_STATE.READY: MECHANICS_WIDGET_CONST.READY,
     PHASED_MECHANIC_STATE.ACTIVE: MECHANICS_WIDGET_CONST.ACTIVE,
     PHASED_MECHANIC_STATE.PREPARING: MECHANICS_WIDGET_CONST.PREPARING,
     PHASED_MECHANIC_STATE.DISABLED: MECHANICS_WIDGET_CONST.DISABLE}
    _HOT_KEY_MAP = {CommandMapping.CMD_CM_VEHICLE_SWITCH_AUTOROTATION: [HotKeyData(VehicleMechanicCommand.ALTERNATIVE_ACTIVATE.value, False)]}

    def __init__(self):
        super(SpecBoostModeWidget, self).__init__()
        self.__progressUpdaters = {}

    @eventHandler
    def onComponentParamsCollected(self, params):
        self.as_setMechanicVariantS(params.mechanicVariant.value)

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
        super(SpecBoostModeWidget, self)._populate()

    def _dispose(self):
        self.__progressUpdaters.clear()
        super(SpecBoostModeWidget, self)._dispose()

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanicKeys.COMBAT_THROTTLE, self),
         VehicleMechanicPassengerUpdater(VehicleMechanicKeys.COMBAT_THROTTLE, self),
         VehicleMechanicStatesUpdater(VehicleMechanicKeys.COMBAT_THROTTLE, self),
         HotKeysViewUpdater(list(self._HOT_KEY_MAP.keys()), self)]

    def __getDisplayState(self, state):
        return self.__SPEC_BOOST_MODE_UI_STATES[state.state]

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
