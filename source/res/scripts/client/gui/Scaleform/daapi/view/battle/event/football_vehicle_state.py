# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/football_vehicle_state.py
import BigWorld
from debug_utils import LOG_WARNING
from gui.battle_control.controllers.football_ctrl import IFootballView, IFootballEntitiesView
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import assembleVehicleTraces
_TIME_BEFORE_FADE = 0.3

class FootballVehiclesWatcher(IFootballView, IFootballEntitiesView):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FootballVehiclesWatcher, self).__init__()
        self.__callbackID = None
        return

    def onFootballFadeOut(self, canFadeOut, delay):
        delay = max(0.0, delay - _TIME_BEFORE_FADE)
        if delay:
            self.__callbackID = BigWorld.callback(delay, self.__onDelayEnd)

    def onReturnToPlay(self, data):
        self.__clearCallback()
        self.__arenaVehiclesIterator(self.__allowVehiclesTraces)

    def __onDelayEnd(self):
        self.__callbackID = None
        self.__arenaVehiclesIterator(self.__forbidVehiclesTraces)
        return

    def __arenaVehiclesIterator(self, methodToCall):
        for vInfo, _ in self._sessionProvider.getArenaDP().getVehiclesItemsGenerator():
            vehicleId = vInfo.vehicleID
            vehicle = BigWorld.entities.get(vehicleId)
            if vehicle:
                methodToCall(vehicle)
            LOG_WARNING('Vehicle with id "{}" has not been found'.format(vehicleId))

    def __forbidVehiclesTraces(self, vehicle):
        vehicle.appearance.vehicleTraces = None
        return

    def __allowVehiclesTraces(self, vehicle):
        if vehicle.appearance and vehicle.appearance.vehicleTraces is None:
            assembleVehicleTraces(vehicle.appearance, vehicle.appearance.filter, vehicle.appearance.lodCalculator.lodStateLink)
            vehicle.appearance.vehicleTraces.activate()
        return

    def clear(self):
        self.__clearCallback()

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return
