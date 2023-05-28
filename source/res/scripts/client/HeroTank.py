# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import math
import random
from typing import TYPE_CHECKING
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController, ILimitedUIController
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from constants import IS_DEVELOPMENT
if TYPE_CHECKING:
    from vehicle_outfit.outfit import Outfit as TOutfit
    from items.vehicles import VehicleDescrType

class _HeroTankAppearance(HangarVehicleAppearance):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, spaceId, vEntity, turretYaw=0.0, gunPitch=0.0):
        super(_HeroTankAppearance, self).__init__(spaceId, vEntity)
        self.__season = random.choice(SeasonType.COMMON_SEASONS)
        self.__turretYaw = turretYaw
        self.__gunPitch = gunPitch
        self.__typeDescriptor = vEntity.typeDescriptor

    def _getActiveOutfit(self, vDesc):
        styleId = self._heroTankCtrl.getCurrentTankStyleId()
        vehicleCD = vDesc.makeCompactDescr()
        if styleId:
            style = self._c11nService.getItemByID(GUI_ITEM_TYPE.STYLE, styleId)
            return style.getOutfit(self.__season, vehicleCD=vehicleCD)
        return self._c11nService.getEmptyOutfitWithNationalEmblems(vehicleCD)

    def _getTurretYaw(self):
        return self.__turretYaw

    def _getGunPitch(self):
        return self.__gunPitch


class HeroTank(ClientSelectableCameraVehicle):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __limitedUIController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        self.__heroTankCD = None
        self.__isHidden = False
        ClientSelectableCameraVehicle.__init__(self)
        return

    def onEnterWorld(self, prereqs):
        super(HeroTank, self).onEnterWorld(prereqs)
        self._hangarSpace.onHeroTankReady += self._updateHeroTank
        self._heroTankCtrl.onUpdated += self._updateHeroTank
        self._heroTankCtrl.onInteractive += self._updateInteractive
        self._heroTankCtrl.onHidden += self.__onHidden
        self.__limitedUIController.startObserve(LuiRules.HERO_TANK, self.__updateHeroTankVisibility)

    def onLeaveWorld(self):
        self._heroTankCtrl.onHidden -= self.__onHidden
        self._hangarSpace.onHeroTankReady -= self._updateHeroTank
        self._heroTankCtrl.onUpdated -= self._updateHeroTank
        self._heroTankCtrl.onInteractive -= self._updateInteractive
        self.__limitedUIController.stopObserve(LuiRules.HERO_TANK, self.__updateHeroTankVisibility)
        super(HeroTank, self).onLeaveWorld()

    def onMouseClick(self):
        ClientSelectableCameraObject.switchCamera(self, 'HeroTank')
        return self.state != CameraMovementStates.FROM_OBJECT

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            self.removeVehicle()
        self.__heroTankCD = None
        return

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None, outfit=None):
        if self.__isInPreview() or self.__isHidden:
            return
        if self.__heroTankCD and not self.__isInPreview():
            self.typeDescriptor = HeroTank.__getVehicleDescriptorByIntCD(self.__heroTankCD)
        super(HeroTank, self).recreateVehicle(typeDescriptor, state, callback, outfit)

    def _createAppearance(self):
        vehicleTurretYaw = math.radians(self.vehicleTurretYaw)
        vehicleGunPitch = math.radians(self.vehicleGunPitch)
        return _HeroTankAppearance(self.spaceID, self, turretYaw=vehicleTurretYaw, gunPitch=vehicleGunPitch)

    def _updateHeroTank(self):
        if g_currentPreviewVehicle.item is not None:
            if g_currentPreviewVehicle.item.intCD == self.__heroTankCD:
                return
        allowShowHeroTank = self.__limitedUIController.isRuleCompleted(LuiRules.HERO_TANK)
        heroTankCD = self._heroTankCtrl.getRandomTankCD()
        if allowShowHeroTank and heroTankCD:
            self.__heroTankCD = heroTankCD
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
            g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_LOADED, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__heroTankCD is None:
            self.removeModelFromScene()
        return

    def _onVehicleDestroy(self):
        g_eventBus.handleEvent(events.HangarVehicleEvent(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateHeroTankVisibility(self, *_):
        self._updateHeroTank()

    @staticmethod
    def __getVehicleDescriptorByIntCD(vehicleIntCD):
        _, nationId, itemId = vehicles.parseIntCompactDescr(vehicleIntCD)
        return vehicles.VehicleDescr(typeID=(nationId, itemId))

    @staticmethod
    def __isInPreview():
        return g_currentPreviewVehicle.item and g_currentPreviewVehicle.isHeroTank

    def __onHidden(self, isHidden):
        if self.__isHidden != isHidden:
            self.__isHidden = isHidden
            if self.__isHidden and not self.__isInPreview():
                self.removeVehicle()
            elif not self.__isHidden and self._heroTankCtrl.getRandomTankCD():
                self.recreateVehicle()


def debugReloadHero(heroName):
    if not IS_DEVELOPMENT:
        return
    for e in BigWorld.entities.values():
        if isinstance(e, HeroTank):
            heroDescriptor = vehicles.VehicleDescr(typeName=heroName)
            e.recreateVehicle(heroDescriptor)
            return
