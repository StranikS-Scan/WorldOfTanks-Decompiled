# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/VehicleAppearance.py
# Compiled at: 2018-12-11 23:56:21
import BigWorld
import ResMgr
import Math
import Pixie
import weakref
from constants import HAS_DEV_RESOURCES
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION
from helpers import bound_effects
from helpers import DecalMap
from helpers.EffectsList import EffectsListPlayer
import items.vehicles
import random
import math
import time
from itertools import chain
from Event import Event
from functools import partial
import material_kinds
import Avatar
import VehicleStickers
from Vibroeffects.ControllersManager import ControllersManager as VibrationControllersManager
from LightFx.LightControllersManager import LightControllersManager as LightFxControllersManager
import LightFx.LightManager
_ENABLE_VEHICLE_VALIDATION = False
_VEHICLE_DISAPPEAR_TIME = 0.2
_VEHICLE_APPEAR_TIME = 0.2
_ROOT_NODE_NAME = 'V'
_GUN_RECOIL_NODE_NAME = 'G'
_PERIODIC_TIME = 0.25
_LOD_DISTANCE_SOUNDS = 80
_LOD_DISTANCE_EXHAUST = 200
_LOD_DISTANCE_DUST = 100
_MOVE_THROUGH_WATER_SOUND = '/vehicles/tanks/water'
_TURRET_ROTATION_SOUND = '/vehicles/tanks/turrets/turret_mid'
_ENABLE_TURRET_ROTATION_SOUND = False
_TURRET_SOUND_MIN_YAW_SPEED = 0.01
_TURRET_SOUND_PREDICT_STOP_TIME = 0.2
_CAMOUFLAGE_MIN_INTENSITY = 1.0

class VehicleAppearance(object):
    gunRecoil = property(lambda self: self.__gunRecoil)
    fashion = property(lambda self: self.__fashion)

    def __init__(self):
        self.modelsDesc = {'chassis': {'model': None,
                     'boundEffects': None,
                     '_visibility': (True, True),
                     '_fetchedModel': None,
                     '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.chassis['models'][state],
                     '_callbackFunc': '_VehicleAppearance__onChassisModelLoaded'},
         'hull': {'model': None,
                  'boundEffects': None,
                  '_visibility': (True, True),
                  '_node': None,
                  '_fetchedModel': None,
                  '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.hull['models'][state],
                  '_callbackFunc': '_VehicleAppearance__onHullModelLoaded'},
         'turret': {'model': None,
                    'boundEffects': None,
                    '_visibility': (True, True),
                    '_node': None,
                    '_fetchedModel': None,
                    '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.turret['models'][state],
                    '_callbackFunc': '_VehicleAppearance__onTurretModelLoaded'},
         'gun': {'model': None,
                 'boundEffects': None,
                 '_visibility': (True, True),
                 '_fetchedModel': None,
                 '_node': None,
                 '_stateFunc': lambda vehicle, state: vehicle.typeDescriptor.gun['models'][state],
                 '_callbackFunc': '_VehicleAppearance__onGunModelLoaded'}}
        self.turretMatrix = Math.WGAdaptiveMatrixProvider()
        self.gunMatrix = Math.WGAdaptiveMatrixProvider()
        self.__vehicle = None
        self.__skeletonCollider = None
        self.__engineSound = None
        self.__movementSound = None
        self.__waterSound = None
        self.__isInWater = False
        self.__vibrationsCtrl = None
        self.__lightFxCtrl = None
        self.__fashion = None
        self.__crashedTracksCtrl = None
        self.__gunRecoil = None
        self.__firstInit = True
        self.__curDamageState = None
        self.__loadingProgress = len(self.modelsDesc)
        self.__actualDamageState = None
        self.__invalidateLoading = False
        self.__exhaust = []
        self.__showStickers = True
        self.__effectsPlayer = None
        self.__engineMode = (0, 0)
        self.__engineSndVariation = [0, 0]
        self.__exhaustDisabledByLOD = False
        self.__dustDisabled = False
        self.__dustTrails = {}
        self.__trackSounds = [None, None]
        self.__currTerrainMatKind = [-1, -1]
        self.__turretSound = None
        self.__prevTurretYaw = None
        self.__periodicTimerID = None
        self.__stickers = {}
        self.__damageStickersTexSize = None
        self.onModelChanged = Event()
        return

    def getTerrainMatKind(self):
        return self.__currTerrainMatKind

    def isInWater(self):
        return self.__isInWater

    def prerequisites(self, vehicle):
        self.__curDamageState = self.__getDamageModelsState(vehicle.health)
        out = []
        for desc in self.modelsDesc.itervalues():
            out.append(desc['_stateFunc'](vehicle, self.__curDamageState))

        vDesc = vehicle.typeDescriptor
        out.append(vDesc.type.camouflageExclusionMask)
        customization = items.vehicles.g_cache.customization(vDesc.type.id[0])
        camouflageParams = self.__getCamouflageParams(vehicle)
        if camouflageParams is not None and customization is not None:
            camouflageId = camouflageParams[0]
            camouflageDesc = customization['camouflages'].get(camouflageId)
            if camouflageDesc is not None and camouflageDesc['texture'] != '':
                out.append(camouflageDesc['texture'])
                for tgDesc in (vDesc.turret, vDesc.gun):
                    exclMask = tgDesc.get('camouflageExclusionMask')
                    if exclMask is not None and exclMask != '':
                        out.append(exclMask)

        return out

    def destroy(self):
        vehicle = self.__vehicle
        self.__vehicle = None
        if HAS_DEV_RESOURCES and _ENABLE_VEHICLE_VALIDATION and self.__validateCallbackId is not None:
            BigWorld.cancelCallback(self.__validateCallbackId)
            self.__validateCallbackId = None
        self.__skeletonCollider.destroy()
        BigWorld.delShadowEntity(vehicle)
        if self.__engineSound is not None:
            self.__engineSound.stop()
            self.__engineSound = None
        if self.__movementSound is not None:
            self.__movementSound.stop()
            self.__movementSound = None
        if self.__waterSound is not None:
            self.__waterSound.stop()
            self.__waterSound = None
        if self.__turretSound is not None:
            self.__turretSound.stop()
            self.__turretSound = None
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.destroy()
            self.__vibrationsCtrl = None
        if self.__lightFxCtrl is not None:
            self.__lightFxCtrl.destroy()
            self.__lightFxCtrl = None
        self.__stopEffects()
        self.__detachDustTrails()
        self.__destroyTrackDamageSounds()
        vehicle.stopHornSound(True)
        for desc in self.modelsDesc.iteritems():
            boundEffects = desc[1].get('boundEffects', None)
            if boundEffects is not None:
                boundEffects.destroy()

        if vehicle.isPlayer:
            player = BigWorld.player()
            if player.inputHandler is not None:
                arcadeCamera = player.inputHandler.ctrls['arcade'].camera
                if arcadeCamera is not None:
                    hull = self.modelsDesc['hull']['model']
                    turret = self.modelsDesc['turret']['model']
                    arcadeCamera.removeModelsToCollideWith((hull, turret))
        vehicle.model.delMotor(vehicle.model.motors[0])
        vehicle.filter.vehicleCollisionCallback = None
        vehicle.filter.isLaggingStateChangedCallback = None
        self.__stickers = None
        self.modelsDesc = None
        self.onModelChanged = None
        id = getattr(self, '_VehicleAppearance__stippleCallbackID', None)
        if id is not None:
            BigWorld.cancelCallback(id)
            self.__stippleCallbackID = None
        if self.__periodicTimerID is not None:
            BigWorld.cancelCallback(self.__periodicTimerID)
            self.__periodicTimerID = None
        self.__crashedTracksCtrl.destroy()
        self.__crashedTracksCtrl = None
        return

    def start(self, vehicle, prereqs=None):
        self.__vehicle = vehicle
        descr = vehicle.typeDescriptor
        player = BigWorld.player()
        BigWorld.addShadowEntity(vehicle)
        if prereqs is None:
            descr.chassis['hitTester'].loadBspModel()
            descr.hull['hitTester'].loadBspModel()
            descr.turret['hitTester'].loadBspModel()
        if vehicle.useAdvancedPhysics:
            filter = BigWorld.WGVehicleFilter2()
        else:
            filter = BigWorld.WGVehicleFilter()
        vehicle.filter = filter
        filter.vehicleWidth = descr.chassis['topRightCarryingPoint'][0] * 2
        filter.vehicleCollisionCallback = player.handleVehicleCollidedVehicle
        filter.isLaggingStateChangedCallback = self.__onIsLaggingStateChanged
        filter.vehicleMaxMove = descr.physics['speedLimits'][0] * 2.0
        filter.vehicleMinNormalY = descr.physics['minPlaneNormalY']
        for p1, p2, p3 in descr.physics['carryingTriangles']:
            filter.addTriangle((p1[0], 0, p1[1]), (p2[0], 0, p2[1]), (p3[0], 0, p3[1]))

        self.turretMatrix.target = filter.turretMatrix
        self.gunMatrix.target = filter.gunMatrix
        self.__createGunRecoil()
        self.__createStickers()
        self.__createExhaust()
        self.__skeletonCollider = _SkeletonCollider(vehicle, self)
        self.__crashedTracksCtrl = _CrashedTrackController(vehicle, self)
        self.__fashion = BigWorld.WGVehicleFashion()
        _setupVehicleFashion(self.__fashion, self.__vehicle)
        for desc in self.modelsDesc.itervalues():
            modelName = desc['_stateFunc'](vehicle, self.__curDamageState)
            if prereqs is not None:
                try:
                    desc['model'] = prereqs[modelName]
                except Exception:
                    LOG_ERROR("can't load model <%s> from prerequisites." % modelName)

                if desc['model'] is None:
                    desc['model'] = BigWorld.Model(desc['_stateFunc'](vehicle, 'undamaged'))
            else:
                desc['model'] = BigWorld.Model(modelName)
            desc['model'].outsideOnly = 1
            if desc.has_key('boundEffects'):
                desc['boundEffects'] = bound_effects.ModelBoundEffects(desc['model'])

        self.__setupModels()
        state = self.__curDamageState
        if state == 'destroyed':
            self.__playEffect('destruction', 'static')
        elif state == 'exploded':
            self.__playEffect('explosion', 'static')
        self.__firstInit = False
        if self.__invalidateLoading:
            self.__invalidateLoading = True
            self.__fetchModels(self.__actualDamageState)
        if vehicle.isAlive():
            model = self.modelsDesc['hull']['model']
            self.__engineSound = _getSound(model, descr.engine['sound'])
            self.__movementSound = _getSound(model, descr.chassis['sound'])
            self.__isEngineSoundMutedByLOD = False
        if vehicle.isAlive() and self.__vehicle.isPlayer:
            self.__vibrationsCtrl = VibrationControllersManager()
            if LightFx.LightManager.g_instance is not None and LightFx.LightManager.g_instance.isEnabled():
                self.__lightFxCtrl = LightFxControllersManager(self.__vehicle)
        vehicle.model.stipple = True
        self.__stippleCallbackID = BigWorld.callback(_VEHICLE_APPEAR_TIME, self.__disableStipple)
        self.__setupDustTrails()
        self.__setupTrackDamageSounds()
        self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME * random.uniform(0.01, 1.0), self.__onPeriodicTimer)
        return

    def showStickers(self, bool):
        self.__showStickers = bool
        for compName, stickerDesc in self.__stickers.iteritems():
            alpha = stickerDesc['alpha'] if bool else 0.0
            stickerDesc['stickers'].setAlphas(alpha, alpha)

    def changeVisibility(self, modelName, modelVisible, attachmentsVisible):
        desc = self.modelsDesc.get(modelName, None)
        if desc is None:
            LOG_ERROR("invalid model's description name <%s>." % modelName)
        desc['model'].visible = modelVisible
        desc['model'].visibleAttachments = attachmentsVisible
        desc['_visibility'] = (modelVisible, attachmentsVisible)
        if modelName == 'chassis':
            self.__crashedTracksCtrl.setVisible(modelVisible)
        return

    def onVehicleHealthChanged(self):
        vehicle = self.__vehicle
        if not vehicle.isAlive():
            BigWorld.wgDelEdgeDetectEntity(vehicle)
            if vehicle.health > 0:
                self.changeEngineMode((0, 0))
            elif self.__engineSound is not None:
                self.__engineSound.stop()
                self.__engineSound = None
            if self.__movementSound is not None:
                self.__movementSound.stop()
                self.__movementSound = None
            if self.__waterSound is not None:
                self.__waterSound.stop()
                self.__waterSound = None
            if self.__turretSound is not None:
                self.__turretSound.stop()
                self.__turretSound = None
        state = self.__getDamageModelsState(vehicle.health)
        if state != self.__curDamageState:
            if self.__loadingProgress == len(self.modelsDesc) and not self.__firstInit:
                if state == 'undamaged':
                    self.__stopEffects()
                elif state == 'destroyed':
                    self.__playEffect('destruction')
                elif state == 'exploded':
                    self.__playEffect('explosion')
                self.__fetchModels(state)
            else:
                self.__actualDamageState = state
                self.__invalidateLoading = True
        return

    def changeEngineMode(self, mode):
        self.__engineMode = mode
        powerMode = mode[0]
        dirFlags = mode[1]
        self.__changeExhaust(powerMode)
        self.__updateBlockedMovement()
        sound = self.__engineSound
        if sound is not None:
            param = sound.param('load')
            if param is not None:
                param.value = powerMode + (0.0 if param.value != powerMode else 0.001)
                self.__engineSndVariation = [BigWorld.time() + 1.0, False]
        return

    def removeDamageSticker(self, code):
        for stickerDesc in self.__stickers.itervalues():
            dmgSticker = stickerDesc['damageStickers'].get(code)
            if dmgSticker is not None:
                if dmgSticker['handle'] is not None:
                    stickerDesc['stickers'].delDamageSticker(dmgSticker['handle'])
                del stickerDesc['damageStickers'][code]

        return

    def addDamageSticker(self, code, componentName, stickerID, segStart, segEnd):
        stickerDesc = self.__stickers[componentName]
        if stickerDesc['damageStickers'].has_key(code):
            return
        desc = items.vehicles.g_cache.damageStickers['descrs'][stickerID]
        texSize = self.__damageStickersTexSize
        texCoords = Math.Vector4(desc['texCoords'][0] / texSize[0], desc['texCoords'][1] / texSize[1], desc['texSizes'][0] / texSize[0], desc['texSizes'][1] / texSize[1])
        segment = segEnd - segStart
        segLen = segment.lengthSquared
        if segLen != 0:
            segStart -= 0.25 * segment / math.sqrt(segLen)
        angle = random.random() * math.pi * 2.0
        rotAxis = 0
        for i in xrange(1, 3):
            if abs(segment[i]) > abs(segment[rotAxis]):
                rotAxis = i

        up = Math.Vector3()
        up[(rotAxis + 1) % 3] = math.sin(angle)
        up[(rotAxis + 2) % 3] = math.cos(angle)
        stickerDesc = self.__stickers[componentName]
        model = self.modelsDesc[componentName]['model']
        handle = stickerDesc['stickers'].addDamageSticker(texCoords, segStart, segEnd, desc['modelSizes'], up)
        stickerDesc['damageStickers'][code] = {'texCoords': texCoords,
         'rayStart': segStart,
         'rayEnd': segEnd,
         'up': up,
         'sizes': desc['modelSizes'],
         'handle': handle}

    def receiveShotImpulse(self, dir, impulse):
        if self.__curDamageState == 'undamaged':
            self.__fashion.receiveShotImpulse(dir, impulse)
            self.__crashedTracksCtrl.receiveShotImpulse(dir, impulse)

    def addCrashedTrack(self, isLeft):
        self.__crashedTracksCtrl.addTrack(isLeft)
        sound = self.__trackSounds[0 if isLeft else 1]
        if sound is not None and sound[1] is not None:
            sound[1].play()
        return

    def delCrashedTrack(self, isLeft):
        self.__crashedTracksCtrl.delTrack(isLeft)

    def __fetchModels(self, modelState):
        self.__curDamageState = modelState
        self.__loadingProgress = 0
        for desc in self.modelsDesc.itervalues():
            BigWorld.fetchModel(desc['_stateFunc'](self.__vehicle, modelState), getattr(self, desc['_callbackFunc']))

    def __attemptToSetupModels(self):
        self.__loadingProgress += 1
        if self.__loadingProgress == len(self.modelsDesc):
            if self.__invalidateLoading:
                self.__invalidateLoading = False
                self.__fetchModels(self.__actualDamageState)
            else:
                self.__setupModels()

    def __setupModels(self):
        vehicle = self.__vehicle
        chassis = self.modelsDesc['chassis']
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        if not self.__firstInit:
            self.__detachStickers()
            delattr(gun['model'], 'wg_gunRecoil')
            self.__gunFireNode = None
            self.__attachExhaust(False)
            self.__detachDustTrails()
            self.__destroyTrackDamageSounds()
            self.__skeletonCollider.detach()
            self.__crashedTracksCtrl.reset()
            chassis['model'].stopSoundsOnDestroy = False
            hull['model'].stopSoundsOnDestroy = False
            turret['model'].stopSoundsOnDestroy = False
            hull['_node'].detach(hull['model'])
            turret['_node'].detach(turret['model'])
            gun['_node'].detach(gun['model'])
            chassis['model'] = chassis['_fetchedModel']
            hull['model'] = hull['_fetchedModel']
            turret['model'] = turret['_fetchedModel']
            gun['model'] = gun['_fetchedModel']
            delattr(vehicle.model, 'wg_fashion')
            self.__reattachEffects()
        vehicle.model = None
        vehicle.model = chassis['model']
        vehicle.model.delMotor(vehicle.model.motors[0])
        matrix = vehicle.matrix
        matrix.notModel = True
        vehicle.model.addMotor(BigWorld.Servo(matrix))
        self.__assembleModels()
        self.__skeletonCollider.attach()
        if not self.__firstInit:
            chassis['boundEffects'].reattachTo(chassis['model'])
            hull['boundEffects'].reattachTo(hull['model'])
            turret['boundEffects'].reattachTo(turret['model'])
            gun['boundEffects'].reattachTo(gun['model'])
        modelsState = self.__curDamageState
        if modelsState == 'undamaged':
            self.__attachStickers()
            vehicle.model.wg_fashion = self.__fashion
            self.__attachExhaust(True)
            gun['model'].wg_gunRecoil = self.__gunRecoil
            self.__gunFireNode = gun['model'].node('HP_gunFire')
        elif modelsState == 'destroyed' or modelsState == 'exploded':
            self.__attachStickers(0.3, True)
        else:
            assert False
        self.__updateCamouflage()
        self.__applyVisibility()
        self.onModelChanged()
        return

    def __reattachEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.reattachTo(self.modelsDesc['hull']['model'])
        return

    def __playEffect(self, kind, *modifs):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.stop()
        vehicle = self.__vehicle
        effects = random.choice(vehicle.typeDescriptor.type.effects[kind])
        self.__effectsPlayer = EffectsListPlayer(effects[1], effects[0], showShockWave=vehicle.isPlayer, showFlashBang=vehicle.isPlayer, start=vehicle.position + Math.Vector3(0.0, -1.0, 0.0), end=vehicle.position + Math.Vector3(0.0, 1.0, 0.0))
        self.__effectsPlayer.play(self.modelsDesc['hull']['model'], *modifs)
        return

    def __updateCamouflage(self):
        texture = ''
        colors = [0,
         0,
         0,
         0]
        weights = Math.Vector4(1, 0, 0, 0)
        camouflagePresent = False
        vDesc = self.__vehicle.typeDescriptor
        camouflageParams = self.__getCamouflageParams(self.__vehicle)
        customization = items.vehicles.g_cache.customization(vDesc.type.id[0])
        defaultTiling = None
        if camouflageParams is not None and customization is not None:
            camouflage = customization['camouflages'].get(camouflageParams[0])
            if camouflage is not None:
                camouflagePresent = True
                texture = camouflage['texture']
                colors = camouflage['colors']
                weights = Math.Vector4((colors[0] >> 24) / 255.0, (colors[1] >> 24) / 255.0, (colors[2] >> 24) / 255.0, (colors[3] >> 24) / 255.0)
                defaultTiling = camouflage['tiling'].get(vDesc.type.compactDescr)
        if self.__curDamageState != 'undamaged':
            weights *= 0.1
        if camouflageParams is not None:
            _, camStartTime, camNumDays = camouflageParams
            if camNumDays > 0:
                timeAmount = (time.time() - camStartTime) / (camNumDays * 86400)
                if timeAmount > 1.0:
                    weights *= _CAMOUFLAGE_MIN_INTENSITY
                elif timeAmount > 0:
                    weights *= (1.0 - timeAmount) * (1.0 - _CAMOUFLAGE_MIN_INTENSITY) + _CAMOUFLAGE_MIN_INTENSITY
        for descId in ('chassis', 'hull', 'turret', 'gun'):
            exclusionMap = vDesc.type.camouflageExclusionMask
            tiling = defaultTiling
            if tiling is None:
                tiling = vDesc.type.camouflageTiling
            model = self.modelsDesc[descId]['model']
            tgDesc = None
            if descId == 'turret':
                tgDesc = vDesc.turret
            elif descId == 'gun':
                tgDesc = vDesc.gun
            if tgDesc is not None:
                coeff = tgDesc.get('camouflageTiling')
                if coeff is not None:
                    if tiling is not None:
                        tiling = (tiling[0] * coeff[0],
                         tiling[1] * coeff[1],
                         tiling[2] * coeff[2],
                         tiling[3] * coeff[3])
                    else:
                        tiling = coeff
                if tgDesc.has_key('camouflageExclusionMask'):
                    exclusionMap = tgDesc['camouflageExclusionMask']
            if camouflagePresent and exclusionMap != '':
                useCamouflage = texture != ''
                fashion = None
                if hasattr(model, 'wg_fashion'):
                    fashion = model.wg_fashion
                elif hasattr(model, 'wg_gunRecoil'):
                    fashion = model.wg_gunRecoil
                elif useCamouflage:
                    fashion = model.wg_baseFashion = BigWorld.WGBaseFashion()
                elif hasattr(model, 'wg_baseFashion'):
                    delattr(model, 'wg_baseFashion')
                if fashion is not None:
                    useCamouflage and fashion.setCamouflage(texture, exclusionMap, tiling, colors[0], colors[1], colors[2], colors[3], weights)
                else:
                    fashion.removeCamouflage()

        return

    def __getCamouflageParams(self, vehicle):
        vDesc = vehicle.typeDescriptor
        vehicleInfo = BigWorld.player().arena.vehicles.get(vehicle.id)
        if vehicleInfo is not None:
            camouflagePseudoname = vehicleInfo['actions'].get('hunting')
            if camouflagePseudoname is not None:
                camouflIdsByNation = {0: {'black': 29,
                     'gold': 30,
                     'red': 31,
                     'silver': 32},
                 1: {'black': 25,
                     'gold': 26,
                     'red': 27,
                     'silver': 28}}
                camouflIds = camouflIdsByNation.get(vDesc.type.id[0])
                if camouflIds is not None:
                    ret = camouflIds.get(camouflagePseudoname)
                    if ret is not None:
                        return (ret, time.time(), 100.0)
        return vDesc.camouflage

    def __stopEffects(self):
        if self.__effectsPlayer is not None:
            self.__effectsPlayer.stop()
        self.__effectsPlayer = None
        return

    def __onPeriodicTimer(self):
        self.__periodicTimerID = None
        try:
            self.__updateVibrations()
        except Exception:
            LOG_CURRENT_EXCEPTION()

        try:
            if self.__lightFxCtrl is not None:
                self.__lightFxCtrl.update(self.__vehicle)
        except:
            LOG_CURRENT_EXCEPTION()

        if not self.__vehicle.isAlive():
            return
        else:
            try:
                self.__isInWater = BigWorld.wg_collideWater(self.__vehicle.position, self.__vehicle.position + Math.Vector3(0, 2, 0)) != -1
                self.__distanceFromPlayer = (BigWorld.camera().position - self.__vehicle.position).length
                self.__updateCurrTerrainMatKinds()
                self.__updateMovementSounds()
                self.__updateTurretSound()
                self.__updateBlockedMovement()
                self.__updateEffectsLOD()
                self.__updateDustTrails()
            except Exception:
                LOG_CURRENT_EXCEPTION()

            self.__periodicTimerID = BigWorld.callback(_PERIODIC_TIME, self.__onPeriodicTimer)
            return

    def __updateMovementSounds(self):
        vehicle = self.__vehicle
        isTooFar = self.__distanceFromPlayer > _LOD_DISTANCE_SOUNDS
        if isTooFar != self.__isEngineSoundMutedByLOD:
            self.__isEngineSoundMutedByLOD = isTooFar
            if isTooFar:
                if self.__engineSound is not None:
                    self.__engineSound.stop()
                if self.__movementSound is not None:
                    self.__movementSound.stop()
                if self.__waterSound is not None:
                    self.__waterSound.stop()
            else:
                if self.__engineSound is not None:
                    self.__engineSound.play()
                if self.__movementSound is not None:
                    self.__movementSound.play()
                if self.__waterSound is not None:
                    self.__waterSound.play()
                self.changeEngineMode(self.__engineMode)
        time = BigWorld.time()
        sound = self.__engineSound
        powerMode = self.__engineMode[0]
        if sound is not None:
            param = sound.param('load')
            if param is not None:
                if param.value == 0.0 and param.value != powerMode:
                    seekSpeed = param.seekSpeed
                    param.seekSpeed = 0
                    param.value = powerMode
                    param.seekSpeed = seekSpeed
                    self.__engineSndVariation = [time + 1.0, False]
                if time >= self.__engineSndVariation[0]:
                    if powerMode >= 3.0:
                        if self.__engineSndVariation[1]:
                            self.__engineSndVariation[1] = False
                            param.value = powerMode + (random.random() * 0.1 - 0.05)
                        elif random.random() < 0.35:
                            peak = random.random() * 0.35 + 0.1
                            self.__engineSndVariation[0] = time + peak * 0.9
                            self.__engineSndVariation[1] = True
                            param.value = powerMode + peak
                    elif powerMode >= 2.0:
                        self.__engineSndVariation[0] = time + random.choice((0.5, 0.25, 0.75, 0.25))
                        value = param.value + (random.random() * 0.17 - 0.085)
                        value = min(value, powerMode + 0.25)
                        value = max(value, powerMode - 0.1)
                        param.value = value
        speedFraction = vehicle.filter.speedInfo.value[0]
        speedFraction = abs(speedFraction / vehicle.typeDescriptor.physics['speedLimits'][0])
        sound = self.__movementSound
        if sound is not None:
            param = sound.param('speed')
            if param is not None:
                param.value = min(1.0, speedFraction)
        if self.__isInWater and powerMode > 1.0 and speedFraction > 0.01:
            if self.__waterSound is None:
                self.__waterSound = _getSound(self.modelsDesc['chassis']['model'], _MOVE_THROUGH_WATER_SOUND)
                self.__waterSound.play()
        elif self.__waterSound is not None:
            self.__waterSound.stop()
            self.__waterSound = None
        return

    def __updateTurretSound(self):
        if not _ENABLE_TURRET_ROTATION_SOUND:
            return
        else:
            gunRotator = BigWorld.player().gunRotator
            currYaw = Math.Matrix(gunRotator.turretMatrix).yaw
            if self.__prevTurretYaw is None:
                self.__prevTurretYaw = currYaw
                return
            prevParamValue = 0
            if self.__turretSound is not None:
                param = self.__turretSound.param('speed')
                if param is not None:
                    prevParamValue = param.value
            yawSpeed = abs(currYaw - self.__prevTurretYaw) / _PERIODIC_TIME
            if yawSpeed >= _TURRET_SOUND_MIN_YAW_SPEED and gunRotator.estimatedTurretRotationTime > _TURRET_SOUND_PREDICT_STOP_TIME:
                if self.__turretSound is None:
                    self.__turretSound = _getSound(self.modelsDesc['turret']['model'], _TURRET_ROTATION_SOUND)
                    self.__turretSound.play()
                elif prevParamValue > 1.0:
                    _seekSoundParam(self.__turretSound, 'speed', 0)
            elif self.__turretSound is not None:
                if prevParamValue < 2.0:
                    _seekSoundParam(self.__turretSound, 'speed', 2.0)
            self.__prevTurretYaw = currYaw
            return

    def __updateBlockedMovement(self):
        blockingForce = 0.0
        powerMode, dirFlags = self.__engineMode
        vehSpeed = self.__vehicle.filter.speedInfo.value[0]
        if abs(vehSpeed) < 0.25 and powerMode > 1:
            if dirFlags & 1:
                blockingForce = -0.5
            elif dirFlags & 2:
                blockingForce = 0.5
        self.fashion.staticPitchSwingForce = blockingForce

    def __updateEffectsLOD(self):
        disableExhaust = self.__distanceFromPlayer > _LOD_DISTANCE_EXHAUST
        if disableExhaust != self.__exhaustDisabledByLOD:
            self.__exhaustDisabledByLOD = disableExhaust
            self.__changeExhaust(self.__engineMode[0])
        if not self.__distanceFromPlayer > _LOD_DISTANCE_DUST:
            disableDust = not BigWorld.wg_isVehicleDustEnabled()
            if disableDust != self.__dustDisabled:
                self.__dustDisabled = disableDust
                disableDust and self.__detachDustTrails()

    def __setupDustTrails(self):
        model = self.modelsDesc['chassis']['model']
        trPoint = self.__vehicle.typeDescriptor.chassis['topRightCarryingPoint']
        mMidLeft = Math.Matrix()
        mMidLeft.setTranslate((-trPoint[0], 0, trPoint[1] * 0.5))
        mMidRight = Math.Matrix()
        mMidRight.setTranslate((trPoint[0], 0, trPoint[1] * 0.5))
        self.__dustTrailNodes = [model.node('', mMidLeft), model.node('', mMidRight)]
        i = 0
        for nodeName in ('HP_Track_LFront', 'HP_Track_RFront', 'HP_Track_LRear', 'HP_Track_RRear'):
            node = None
            try:
                node = model.node(nodeName)
            except:
                matr = mMidLeft if i % 2 == 0 else mMidRight
                node = model.node('', matr)

            self.__dustTrailNodes.append(node)

        self.__dustTrailsDelayBeforeShow = BigWorld.time() + 2.0
        return

    def __detachDustTrails(self):
        for node in self.__dustTrails.iterkeys():
            for dustTrailState in self.__dustTrails[node]:
                node.detach(dustTrailState[0])

        self.__dustTrails = {}

    def __setupTrackDamageSounds(self):
        for i in xrange(2):
            try:
                fakeModel = BigWorld.player().newFakeModel()
                self.__dustTrailNodes[i].attach(fakeModel)
                self.__trackSounds[i] = (fakeModel, fakeModel.getSound('/hits/hits/hit_treads'))
            except:
                self.__trackSounds[i] = None
                LOG_CURRENT_EXCEPTION()

        return

    def __destroyTrackDamageSounds(self):
        for i in xrange(2):
            if self.__trackSounds[i] is not None:
                self.__dustTrailNodes[i].detach(self.__trackSounds[i][0])

        self.__trackSounds = [None, None]
        return

    def __updateCurrTerrainMatKinds(self):
        worldMatrix = self.modelsDesc['chassis']['model'].matrix
        for iTrack in xrange(2):
            centerNode = self.__dustTrailNodes[iTrack]
            mMidNode = Math.Matrix(centerNode.local)
            mMidNode.postMultiply(worldMatrix)
            testPoint = mMidNode.translation
            res = BigWorld.wg_collideSegment(self.__vehicle.spaceID, testPoint + (0, 2, 0), testPoint + (0, -2, 0), 16)
            self.__currTerrainMatKind[iTrack] = res[2] if res is not None else 0

        self.__fashion.setCurrTerrainMatKinds(self.__currTerrainMatKind[0], self.__currTerrainMatKind[1])
        return

    def __updateDustTrails(self):
        if self.__dustDisabled:
            return
        elif self.__vehicle.typeDescriptor.chassis['effects'] is None:
            self.__dustDisabled = True
            return
        else:
            time = BigWorld.time()
            if time < self.__dustTrailsDelayBeforeShow:
                return
            movementInfo = Math.Vector4(self.__fashion.movementInfo.value)
            maxMovement = self.__fashion.maxMovement
            for iTrack in xrange(2):
                trackSpeedRel = movementInfo[iTrack + 1] / maxMovement
                centerNode = self.__dustTrailNodes[iTrack]
                activeCornerNode = self.__dustTrailNodes[2 + iTrack + (0 if trackSpeedRel <= 0 else 2)]
                inactiveCornerNode = self.__dustTrailNodes[2 + iTrack + (0 if trackSpeedRel > 0 else 2)]
                currMatKind = self.__currTerrainMatKind[iTrack]
                if trackSpeedRel != 0:
                    self.__createDustParticleSystemIfNeeded(centerNode, iTrack, 'dust', currMatKind, 100 + iTrack)
                    self.__createDustParticleSystemIfNeeded(activeCornerNode, iTrack, 'mud', currMatKind, 102 + iTrack)
                for node in (centerNode, activeCornerNode, inactiveCornerNode):
                    nodeEffects = self.__dustTrails.get(node)
                    if nodeEffects is not None:
                        for nodeEffect in nodeEffects:
                            if not nodeEffect[1] != currMatKind:
                                stopParticles = node == inactiveCornerNode
                                relEmissionRate = 0
                                relEmissionRate = self.__isInWater or nodeEffect[2] + (-0.25 if stopParticles else 0.25)
                                relEmissionRate = min(relEmissionRate, 1.0)
                                relEmissionRate = max(relEmissionRate, 0.0)
                            nodeEffect[2] = relEmissionRate
                            pixie = nodeEffect[0]
                            emissionRate = 150.0 * relEmissionRate * abs(trackSpeedRel)
                            emissionRate = min(emissionRate, 1.0)
                            basicEmissionRates = nodeEffect[4]
                            for i in xrange(pixie.nSystems()):
                                source = pixie.system(i).action(1)
                                source.rate = emissionRate * basicEmissionRates[i]

                for node, nodeEffects in self.__dustTrails.iteritems():
                    for nodeEffect in nodeEffects:
                        effectInactive = abs(nodeEffect[2] * trackSpeedRel) < 0.0001
                        if effectInactive:
                            timeOfStop = nodeEffect[3]
                            if timeOfStop == 0:
                                nodeEffect[3] = time
                            elif time - timeOfStop > 5.0:
                                pixie = nodeEffect[0]
                                node.detach(pixie)
                                nodeEffects.remove(nodeEffect)
                        else:
                            nodeEffect[3] = 0

            return

    def switchFireVibrations(self, bStart):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.switchFireVibrations(bStart)
        return

    def executeHitVibrations(self, shotResult):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeHitVibrations(shotResult)
        return

    def executeRammingVibrations(self, matKind=None):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeRammingVibrations(self.__vehicle.getSpeed(), matKind)
        return

    def executeShootingVibrations(self, caliber):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeShootingVibrations(caliber)
        return

    def executeCriticalHitVibrations(self, vehicle, extrasName):
        if self.__vibrationsCtrl is not None:
            self.__vibrationsCtrl.executeCriticalHitVibrations(vehicle, extrasName)
        return

    def __updateVibrations(self):
        if self.__vibrationsCtrl is None:
            return
        else:
            vehicle = self.__vehicle
            crashedTrackCtrl = self.__crashedTracksCtrl
            self.__vibrationsCtrl.update(vehicle, crashedTrackCtrl.isLeftTrackBroken(), crashedTrackCtrl.isRightTrackBroken())
            return

    def __createDustParticleSystemIfNeeded(self, node, iTrack, effectGroup, currMatKind, drawOrder):
        if currMatKind != 0:
            effectIndex = material_kinds.EFFECT_MATERIAL_INDEXES_BY_IDS.get(currMatKind)
            if effectIndex is None:
                return
        else:
            effectIndex = -1
            player = BigWorld.player()
            if isinstance(player, Avatar.PlayerAvatar):
                arenaSpecificEffect = player.arena.typeDescriptor.defaultGroundEffect
                if arenaSpecificEffect is not None:
                    if arenaSpecificEffect == 'None':
                        return
                    if not isinstance(arenaSpecificEffect, int):
                        effectIndex = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES.get(arenaSpecificEffect)
                        effectIndex = -1 if effectIndex is None else effectIndex
                        player.arena.typeDescriptor.defaultGroundEffect = effectIndex
                    else:
                        effectIndex = arenaSpecificEffect
        effectDesc = self.__vehicle.typeDescriptor.chassis['effects'].get(effectGroup)
        if effectDesc is None:
            return
        else:
            effectName = effectDesc[0].get(effectIndex)
            if effectName is None or effectName == 'none' or effectName == 'None':
                return
            if isinstance(effectName, list):
                effectName = effectName[iTrack]
            nodeEffects = self.__dustTrails.get(node)
            if nodeEffects is None:
                nodeEffects = []
                self.__dustTrails[node] = nodeEffects
            else:
                for nodeEffect in nodeEffects:
                    if nodeEffect[1] == currMatKind:
                        return

            pixie = Pixie.create(effectName)
            pixie.drawOrder = drawOrder
            node.attach(pixie)
            basicRates = []
            for i in xrange(pixie.nSystems()):
                source = pixie.system(i).action(1)
                basicRates.append(source.rate)

            nodeEffects.append([pixie,
             currMatKind,
             0,
             0,
             basicRates])
            return

    def __getDamageModelsState(self, vehicleHealth):
        if vehicleHealth > 0:
            return 'undamaged'
        elif vehicleHealth == 0:
            return 'destroyed'
        else:
            return 'exploded'

    def __onChassisModelLoaded(self, model):
        self.__onModelLoaded('chassis', model)

    def __onHullModelLoaded(self, model):
        self.__onModelLoaded('hull', model)

    def __onTurretModelLoaded(self, model):
        self.__onModelLoaded('turret', model)

    def __onGunModelLoaded(self, model):
        self.__onModelLoaded('gun', model)

    def __onModelLoaded(self, name, model):
        if self.modelsDesc is None:
            return
        else:
            desc = self.modelsDesc[name]
            if model is not None:
                desc['_fetchedModel'] = model
            else:
                desc['_fetchedModel'] = desc['model']
                modelState = desc['_stateFunc'](self.__vehicle, self.__curDamageState)
                LOG_ERROR('Model %s not loaded.' % modelState)
            self.__attemptToSetupModels()
            return

    def __assembleModels(self):
        vehicle = self.__vehicle
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        try:
            hull['_node'] = vehicle.model.node(_ROOT_NODE_NAME)
            hull['_node'].attach(hull['model'])
            turret['_node'] = hull['model'].node('HP_turretJoint', self.turretMatrix)
            turret['_node'].attach(turret['model'])
            gun['_node'] = turret['model'].node('HP_gunJoint', self.gunMatrix)
            gun['_node'].attach(gun['model'])
            if vehicle.isPlayer:
                player = BigWorld.player()
                if player.inputHandler is not None:
                    arcadeCamera = player.inputHandler.ctrls['arcade'].camera
                    if arcadeCamera is not None:
                        arcadeCamera.addModelsToCollideWith([hull['model'], turret['model']])
        except Exception:
            LOG_ERROR('Can not assemble models for %s.' % vehicle.typeDescriptor.name)
            raise

        if HAS_DEV_RESOURCES and _ENABLE_VEHICLE_VALIDATION:
            self.__validateCallbackId = BigWorld.callback(0.01, self.__validateAssembledModel)
        return

    def __applyVisibility(self):
        vehicle = self.__vehicle
        chassis = self.modelsDesc['chassis']
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        chassis['model'].visible = chassis['_visibility'][0]
        chassis['model'].visibleAttachments = chassis['_visibility'][1]
        hull['model'].visible = hull['_visibility'][0]
        hull['model'].visibleAttachments = hull['_visibility'][1]
        turret['model'].visible = turret['_visibility'][0]
        turret['model'].visibleAttachments = turret['_visibility'][1]
        gun['model'].visible = gun['_visibility'][0]
        gun['model'].visibleAttachments = gun['_visibility'][1]

    def __validateAssembledModel(self):
        self.__validateCallbackId = None
        vehicle = self.__vehicle
        vDesc = vehicle.typeDescriptor
        state = self.__curDamageState
        chassis = self.modelsDesc['chassis']
        hull = self.modelsDesc['hull']
        turret = self.modelsDesc['turret']
        gun = self.modelsDesc['gun']
        _validateCfgPos(chassis, hull, vDesc.chassis['hullPosition'], 'hullPosition', vehicle, state)
        _validateCfgPos(hull, turret, vDesc.hull['turretPositions'][0], 'turretPosition', vehicle, state)
        _validateCfgPos(turret, gun, vDesc.turret['gunPosition'], 'gunPosition', vehicle, state)
        return

    def __createExhaust(self):
        exhaust = self.__vehicle.typeDescriptor.hull['exhaust']
        pixieName = exhaust['pixie']
        rates = exhaust['rates']
        for i in xrange(len(exhaust['nodes'])):
            pixie = Pixie.create(pixieName)
            pixie.drawOrder = 50 + i
            self.__exhaust.append([None, pixie])
            for i in xrange(pixie.nSystems()):
                source = pixie.system(i).action(1)
                source.rate = rates[0]

        return

    def __attachExhaust(self, attach):
        nodes = self.__vehicle.typeDescriptor.hull['exhaust']['nodes']
        hullModel = self.modelsDesc['hull']['model']
        if attach:
            for i in xrange(len(nodes)):
                pair = self.__exhaust[i]
                pair[0] = hullModel.node(nodes[i])
                pair[0].attach(pair[1])

        else:
            for pair in self.__exhaust:
                if pair[0] is not None:
                    pair[0].detach(pair[1])

        return

    def __changeExhaust(self, engineMode):
        rates = self.__vehicle.typeDescriptor.hull['exhaust']['rates']
        for pair in self.__exhaust:
            pixie = pair[1]
            for i in xrange(pixie.nSystems()):
                source = pixie.system(i).action(1)
                source.rate = rates[engineMode] if not self.__exhaustDisabledByLOD else 0

    def __createGunRecoil(self):
        recoilDescr = self.__vehicle.typeDescriptor.gun['recoil']
        recoil = BigWorld.WGGunRecoil(_GUN_RECOIL_NODE_NAME)
        recoil.setLod(recoilDescr['lodDist'])
        recoil.setDuration(recoilDescr['backoffTime'], recoilDescr['returnTime'])
        recoil.setDepth(recoilDescr['amplitude'])
        self.__gunRecoil = recoil

    def __createStickers(self):
        vDesc = self.__vehicle.typeDescriptor
        g_cache = items.vehicles.g_cache
        damageTexName = g_cache.damageStickers['textureName']
        damageTex = BigWorld.PyTextureProvider(damageTexName)
        self.__damageStickersTexSize = (float(damageTex.width), float(damageTex.height))
        emblemPositions = (('hull', vDesc.hull['emblemSlots']), ('gun' if vDesc.turret['showEmblemsOnGun'] else 'turret', vDesc.turret['emblemSlots']), ('turret' if vDesc.turret['showEmblemsOnGun'] else 'gun', []))
        clanID = BigWorld.player().arena.vehicles[self.__vehicle.id]['clanDBID']
        for componentName, slots in emblemPositions:
            stickers = VehicleStickers.VehicleStickers(vDesc, slots)
            stickers.setClanID(clanID)
            self.__stickers[componentName] = {'stickers': stickers,
             'damageStickers': {},
             'alpha': 1.0}

    def __attachStickers(self, alpha=1.0, emblemsOnly=False):
        actualAlpha = alpha * self.__vehicle.typeDescriptor.type.emblemsAlpha
        actualAlpha = alpha if self.__showStickers else 0.0
        isDamaged = self.__curDamageState != 'undamaged'
        for componentName, stickerDesc in self.__stickers.iteritems():
            stickers = stickerDesc['stickers']
            stickers.setAlphas(actualAlpha, actualAlpha)
            stickerDesc['alpha'] = actualAlpha
            model = self.modelsDesc[componentName]['model']
            node = self.modelsDesc[componentName]['_node']
            stickers.attachStickers(model, node, isDamaged)
            if emblemsOnly:
                continue
            for dmgSticker in stickerDesc['damageStickers'].itervalues():
                if dmgSticker['handle'] is not None:
                    stickers.delDamageSticker(dmgSticker['handle'])
                    dmgSticker['handle'] = None
                    LOG_WARNING('Adding %s damage sticker to occupied slot' % componentName)
                dmgSticker['handle'] = stickers.addDamageSticker(dmgSticker['texCoords'], dmgSticker['rayStart'], dmgSticker['rayEnd'], dmgSticker['sizes'], dmgSticker['rayUp'])

        return

    def __detachStickers(self):
        for componentName, stickerDesc in self.__stickers.iteritems():
            stickerDesc['stickers'].detachStickers()
            for dmgSticker in stickerDesc['damageStickers'].itervalues():
                dmgSticker['handle'] = None

        return

    def __disableStipple(self):
        self.__vehicle.model.stipple = False
        self.__stippleCallbackID = None
        return

    def __onIsLaggingStateChanged(self, isLaggingNow):
        if self.__fashion is None:
            return
        else:
            if not isLaggingNow:
                self.__fashion.disableAccelSwinging = True
                BigWorld.callback(1.0, self.__reEnableAccelSwinging)
            return

    def __reEnableAccelSwinging(self):
        if self.__fashion is not None:
            self.__fashion.disableAccelSwinging = False
        return


class StippleManager():

    def __init__(self):
        self.__stippleDescs = {}

    def showFor(self, vehicle, model):
        model.stipple = True
        BigWorld.player().addModel(model)
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self.__removeStippleModel, vehicle.id))
        self.__stippleDescs[vehicle.id] = (model, callbackID)

    def hideIfExistFor(self, vehicle):
        desc = self.__stippleDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            BigWorld.player().delModel(desc[0])
            del self.__stippleDescs[vehicle.id]
        return

    def destroy(self):
        for model, callbackID in self.__stippleDescs.itervalues():
            BigWorld.cancelCallback(callbackID)
            BigWorld.player().delModel(model)

        self.__stippleDescs = None
        return

    def __removeStippleModel(self, vehID):
        BigWorld.player().delModel(self.__stippleDescs[vehID][0])
        del self.__stippleDescs[vehID]


class _CrashedTrackController():

    def __init__(self, vehicle, va):
        self.__vehicle = vehicle.proxy
        self.__va = weakref.ref(va)
        self.__flags = 0
        self.__model = None
        self.__fashion = None
        self.__inited = True
        self.__forceHide = False
        self.__loadInfo = [False, False]
        return

    def isLeftTrackBroken(self):
        return self.__flags & 1

    def isRightTrackBroken(self):
        return self.__flags & 2

    def destroy(self):
        self.__vehicle = None
        return

    def setVisible(self, bool):
        self.__forceHide = not bool
        self.__setupTracksHiding(not bool)

    def addTrack(self, isLeft):
        if not self.__inited:
            return
        else:
            if isLeft:
                self.__flags |= 1
            else:
                self.__flags |= 2
            if self.__model is None:
                self.__loadInfo = [True, isLeft]
                BigWorld.fetchModel(self.__va().modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed'), self.__onModelLoaded)
            if self.__fashion is None:
                self.__fashion = BigWorld.WGVehicleFashion(True)
                _setupVehicleFashion(self.__fashion, self.__vehicle, True)
            self.__setupTracksHiding()
            return

    def delTrack(self, isLeft):
        if not self.__inited or self.__fashion is None:
            return
        else:
            if self.__loadInfo[0] and self.__loadInfo[1] == isLeft:
                self.__loadInfo = [False, False]
            if isLeft:
                self.__flags &= -2
            else:
                self.__flags &= -3
            self.__setupTracksHiding()
            if self.__flags == 0 and self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            return

    def receiveShotImpulse(self, dir, impulse):
        if not self.__inited or self.__fashion is None:
            return
        else:
            self.__fashion.receiveShotImpulse(dir, impulse)
            return

    def reset(self):
        if not self.__inited:
            return
        else:
            self.__flags = 0
            if self.__model is not None:
                self.__va().modelsDesc['chassis']['model'].root.detach(self.__model)
                self.__model = None
                self.__fashion = None
            return

    def __setupTracksHiding(self, force=False):
        if force or self.__forceHide:
            tracks = (True, True)
            invTracks = (True, True)
        else:
            tracks = (self.__flags & 1, self.__flags & 2)
            invTracks = (not tracks[0], not tracks[1])
        self.__va().fashion.hideTracks(*tracks)
        if self.__fashion is not None:
            self.__fashion.hideTracks(*invTracks)
        return

    def __onModelLoaded(self, model):
        if self.__va() is None or not self.__loadInfo[0] or not self.__inited:
            return
        else:
            va = self.__va()
            self.__loadInfo = [False, False]
            if model:
                self.__model = model
            else:
                self.__inited = False
                modelState = va.modelsDesc['chassis']['_stateFunc'](self.__vehicle, 'destroyed')
                LOG_ERROR('Model %s not loaded.' % modelState)
                return
            try:
                self.__model.wg_fashion = self.__fashion
                va.modelsDesc['chassis']['model'].root.attach(self.__model)
            except:
                va.fashion.hideTracks(False, False)
                self.__inited = False
                LOG_CURRENT_EXCEPTION()

            return


class _SkeletonCollider():

    def __init__(self, vehicle, vehicleAppearance):
        self.__vehicle = vehicle.proxy
        self.__vAppearance = weakref.proxy(vehicleAppearance)
        self.__boxAttachments = list()
        descr = vehicle.typeDescriptor
        descList = [('Scene Root', descr.chassis['hitTester'].bbox),
         ('Scene Root', descr.hull['hitTester'].bbox),
         ('Scene Root', descr.turret['hitTester'].bbox),
         ('Scene Root', descr.gun['hitTester'].bbox)]
        self.__createBoxAttachments(descList)
        vehicle.skeletonCollider = BigWorld.SkeletonCollider()
        for boxAttach in self.__boxAttachments:
            vehicle.skeletonCollider.addCollider(boxAttach)

        self.__vehicleHeight = self.__computeVehicleHeight()

    def destroy(self):
        delattr(self.__vehicle, 'skeletonCollider')
        self.__vehicle = None
        self.__vAppearance = None
        self.__boxAttachments = None
        return

    def attach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).attach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).attach(collider)
        self.__vehicle.model.height = self.__vehicleHeight

    def detach(self):
        va = self.__vAppearance.modelsDesc
        collider = self.__vehicle.skeletonCollider.getCollider(0)
        va['chassis']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(1)
        va['hull']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(2)
        va['turret']['model'].node(collider.name).detach(collider)
        collider = self.__vehicle.skeletonCollider.getCollider(3)
        va['gun']['model'].node(collider.name).detach(collider)

    def __computeVehicleHeight(self):
        desc = self.__vehicle.typeDescriptor
        turretBBox = desc.turret['hitTester'].bbox
        gunBBox = desc.gun['hitTester'].bbox
        hullBBox = desc.hull['hitTester'].bbox
        hullTopY = desc.chassis['hullPosition'][1] + hullBBox[1][1]
        turretTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + turretBBox[1][1]
        gunTopY = desc.chassis['hullPosition'][1] + desc.hull['turretPositions'][0][1] + desc.turret['gunPosition'][1] + gunBBox[1][1]
        return max(hullTopY, max(turretTopY, gunTopY))

    def __createBoxAttachments(self, descList):
        for desc in descList:
            boxAttach = BigWorld.BoxAttachment()
            boxAttach.name = desc[0]
            boxAttach.minBounds = desc[1][0]
            boxAttach.maxBounds = desc[1][1]
            self.__boxAttachments.append(boxAttach)


def _almostZero(val, epsilon=0.0004):
    return -epsilon < val < epsilon


def _createWheelsListByTemplate(startIndex, template, count):
    return [ '%s%d' % (template, i) for i in range(startIndex, startIndex + count) ]


def _setupVehicleFashion(fashion, vehicle, isCrashedTrack=False):
    vDesc = vehicle.typeDescriptor
    tracesCfg = vDesc.chassis['traces']
    tracksCfg = vDesc.chassis['tracks']
    wheelsCfg = vDesc.chassis['wheels']
    swingingCfg = vDesc.hull['swinging']
    fashion.movementInfo = vehicle.filter.movementInfo
    fashion.maxMovement = vDesc.physics['speedLimits'][0]
    fashion.setPitchSwinging(_ROOT_NODE_NAME, *swingingCfg['pitchParams'])
    fashion.setRollSwinging(_ROOT_NODE_NAME, *swingingCfg['rollParams'])
    fashion.setShotSwinging(_ROOT_NODE_NAME, swingingCfg['sensitivityToImpulse'])
    fashion.setLods(tracesCfg['lodDist'], wheelsCfg['lodDist'], tracksCfg['lodDist'], swingingCfg['lodDist'])
    fashion.setTracks(tracksCfg['leftMaterial'], tracksCfg['rightMaterial'], tracksCfg['textureScale'])
    if isCrashedTrack:
        return
    for group in wheelsCfg['groups']:
        nodes = _createWheelsListByTemplate(group[3], group[1], group[2])
        fashion.addWheelGroup(group[0], group[4], nodes)

    for wheel in wheelsCfg['wheels']:
        fashion.addWheel(wheel[0], wheel[2], wheel[1])

    textures = {}
    for matKindName, texId in DecalMap.g_instance.getTextureSet(tracesCfg['textureSet']).iteritems():
        for matKind in material_kinds.EFFECT_MATERIAL_IDS_BY_NAMES[matKindName]:
            textures[matKind] = texId

    fashion.setTrackTraces(tracesCfg['bufferPrefs'], textures, tracesCfg['centerOffset'], tracesCfg['size'])


def _getSound(model, soundName):
    try:
        sound = model.playSound(soundName)
        if sound is None:
            raise Exception, "can not load sound '%s'" % soundName
        return sound
    except Exception:
        LOG_CURRENT_EXCEPTION()
        return

    return


def _restoreSoundParam(sound, paramName, paramValue):
    param = sound.param(paramName)
    if param is not None and param.value == 0.0 and param.value != paramValue:
        seekSpeed = param.seekSpeed
        param.seekSpeed = 0
        param.value = paramValue
        param.seekSpeed = seekSpeed
    return


def _seekSoundParam(sound, paramName, paramValue):
    param = sound.param(paramName)
    if param is not None and param.value != paramValue:
        seekSpeed = param.seekSpeed
        param.seekSpeed = 0
        param.value = paramValue
        param.seekSpeed = seekSpeed
    return


def _validateCfgPos(srcModelDesc, dstModelDesc, cfgPos, paramName, vehicle, state):
    invMat = Math.Matrix(srcModelDesc['model'].root)
    invMat.invert()
    invMat.preMultiply(Math.Matrix(dstModelDesc['_node']))
    realOffset = invMat.applyToOrigin()
    length = (realOffset - cfgPos).length
    if length > 0.01 and not _almostZero(realOffset.length):
        modelState = srcModelDesc['_stateFunc'](self.__vehicle, state)
        LOG_WARNING('%s parameter is incorrect. \n Note: it must be <%s>.\nPlayer: %s; Model: %s' % (paramName,
         realOffset,
         vehicle.publicInfo['name'],
         modelState))
        dstModelDesc['model'].visibleAttachments = True
        dstModelDesc['model'].visible = False
