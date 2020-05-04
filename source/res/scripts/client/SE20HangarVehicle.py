# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SE20HangarVehicle.py
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LOBBY_TYPE
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from items import vehicles
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ModelStates
from gui.prb_control.entities.listener import IGlobalListener
from constants import QUEUE_TYPE
from gui.prb_control.dispatcher import g_prbLoader
_GREEN_MARKER_ID = 2

class _SE20HangarVehicleAppearance(HangarVehicleAppearance):

    def __init__(self, spaceId, vEntity):
        super(_SE20HangarVehicleAppearance, self).__init__(spaceId, vEntity)
        self._turretYaw = 0
        self._gunPitch = 0
        self._turretYawLimits = (0, 0)
        self._gunPitchLimits = (0, 0)

    def setTurretYaw(self, value):
        self._turretYaw = value

    def setGunPitch(self, value):
        self._gunPitch = value

    def setTurretYawLimits(self, value):
        self._turretYawLimits = value

    def setGunPitchLimits(self, value):
        self._gunPitchLimits = value

    def getTurretYaw(self):
        return self._turretYaw

    def getGunPitch(self):
        return self._gunPitch

    def getTurretYawLimits(self):
        return self._turretYawLimits

    def getGunPitchLimits(self):
        return self._gunPitchLimits

    def _getActiveOutfit(self):
        return self.itemsFactory.createOutfit()


class SE20HangarVehicle(ClientSelectableCameraVehicle, IGlobalListener):
    _gameEventController = dependency.descriptor(IGameEventController)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(SE20HangarVehicle, self).__init__()
        self.setEnable(True)
        self.markerStyleId = _GREEN_MARKER_ID
        self.__isLazyVehicleUpdateDone = False
        self.__prbDispatcher = None
        self.__currentVehInfo = None
        return

    def onEnterWorld(self, prereqs):
        super(SE20HangarVehicle, self).onEnterWorld(prereqs)
        self.__prbDispatcher = g_prbLoader.getDispatcher()
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.addListener(self)
        self._hangarSpace.onSpaceCreate += self.onSpaceCreate
        self._gameEventController.onProgressChanged += self._updateSE20Vehicle
        self._gameEventController.onSelectedCommanderChanged += self._updateSE20Vehicle
        return

    def onLeaveWorld(self):
        self._hangarSpace.onSpaceCreate -= self.onSpaceCreate
        self._gameEventController.onProgressChanged -= self._updateSE20Vehicle
        self._gameEventController.onSelectedCommanderChanged -= self._updateSE20Vehicle
        if self.__prbDispatcher is not None:
            self.__prbDispatcher.removeListener(self)
        super(SE20HangarVehicle, self).onLeaveWorld()
        return

    def onPrbEntitySwitched(self):
        self._lazySE20VehicleUpdate()

    def onSpaceCreate(self):
        self._lazySE20VehicleUpdate()

    def setHighlight(self, _):
        pass

    def onMouseClick(self):
        pass

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        if self.vehicleType is not None and self.vehicleType != '':
            self.__currentVehInfo = None
            self.typeDescriptor = vehicles.VehicleDescr(typeName=self.vehicleType)
        else:
            selectedGeneral = self._gameEventController.getSelectedCommander()
            if selectedGeneral is not None:
                currentLevel = selectedGeneral.getCurrentProgressLevel()
                currentVehInfo = (selectedGeneral, currentLevel)
                if self.__currentVehInfo == currentVehInfo:
                    return
                self.__currentVehInfo = currentVehInfo
                for i, typeCompDescr in enumerate(selectedGeneral.getVehiclesByLevel(currentLevel), 1):
                    if i == self.vehicleIndex:
                        self.typeDescriptor = self.__getVehicleDescriptorByIntCD(typeCompDescr)
                        break

            else:
                self.typeDescriptor = typeDescriptor
        self._onVehicleDestroy()
        if not self.typeDescriptor:
            self.removeVehicle()
        super(SE20HangarVehicle, self).recreateVehicle(self.typeDescriptor, state, callback)
        return

    def _createAppearance(self):
        vehicleAppearance = _SE20HangarVehicleAppearance(self.spaceID, self)
        vehicleAppearance.setTurretYaw(self.vehicleTurretYaw)
        vehicleAppearance.setGunPitch(self.vehicleGunPitch)
        vehicleAppearance.setTurretYawLimits((self.yawLimitMin, self.yawLimitMax))
        vehicleAppearance.setGunPitchLimits((self.pitchLimitMin, self.pitchLimitMax))
        return vehicleAppearance

    def _updateSE20Vehicle(self):
        if self.vehicleIndex >= 0:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()

    def _lazySE20VehicleUpdate(self):
        if self.__prbDispatcher is None or self.__isLazyVehicleUpdateDone:
            return
        else:
            prbEntity = self.__prbDispatcher.getEntity()
            if prbEntity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES:
                self.__isLazyVehicleUpdateDone = True
                self._updateSE20Vehicle()
            return

    def _onVehicleLoaded(self):
        super(SE20HangarVehicle, self)._onVehicleLoaded()
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self,
         'lobbyType': LOBBY_TYPE.EVENT}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self,
         'lobbyType': LOBBY_TYPE.EVENT}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))
