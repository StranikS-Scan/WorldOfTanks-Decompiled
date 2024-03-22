# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SimulatedVehicle.py
import logging
import BigWorld
import Math
from functools import partial
from Event import Event
from VehicleEffects import DamageFromShotDecoder
from cgf_obsolete_script.script_game_object import ScriptGameObject
from constants import VEHICLE_SIEGE_STATE, SPECIAL_VEHICLE_HEALTH, VEHICLE_HIT_EFFECT
from gui.battle_control import vehicle_getter
from helpers import dependency
from items import vehicles
from shared_utils.vehicle_utils import createWheelFilters
from skeletons.vehicle_appearance_cache import IAppearanceCache
from vehicle_systems.appearance_cache import VehicleAppearanceCacheInfo
from vehicle_systems.tankStructure import TankPartIndexes
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

    def getSpeed(self):
        return self._speedInfo.value[0]

    @property
    def isCrewActive(self):
        return self._isCrewActive

    def isAlive(self):
        return True

    def isOnFire(self):
        return 'fire' in self.dynamicComponents

    def showCollisionEffect(self, hitPos, collisionEffectName='collisionVehicle', collisionNormal=None, isTracks=False, damageFactor=0, impulse=None, pcEnergy=None):
        pass

    def getMatinfo(self, parIndex, matKind):
        matInfo = None
        if parIndex == TankPartIndexes.CHASSIS:
            matInfo = self.typeDescriptor.chassis.materials.get(matKind)
        elif parIndex == TankPartIndexes.HULL:
            matInfo = self.typeDescriptor.hull.materials.get(matKind)
        elif parIndex == TankPartIndexes.TURRET:
            matInfo = self.typeDescriptor.turret.materials.get(matKind)
        elif parIndex == TankPartIndexes.GUN:
            matInfo = self.typeDescriptor.gun.materials.get(matKind)
        return matInfo

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

    @property
    def gunFireMatrix(self, gunIndex=0):
        multiGun = self.typeDescriptor.turret.multiGun
        if self.typeDescriptor.isDualgunVehicle and multiGun is not None:
            gunFireHP = multiGun[gunIndex].gunFire
            gunMatrix = self.appearance.compoundModel.node(gunFireHP)
        else:
            gunMatrix = self.appearance.compoundModel.node('HP_gunFire')
        return gunMatrix

    @property
    def gunFirePosition(self, gunIndex=0):
        return Math.Matrix(self.gunFireMatrix).translation

    @property
    def gunJointMatrix(self):
        return self.appearance.compoundModel.node('HP_gunJoint')

    @property
    def gunJointPosition(self):
        return Math.Matrix(self.gunJointMatrix).translation

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

    def _createAppearance(self, entityID, forceReloading):
        if forceReloading:
            oldAppearance = self.__appearanceCache.removeAppearance(entityID)
            if oldAppearance is not None:
                oldAppearance.destroy()
        newInfo = VehicleAppearanceCacheInfo(self.typeDescriptor, self.health, self.isCrewActive, self.isTurretDetached, self.publicInfo.outfit)
        appearance = self.__appearanceCache.getAppearance(entityID, newInfo, self.__onAppearanceReady)
        appearance.setUseEngStartControlIdle(True)
        return appearance

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

    def __applyDamageSticker(self):
        if self.isStarted:
            prev = self.__prevDamageStickers
            curr = frozenset(self.simulationData_damageStickers)
            self.__prevDamageStickers = curr
            for sticker in prev.difference(curr):
                self.appearance.removeDamageSticker(sticker)

            maxComponentIdx = self.getMaxComponentIndex()
            for sticker in curr.difference(prev):
                self.appearance.addDamageSticker(sticker, *DamageFromShotDecoder.decodeSegment(sticker, self.appearance.collisions, maxComponentIdx))

    def getMaxComponentIndex(self, skipWheels=False):
        maxComponentIdx = TankPartIndexes.ALL[-1]
        wheelsConfig = self.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
        if wheelsConfig and not skipWheels:
            maxComponentIdx = maxComponentIdx + wheelsConfig.getNonTrackWheelsCount()
        return maxComponentIdx

    def decodeHitPoints(self, points):
        maxComponentIdx = self.getMaxComponentIndex(skipWheels=True)
        return DamageFromShotDecoder.decodeHitPoints(points, self.appearance.collisions, maxComponentIdx, self.typeDescriptor)

    def __calcMaxHitEffectAndHasPiercedShot(self, shotPoints):
        maxHitEffectCode = VEHICLE_HIT_EFFECT.ARMOR_PIERCED_NO_DAMAGE
        for shotPoint in shotPoints:
            if shotPoint.hitEffectCode > maxHitEffectCode:
                maxHitEffectCode = shotPoint.hitEffectCode

        return (maxHitEffectCode, DamageFromShotDecoder.hasDamaged(maxHitEffectCode))

    def __getComponentInfo(self, projData):
        origin = projData['origin']
        points = projData['segments']
        longestDistSquared = lastHitPoint = None
        decodedPoints = self.decodeHitPoints(points)
        _, hasPiercedHit = self.__calcMaxHitEffectAndHasPiercedShot(decodedPoints)
        if not decodedPoints and not hasPiercedHit:
            return (False, None, None)
        else:
            compoundModel = self.appearance.compoundModel
            for hitPoint in decodedPoints:
                compoundMatrix = Math.Matrix(compoundModel.node(hitPoint.componentName))
                worldHitPoint = compoundMatrix.applyPoint(hitPoint.matrix.translation)
                distSquared = (worldHitPoint - origin).lengthSquared
                if lastHitPoint is None or distSquared > longestDistSquared:
                    longestDistSquared = distSquared
                    lastHitPoint = hitPoint

            componentName = lastHitPoint.componentName
            compoundMatrix = Math.Matrix(compoundModel.node(componentName))
            return (True, componentName, compoundMatrix)

    def __showDamageStickers(self, segments):
        maxComponentIdx = self.getMaxComponentIndex()
        for sticker in segments:
            self.__decodeAndAddSticker(sticker, maxComponentIdx)

    def showKillingSticker(self, shellCompactDescr, hasProjectilePierced, segments):
        if not segments:
            return
        else:
            shellDescr = vehicles.getItemByCompactDescr(shellCompactDescr)
            hasProjectilePierced = 'armorPierced' if hasProjectilePierced else 'armorResisted'
            shellStickers = vehicles.g_cache.shotEffects[shellDescr.effectsIndex]['targetStickers']
            stickerID = shellStickers[hasProjectilePierced]
            if stickerID is not None:
                maxComponentID = self.getMaxComponentIndex()
                for segment in segments:
                    sticker = segment | stickerID
                    self.__decodeAndAddSticker(sticker, maxComponentID)

            return

    def __decodeAndAddSticker(self, sticker, componentID):
        componentName, value, start, end = DamageFromShotDecoder.decodeSegment(sticker, self.appearance.collisions, componentID, self.typeDescriptor)
        if componentName == TankPartIndexes.CHASSIS or None in (start, end, value):
            return
        else:
            self.appearance.addDamageSticker(sticker, componentName, value, start, end)
            return

    def updateBrokenTracks(self, trackState):
        if not self.__brokenTrackVisible:
            self.__brokenTrackVisible = [False] * len(trackState)
        for index, isTrackBroken in enumerate(trackState):
            if isTrackBroken and self.__brokenTrackVisible[index] != isTrackBroken:
                self.__brokenTrackVisible[index] = isTrackBroken
                self.appearance.addSimulatedCrashedTrack(index, self.simulationData_tracksInAir)
