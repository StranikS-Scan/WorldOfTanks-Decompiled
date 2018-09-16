# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import random
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from gui.shared.utils.HangarSpace import g_hangarSpace

class _HeroTankAppearance(HangarVehicleAppearance):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, spaceId, vEntity):
        super(_HeroTankAppearance, self).__init__(spaceId, vEntity)
        self.__season = random.choice(SeasonType.COMMON_SEASONS)

    def _getActiveOutfit(self):
        styleId = self._heroTankCtrl.getCurrentTankStyleId()
        if styleId:
            style = self._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            return style.getOutfit(self.__season)
        return self._c11nService.getEmptyOutfit()


class HeroTank(ClientSelectableCameraVehicle):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)

    def __init__(self):
        self.__heroTankCD = None
        ClientSelectableCameraVehicle.__init__(self)
        return

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
        if self.__heroTankCD:
            self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self.__heroTankCD)
        super(HeroTank, self).recreateVehicle(typeDescriptor, state, callback)

    def _createAppearance(self):
        return _HeroTankAppearance(self.spaceID, self)

    def _updateHeroTank(self):
        self.__heroTankCD = self._heroTankCtrl.getRandomTankCD()
        if self.__heroTankCD:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()

    def _onVehicleLoaded(self):
        super(HeroTank, self)._onVehicleLoaded()
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))
