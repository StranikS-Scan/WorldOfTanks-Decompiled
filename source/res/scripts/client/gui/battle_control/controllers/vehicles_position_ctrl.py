# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_position_ctrl.py
from functools import partial
import BigWorld
from helpers import dependency
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from skeletons.gui.battle_session import IBattleSessionProvider
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE

class VehiclePositionController(IArenaVehiclesController):
    _TELEPORT_DISTANCE = 5.0
    _TICK_UPDATE = 0.1
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(VehiclePositionController, self).__init__()
        self._vehiclesPositionParams = {'data': {},
         'lastCheckTime': {},
         'prevData': {}}
        self.__pluginID = 'vehicles'
        self.__minimapPlugin = None
        self._vehiclesCallback = {}
        return

    def startControl(self, battleCtx, arenaVisitor):
        g_eventBus.addListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)

    def stopControl(self):
        self.__minimapPlugin = None
        self._vehiclesPositionParams.clear()
        self.clearCallback()
        g_eventBus.removeListener(events.ComponentEvent.COMPONENT_REGISTERED, self.__onComponentRegistered, scope=EVENT_BUS_SCOPE.GLOBAL)
        return

    def clearCallback(self):
        for callbackID in self._vehiclesCallback.itervalues():
            if callbackID:
                BigWorld.cancelCallback(callbackID)

        self._vehiclesCallback.clear()

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLES_POSITION

    def getCtrlScope(self):
        return _SCOPE.VEHICLES

    def setPositionParams(self, vehiclesPositionsData):
        player = BigWorld.player()
        playerVehicleID = player.playerVehicleID if player else None
        if playerVehicleID is None:
            return
        else:
            for vehicleID in list(self._vehiclesCallback):
                self.__removeVehiclePositionData(vehicleID)

            for positionData in vehiclesPositionsData:
                vehicleID = positionData['vehicleID']
                vehiclePositionData = {'position': positionData['position'],
                 'velocity': positionData['velocity']}
                if vehicleID == playerVehicleID:
                    continue
                if BigWorld.entities.get(vehicleID):
                    continue
                self._vehiclesPositionParams['data'][vehicleID] = vehiclePositionData
                self._vehiclesPositionParams['prevData'][vehicleID] = vehiclePositionData
                self._vehiclesPositionParams['lastCheckTime'][vehicleID] = BigWorld.time()
                self._vehiclesCallback[vehicleID] = BigWorld.callback(self._TICK_UPDATE, partial(self.__updatePosition, vehicleID))

            return

    def __updatePosition(self, vehicleID):
        self._vehiclesCallback[vehicleID] = None
        prevDataByVehID = self._vehiclesPositionParams['prevData'][vehicleID]
        lastCheckTime = self._vehiclesPositionParams['lastCheckTime']
        vehicle = BigWorld.entities.get(vehicleID)
        if vehicle or self.__minimapPlugin is None:
            return
        else:
            positionData = self._vehiclesPositionParams['data'][vehicleID]
            position = positionData['position']
            if (prevDataByVehID['position'] - position).length < self._TELEPORT_DISTANCE:
                dt = BigWorld.time() - lastCheckTime[vehicleID]
                position = prevDataByVehID['position'] + positionData['velocity'] * dt
            positionData['position'] = position
            lastCheckTime[vehicleID] = BigWorld.time()
            self.__minimapPlugin.updateVehiclePosition(vehicleID, position)
            self._vehiclesCallback[vehicleID] = BigWorld.callback(self._TICK_UPDATE, partial(self.__updatePosition, vehicleID))
            return

    def __removeVehiclePositionData(self, vehicleID):
        if vehicleID in self._vehiclesCallback:
            callbackID = self._vehiclesCallback[vehicleID]
            if callbackID:
                BigWorld.cancelCallback(callbackID)
            del self._vehiclesCallback[vehicleID]
        vehiclesPositionParams = self._vehiclesPositionParams
        for dictData in vehiclesPositionParams.itervalues():
            if vehicleID in dictData:
                del dictData[vehicleID]

    def __onComponentRegistered(self, event):
        alias = event.alias
        if alias == BATTLE_VIEW_ALIASES.MINIMAP:
            plugin = event.componentPy.getPlugin(self.__pluginID)
            if plugin is not None:
                self.__minimapPlugin = plugin
        return
