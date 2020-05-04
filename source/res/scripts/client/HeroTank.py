# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import math
import random
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from CurrentVehicle import g_currentPreviewVehicle
from gui.Scaleform.daapi.view.lobby.lobby_vehicle_marker_view import LOBBY_TYPE
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from constants import IS_DEVELOPMENT

class _HeroTankAppearance(HangarVehicleAppearance):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, spaceId, vEntity, turretYaw=0.0, gunPitch=0.0):
        super(_HeroTankAppearance, self).__init__(spaceId, vEntity)
        self.__season = random.choice(SeasonType.COMMON_SEASONS)
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch

    def _getActiveOutfit(self):
        styleId = self._heroTankCtrl.getCurrentTankStyleId()
        if styleId:
            style = self._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            return style.getOutfit(self.__season)
        return self._c11nService.getEmptyOutfit()

    def _getTurretYaw(self):
        return self.__turretYaw

    def _getGunPitch(self):
        return self.__gunPitch


class HeroTank(ClientSelectableCameraVehicle):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        self._heroTankCD = None
        ClientSelectableCameraVehicle.__init__(self)
        return

    def onEnterWorld(self, prereqs):
        super(HeroTank, self).onEnterWorld(prereqs)
        self._hangarSpace.onHeroTankReady += self._updateHeroTank
        self._heroTankCtrl.onUpdated += self._updateHeroTank
        self._heroTankCtrl.onInteractive += self._updateInteractive
        g_currentPreviewVehicle.onSelected += self._updateHeroTank

    def onLeaveWorld(self):
        g_currentPreviewVehicle.onSelected -= self._updateHeroTank
        self._hangarSpace.onHeroTankReady -= self._updateHeroTank
        self._heroTankCtrl.onUpdated -= self._updateHeroTank
        self._heroTankCtrl.onInteractive -= self._updateInteractive
        super(HeroTank, self).onLeaveWorld()

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None):
        if self.__isInPreview():
            return
        if self._heroTankCD and not self.__isInPreview():
            self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self._heroTankCD)
        super(HeroTank, self).recreateVehicle(typeDescriptor, state, callback)

    def _createAppearance(self):
        vehicleTurretYaw = math.radians(self.vehicleTurretYaw)
        vehicleGunPitch = math.radians(self.vehicleGunPitch)
        return _HeroTankAppearance(self.spaceID, self, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch)

    def _updateHeroTank(self):
        if g_currentPreviewVehicle.item is not None:
            if g_currentPreviewVehicle.item.intCD == self._heroTankCD:
                return
        self._heroTankCD = self._heroTankCtrl.getRandomTankCD()
        if self._heroTankCD:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()
        return

    def _updateInteractive(self, interactive):
        if self.enabled != interactive:
            self.setEnable(interactive)
            self._onVehicleDestroy()
            self.recreateVehicle()

    def _onVehicleLoaded(self):
        super(HeroTank, self)._onVehicleLoaded()
        if self.enabled:
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self,
             'lobbyType': LOBBY_TYPE.REGULAR}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self,
         'lobbyType': LOBBY_TYPE.REGULAR}), scope=EVENT_BUS_SCOPE.LOBBY)

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))

    @staticmethod
    def __isInPreview():
        return g_currentPreviewVehicle.item and g_currentPreviewVehicle.isHeroTank


def debugReloadHero(heroName):
    if not IS_DEVELOPMENT:
        return
    for e in BigWorld.entities.values():
        if isinstance(e, HeroTank):
            heroDescriptor = vehicles.VehicleDescr(typeName=heroName)
            e.recreateVehicle(heroDescriptor)
            return
