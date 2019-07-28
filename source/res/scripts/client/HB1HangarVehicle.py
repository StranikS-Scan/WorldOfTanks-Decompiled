# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HB1HangarVehicle.py
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ModelStates
from items import vehicles

class _HB1HangarVehicleAppearance(HangarVehicleAppearance):

    def __init__(self, spaceId, vEntity):
        super(_HB1HangarVehicleAppearance, self).__init__(spaceId, vEntity)
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


class HB1HangarVehicle(ClientSelectableCameraVehicle):
    _gameEventController = dependency.descriptor(IGameEventController)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        ClientSelectableCameraVehicle.__init__(self)
        self.enable(True)

    def onEnterWorld(self, prereqs):
        super(HB1HangarVehicle, self).onEnterWorld(prereqs)
        self._hangarSpace.onSpaceCreate += self._updateHB1Vehicle
        self._gameEventController.onProgressChanged += self._updateHB1Vehicle
        self._gameEventController.onSelectedGeneralChanged += self._updateHB1Vehicle

    def onLeaveWorld(self):
        self._hangarSpace.onSpaceCreate -= self._updateHB1Vehicle
        self._gameEventController.onProgressChanged -= self._updateHB1Vehicle
        self._gameEventController.onSelectedGeneralChanged -= self._updateHB1Vehicle
        super(HB1HangarVehicle, self).onLeaveWorld()

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        self._onVehicleDestroy()
        self.typeDescriptor = typeDescriptor
        if self.vehicleType is not None and self.vehicleType != '':
            self.typeDescriptor = vehicles.VehicleDescr(typeName=self.vehicleType)
        else:
            selectedGeneral = self._gameEventController.getSelectedGeneral()
            if selectedGeneral is not None:
                currentLevel = selectedGeneral.getCurrentProgressLevel()
                for i, typeCompDescr in enumerate(selectedGeneral.getVehiclesByLevel(currentLevel), 1):
                    if i == self.vehicleIndex:
                        self.typeDescriptor = self.__getVehicleDescriptorByIntCD(typeCompDescr)
                        break

        if not self.typeDescriptor:
            self.removeVehicle()
        super(HB1HangarVehicle, self).recreateVehicle(self.typeDescriptor, state, callback)
        return

    def _createAppearance(self):
        vehicleAppearance = _HB1HangarVehicleAppearance(self.spaceID, self)
        vehicleAppearance.setTurretYaw(self.vehicleTurretYaw)
        vehicleAppearance.setGunPitch(self.vehicleGunPitch)
        vehicleAppearance.setTurretYawLimits((self.yawLimitMin, self.yawLimitMax))
        vehicleAppearance.setGunPitchLimits((self.pitchLimitMin, self.pitchLimitMax))
        return vehicleAppearance

    def _updateHB1Vehicle(self):
        if self.vehicleIndex >= 0:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()

    def _onVehicleLoaded(self):
        super(HB1HangarVehicle, self)._onVehicleLoaded()
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self,
         'lobbyType': 'event'}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self,
         'lobbyType': 'event'}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))
