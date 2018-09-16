# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from helpers import dependency
from skeletons.gui.game_control import IHeroTankController
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from gui.shared.utils.HangarSpace import g_hangarSpace

class HeroTank(ClientSelectableCameraVehicle):
    appearance = property(lambda self: self.__vAppearance)
    _heroTankCtrl = dependency.descriptor(IHeroTankController)

    def __init__(self):
        self.__heroTankName = ''
        ClientSelectableCameraVehicle.__init__(self)

    def onEnterWorld(self, prereqs):
        super(HeroTank, self).onEnterWorld(prereqs)
        g_hangarSpace.onHeroTankReady += self._updateHeroTank
        self._heroTankCtrl.onUpdated += self._updateHeroTank

    def onLeaveWorld(self):
        g_hangarSpace.onHeroTankReady -= self._updateHeroTank
        self._heroTankCtrl.onUpdated -= self._updateHeroTank
        super(HeroTank, self).onLeaveWorld()

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        if self.__heroTankName:
            self.typeDescriptor = vehicles.VehicleDescr(typeName=self.__heroTankName)
        super(HeroTank, self).recreateVehicle(typeDescriptor, state, callback)

    def _updateHeroTank(self):
        self.__heroTankName = self._heroTankCtrl.getRandomTank()
        if self.__heroTankName:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()

    def _onVehicleLoaded(self):
        super(HeroTank, self)._onVehicleLoaded()
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)
