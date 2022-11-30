# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/HeroTank.py
import math
import random
from typing import TYPE_CHECKING
from functools import partial
import ResMgr
import BigWorld
from ClientSelectableCameraVehicle import ClientSelectableCameraVehicle
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle
from gui.hangar_vehicle_appearance import HangarVehicleAppearance
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates
from gui.shared import events, EVENT_BUS_SCOPE, g_eventBus
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, newFakeModel
from items.components.c11n_constants import SeasonType
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IHeroTankController
from skeletons.gui.shared.utils import IHangarSpace
from vehicle_systems.tankStructure import ModelStates
from items import vehicles
from helpers.EffectsList import EffectsListPlayer, effectsFromSection
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
    _HERO_PURCHASED = 'on_purchased'
    _HERO_SWITCH = 'on_switch'

    def __init__(self):
        self.__heroTankCD = None
        self.__effects = {}
        self.__fakeEffectModel = None
        ClientSelectableCameraVehicle.__init__(self)
        return

    def onEnterWorld(self, prereqs):
        super(HeroTank, self).onEnterWorld(prereqs)
        self._hangarSpace.onHeroTankReady += self._updateHeroTank
        self._heroTankCtrl.onUpdated += self._updateHeroTank
        self._heroTankCtrl.onInteractive += self._updateInteractive
        self._heroTankCtrl.onHeroTankChanged += self._drawTankSwitchedEffect
        self._heroTankCtrl.onHeroTankBought += self._drawTankBoughtEffect
        self._heroTankCtrl.onVisibilityChanged += self._onVisibilityChanged
        g_currentPreviewVehicle.onSelected += self._updateHeroTank

    def prerequisites(self):
        self.__readHeroEffects()
        return super(HeroTank, self).prerequisites()

    def onLeaveWorld(self):
        self._hangarSpace.onHeroTankReady -= self._updateHeroTank
        self._heroTankCtrl.onUpdated -= self._updateHeroTank
        self._heroTankCtrl.onInteractive -= self._updateInteractive
        self._heroTankCtrl.onHeroTankChanged -= self._drawTankSwitchedEffect
        self._heroTankCtrl.onHeroTankBought -= self._drawTankBoughtEffect
        self._heroTankCtrl.onVisibilityChanged -= self._onVisibilityChanged
        g_currentPreviewVehicle.onSelected -= self._updateHeroTank
        for effect in self.__effects.values():
            if effect.isStarted:
                effect.stop()

        self.__effects = None
        if self.__fakeEffectModel is not None:
            BigWorld.delModel(self.__fakeEffectModel)
        self.__fakeEffectModel = None
        super(HeroTank, self).onLeaveWorld()
        return

    def onMouseClick(self):
        ClientSelectableCameraObject.switchCamera(self, 'HeroTank')
        return self.state != CameraMovementStates.FROM_OBJECT

    def removeModelFromScene(self):
        if self.isVehicleLoaded:
            self._onVehicleDestroy()
            BigWorld.destroyEntity(self.id)

    def setEnable(self, enabled):
        super(HeroTank, self).setEnable(enabled)
        self.__notifyAboutMarkerUpdateRequired()

    def recreateVehicle(self, typeDescriptor=None, state=ModelStates.UNDAMAGED, callback=None, outfit=None):
        if self.__isInPreview():
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
        self.__heroTankCD = self._heroTankCtrl.getRandomTankCD()
        if self.__heroTankCD:
            self.recreateVehicle()
        else:
            self.removeModelFromScene()
        return

    def _updateInteractive(self, interactive):
        if self.enabled != interactive:
            self.setEnable(interactive)
            self._onVehicleDestroy()
            self.recreateVehicle()

    def _drawTankSwitchedEffect(self):
        self.__playEffect(self._HERO_SWITCH)
        self._heroTankCtrl.setEffectPlayedTime()

    def _drawTankBoughtEffect(self):
        self.__playEffect(self._HERO_PURCHASED)

    def _onVehicleLoaded(self):
        super(HeroTank, self)._onVehicleLoaded()
        self.__notifyAboutLoadingDone()

    def _onVehicleDestroy(self):
        self.__dispatch(events.HangarVehicleEvent.ON_HERO_TANK_DESTROY)

    def _onVisibilityChanged(self, visible):
        if visible:
            self.recreateVehicle(callback=partial(self.setEnable, True))
        else:
            self.setEnable(False)
            self.removeVehicle()
            self._onVehicleDestroy()

    def __notifyAboutLoadingDone(self):
        if self.enabled:
            self.__dispatch(events.HangarVehicleEvent.ON_HERO_TANK_LOADED)

    def __notifyAboutMarkerUpdateRequired(self):
        if self.enabled:
            self.__dispatch(events.HangarVehicleEvent.ON_HERO_TANK_LABEL_UPDATE_REQUIRED)

    def __dispatch(self, eventType):
        g_eventBus.handleEvent(events.HangarVehicleEvent(eventType, ctx={'entity': self}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __readHeroEffects(self):
        if not self.effectsXmlPath:
            return
        else:
            rootSection = ResMgr.openSection(self.effectsXmlPath)
            if rootSection is None:
                return
            effectsSection = rootSection['effects']
            if effectsSection is None:
                return
            for effectValues in effectsSection.values():
                name = effectValues.name
                effect = effectsFromSection(effectValues)
                player = EffectsListPlayer(effect.effectsList, effect.keyPoints)
                self.__effects[name] = player

            return

    def __playEffect(self, effectName):
        effect = self.__effects.get(effectName, None)
        if effect is None:
            return
        else:
            if self.__fakeEffectModel is None:
                self.__fakeEffectModel = newFakeModel()
                self.__fakeEffectModel.position = self.position
                BigWorld.addModel(self.__fakeEffectModel)
            if effect.isStarted:
                effect.stop()
            effect.play(self.__fakeEffectModel)
            return

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
