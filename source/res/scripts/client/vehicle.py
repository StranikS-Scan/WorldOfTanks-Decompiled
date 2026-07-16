# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/Vehicle.py
from __future__ import absolute_import, division
import functools
import logging
import math
import random
import typing
import weakref
from collections import namedtuple
from typing import List
import BigWorld
import CGF
import GenericComponents
import InstantStatuses
import Math
import Statuses
import WoT
import AreaDestructibles
import BattleReplay
import DestructiblesCache
import TriggersManager
import constants
import physics_shared
from CGF import TransformComponent
from account_helpers.settings_core.settings_constants import GAME
from aih_constants import ShakeReason
from cgf_components.arena_camera_manager import ArenaCameraSystem
from cgf_modules import game_events
from cgf_modules.game_events import ArmorHitPlacement
from cgf_script.entity_dyn_components import BWEntitiyComponentTracker
from constants import VEHICLE_HIT_EFFECT, VEHICLE_SIEGE_STATE, ATTACK_REASON_INDICES, ATTACK_REASON, SPT_MATKIND
from helpers.collisions import SegmentCollisionResultExt
from vehicle_systems.components.vehicle_assembly_manager import GunInfoAssembler
from common_tank_structure import VehicleAppearanceCacheInfo
from DamageComponents import DamageZoneType
from gui.battle_control import vehicle_getter, avatar_getter
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID as _FET, VEHICLE_VIEW_STATE
from gui.shared.utils.decorators import ReprInjector
from gun_rotation_shared import decodeGunAngles
from helpers import dependency
from helpers.EffectMaterialCalculation import calcSurfaceMaterialNearPoint
from helpers.EffectsList import SoundStartParam
from items import vehicles
from items.components.component_constants import DEFAULT_TRACK_HIT_VECTOR, DEFAULT_GUN_BURST
from material_kinds import EFFECT_MATERIAL_INDEXES_BY_NAMES, EFFECT_MATERIALS
from PlayerEvents import g_playerEvents
from shared_utils import nextTick
from shared_utils.vehicle_utils import createWheelFilters, getMatinfo
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.vehicle_appearance_cache import IAppearanceCache
from soft_exception import SoftException
from TriggersManager import TRIGGER_TYPE
from VehicleEffects import DamageFromShotDecoder
from helpers.StubCollisionComponent import StubCollisionComponent
from vehicles.entities.vehicle_events import createVehicleEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleMechanicComponent, getVehicleDescrMechanicParams
from vehicle_systems.components.shot_damage_components import ShotDamageComponent
from vehicle_systems.components import vehicle_variable_storage as var_storage
from vehicle_systems.entity_components.battle_abilities_component import BattleAbilitiesComponent
from vehicle_systems.components.vehicle_pickup_component import VehiclePickupComponent
from vehicle_systems.tankStructure import TankPartNames, TankPartIndexes, TankSoundObjectsIndexes
from vehicle_systems.instant_status_helpers import invokeInstantStatusForVehicle
from visual_script.misc import ASPECT
if typing.TYPE_CHECKING:
    import OwnVehicle
    from vehicles.entities.vehicle_events import IVehicleEvents
    from vehicle_systems.CompoundAppearance import CompoundAppearance
_logger = logging.getLogger(__name__)
LOW_ENERGY_COLLISION_D = 0.3
HIGH_ENERGY_COLLISION_D = 0.6
_g_respawnQueue = {}

class _Vector4Provider(object):
    __slots__ = ('_v',)

    @property
    def value(self):
        return self._v

    def __int__(self):
        self._v = Math.Vector4(0.0, 0.0, 0.0, 0.0)


class _VehicleSpeedProvider(object):
    __slots__ = ('__value',)

    @property
    def value(self):
        return self.__value.value

    def __init__(self):
        self.__value = Math.Vector4Basic()

    def set(self, val):
        self.__value = val

    def reset(self):
        self.__value = Math.Vector4Basic()


StunInfo = namedtuple('StunInfo', ('startTime',
 'endTime',
 'duration',
 'totalTime'))
DebuffInfo = namedtuple('DebuffInfo', ('duration', 'animated'))
VEHICLE_COMPONENTS = {BattleAbilitiesComponent}

def _logVehicle(logger, msg, vID, *args, **kwargs):
    logger(('[%d] ' + msg), vID, *args, **kwargs)


@ReprInjector.simple('id')
class Vehicle(BigWorld.Entity, BWEntitiyComponentTracker, BattleAbilitiesComponent):
    guiSessionProvider = dependency.descriptor(IBattleSessionProvider)
    lobbyContext = dependency.descriptor(ILobbyContext)
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    __appearanceCache = dependency.descriptor(IAppearanceCache)
    __settingsCore = dependency.descriptor(ISettingsCore)

    @property
    def isEnteringWorld(self):
        return self.__isEnteringWorld

    @property
    def isTurretDetached(self):
        return constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health) and self.__turretDetachmentConfirmed

    @property
    def isTurretMarkedForDetachment(self):
        return constants.SPECIAL_VEHICLE_HEALTH.IS_TURRET_DETACHED(self.health)

    @property
    def isTurretDetachmentConfirmationNeeded(self):
        return not self.__turretDetachmentConfirmed

    @property
    def hasMovingFlags(self):
        return self.engineMode is not None and self.engineMode[1] & 3

    @property
    def activeGunIndexes(self):
        return self.twinGunIndexes or (self.dualGunIndex,)

    @property
    def dualGunIndex(self):
        return self.__dualGunIndex

    @property
    def twinGunIndexes(self):
        ctrl = self.getVehicleMechanicComponent(VehicleMechanic.TWIN_GUN)
        return ctrl.getActiveGunIndexes() if ctrl is not None else ()

    @property
    def speedInfo(self):
        return self.__speedInfo

    @property
    def isWheeledTech(self):
        return self.typeDescriptor.type.isWheeledVehicle

    @property
    def hasSpeedometer(self):
        return self.typeDescriptor.type.hasSpeedometer

    @property
    def isScout(self):
        return 'scout' in self.typeDescriptor.type.tags

    @property
    def isTrackWithinTrack(self):
        return self.typeDescriptor is not None and self.typeDescriptor.isTrackWithinTrack

    @property
    def isMainMultiGun(self):
        return self.typeDescriptor is not None and self.typeDescriptor.gun.multiGun

    @property
    def wheelsScrollSmoothed(self):
        time = BigWorld.time()
        if self.__wheelsScrollFilter is not None:
            return [ scrollFilter.output(time) for scrollFilter in self.__wheelsScrollFilter ]
        else:
            return

    @property
    def wheelsScrollFilters(self):
        return self.__wheelsScrollFilter

    @property
    def wheelsSteeringSmoothed(self):
        time = BigWorld.time()
        if self.__wheelsSteeringFilter is not None:
            return [ steeringFilter.output(time) for steeringFilter in self.__wheelsSteeringFilter ]
        else:
            return []

    @property
    def wheelsSteeringFilters(self):
        return self.__wheelsSteeringFilter

    @property
    def maxHealth(self):
        return self.publicInfo.maxHealth

    @property
    def typeCompDescr(self):
        return self.typeDescriptor and self.typeDescriptor.makeCompactDescr()

    @property
    def battleModifiers(self):
        return self.guiSessionProvider.arenaVisitor.getArenaModifiers()

    @property
    def cameraTargetMatrix(self):
        self.set_postmortemViewPointName()
        return self.__cameraTargetMatrix

    @property
    def isPostmortemViewPointDefined(self):
        return self.postmortemViewPointName is not None and self.postmortemViewPointName != ''

    @property
    def isPlayerTeam(self):
        return self.guiSessionProvider.getCtx().isAlly(self.id)

    @property
    def events(self):
        return self.__events

    def getBounds(self, partIdx):
        if self.appearance is not None:
            if self.appearance.collisions:
                return self.appearance.collisions.getExtendedBoundingBox(partIdx)
        return (Math.Vector3(0.0, 0.0, 0.0), Math.Vector3(0.0, 0.0, 0.0), 0)

    def getSpeed(self):
        return self.__speedInfo.value[0]

    def getMasterVehID(self):
        return self.masterVehID

    def __init__(self):
        self.__logVehicle(_logger.debug, '__init__')
        self.__events = createVehicleEvents(self)
        for comp in VEHICLE_COMPONENTS:
            comp.__init__(self)

        self.proxy = weakref.proxy(self)
        self.extras = {}
        self.extrasHitPoint = {}
        self.typeDescriptor = None
        self.appearance = None
        self.isPlayerVehicle = False
        self.isStarted = False
        self.__isEnteringWorld = False
        self.__turretDetachmentConfirmed = False
        self.__speedInfo = _VehicleSpeedProvider()
        self.respawnCompactDescr = None
        self.respawnOutfitCompactDescr = None
        self.__waitingForAppearanceReload = False
        self.__cachedStunInfo = StunInfo(0.0, 0.0, 0.0, 0.0)
        self.__burnoutStarted = False
        self.__handbrakeFired = False
        self.__wheelsScrollFilter = None
        self.__wheelsSteeringFilter = None
        self.isUpgrading = False
        self.isLeavingWorldForRespawn = False
        self.isForceReloading = False
        self.__dualGunIndex = None
        self.refreshNationalVoice()
        self.__prevHealth = None
        self.__quickShellChangerIsActive = False
        self.__isInDebuff = False
        self.__cameraTargetMatrix = Math.WGAdaptiveMatrixProvider()
        self.set_postmortemViewPointName()
        g_playerEvents.onVehicleEntityCreated(self)
        return

    def reload(self):
        self.__logVehicle(_logger.debug, 'reload')
        vehicles.reload()
        Vehicle.respawnVehicle(self.id, self.publicInfo.compDescr)

    def __checkDelayedRespawn(self):
        global _g_respawnQueue
        pair = _g_respawnQueue.pop(self.id, None)
        if pair is not None:
            self.__logVehicle(_logger.info, 'found delayed respawn request')
            self.respawnCompactDescr = pair[0]
            self.respawnOutfitCompactDescr = pair[1]
            return True
        else:
            return False

    def onEnterWorld(self, _=None):
        self.__logVehicle(_logger.debug, 'onEnterWorld')
        isDelayedRespawn = self.__checkDelayedRespawn()
        if self.respawnOutfitCompactDescr is not None:
            outfitDescr = self.respawnOutfitCompactDescr
            self.respawnOutfitCompactDescr = None
        else:
            outfitDescr = self.publicInfo.outfit
        oldTypeDescriptor = self.typeDescriptor
        self.typeDescriptor = self.getDescr(None if isDelayedRespawn else self.respawnCompactDescr)
        forceReloading = self.respawnCompactDescr is not None
        queue = CGF.CommandQueue(self.spaceID)
        queue.setGameObjectName(self.entityGameObject, 'Vehicle: {}, id: {}'.format(self.typeDescriptor.name, self.id))
        var_storage.createForRoot(self, queue)
        if 'battle_royale' in self.typeDescriptor.type.tags:
            from InBattleUpgrades import onBattleRoyalePrerequisites
            forceReloading = onBattleRoyalePrerequisites(self, oldTypeDescriptor, forceReloading)
        strCD = self.typeDescriptor.makeCompactDescr()
        newInfo = VehicleAppearanceCacheInfo(self.typeDescriptor, self.health, self.isCrewActive, self.isTurretDetached, outfitDescr, forceDynAttachmentLoading=False, entityGameObject=self.entityGameObject, respawnID=self.publicInfo['respawnID'])
        ctrl = self.guiSessionProvider.dynamic.appearanceCache
        if ctrl is not None:
            appearance = ctrl.getAppearance(self.id, newInfo, None, strCD, False)
            if appearance:
                forceReloading = forceReloading or appearance.isAlive != self.isAlive()
            if forceReloading:
                oldStrCD = oldTypeDescriptor.makeCompactDescr() if oldTypeDescriptor is not None else None
                appearance = ctrl.reloadAppearance(self.id, newInfo, self.__onAppearanceReady, strCD, oldStrCD)
                if appearance is not None:
                    self.appearance = appearance
                else:
                    self.__waitingForAppearanceReload = True
            else:
                self.appearance = ctrl.getAppearance(self.id, newInfo, self.__onAppearanceReady, strCD)
        else:
            self.__logVehicle(_logger.error, 'Failed to load vehicle appearance. No AppearanceCache controller. vInfo=%s; strCD=%r', newInfo._asdict(), strCD)
        self.respawnCompactDescr = None
        self.set_vehPostProgression(self.vehPostProgression)
        self.set_customRoleSlotTypeId(self.customRoleSlotTypeId)
        return

    def getDescr(self, respawnCompactDescr):
        if respawnCompactDescr is not None:
            self.isCrewActive = True
            descr = vehicles.VehicleDescr(respawnCompactDescr, extData=self)
            self.__turretDetachmentConfirmed = False
            if 'battle_royale' not in descr.type.tags and not self.enableExternalRespawn:
                self.health = self.publicInfo.maxHealth
                self.__prevHealth = self.publicInfo.maxHealth
            return descr
        else:
            return vehicles.VehicleDescr(compactDescr=_stripVehCompDescrIfRoaming(self.publicInfo.compDescr), extData=self)

    @staticmethod
    def deferredRespawnVehicle(vehicleObj):
        if hasattr(vehicleObj, 'respawnCompactDescr') and vehicleObj.respawnCompactDescr:
            _logVehicle(_logger.debug, 'respawn vehCD is still valid, calling respawnVehicle again', vehicleObj.id)
            vehicleObj.respawnVehicle(vehicleObj.id, vehicleObj.respawnCompactDescr)

    @staticmethod
    def respawnVehicle(vID, compactDescr=None, outfitCompactDescr=None):
        vehicle = BigWorld.entities.get(vID)
        avatar = BigWorld.player()
        if vID == avatar.playerVehicleID:
            ctrl = avatar.guiSessionProvider.shared.killCamCtrl
            if ctrl:
                ctrl.respawnRequested()
        if vehicle is not None:
            _logVehicle(_logger.info, 'respawnVehicle %r -> %r', vID, vehicle.typeCompDescr, compactDescr)
            vehInfo = avatar.arena.vehicles[vID]
            avatarVehicle = avatar.vehicle
            isVehicleAlive = vehInfo['isAlive'] and vehicle.isAlive()
            isVehicleEntityReady = avatar.playerVehicleID != vID or avatarVehicle and avatarVehicle.id == avatar.playerVehicleID
            if not isVehicleAlive or not isVehicleEntityReady:
                nextTick(functools.partial(Vehicle.respawnVehicle, vID, compactDescr, outfitCompactDescr))()
                return
            vehicle.respawnCompactDescr = compactDescr
            vehicle.respawnOutfitCompactDescr = outfitCompactDescr
            _g_respawnQueue.pop(vID, None)
            vehicle.isLeavingWorldForRespawn = True
            try:
                vehicle.onLeaveWorld()
                vehicle.onEnterWorld()
            finally:
                vehicle.isLeavingWorldForRespawn = False

        else:
            _logVehicle(_logger.debug, 'Delayed respawnVehicle %r', vID, compactDescr)
            _g_respawnQueue[vID] = [compactDescr, outfitCompactDescr]
        return

    @staticmethod
    def onArenaDestroyed():
        _logger.debug('onArenaDestroyed')
        _g_respawnQueue.clear()

    def __initAdditionalFilters(self):
        self.__wheelsScrollFilter, self.__wheelsSteeringFilter = createWheelFilters(self.typeDescriptor)

    def __onAppearanceReady(self, appearance):
        self.__logVehicle(_logger.info, '__onAppearanceReady %s %r', id(appearance), appearance.vStrCD)
        self.appearance = appearance
        self.__waitingForAppearanceReload = False
        self.__isEnteringWorld = True
        self.__prevDamageStickerCodes = frozenset()
        self.__prevPublicStateModifiers = frozenset()
        self.targetFullBounds = True
        self.__initAdditionalFilters()
        player = BigWorld.player()
        player.vehicle_onAppearanceReady(self)
        if self.isPlayerVehicle and player.initCompleted:
            self.cell.sendStateToOwnClient()
        player.initSpace()
        self.__isEnteringWorld = False
        self.isForceReloading = False
        self.__prevHealth = self.maxHealth
        self.resetProperties()
        self.__events.onAppearanceReady()
        self.appearance.onAppearanceActivated += self.__onActivateAppearance
        if appearance.isComponentsCreated:
            self.__events.onAppearanceComponentsReady()
        else:
            self.appearance.onComponentsCreated += self.__onCreateAppearanceComponents

    def __onVehicleInfoAdded(self, vehID):
        if self.id != vehID:
            self.__logVehicle(_logger.warning, '__onVehicleInfoAdded - skip info for %d', vehID)
            return
        player = BigWorld.player()
        player.arena.onVehicleAdded -= self.__onVehicleInfoAdded
        self.__logVehicle(_logger.debug, '__onVehicleInfoAdded - setVehicleInfo')
        self.appearance.setVehicleInfo(player.arena.vehicles[vehID])

    def __resetAppearance(self):
        if self.appearance is not None:
            self.__logVehicle(_logger.info, '__resetAppearance %s', id(self.appearance))
            self.events.onAppearanceReset()
            self.appearance.onComponentsCreated -= self.__onCreateAppearanceComponents
            self.appearance.onAppearanceActivated -= self.__onActivateAppearance
            self.appearance = None
        return

    def onLeaveWorld(self):
        self.__logVehicle(_logger.debug, 'onLeaveWorld')
        self.__appearanceCache.stopLoading(self.id, self.typeDescriptor.makeCompactDescr())
        self.__stopExtras()
        BigWorld.player().vehicle_onLeaveWorld(self)
        self.__resetAppearance()

    def onDestroy(self):
        self.__events.destroy()

    def showShooting(self, burstCount, currentGuns, shellType, isPredictedShot=False):
        blockShooting = self.siegeState is not None and self.siegeState in VEHICLE_SIEGE_STATE.SWITCHING and not self.typeDescriptor.hasAutoSiegeMode and isPredictedShot
        if not self.isStarted or blockShooting:
            return
        else:
            if not isPredictedShot and self.isPlayerVehicle and not BigWorld.player().isWaitingForShot:
                if not BattleReplay.g_replayCtrl.isPlaying:
                    return
            extra = self.typeDescriptor.extrasDict[self.typeDescriptor.shootExtraName]
            extra.stopFor(self)
            extra.startFor(self, (burstCount, currentGuns, shellType))
            if self.isPlayerVehicle:
                if not isPredictedShot:
                    BigWorld.player().cancelWaitingForShot()
            return

    def calcMaxComponentIdx(self):
        maxComponentIdx = TankPartIndexes.ALL[-1]
        if self.appearance.typeDescriptor.chassis.tracks is not None:
            tracks = self.appearance.typeDescriptor.chassis.tracks.trackPairs
            maxComponentIdx += len(tracks) - 1
        wheelsConfig = self.appearance.typeDescriptor.chassis.generalWheelsAnimatorConfig
        if wheelsConfig:
            maxComponentIdx = maxComponentIdx + wheelsConfig.getNonTrackWheelsCount()
        return maxComponentIdx

    def showDamageFromShot(self, attackerID, hitPoints, effectsIndex, prefabEffIndex, damage, damageFactor, lastMaterialIsShield, shellVelocity, gunInstallationIndex):
        if not self.isStarted:
            return
        else:
            self.__events.onShowDamageFromShot(attackerID, hitPoints, effectsIndex, damageFactor, lastMaterialIsShield)
            invokeInstantStatusForVehicle(self, InstantStatuses.ProjectileHitsReceivedComponent)
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            decodedPoints = []
            collisionComponent = self.__getCollisionComponent()
            if collisionComponent is not None:
                decodedPoints = DamageFromShotDecoder.parseHitPoints(hitPoints, collisionComponent)
            if not decodedPoints:
                return
            firstHitPoint = decodedPoints[0]
            maxPriorityHitPoint = decodedPoints[-1]
            maxHitEffectCode = maxPriorityHitPoint.hitEffectCode
            hasDamageHit = DamageFromShotDecoder.hasDamaged(maxHitEffectCode)
            hasPiercedHit = maxHitEffectCode in VEHICLE_HIT_EFFECT.PIERCED_HITS
            compoundModel = self.appearance.compoundModel
            compMatrix = Math.Matrix(compoundModel.node(firstHitPoint.componentName))
            firstHitDirLocal = firstHitPoint.matrix.applyToAxis(2)
            firstHitDir = compMatrix.applyVector(firstHitDirLocal)
            partTransform = self.appearance.collisions.getPartTransform(firstHitPoint.componentIdx) if firstHitPoint.isDynCollision else compMatrix
            self.appearance.receiveShotImpulse(firstHitDir, effectsDescr['targetImpulse'])
            player = BigWorld.player()
            player.inputHandler.onVehicleShaken(self, ShakeReason.HIT if hasDamageHit else ShakeReason.HIT_NO_DAMAGE, partTransform.translation, firstHitDir, effectsDescr['caliber'], effectsDescr['targetCameraSensitivity'])
            sessionProvider = self.guiSessionProvider
            if not BattleReplay.g_replayCtrl.isTimeWarpInProgress:
                showFriendlyFlashBang = False
                isAlly = sessionProvider.getArenaDP().isAlly(attackerID)
                if isAlly:
                    isFriendlyFireMode = sessionProvider.arenaVisitor.bonus.isFriendlyFireMode()
                    hasCustomAllyDamageEffect = sessionProvider.arenaVisitor.bonus.hasCustomAllyDamageEffect()
                    showFriendlyFlashBang = isFriendlyFireMode and hasCustomAllyDamageEffect
                showFullscreenEffs = self.isPlayerVehicle and self.isAlive()
                keyPoints, effects, _ = effectsDescr[maxPriorityHitPoint.hitEffectGroup]
                self.appearance.boundEffects.addNewToNode(TankPartNames.getActualNodeNameByPartName(maxPriorityHitPoint.componentName, self.isAlive()), maxPriorityHitPoint.matrix, effects, keyPoints, isPlayerVehicle=self.isPlayerVehicle, showShockWave=showFullscreenEffs, showFlashBang=showFullscreenEffs and not showFriendlyFlashBang, showFriendlyFlashBang=showFullscreenEffs and showFriendlyFlashBang, entity_id=self.id, damageFactor=damageFactor, attackerID=attackerID, hitdir=firstHitDir, surfaceNormal=maxPriorityHitPoint.matrix.applyVector(Math.Vector3(0, 0, -1)), componentIdx=maxPriorityHitPoint.componentIdx, isDynCollision=maxPriorityHitPoint.isDynCollision)
                prefabHit = effectsDescr['hitPrefabs'].get(maxPriorityHitPoint.hitEffectGroup) if 'hitPrefabs' in effectsDescr else None
                if prefabHit:

                    def hitLoadCallback(objects, queue):
                        root = objects[0]
                        if self.isAlive():
                            queue.createComponent(root, ShotDamageComponent, firstHitPoint.componentName, compoundModel)
                            return True
                        return False

                    partGO = self.appearance.partsGameObjects.getPartGameObject(prefabHit, self.spaceID, self.appearance.gameObject)
                    CGF.loadAndCreatePrefabWithParent(prefabHit, partGO, firstHitPoint.matrix, hitLoadCallback)
                nodeName = TankPartNames.getActualNodeNameByPartName(firstHitPoint.componentName, self.isAlive())
                hitGo = GenericComponents.findSlot(self.entityGameObject, nodeName)
                if hitGo.valid:
                    isWheel = firstHitPoint.componentName in self.typeDescriptor.chassis.wheelsArmor
                    location = firstHitPoint.matrix.translation
                    effGroup = maxPriorityHitPoint.hitEffectGroup
                    armorHitPlacement = ArmorHitPlacement.WHEEL if isWheel else ArmorHitPlacement.REGULAR
                    if isWheel:
                        transformComponent = hitGo.findRead(TransformComponent)
                        if transformComponent:
                            transform = transformComponent.transform
                            transform.translation = Math.Vector3(0, 0, 0)
                            transform.invert()
                            location = transform.applyVector(location)
                    CGF.postEvent(self.spaceID, game_events.VehicleHitEvent(self.entityGameObject, hitGo, location, firstHitPoint.normal, game_events.GunShellInfo(firstHitPoint.caliber, firstHitPoint.shellType), shellVelocity, damage, firstHitDirLocal, prefabEffIndex, effGroup, maxHitEffectCode, armorHitPlacement))
                else:
                    self.__logVehicle(_logger.error, 'Unable to post VehicleHitEvent: hitGo was not found by name: %s', firstHitPoint.componentName)
            if not self.isAlive():
                return
            soundNotifications = getSoundNotifications()
            needArmorScreenNotDamageSound = soundNotifications is not None and lastMaterialIsShield and not damageFactor and maxHitEffectCode not in VEHICLE_HIT_EFFECT.RICOCHETS and self.__settingsCore.getSetting(GAME.SHOW_DAMAGE_ICON)
            vehicleCtrl = self.guiSessionProvider.shared.vehicleState
            controllingVehicleID = vehicleCtrl.getControllingVehicleID() if vehicleCtrl is not None else -1
            isAttacker = attackerID == controllingVehicleID and maxHitEffectCode is not None and self.id != controllingVehicleID
            isObserverFPV = avatar_getter.isObserverSeesAll() and BigWorld.player().isObserverFPV
            if isAttacker or isObserverFPV:
                ctrl = sessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.updateMarkerHitState(self.id, None, maxPriorityHitPoint.componentName, maxHitEffectCode, gunInstallationIndex, damage, damageFactor, lastMaterialIsShield, hasPiercedHit)
                if needArmorScreenNotDamageSound:
                    soundNotifications.play('ui_armor_screen_not_damage_PC_NPC')
            elif self.id == controllingVehicleID and attackerID != self.id and needArmorScreenNotDamageSound:
                soundNotifications.play('ui_armor_screen_not_damage_NPC_PC')
            return

    def showDamageFromExplosion(self, attackerID, center, effectsIndex, damage, damageFactor, gunInstallationIndex):
        if not self.isStarted:
            return
        else:
            effectsDescr = vehicles.g_cache.shotEffects[effectsIndex]
            direction = self.position - center
            direction.normalise()
            self.appearance.receiveShotImpulse(direction, effectsDescr['targetImpulse'] / 4.0)
            if not self.isAlive():
                return
            self.showSplashHitEffect(effectsIndex, damageFactor)
            if self.id == attackerID:
                return
            player = BigWorld.player()
            player.inputHandler.onVehicleShaken(self, ShakeReason.SPLASH, center, direction, effectsDescr['caliber'], effectsDescr['targetCameraSensitivity'])
            if attackerID == player.playerVehicleID:
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.updateMarkerHitState(self.id, _FET.VEHICLE_ARMOR_PIERCED, gunInstallationIndex=gunInstallationIndex, damage=damage)
            return

    def showVehicleCollisionEffect(self, pos, delta_spd, energy=0):
        if not self.isStarted:
            return
        else:
            if delta_spd >= 3:
                effectName = 'collisionVehicleHeavy2'
                mass = self.typeDescriptor.physics['weight']
                if mass < 18000:
                    effectName = 'collisionVehicleHeavy1'
                elif mass > 46000:
                    effectName = 'collisionVehicleHeavy3'
            else:
                effectName = 'collisionVehicleLight'
            self.showCollisionEffect(pos, effectName, None, False, 0, None, energy)
            return

    def showCollisionEffect(self, hitPos, collisionEffectName='collisionVehicle', collisionNormal=None, isTracks=False, damageFactor=0, impulse=None, pcEnergy=None):
        invWorldMatrix = Math.Matrix(self.matrix)
        invWorldMatrix.invert()
        rot = Math.Matrix()
        if collisionNormal is None:
            rot.setRotateYPR((random.uniform(-3.14, 3.14), random.uniform(-1.5, 1.5), 0.0))
        else:
            rot.setRotateYPR((0, 0, 0))
        mat = Math.Matrix()
        mat.setTranslate(hitPos)
        mat.preMultiply(rot)
        mat.postMultiply(invWorldMatrix)
        if pcEnergy is not None:
            collisionEnergy = [SoundStartParam('RTPC_ext_collision_impulse_tank', pcEnergy)]
        else:
            collisionEnergy = []
        effectsList = self.typeDescriptor.type.effects.get(collisionEffectName, [])
        if effectsList:
            keyPoints, effects, _ = random.choice(effectsList)
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effects, keyPoints, entity=self, surfaceNormal=collisionNormal, isTracks=isTracks, impulse=impulse, damageFactor=damageFactor, hitPoint=hitPos, soundParams=collisionEnergy)
        return

    def showSplashHitEffect(self, effectsIndex, damageFactor):
        effectsList = vehicles.g_cache.shotEffects[effectsIndex].get('armorSplashHit', None)
        if effectsList:
            mat = Math.Matrix()
            mat.setTranslate((0.0, 0.0, 0.0))
            self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, mat, effectsList[1], effectsList[0], entity=self, damageFactor=damageFactor)
        return

    def set_postmortemViewPointName(self, _=None):
        cameraManager = CGF.getSystem(self.spaceID, ArenaCameraSystem)
        if cameraManager is not None and self.postmortemViewPointName:
            transform = cameraManager.getCameraTransform(self.postmortemViewPointName)
            if transform is not None:
                self.__cameraTargetMatrix.target = transform
                return
        self.__cameraTargetMatrix.target = self.matrix
        return

    def set_isHidden(self, _=None):
        if self.isHidden and self.isStarted:
            self.stopVisual()

    def set_burnoutLevel(self, _=None):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            isAttachedVehicle = self.id == attachedVehicle.id
            if self.appearance.detailedEngineState:
                self.appearance.detailedEngineState.throttle = 1 if self.burnoutLevel > 0.01 else 0
            if self.burnoutLevel > 0 and not self.__handbrakeFired:
                if self.getSpeed() > 0.5:
                    if not self.__burnoutStarted:
                        soundObject = self.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
                        soundObject.play('wheel_vehicle_burnout')
                        self.__burnoutStarted = True
            else:
                self.__burnoutStarted = False
            if isAttachedVehicle:
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BURNOUT, self.burnoutLevel)
            return

    def set_wheelsState(self, prev=0):
        if self.appearance is None:
            return
        else:
            __WHEEL_DESTROYED = 3
            for i in range(0, 8):
                prevState = prev >> i * 2 & 3
                newState = self.wheelsState >> i * 2 & 3
                if prevState != newState:
                    if newState == __WHEEL_DESTROYED:
                        self.appearance.onChassisDestroySound(False, True, i)
                    elif prevState == __WHEEL_DESTROYED:
                        self.appearance.onChassisDestroySound(False, False, i)

            return

    def set_damageStickers(self, _=None):
        self.__setDamageStickers(True)

    def __setDamageStickers(self, isActive):
        if not hasattr(self, 'isStarted') or not self.isStarted or not self.appearance.collisions:
            return
        else:
            prev = self.__prevDamageStickerCodes
            stickerMap = {DamageFromShotDecoder.encodeHitPoint(hitPoint):hitPoint for hitPoint in self.damageStickers}
            curr = set(stickerMap.keys())
            for code in prev.difference(curr):
                self.appearance.removeDamageSticker(code)

            for code in curr.difference(prev):
                hitPoint = stickerMap[code]
                parsedHitPoint = DamageFromShotDecoder.parseDamageStickerHitPoint(hitPoint, self.appearance.collisions)
                if parsedHitPoint is None:
                    curr.discard(code)
                stickerID, data = parsedHitPoint
                self.appearance.addDamageSticker(code, stickerID, data, isActive)

            self.__prevDamageStickerCodes = frozenset(curr)
            return

    def set_publicStateModifiers(self, _=None):
        if self.isStarted:
            prev = self.__prevPublicStateModifiers
            curr = frozenset(self.publicStateModifiers)
            self.__prevPublicStateModifiers = curr
            self.__updateModifiers(curr.difference(prev), prev.difference(curr))
            if not self.isPlayerVehicle:
                self.updateStunInfo()

    def set_engineMode(self, _=None):
        if self.isStarted and self.isAlive():
            self.appearance.changeEngineMode(self.engineMode, True)

    def set_isStrafing(self, _=None):
        if hasattr(self.filter, 'isStrafing'):
            self.filter.isStrafing = self.isStrafing

    def set_gunAnglesPacked(self, _=None):
        if self.typeDescriptor is not None:
            if self.typeDescriptor.gun.staticPitch is not None and self.siegeState in VEHICLE_SIEGE_STATE.SWITCHING:
                return
            syncGunAngles = getattr(self.filter, 'syncGunAngles', None)
            if syncGunAngles:
                yaw, pitch = decodeGunAngles(self.gunAnglesPacked, self.typeDescriptor.gun.pitchLimits['absolute'])
                syncGunAngles(yaw, pitch)
        return

    def set_health(self, _=None):
        pass

    def set_isCrewActive(self, _=None):
        if self.isStarted:
            self.appearance.onVehicleHealthChanged()
            if not self.isPlayerVehicle:
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.setVehicleNewHealth(self.id, self.health)
            if not self.isCrewActive and self.health > 0:
                self.__onVehicleDeath()
        return

    def set_isSpeedCapturing(self, _=None):
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (True, self.isSpeedCapturing))
        return

    def set_isBlockingCapture(self, _=None):
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidatePassiveEngineering(self.id, (False, self.isBlockingCapture))
        return

    def set_steeringAngles(self, prev=None):
        if self.__wheelsSteeringFilter is not None:
            for packedValue, steeringFilter in zip(self.steeringAngles, self.__wheelsSteeringFilter):
                unpackedValue = WoT.unpackWheelSteering(packedValue)
                steeringFilter.input(BigWorld.time(), unpackedValue)

        return

    def set_wheelsScroll(self, prev=None):
        if self.__wheelsScrollFilter is not None:
            for packedValue, scrollFilter in zip(self.wheelsScroll, self.__wheelsScrollFilter):
                unpackedValue = WoT.unpackWheelScroll(packedValue)
                scrollFilter.input(BigWorld.time(), unpackedValue)

        return

    def set_dotEffect(self, _=None):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            if self.id == attachedVehicle.id:
                self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DOT_EFFECT, self.dotEffect)
            return

    def set_crewCompactDescrs(self, _=None):
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setCrew(self.id, list(self.crewCompactDescrs))
        return

    def set_customRoleSlotTypeId(self, _=None):
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setDynSlotType(self.id, self.customRoleSlotTypeId)
        return

    def set_enhancements(self, _=None):
        enhancements = self.enhancements
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None and enhancements is not None:
            ctrl.setEnhancements(self.id, enhancements.copy())
        return

    def set_onRespawnReloadTimeFactor(self, _None):
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setRespawnReloadFactor(self.id, self.onRespawnReloadTimeFactor)
        return

    def set_setups(self, _=None):
        setups = self.setups
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None and setups is not None:
            ctrl.setSetups(self.id, setups.copy())
        return

    def set_setupsIndexes(self, _=None):
        setupsIndexes = self.setupsIndexes
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None and setupsIndexes is not None:
            ctrl.setSetupsIndexes(self.id, setupsIndexes.copy())
        return

    def set_siegeState(self, _=None):
        avatar = BigWorld.player()
        if not avatar.userSeesWorld():
            return
        else:
            ctrl = self.guiSessionProvider.shared.prebattleSetups
            if ctrl is not None:
                ctrl.setSiegeState(self.id, self.siegeState)
            if not self.isPlayerVehicle and self.typeDescriptor is not None and self.typeDescriptor.hasSiegeMode:
                self.onSiegeStateUpdated(self.siegeState, 0.0)
            return

    def set_publicInfo(self, _):
        var_storage.update(self.entityGameObject, var_storage.VehicleRootVars.MAX_HEALTH.value, self.maxHealth)
        self.refreshNationalVoice()

    def set_vehPostProgression(self, _=None):
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setPostProgression(self.id, list(self.vehPostProgression))
        return

    def set_disabledSwitches(self, _=None):
        ctrl = self.guiSessionProvider.shared.prebattleSetups
        if ctrl is not None:
            ctrl.setDisabledSwitches(self.id, self.disabledSwitches)
        return

    def onVehiclePickup(self):
        queue = CGF.CommandQueue(self.spaceID)
        queue.createComponent(self.entityGameObject, VehiclePickupComponent, self.appearance)
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None or self.id != attachedVehicle.id:
            return
        else:
            soundObject = self.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.CHASSIS)
            if soundObject is not None:
                soundObject.play('lift_overs')
            return

    def onExtraHitted(self, extraIndex, hitPoint):
        self.extrasHitPoint[extraIndex] = hitPoint

    def getExtraHitPoint(self, extraIndex):
        return DEFAULT_TRACK_HIT_VECTOR if extraIndex is None or extraIndex not in self.extrasHitPoint else self.extrasHitPoint[extraIndex]

    def set_perks(self, _=None):
        ctrl = self.guiSessionProvider.dynamic.perks
        if ctrl is not None:
            ctrl.updatePerks(self.perks)
        return

    def set_perksRibbonNotify(self, _=None):
        ctrl = self.guiSessionProvider.dynamic.perks
        if ctrl is not None and self.perksRibbonNotify:
            ctrl.notifyRibbonChanges(self.perksRibbonNotify)
        return

    def onHealthChanged(self, newHealth, oldHealth, attackerID, attackReasonID, attackReasonExtID):
        if newHealth > 0 >= self.health:
            self.health = newHealth
            self.__prevHealth = newHealth
            return
        else:
            self.guiSessionProvider.setVehicleHealth(self.isPlayerVehicle, self.id, newHealth, attackerID, attackReasonID)
            if not self.isStarted:
                self.__prevHealth = newHealth
                return
            player = BigWorld.player()
            attachedVehicle = player.getVehicleAttached()
            player.arena.onVehicleHealthChanged(self.id, attackerID, oldHealth - newHealth)
            self.__events.onVehicleHealthChanged(self.id, newHealth, oldHealth)
            if not self.appearance.damageState.isCurrentModelDamaged:
                self.appearance.onVehicleHealthChanged()
            if self.health <= 0:
                if self.isCrewActive:
                    self.__onVehicleDeath()
                if player.isObserver() and player.isObserverFPV and self.id == attachedVehicle.id:
                    player.switchObserverFPV()
            if self.isPlayerVehicle:
                TriggersManager.g_manager.activateTrigger(TRIGGER_TYPE.PLAYER_RECEIVE_DAMAGE, attackerId=attackerID)
            if attackReasonID == ATTACK_REASON_INDICES[ATTACK_REASON.WORLD_COLLISION]:
                damageFactor = (self.__prevHealth - newHealth) * 100.0 / self.maxHealth
                if damageFactor > 1:
                    effectsList = self.typeDescriptor.type.effects.get('collisionDamage')
                    if effectsList is not None:
                        keyPoints, effects, _ = random.choice(effectsList)
                        self.appearance.boundEffects.addNewToNode(TankPartNames.HULL, None, effects, keyPoints, entity=self, damageFactor=damageFactor)
            elif attackReasonID == ATTACK_REASON_INDICES[ATTACK_REASON.DAMAGE_ZONE] and attackReasonExtID == int(DamageZoneType.FIRE_DAMAGE_ZONE) and attachedVehicle:
                soundObject = self.appearance.engineAudition.getSoundObject(TankSoundObjectsIndexes.ENGINE)
                if soundObject is not None:
                    soundObject.play('fire_damage_PC' if self.id == attachedVehicle.id else 'fire_damage_NPC')
            self.__prevHealth = newHealth
            return

    def set_stunInfo(self, prev=None):
        self.__logVehicle(_logger.debug, 'Set stun info(curr, prev): %s, %s', self.stunInfo, prev)
        queue = CGF.CommandQueue(self.spaceID)
        if self.stunInfo > 0.0 and self.appearance.gameObject.hasComponent(Statuses.StunComponent):
            queue.createComponent(self.appearance.gameObject, Statuses.StunComponent)
        if self.stunInfo < 0.01:
            queue.removeComponent(self.appearance.gameObject, Statuses.StunComponent)
        self.updateStunInfo()

    def __updateCachedStunInfo(self, endTime):
        if endTime:
            cachedStartTime = self.__cachedStunInfo.startTime
            startTime = cachedStartTime if cachedStartTime > 0.0 else BigWorld.serverTime()
            totalTime = max(self.__cachedStunInfo.duration, endTime - startTime)
            duration = endTime - BigWorld.serverTime() if endTime > 0.0 else 0.0
            self.__cachedStunInfo = StunInfo(startTime, endTime, duration, totalTime)
        else:
            self.__cachedStunInfo = StunInfo(0.0, 0.0, 0.0, 0.0)

    def getStunInfo(self):
        self.__updateCachedStunInfo(self.stunInfo)
        return self.__cachedStunInfo

    def updateStunInfo(self):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            self.__updateCachedStunInfo(self.stunInfo)
            if self.lobbyContext.getServerSettings().spgRedesignFeatures.isStunEnabled():
                isAttachedVehicle = self.id == attachedVehicle.id
                if isAttachedVehicle:
                    self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.STUN, self.__cachedStunInfo)
                    TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.STUN, stunInfo=self.__cachedStunInfo)
                if not self.isPlayerVehicle:
                    ctrl = self.guiSessionProvider.shared.feedback
                    if ctrl is not None:
                        ctrl.invalidateStun(self.id, self.__cachedStunInfo)
            else:
                self.__logVehicle(_logger.warning, 'Stun features is disabled!')
            return

    def showAmmoBayEffect(self, mode, fireballVolume, projectedTurretSpeed):
        if self.isStarted:
            self.appearance.showAmmoBayEffect(mode, fireballVolume)

    def onPushed(self, x, z):
        try:
            distSqr = BigWorld.player().position.distSqrTo(self.position)
            if distSqr > 1600.0:
                self.filter.setPosition(x, z)
        except Exception:
            pass

    def showRammingEffect(self, energy, speedDiff, point):
        if not self.isStarted:
            return
        else:
            effectName = 'rammingCollisionLight'
            improvedRammingParams = getVehicleDescrMechanicParams(self.typeDescriptor, VehicleMechanic.IMPROVED_RAMMING)
            if improvedRammingParams is not None:
                if speedDiff > improvedRammingParams.effectSpeedThreshold:
                    effectName = 'rammingCollisionHeavy'
            elif energy >= constants.RAMMING_EFFECT_THRESHOLD:
                effectName = 'rammingCollisionHeavy'
            self.showCollisionEffect(point, effectName)
            return

    def onStaticCollision(self, energy, point, normal, miscFlags, damage, destrEffectIdx, destrMaxHealth):
        if not self.isStarted:
            return
        self.appearance.stopSwinging()
        BigWorld.player().inputHandler.onVehicleCollision(self, self.getSpeed())
        isTrackCollision = bool(miscFlags & 1)
        isSptCollision = bool(miscFlags >> 1 & 1)
        isSptDestroyed = bool(miscFlags >> 2 & 1)
        if isSptDestroyed:
            return
        hitPoint = point
        surfNormal = normal
        matKind = SPT_MATKIND.SOLID
        if destrEffectIdx < 0:
            if not isSptCollision:
                surfaceMaterial = calcSurfaceMaterialNearPoint(hitPoint, normal, self.spaceID)
                hitPoint, surfNormal, matKind, effectIdx = surfaceMaterial
            else:
                effectIdx = EFFECT_MATERIAL_INDEXES_BY_NAMES['wood']
            if matKind != 0:
                self.__showStaticCollisionEffect(energy, effectIdx, hitPoint, surfNormal, isTrackCollision, damage * 100.0)
        else:
            self.__showDynamicCollisionEffect(energy, destrMaxHealth, hitPoint, surfNormal)

    def getAimParams(self):
        if self.appearance is not None:
            turretYaw = Math.Matrix(self.appearance.turretMatrix).yaw
            gunPitch = Math.Matrix(self.appearance.gunMatrix).pitch
            return (turretYaw, gunPitch)
        else:
            return (0.0, 0.0)

    def onSiegeStateUpdated(self, newState, timeToNextMode):
        if not self.isStarted:
            return
        else:
            if self.typeDescriptor is not None and self.typeDescriptor.hasSiegeMode:
                self.typeDescriptor.onSiegeStateChanged(newState)
                self.appearance.onSiegeStateChanged(newState)
                self.__events.onSiegeStateUpdated(newState, timeToNextMode)
                if self.isPlayerVehicle or self.id == BigWorld.player().observedVehicleID:
                    inputHandler = BigWorld.player().inputHandler
                    if inputHandler.siegeModeNotifier:
                        inputHandler.siegeModeNotifier.notifySiegeModeChanged(self.id, newState, timeToNextMode)
            else:
                self.__logVehicle(_logger.error, 'onSiegeStateUpdated is called for not siege or None typeDescriptor')
            return

    def getVehicleMechanicComponent(self, mechanicName):
        return getVehicleMechanicComponent(self, mechanicName)

    def getSiegeSwitchTimeLeft(self):
        ownVehicle = self.dynamicComponents.get('ownVehicle')
        return 0.0 if ownVehicle is None else ownVehicle.getSiegeStateTimeLeft()

    def onActiveDualGunChanged(self, dualGunIndex, switchTimes):
        if not self.isStarted:
            return
        else:
            if self.typeDescriptor is not None and self.typeDescriptor.isDualgunVehicle:
                if self.__dualGunIndex == dualGunIndex:
                    return
                self.__dualGunIndex = dualGunIndex
                swElapsedTime = switchTimes[2] - switchTimes[1]
                afterShotDelay = self.typeDescriptor.gun.dualGun.afterShotDelay
                leftDelayTime = max(afterShotDelay - swElapsedTime, 0.0)
                ctrl = self.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateActiveGunChanges(self.id, [dualGunIndex], leftDelayTime)
            else:
                self.__logVehicle(_logger.error, 'onActiveDualGunChanged called for not dual or None typeDescriptor')
            return

    def collideSegmentExt(self, startPoint, endPoint):
        if self.appearance.collisions:
            collisions = self.appearance.collisions.collideAllWorld(startPoint, endPoint)
            if collisions:
                res = []
                for collision in collisions:
                    matInfo = self.getMatinfo(collision[3], collision[2])
                    res.append(SegmentCollisionResultExt(collision[0], collision[1], matInfo, collision[3]))

                return res
        return None

    def getMatinfo(self, partIndex, matKind):
        return getMatinfo(self, partIndex, matKind, self.isWheeledTech)

    def isAlive(self):
        return self.isCrewActive and self.health > 0

    def isPitchHullAimingAvailable(self):
        return self.typeDescriptor is not None and self.typeDescriptor.isPitchHullAimingAvailable

    def getServerGunAngles(self):
        return decodeGunAngles(self.gunAnglesPacked, self.typeDescriptor.gun.pitchLimits['absolute'])

    def startVisual(self):
        self.__logVehicle(_logger.debug, 'startVisual')
        if self.isHidden:
            self.__logVehicle(_logger.info, 'Vehicle is marked as hidden')
            return
        elif self.__waitingForAppearanceReload:
            self.__logVehicle(_logger.info, 'Waiting for appearance reload')
            return
        elif not self.appearance.isConstructed:
            self.__logVehicle(_logger.warning, 'Vehicle appearance is not constructed')
            return
        else:
            if self.isStarted:
                raise SoftException('Vehicle is already started')
            self.appearance.setVehicle(self)
            self.appearance.activate(self.entityGameObject.uuid)
            self.isStarted = True
            self.set_publicStateModifiers()
            if TriggersManager.g_manager:
                TriggersManager.g_manager.fireTrigger(TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED, vehicleId=self.id, isVisible=True)
            self.startGUIVisual()
            self.refreshBuffEffects()
            if self.isSpeedCapturing:
                self.set_isSpeedCapturing()
            if self.isBlockingCapture:
                self.set_isBlockingCapture()
            progressionCtrl = self.guiSessionProvider.dynamic.progression
            if progressionCtrl is not None:
                progressionCtrl.vehicleVisualChangingFinished(self.id)
            BigWorld.callback(0.0, lambda : Vehicle.deferredRespawnVehicle(self))
            self.refreshNationalVoice()
            self.set_quickShellChangerFactor()
            return

    def startGUIVisual(self):
        self.guiSessionProvider.startVehicleVisual(self.proxy, True)
        if not self.isAlive():
            self.__onVehicleDeath(True)
        if self.stunInfo > 0.0:
            self.updateStunInfo()

    def refreshNationalVoice(self):
        player = BigWorld.player()
        if self.id == player.observedVehicleID:
            self.__specialSounds.setPlayerVehicle(self.publicInfo, False)
        elif self.id == player.playerVehicleID:
            self.__specialSounds.setPlayerVehicle(self.publicInfo, True)

    def stopVisual(self):
        self.__logVehicle(_logger.debug, 'stopVisual')
        if not self.isStarted:
            raise SoftException('Vehicle is already stopped')
        self.__stopExtras()
        if TriggersManager.g_manager:
            TriggersManager.g_manager.fireTriggerInstantly(TriggersManager.TRIGGER_TYPE.VEHICLE_VISUAL_VISIBILITY_CHANGED, vehicleId=self.id, isVisible=False)
        self.appearance.deactivate()
        self.stopGUIVisual()
        self.__resetAppearance()
        self.isStarted = False
        self.__speedInfo.reset()
        if self.__isInDebuff:
            self.onDebuffEffectApplied(False)

    def stopGUIVisual(self):
        self.guiSessionProvider.stopVehicleVisual(self.id, self.isPlayerVehicle)

    def show(self, show):
        if show:
            drawFlags = BigWorld.DrawAll
        else:
            drawFlags = BigWorld.ShadowPassBit
        if self.isStarted:
            va = self.appearance
            if va.tracks:
                va.tracks.setPhysicalDestroyedTracksVisible(show)
            va.changeDrawPassVisibility(drawFlags)
            va.showStickers(show)

    def addCameraCollider(self):
        if self.appearance is not None:
            self.appearance.addCameraCollider()
        return

    def removeCameraCollider(self):
        if self.appearance is not None:
            self.appearance.removeCameraCollider()
        return

    def changeVehicleExtrasSetting(self, extraName, newValue):
        extra = self.typeDescriptor.extrasDict[extraName]
        if self.extras.has_key(extra.index):
            extra.updateFor(self, newValue)

    def getOptionalDevices(self):
        return vehicle_getter.getOptionalDevices() if self.isPlayerVehicle else []

    def _isDestructibleMayBeBroken(self, chunkID, itemIndex, matKind, itemFilename, itemScale, vehSpeed):
        desc = AreaDestructibles.g_cache.getDescByFilename(itemFilename)
        if desc is None:
            return False
        else:
            ctrl = AreaDestructibles.g_destructiblesManager.getController(chunkID)
            if ctrl is None:
                return False
            if ctrl.isDestructibleBroken(itemIndex, matKind, desc['type']):
                return True
            mass = self.typeDescriptor.physics['weight']
            instantDamage = 0.5 * mass * vehSpeed * vehSpeed * 0.00015
            if desc['type'] == DestructiblesCache.DESTR_TYPE_STRUCTURE:
                moduleDesc = desc['modules'].get(matKind)
                if moduleDesc is None:
                    return False
                refHealth = moduleDesc['health']
            else:
                unitMass = AreaDestructibles.g_cache.unitVehicleMass
                instantDamage *= math.pow(mass / unitMass, desc['kineticDamageCorrection'])
                refHealth = desc['health']
            return DestructiblesCache.scaledDestructibleHealth(itemScale, refHealth) < instantDamage

    def __showStaticCollisionEffect(self, energy, effectIdx, hitPoint, normal, isTrackCollision, damageFactor):
        heavyVelocities = self.typeDescriptor.type.heavyCollisionEffectVelocities
        heavyEnergy = heavyVelocities['track'] if isTrackCollision else heavyVelocities['hull']
        heavyEnergy = 0.5 * heavyEnergy * heavyEnergy
        postfix = '%sCollisionLight' if energy < heavyEnergy else '%sCollisionHeavy'
        effectName = ''
        if effectIdx < len(EFFECT_MATERIALS):
            effectName = EFFECT_MATERIALS[effectIdx]
        effectName = postfix % effectName
        if effectName in self.typeDescriptor.type.effects:
            self.showCollisionEffect(hitPoint, effectName, normal, isTrackCollision, damageFactor, self.__getImpulse(self.getSpeed()))

    def __showDynamicCollisionEffect(self, energy, destrMaxHealth, hitPoint, surfNormal):
        effectName = 'dynamicCollision'
        if effectName in self.typeDescriptor.type.effects:
            self.showCollisionEffect(hitPoint, effectName, surfNormal, False, 0, self.__getDynamicImpulse(self.getSpeed(), destrMaxHealth))

    def __startWGPhysics(self):
        if not hasattr(self.filter, 'setVehiclePhysics'):
            return
        typeDescr = self.typeDescriptor
        isWheeled = 'wheeledVehicle' in self.typeDescriptor.type.tags
        physics = BigWorld.WGWheeledPhysics() if isWheeled else BigWorld.WGTankPhysics()
        physics_shared.initVehiclePhysicsClient(physics, typeDescr)
        arenaMinBound, arenaMaxBound = (-10000, -10000), (10000, 10000)
        physics.setArenaBounds(arenaMinBound, arenaMaxBound)
        physics.owner = weakref.ref(self)
        physics.staticMode = False
        physics.movementSignals = 0
        self.filter.setVehiclePhysics(physics)
        yaw, pitch = decodeGunAngles(self.gunAnglesPacked, typeDescr.gun.pitchLimits['absolute'])
        self.filter.syncGunAngles(yaw, pitch)
        self.__speedInfo.set(self.filter.speedInfo)

    def __stopWGPhysics(self):
        self.__speedInfo.reset()

    def __getImpulse(self, speed):
        mass = self.typeDescriptor.physics['weight']
        maxSpeed = self.typeDescriptor.physics['speedLimits'][0]
        return math.fabs(speed * mass / (maxSpeed * mass))

    def __getDynamicImpulse(self, speed, maxHealth):
        maxSpeed = 20.0
        relSpeed = min(math.fabs(speed / maxSpeed), 1.0)
        relSpeed *= relSpeed
        relHeath = min(min(maxHealth, 90.0) / 90.0, 1.0)
        return 0.5 * (relSpeed + relHeath)

    def __stopExtras(self):
        extraTypes = self.typeDescriptor.extras
        for index, data in self.extras.items():
            extraTypes[index].stop(data)

        if self.extras:
            self.__logVehicle(_logger.warning, 'this code point should have never been reached')

    def __updateModifiers(self, addedExtras, removedExtras):
        extraTypes = self.typeDescriptor.extras
        for idx in removedExtras:
            extraTypes[idx].stopFor(self)

        for idx in addedExtras:
            try:
                extraTypes[idx].startFor(self)
            except Exception:
                self.__logVehicle(_logger.exception, 'Update modifiers')

    def __onVehicleDeath(self, isDeadStarted=False):
        if not self.isPlayerVehicle:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.setVehicleState(self.id, _FET.VEHICLE_DEAD, isDeadStarted)
        TriggersManager.g_manager.fireTrigger(TRIGGER_TYPE.VEHICLE_DESTROYED, vehicleId=self.id)
        self._removeInspire()
        self._removeHealing()
        bwfilter = self.filter
        if hasattr(bwfilter, 'velocityErrorCompensation'):
            bwfilter.velocityErrorCompensation = 100.0
        return

    def __logVehicle(self, logger, msg, *args, **kwargs):
        _logVehicle(logger, msg, self.id, *args, **kwargs)

    def confirmTurretDetachment(self):
        self.__turretDetachmentConfirmed = True
        if self.isTurretDetached:
            self.appearance.updateTurretVisibility()
        else:
            self.__logVehicle(_logger.error, 'confirmTurretDetachment is called without detached turret')

    def updateLaserSight(self, vehicleID, isTakesAim, beamMode):
        if self.id == vehicleID and not self.isPlayerVehicle:
            extra = self.typeDescriptor.extrasDict['laserSight']
            if extra.isRunningFor(self):
                args = {'isTakesAim': isTakesAim,
                 'beamMode': beamMode}
                extra.updateFor(self, args)

    def drawEdge(self, forceSimpleEdge=False):
        if self.appearance and self.appearance.highlighter:
            self.appearance.highlighter.highlight(True, forceSimpleEdge)

    def removeEdge(self, forceSimpleEdge=False):
        if self.appearance and self.appearance.highlighter:
            self.appearance.highlighter.highlight(False, forceSimpleEdge)

    def addModel(self, model):
        super(Vehicle, self).addModel(model)
        highlighter = self.appearance.highlighter
        if not highlighter:
            self.__logVehicle(_logger.error, "Vehicle appearance's Highlighter component is not ready/not created")
            return
        if highlighter.isOn:
            highlighter.highlight(False)
            highlighter.highlight(True)

    def delModel(self, model):
        if self.isDestroyed or not hasattr(self, 'appearance'):
            self.__logVehicle(_logger.warning, 'DelModel called by %s after destroy', type(model))
            return
        highlighter = self.appearance.highlighter
        hlOn = False
        if highlighter:
            hlOn = highlighter.isOn
            hlSimpleEdge = highlighter.isSimpleEdge
            highlighter.removeHighlight()
        super(Vehicle, self).delModel(model)
        if hlOn:
            highlighter.highlight(True, hlSimpleEdge)

    def notifyInputKeysDown(self, movementDir, rotationDir, handbrakeFired):
        self.filter.notifyInputKeysDown(movementDir, rotationDir)
        self.__handbrakeFired = handbrakeFired
        if self.appearance.detailedEngineState:
            self.appearance.detailedEngineState.throttle = movementDir or rotationDir

    def turnoffThrottle(self):
        if self.appearance.detailedEngineState:
            self.appearance.detailedEngineState.throttle = 0

    def onDebuffEffectApplied(self, applied):
        self.__isInDebuff = applied
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is not None and self.id == attachedVehicle.id:
            playerDebuffInfo = DebuffInfo(duration=0.1 if applied else 0, animated=applied)
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.DEBUFF, playerDebuffInfo)
        else:
            ctrl = self.guiSessionProvider.shared.feedback
            if ctrl is not None:
                enemyDebuffInfo = DebuffInfo(duration=99 if applied else 0, animated=True)
                ctrl.invalidateDebuff(self.id, enemyDebuffInfo)
        return

    def onDynamicComponentCreated(self, component):
        super(Vehicle, self).onDynamicComponentCreated(component)
        self.__events.onDynamicComponentCreated(component)

    def onDynamicComponentDestroyed(self, component):
        self.__events.onDynamicComponentDestroyed(component)
        super(Vehicle, self).onDynamicComponentDestroyed(component)

    @property
    def label(self):
        return self.labelComponent.label if hasattr(self, 'labelComponent') else None

    def set_quickShellChangerFactor(self, _=None):
        ammoCtrl = self.guiSessionProvider.shared.ammo
        if ammoCtrl is not None and self.isMyVehicle and self.isAlive():
            shellChangefactor = self.quickShellChangerFactor
            ammoCtrl.setQuickChangerFactor(isActive=0 < shellChangefactor < 1.0, factor=shellChangefactor)
        return

    @property
    def quickShellChangerIsActive(self):
        return self.__quickShellChangerIsActive

    @quickShellChangerIsActive.setter
    def quickShellChangerIsActive(self, value):
        self.__quickShellChangerIsActive = value

    def isOnFire(self):
        return 'fire' in self.dynamicComponents

    def resetProperties(self):
        self.set_burnoutLevel()
        self.__setDamageStickers(False)
        self.set_dotEffect()
        self.set_engineMode()
        self.set_gunAnglesPacked()
        self.set_health()
        self.set_isBlockingCapture()
        self.set_isCrewActive()
        self.set_isSpeedCapturing()
        self.set_isStrafing()
        self.set_publicStateModifiers()
        self.set_siegeState()
        self.set_steeringAngles()
        self.set_stunInfo()
        self.set_wheelsScroll()
        self.set_wheelsState()
        if hasattr(self, 'remoteCamera'):
            self.set_remoteCamera()
        if hasattr(self, 'ownVehicle'):
            self.ownVehicle.initialUpdate(True)

    def set_remoteCamera(self, _=None):
        self.ownVehicle.update_remoteCamera(self.remoteCamera)

    def getVseContextInstance(self, contextName):
        from visual_script.contexts.cgf_context import CGFGameObjectContext
        if contextName == CGFGameObjectContext.__name__:
            if self.entityGameObject:
                return CGFGameObjectContext(self.entityGameObject, ASPECT.CLIENT)
            self.__logVehicle(_logger.error, 'CGFGameObjectContext is not created: self.entityGameObject is None')
        return BigWorld.player().arena.getVseContextInstance(contextName)

    def getGunBurstParams(self, gunDescr):
        chargeableBurst = self.getVehicleMechanicComponent(VehicleMechanic.CHARGEABLE_BURST)
        return DEFAULT_GUN_BURST if chargeableBurst is not None and not chargeableBurst.isBurstActive else gunDescr.burst

    def updateTimeBetweenShots(self, newValue):
        if self.appearance is not None and self.appearance.isCompositionReady:
            GunInfoAssembler.update(self.appearance, var_storage.VehicleGunVars.TIME_BETWEEN_SHOTS.value, newValue)
        return

    def __onCreateAppearanceComponents(self):
        self.__events.onAppearanceComponentsReady()

    def __onActivateAppearance(self):
        avatar = BigWorld.player()
        vehInfo = avatar.arena.vehicles.get(self.id, None)
        if vehInfo is not None:
            self.appearance.setVehicleInfo(vehInfo)
        else:
            avatar.arena.onVehicleAdded += self.__onVehicleInfoAdded
        self.appearance.changeEngineMode(self.engineMode)
        if self.isPlayerVehicle or self.typeDescriptor is None or not self.typeDescriptor.hasSiegeMode:
            self.appearance.changeSiegeState(self.siegeState)
        showEffects = False if BattleReplay.g_replayCtrl.isPlaying and not self.isAlive() else self.isPlayerVehicle
        self.appearance.onVehicleHealthChanged(showEffects)
        if self.isPlayerVehicle:
            if self.isAlive():
                self.appearance.setupGunMatrixTargets(avatar.gunRotator)
        if not self.appearance.isObserver:
            self.show(True)
        self.__setDamageStickers(False)
        if hasattr(self.filter, 'allowStrafeCompensation'):
            self.filter.allowStrafeCompensation = not self.isPlayerVehicle
        if self.isTurretMarkedForDetachment and not self.__turretDetachmentConfirmed:
            self.confirmTurretDetachment()
        self.__startWGPhysics()
        if not self.isPlayerVehicle and self.typeDescriptor is not None and self.typeDescriptor.hasSiegeMode:
            self.onSiegeStateUpdated(self.siegeState, 0.0)
        if self.appearance.highlighter:
            self.appearance.highlighter.setVehicleOwnership()
        elif self.isAlive():
            self.__logVehicle(_logger.error, 'Highlighter component is not ready/not created')
        return

    def __getCollisionComponent(self):
        if self.appearance.collisions:
            return self.appearance.collisions
        else:
            return StubCollisionComponent(self.spaceID) if BattleReplay.g_replayCtrl.isTimeWarpInProgress else None


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _stripVehCompDescrIfRoaming(vehCompDescr, lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings() if lobbyContext is not None else None
    if serverSettings is not None:
        if serverSettings.roaming.isInRoaming():
            vehCompDescr = vehicles.stripCustomizationFromVehicleCompactDescr(vehCompDescr, True, True, False)[0]
    return vehCompDescr
