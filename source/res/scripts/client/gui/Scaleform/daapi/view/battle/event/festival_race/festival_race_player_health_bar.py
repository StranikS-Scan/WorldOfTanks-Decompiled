# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/festival_race/festival_race_player_health_bar.py
from gui.Scaleform.daapi.view.meta.FestivalRacePlayerHealthBarMeta import FestivalRacePlayerHealthBarMeta
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.Scaleform.daapi.view.battle.shared.formatters import formatHealthProgress, normalizeHealthPercent
_STATE_HANDLERS = {VEHICLE_VIEW_STATE.HEALTH: '_updateHealth'}

class FestivalRacePlayerHealthBar(FestivalRacePlayerHealthBarMeta):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FestivalRacePlayerHealthBar, self).__init__()
        self.__maxHealth = 0

    def _populate(self):
        super(FestivalRacePlayerHealthBar, self)._populate()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling += self.__onVehicleControlling
            vehicle = ctrl.getControllingVehicle()
            if vehicle is not None:
                self.__onVehicleControlling(vehicle)
        return

    def __onVehicleControlling(self, vehicle):
        vTypeDesc = vehicle.typeDescriptor
        self.__maxHealth = vTypeDesc.maxHealth
        self.__setupDevicesStates()

    def __setupDevicesStates(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is None:
            return
        else:
            ctrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            for stateID in _STATE_HANDLERS.iterkeys():
                value = ctrl.getStateValue(stateID)
                if value is not None:
                    self.__onVehicleStateUpdated(stateID, value)

            return

    def __onVehicleStateUpdated(self, state, value):
        if state not in _STATE_HANDLERS:
            return
        else:
            handler = getattr(self, _STATE_HANDLERS[state], None)
            if handler and callable(handler):
                handler(value)
            return

    def _updateHealth(self, health):
        if health <= self.__maxHealth and self.__maxHealth > 0:
            healthStr = formatHealthProgress(health, self.__maxHealth)
            healthProgress = normalizeHealthPercent(health, self.__maxHealth)
            self.as_updateHealthS(healthStr, healthProgress)

    def _dispose(self):
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onVehicleControlling -= self.__onVehicleControlling
            ctrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        super(FestivalRacePlayerHealthBar, self)._dispose()
        return
