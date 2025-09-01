# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SimulatedVehicle.py
import logging
from copy import copy
from functools import partial
import BigWorld
import Math
import GenericComponents
from cgf_network import C_INVALID_NETWORK_OBJECT_ID
from Event import Event
from VehicleEffects import DamageFromShotDecoder
from cgf_obsolete_script.script_game_object import ScriptGameObject
from common_tank_structure import VehicleAppearanceCacheInfo
from constants import DEFAULT_GUN_INSTALLATION_INDEX, VEHICLE_SIEGE_STATE, SPECIAL_VEHICLE_HEALTH, VEHICLE_HIT_EFFECT
from gui.battle_control import vehicle_getter
from gui.shared.items_parameters import isAutoShootGun
from helpers import dependency
from items import vehicles
from shared_utils.vehicle_utils import createWheelFilters
from skeletons.vehicle_appearance_cache import IAppearanceCache
from vehicle_systems.tankStructure import TankPartIndexes
from helpers_common import setEncodedSegmentContextData
_logger = logging.getLogger(__name__)
_UNSPOTTED_CONE_WIDTH_SCALE = 1
_UNSPOTTED_CONE_LENGTH_SCALE = 1

class _SimulatedVehicleSpeedProvider(object):
    __slots__ = ('__value',)

    @property
    def value(self):
        return self.__value

    def __init__(self):
        self.__value = Math.Vector4()

    def set(self, val):
        self.__value = val

    def reset(self):
        self.__value = Math.Vector4()


class VehicleBase(object):

    def __init__(self):
        self._wheelsScrollFilter = None
        self._wheelsSteeringFilter = None
        self._isCrewActive = False
        self._speedInfo = _SimulatedVehicleSpeedProvider()
        self.typeDescriptor = None
        self._isEnteringWorld = False
        self.wheelsState = 0
        self.burnoutLevel = 0
        self.isStrafing = False
        return

    def _initAdditionalFilters(self, typeDescriptor):
        self._wheelsScrollFilter, self._wheelsSteeringFilter = createWheelFilters(typeDescriptor)

    @property
    def isEnteringWorld(self):
        return self._isEnteringWorld

    @property
    def isWheeledTech(self):
        return 'wheeledVehicle' in self.typeDescriptor.type.tags

    @property
    def wheelsScrollSmoothed(self):
        if self._wheelsScrollFilter is not None:
            return [ scrollFilter.output(BigWorld.time()) for scrollFilter in self._wheelsScrollFilter ]
        else:
            return

    @property
    def wheelsScrollFilters(self):
        return self._wheelsScrollFilter

    @property
    def wheelsSteeringFilters(self):
        return self._wheelsSteeringFilter

    @property
    def wheelsSteeringSmoothed(self):
        if self._wheelsSteeringFilter is not None:
            return [ steeringFilter.output(BigWorld.time()) for steeringFilter in self._wheelsSteeringFilter ]
        else:
            return

    @property
    def speedInfo(self):
        return self._speedInfo

    @property
    def isCrewActive(self):
        return self._isCrewActive

    def getSpeed(self):
        return self._speedInfo.value[0]

    def isAlive(self):
        return True

    def isOnFire(self):
        return 'fire' in self.dynamicComponents

    def showCollisionEffect(self, hitPos, collisionEffectName='collisionVehicle', collisionNormal=None, isTracks=False, damageFactor=0, impulse=None, pcEnergy=None):
        pass

    def getOptionalDevices(self):
        return vehicle_getter.getOptionalDevices() if self.isPlayerVehicle else []


class SimulatedVehicle(BigWorld.Entity, VehicleBase, ScriptGameObject):
    __appearanceCache = dependency.descriptor(IAppearanceCache)
    isTurretDetached = property(lambda self: SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health) and self.__turretDetachmentConfirmed)
    isTurretMarkedForDetachment = property(lambda self: SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health))
    _CONE_SIZE = 2

    def __init__(self):
        BigWorld.Entity.__init__(self)
        ScriptGameObject.__init__(self, self.spaceID)
        VehicleBase.__init__(self)
        self.isStarted = False
        self.typeDescriptor = vehicles.VehicleDescr(self.publicInfo.compDescr)
        self._initAdditionalFilters(self.typeDescriptor)
        self.appearance = None
        self.__appearanceCacheID = self.id
        self.onAppearanceLoaded = Event()
        self.extras = {}
        turretYaw, gunPitch = self.simulationData_gunAngles
        self.__prereqs = None
        self.turretMatrix = Math.Matrix()
        self.turretMatrix.setRotateYPR((turretYaw, 0.0, 0.0))
        self.gunMatrix = Math.Matrix()
        self.gunMatrix.setRotateYPR((0.0, gunPitch, 0.0))
        self.__prevDamageStickers = frozenset()
        self.__brokenTrackVisible = []
        self.__turretDetachmentConfirmed = False
        self.__damageDecalEffectId = None
        return

    @property
    def turretYaw(self):
        return self.turretMatrix.yaw

    @property
    def gunPitch(self):
        return self.gunMatrix.pitch

    @property
    def health(self):
        return self.simulationData_health

    @property
    def maxHealth(self):
        return self.publicInfo.maxHealth

    @property
    def appearanceCacheID(self):
        return self.__appearanceCacheID

    def getSimulatedSteeringDataLink(self):

        def getWheelAngle(wheelAngle):
            return wheelAngle

        return [ partial(getWheelAngle, wheelAngle) for wheelAngle in self.simulationData_wheelsSteering ]

    def gunOriginMatrix(self, gunInstallationIndex=DEFAULT_GUN_INSTALLATION_INDEX, gunIndex=0):
        gun = self.typeDescriptor.gunInstallations[gunInstallationIndex].gun
        if not gun.multiGun or isAutoShootGun(gun):
            gunOriginMatrix = self.appearance.compoundModel.node('HP_gunJoint')
        else:
            gunNodeName = gun.multiGun[gunIndex].node
            gunOriginMatrix = self.appearance.compoundModel.node(gunNodeName)
        return gunOriginMatrix

    def gunFireMatrix(self, gunInstallationIndex=DEFAULT_GUN_INSTALLATION_INDEX, gunIndex=0):
        gun = self.typeDescriptor.gunInstallations[gunInstallationIndex].gun
        if not gun.multiGun or isAutoShootGun(gun):
            gunFireMatrix = self.appearance.compoundModel.node('HP_gunFire')
        else:
            gunFireHP = gun.multiGun[gunIndex].gunFire
            gunFireMatrix = self.appearance.compoundModel.node(gunFireHP)
        return gunFireMatrix

    def onEnterWorld(self, prereqs):
        self._isEnteringWorld = True
        self.__prereqs = prereqs
        self._isEnteringWorld = False
        self.typeDescriptor = vehicles.VehicleDescr(self.publicInfo.compDescr)
        self.__appearanceCacheID = self.id
        self.appearance = self._createAppearance(self.__appearanceCacheID, forceReloading=True)

    def onLeaveWorld(self):
        self.stopVisual()

    def stopVisual(self):
        if not self.isStarted:
            return
        else:
            self.__stopExtras()
            self.appearance.removeComponentByType(GenericComponents.HierarchyComponent)
            self.appearance.deactivate()
            self.appearance = None
            self.isStarted = False
            self._speedInfo.reset()
            return

    def addModel(self, model):
        super(SimulatedVehicle, self).addModel(model)
        highlighter = self.appearance.highlighter
        if highlighter.isOn:
            highlighter.highlight(False)
            highlighter.highlight(True)

    def delModel(self, model):
        highlighter = self.appearance.highlighter
        hlOn = highlighter.isOn
        hlSimpleEdge = highlighter.isSimpleEdge
        highlighter.removeHighlight()
        super(SimulatedVehicle, self).delModel(model)
        if hlOn:
            highlighter.highlight(True, hlSimpleEdge)

    def getMatinfo(self, partIndex, matKind):
        matInfo = None
        if partIndex > self.appearance.collisions.maxStaticPartIndex:
            matInfo = BigWorld.getMaterialInfo(self.appearance.collisions.getPartGameObject(partIndex), matKind)
        elif partIndex == TankPartIndexes.CHASSIS:
            matInfo = self.typeDescriptor.chassis.materials.get(matKind)
        elif partIndex == TankPartIndexes.HULL:
            matInfo = self.typeDescriptor.hull.materials.get(matKind)
        elif partIndex == TankPartIndexes.TURRET:
            matInfo = self.typeDescriptor.turret.materials.get(matKind)
        elif partIndex == TankPartIndexes.GUN:
            matInfo = self.typeDescriptor.gun.materials.get(matKind)
        return matInfo

    def showKillingSticker(self, shellCompactDescr, isArmorPierced, hitPoints):
        shellDescr = vehicles.getItemByCompactDescr(shellCompactDescr)
        targetSticker = 'armorPierced' if isArmorPierced else 'armorResisted'
        stickerID = vehicles.g_cache.shotEffects[shellDescr.effectsIndex]['targetStickers'][targetSticker]
        if stickerID is None:
            return
        else:
            for hitPoint in hitPoints:
                sticker = copy(hitPoint)
                sticker['segment'] = setEncodedSegmentContextData(sticker['segment'], stickerID)
                self.__decodeAndAddSticker(sticker)

            return

    def _createAppearance(self, entityID, forceReloading):
        if forceReloading:
            oldAppearance = self.__appearanceCache.removeAppearance(entityID)
            if oldAppearance is not None:
                oldAppearance.destroy()
        newInfo = VehicleAppearanceCacheInfo(self.typeDescriptor, self.health, self.isCrewActive, self.isTurretDetached, self.publicInfo.outfit, forceDynAttachmentLoading=True, entityGameObject=self.gameObject)
        appearance = self.__appearanceCache.getAppearance(entityID, newInfo, self.__onAppearanceReady)
        appearance.setUseEngStartControlIdle(True)
        return appearance

    def getDynAttachments(self):
        return self.simulationData_dynAttachmentsInfo

    def __onAppearanceReady(self, appearance):
        _logger.info('__onAppearanceReady(%d)', self.id)
        self.appearance = appearance
        self.__startVisual()
        self.onAppearanceLoaded(self.id)

    def __startVisual(self):
        if self.isStarted:
            return
        else:
            self.appearance = self.__appearanceCache.getAppearance(self.__appearanceCacheID, self.__prereqs)
            self.appearance.setIgnoreEngineStart()
            if not self.appearance.isConstructed:
                self.appearance.construct(isPlayer=False, resourceRefs=self.__prereqs)
            self.appearance.addCameraCollider()
            self.appearance.setVehicle(self)
            self.appearance.removeComponentByType(GenericComponents.HierarchyComponent)
            self.appearance.createComponent(GenericComponents.HierarchyComponent, self.entityGameObject)
            self.appearance.activate()
            self.appearance.changeEngineMode(self.simulationData_engineMode)
            if self.typeDescriptor.hasSiegeMode:
                if self.simulationData_siegeState != 0:
                    self.appearance.changeSiegeState(self.simulationData_siegeState)
                    self.appearance.onSiegeStateChanged(self.simulationData_siegeState, 0.0)
                else:
                    self.appearance.changeSiegeState(VEHICLE_SIEGE_STATE.DISABLED)
            self.appearance.onVehicleHealthChanged(showEffects=False)
            self.isStarted = True
            self.appearance.setupGunMatrixTargets(self)
            self.__showDamageStickers(self.simulationData_damageStickers)
            if self.isTurretMarkedForDetachment:
                self.__turretDetachmentConfirmed = True
                self.appearance.updateTurretVisibility()
            self.__prereqs = None
            return

    def __stopExtras(self):
        extraTypes = self.typeDescriptor.extras
        for index, data in self.extras.items():
            extraTypes[index].stop(data)

        if self.extras:
            _logger.warning('this code point should have never been reached')

    def getMaxComponentIndex(self, skipWheels=False):
        maxComponentIdx = TankPartIndexes.ALL[-1]
        wheelsConfig = self.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
        if wheelsConfig and not skipWheels:
            maxComponentIdx = maxComponentIdx + wheelsConfig.getNonTrackWheelsCount()
        return maxComponentIdx

    def __calcMaxHitEffectAndHasPiercedShot(self, shotPoints):
        maxHitEffectCode = VEHICLE_HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE
        for shotPoint in shotPoints:
            if shotPoint.hitEffectCode > maxHitEffectCode:
                maxHitEffectCode = shotPoint.hitEffectCode

        return (maxHitEffectCode, DamageFromShotDecoder.hasDamaged(maxHitEffectCode))

    def __showDamageStickers(self, stickers):
        for sticker in stickers:
            self.__decodeAndAddSticker(sticker)

    def __decodeAndAddSticker(self, hitPoint):
        networkID = hitPoint['networkID']
        if networkID != C_INVALID_NETWORK_OBJECT_ID:
            return
        else:
            parsedHitPoint = DamageFromShotDecoder.parseHitPoint(hitPoint, self.appearance.collisions)
            if parsedHitPoint is None:
                return
            componentIndex, stickerID, start, end = parsedHitPoint
            if componentIndex <= TankPartIndexes.CHASSIS or None in (start, end, stickerID):
                return
            code = DamageFromShotDecoder.encodeHitPoint(hitPoint)
            self.appearance.addDamageSticker(code, componentIndex, stickerID, start, end)
            return

    def updateBrokenTracks(self, trackStates):
        if not self.__brokenTrackVisible:
            self.__brokenTrackVisible = [False] * len(trackStates)
        for index, trackState in enumerate(trackStates):
            if trackState['isBroken'] and not self.__brokenTrackVisible[index]:
                self.__brokenTrackVisible[index] = True
                self.appearance.addSimulatedCrashedTrack(index, self.simulationData_tracksInAir, trackState['hitPoint'])
