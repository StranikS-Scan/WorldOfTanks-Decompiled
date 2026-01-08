# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/temp_overheat_gun_widget.py
from __future__ import absolute_import, division
import typing
from cache import last_cached_method
from events_containers.common.containers import ContainersListener
from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
from events_handler import eventHandler
from gui.Scaleform.daapi.view.meta.TemperatureGunOverheatWidgetMeta import TemperatureGunOverheatWidgetMeta
from gui.Scaleform.genConsts.MECHANICS_WIDGET_CONST import MECHANICS_WIDGET_CONST as _UI_STATES
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_life_cycle_updater import VehicleMechanicLifeCycleUpdater
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.temp_overheat_gun_updater import ITemperatureOverheatGunStatesListenerLogic, TemperatureOverheatGunStatesUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import DEFAULT_TEMPERATURE_MECHANIC_STATE
from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import DEFAULT_OVERHEAT_MECHANIC_STATE
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater
    from vehicles.mechanics.gun_mechanics.temperature.overheat_gun import IOverheatGunComponentParams, IOverheatGunMechanicState
    from vehicles.mechanics.gun_mechanics.temperature.temperature_gun import ITemperatureGunMechanicState

class TemperatureOverheatGunWidget(TemperatureGunOverheatWidgetMeta, ContainersListener, IComponentLifeCycleListenerLogic, ITemperatureOverheatGunStatesListenerLogic):

    def __init__(self):
        super(TemperatureOverheatGunWidget, self).__init__()
        self.__tempState = DEFAULT_TEMPERATURE_MECHANIC_STATE
        self.__overheatState = DEFAULT_OVERHEAT_MECHANIC_STATE

    @eventHandler
    def onComponentParamsCollected(self, params):
        self.as_setupThresholdsS(params.overheatWarnPercent, params.overheatOffPercent)

    @eventHandler
    def onOverheatStatePrepared(self, state):
        self.__invalidateAll(self.__tempState, state, isInstantly=True)

    @eventHandler
    def onOverheatStateTransition(self, prevState, newState):
        self.__invalidateAll(self.__tempState, newState)

    @eventHandler
    def onTemperatureStatePrepared(self, state):
        self.__invalidateAll(state, self.__overheatState, isInstantly=True)

    @eventHandler
    def onTemperatureStateObservation(self, state):
        self.__invalidateAll(state, self.__overheatState)

    @eventHandler
    def onTemperatureStateTick(self, state):
        self.__invalidateProgresses(state.temperatureProgress, self.__overheatState.overheatTimeLeft(state))

    def _getViewUpdaters(self):
        return [VehicleMechanicLifeCycleUpdater(VehicleMechanic.OVERHEAT_GUN, self), VehicleMechanicPassengerUpdater(VehicleMechanic.OVERHEAT_GUN, self), TemperatureOverheatGunStatesUpdater(self)]

    def __invalidateAll(self, tempState, overheatState, isInstantly=False):
        self.__tempState, self.__overheatState = tempState, overheatState
        self.as_setStateS(_UI_STATES.PREPARING if overheatState.isOverheated else _UI_STATES.ACTIVE, isInstantly)
        self.__invalidateProgresses.reset()
        self.__invalidateProgresses(tempState.temperatureProgress, overheatState.overheatTimeLeft(tempState))

    @last_cached_method()
    def __invalidateProgresses(self, temperatureProgress, overheatTime):
        self.as_setTemperatureS(temperatureProgress)
        self.as_setTimeS(overheatTime)
