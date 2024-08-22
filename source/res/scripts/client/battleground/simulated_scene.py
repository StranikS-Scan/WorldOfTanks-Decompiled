# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/battleground/simulated_scene.py
import math
import logging
import Event
import BigWorld
import Math
import SimulatedVehicle
import math_utils
import AreaDestructibles
from collections import namedtuple
from avatar_components.avatar_postmortem_component import SimulatedVehicleType
from battleground.kill_cam_visuals import EffectsController
from constants import SHELL_TYPES
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from helpers.CallbackDelayer import CallbackPauseManager, TimeDeltaMeter
from vehicle_systems.tankStructure import TankPartNames
from wotdecorators import noexcept
from skeletons.map_activities import IMapActivities
from avatar_components.CombatEquipmentManager import CombatEquipmentManager
from simulation_movement_tracker import SimulationMovementTracker, SimulationMovementData
_ANIMATION_EASING_CURVE = math_utils.linearTween
_ANIMATION_DISTANCE_UPPER_LIMIT = 8.0
ANIMATION_DURATION_BEFORE_SHOT = 3.0
ANIMATION_REAL_TIME_DURATION = 1.0
DATA_POINTS_AMOUNT = 5
_GAMEPLAY_ENTITIES_TO_HIDE = ['Vehicle',
 'DetachedTurret',
 'BasicMine',
 'AreaOfEffect',
 'AttackArtilleryFort',
 'AttackBomber',
 'PersonalDeathZone',
 'ApplicationPoint']
PostEffectSettings = namedtuple('PostEffectSettings', 'contrast, saturation, vignette')
_logger = logging.getLogger(__name__)

class _SimulationTimeScale(object):
    PAUSED = 0.0
    REAL_TIME = 1.0


class SimulatedScene(object):

    def __init__(self, dataSettings):
        super(SimulatedScene, self).__init__()
        self.__enabled = False
        self.__postFx = self._PostEffectsManager(dataSettings)
        self.__vehicleAnimators = {}
        self.__animatorsInProgress = 0
        self.__allAppearanceReadyVehicles = set()
        self.__allSimulatedVehicles = set()
        self.__rawSimulationData = None
        self.__trajectoryPoints = None
        self.__killerIsSpotted = None
        self.__simulatedKillerID = None
        self.__simulatedVictimID = None
        self.__effectsController = EffectsController()
        self.onAllVehiclesLoaded = Event.Event()
        self.onSimulatedSceneHasEnded = Event.Event()
        self.onAnimationsCompleted = Event.Event()
        trackerTickDelay = ANIMATION_REAL_TIME_DURATION / DATA_POINTS_AMOUNT
        self.__movementTracker = SimulationMovementTracker(trackerTickDelay, DATA_POINTS_AMOUNT)
        return

    @property
    def simulatedKillerID(self):
        return self.__simulatedKillerID

    @property
    def simulatedVictimID(self):
        return self.__simulatedVictimID

    def create(self):
        self.__movementTracker.create()

    def destroy(self):
        self.__movementTracker.destroy()
        self.__movementTracker = None
        return

    def enableScene(self, rawSimulationData, trajectoryPoints, killerIsSpotted):
        self.__enabled = True
        self.__rawSimulationData = rawSimulationData
        self.__trajectoryPoints = trajectoryPoints
        self.__killerIsSpotted = killerIsSpotted
        self.__postFx.enablePostEffects()
        self.__hideGameplayEntities()
        BigWorld.PyGroundEffectManager().stopAll()
        BigWorld.wg_clearTraces()
        self.__pauseParticlesAndEffects(True)
        self.__createSimulatedVehicles()
        self.__prepareAnimations()

    def startAnimations(self, shotID):
        shotMomentData, killMomentData = self.__movementTracker.getData(shotID)
        movementDataT0, lastSectionT0 = shotMomentData
        movementDataT1, lastSectionT1 = killMomentData
        movementDataT0, movementDataT1 = self.__truncateMovementData(movementDataT0, movementDataT1)
        if self.__simulatedKillerID:
            killerPosition = Math.Vector3(self.__rawSimulationData.get('attacker').get('position'))
        else:
            killerPosition = None
        playerPosition = Math.Vector3(self.__rawSimulationData.get('player').get('position'))
        self.__animatorsInProgress = len(self.__vehicleAnimators)
        for simVehID, animator in self.__vehicleAnimators.iteritems():
            simVehicle = BigWorld.entity(simVehID)
            if not simVehicle:
                self.__onAnimatorFinished()
                continue
            simPosition = Math.Vector3(simVehicle.simulationData_position)
            if killerPosition:
                distanceToKiller = (killerPosition - simPosition).length
                distanceToPlayer = (playerPosition - simPosition).length
                shouldUseT0 = distanceToKiller < distanceToPlayer
            else:
                shouldUseT0 = False
            movementData = movementDataT0 if shouldUseT0 else movementDataT1
            realID = simVehicle.realVehicleID
            vehMovementData = [ point.get(realID) for point in movementData if realID in point ]
            lastSectionDuration = lastSectionT0 if shouldUseT0 else lastSectionT1
            if vehMovementData:
                lastPointDuration = vehMovementData[-1].duration
            else:
                lastPointDuration = 0
            currentTurretYaw, currentGunPitch = simVehicle.simulationData_gunAngles
            trackStates = simVehicle.simulationData_brokenTracks
            simulatedPoint = SimulationMovementData(lastSectionDuration + lastPointDuration, simPosition, simVehicle.simulationData_rotation, currentTurretYaw, currentGunPitch, trackStates)
            isAttacker = simVehicle.simulationData_simulationType == SimulatedVehicleType.ATTACKER
            if not vehMovementData:
                vehMovementData.append(simulatedPoint)
            elif isAttacker or not shouldUseT0:
                vehMovementData[-1] = simulatedPoint
            animator.start(simVehicle, vehMovementData)

        self.updateParticlesTimeScale()
        return

    def disableScene(self):
        if not self.__enabled:
            self.__onSimulatedSceneEnded()
            return
        else:
            _logger.info('[SimulatedScene] disableScene() Disabling Kill Cam Scene')
            for animator in self.__vehicleAnimators.itervalues():
                animator.onFinished -= self.__onAnimatorFinished
                animator.destroy()

            for simVehID in self.__allSimulatedVehicles:
                simVeh = BigWorld.entity(simVehID)
                if simVeh is not None and not simVeh.isDestroyed:
                    BigWorld.destroyEntity(simVehID)

            self.__allSimulatedVehicles.clear()
            self.__allAppearanceReadyVehicles.clear()
            self.__effectsController.destroy()
            self.__vehicleAnimators.clear()
            self.__postFx.disablePostEffects()
            self.__pauseParticlesAndEffects(False)
            self.__allSimulatedVehicles.clear()
            self.__allAppearanceReadyVehicles.clear()
            self.__showGameplayEntities()
            self.__rawSimulationData = None
            self.__trajectoryPoints = None
            self.__killerIsSpotted = None
            self.__enabled = False
            return

    def hideEdgeEffects(self):
        self.__effectsController.hideEdges()

    def updateParticlesTimeScale(self, isPause=False):
        if isPause or not self.__isVehicleAnimationInProgress():
            timeScale = _SimulationTimeScale.PAUSED
        else:
            timeScale = _SimulationTimeScale.REAL_TIME / ANIMATION_DURATION_BEFORE_SHOT
        BigWorld.wg_setWorldTimeScale(timeScale)
        for animator in self.__vehicleAnimators.itervalues():
            animator.setTimeScale(timeScale)

    def pauseOrResumeAnimations(self, isPause):
        self.updateParticlesTimeScale(isPause)
        for animator in self.__vehicleAnimators.itervalues():
            animator.pause(isPause)

    def vehicleLoaded(self, vehicleID):
        if self.__simulatedKillerID is None or self.__simulatedKillerID != vehicleID:
            simulatedVehicle = BigWorld.entities.get(vehicleID)
            if simulatedVehicle:
                simulatedVehicle.appearance.disableCustomEffects()
        self.__allAppearanceReadyVehicles.add(vehicleID)
        if self.__simulatedVehiclesAppearanceReady():
            self.onAllVehiclesLoaded()
        return

    def displayEffects(self, vehicleID):
        simulatedVehicle = BigWorld.entity(vehicleID)
        segments = self.__rawSimulationData['projectile']['segments'] if 'segments' in self.__rawSimulationData['projectile'] else []
        shellCompDecr = self.__rawSimulationData['projectile']['shellCompDescr'] if 'shellCompDescr' in self.__rawSimulationData['projectile'] else []
        projectileData = self.__rawSimulationData['projectile']
        if segments:
            simulatedVehicle.showKillingSticker(shellCompDecr, projectileData['hasProjectilePierced'], projectileData['hasNonPiercedDamage'], segments)
            decodedHitPoint = calculateWorldHitPoint(simulatedVehicle, segments)
            if decodedHitPoint:
                self.__trajectoryPoints[-1] = decodedHitPoint
        self.__effectsController.displayKillCamEffects(simulatedVehicle.appearance, simulatedVehicle.getMaxComponentIndex(), projectileData['hasProjectilePierced'], projectileData['hasNonPiercedDamage'], self.__isAttackerSPG(), self.__rawSimulationData['attacker']['spotted'], projectileData['shellKind'] == SHELL_TYPES.HIGH_EXPLOSIVE, projectileData['explosionRadius'], self.__trajectoryPoints, segments, projectileData['impactPoint'], projectileData['ricochetCount'] > 0)

    def saveKillSnapshot(self):
        self.__movementTracker.saveSnapshot(isKill=True)

    def setPendingShotID(self, shotID):
        self.__movementTracker.setPendingShotID(shotID)

    def getMovementData(self, shotID):
        return self.__movementTracker.getData(shotID)

    def __onAnimatorFinished(self):
        self.__animatorsInProgress -= 1
        if self.__animatorsInProgress == 0:
            self.onAnimationsCompleted()

    def __simulatedVehiclesAppearanceReady(self):
        return len(self.__allAppearanceReadyVehicles) == len(self.__allSimulatedVehicles)

    def __createSimulatedVehicle(self, simulatedData, isPlayerVehicle=False):
        publicInfo = simulatedData.get('publicInfo', None)
        positionTuple = simulatedData.get('position', None)
        rotationTuple = simulatedData.get('rotation', None)
        if positionTuple is None or publicInfo is None or rotationTuple is None:
            return
        else:
            avatar = BigWorld.player()
            spaceID = avatar.spaceID
            vehID = BigWorld.createEntity('SimulatedVehicle', spaceID, 0, positionTuple, rotationTuple, {'publicInfo': publicInfo,
             'isPlayerVehicle': isPlayerVehicle,
             'realVehicleID': simulatedData.get('vehicleID', None),
             'simulationData_position': simulatedData.get('position', (0, 0, 0)),
             'simulationData_rotation': simulatedData.get('rotation', (0, 0, 0)),
             'simulationData_velocity': simulatedData.get('velocity', (0, 0, 0)),
             'simulationData_angVelocity': simulatedData.get('angVelocity', (0, 0, 0)),
             'simulationData_simulationType': simulatedData.get('simulationType', None),
             'simulationData_health': simulatedData.get('health', publicInfo['maxHealth']),
             'simulationData_engineMode': simulatedData.get('engineMode', (1, 0)),
             'simulationData_gunAngles': simulatedData.get('gunAngles', (0, 0)),
             'simulationData_turretAndGunSpeed': simulatedData.get('turretAndGunSpeed', (0, 0)),
             'simulationData_damageStickers': simulatedData.get('damageStickers', []),
             'simulationData_brokenTracks': simulatedData.get('brokenTracks', []),
             'simulationData_siegeState': simulatedData.get('siegeState', False),
             'simulationData_wheelsState': simulatedData.get('wheelsState', 0),
             'simulationData_wheelsSteering': simulatedData.get('wheelsSteering', []),
             'simulationData_tracksInAir': simulatedData.get('trackInAir', (False, False))})
            simulatedVehicle = BigWorld.entities.get(vehID)
            simulatedVehicle.onAppearanceLoaded += self.vehicleLoaded
            return vehID

    def __truncateMovementData(self, movementDataT0, movementDataT1):
        killerVehicle = BigWorld.entities.get(self.__simulatedKillerID) if self.__simulatedKillerID else None
        if not killerVehicle:
            return (movementDataT0, movementDataT1)
        else:
            killerID = killerVehicle.realVehicleID
            killerMovement = [ point.get(killerID, None) for point in movementDataT0 if killerID in point ]
            playerVehicle = BigWorld.entities.get(self.__simulatedVictimID)
            playerID = playerVehicle.realVehicleID
            playerMovement = [ point.get(playerID, None) for point in movementDataT1 if playerID in point ]
            if not killerMovement or not playerMovement:
                return (movementDataT0, movementDataT1)
            totalDistance = 0.0
            totalDuration = killerMovement[-1].duration if killerMovement else 0.0
            lastPosition = None
            firstIndexT0 = len(killerMovement)
            for point in reversed(killerMovement):
                firstIndexT0 -= 1
                if totalDistance >= _ANIMATION_DISTANCE_UPPER_LIMIT:
                    break
                if not point:
                    continue
                if not lastPosition:
                    lastPosition = point.position
                    continue
                distance = (point.position - lastPosition).length
                totalDistance += distance
                totalDuration += point.duration

            playerDuration = 0.0
            firstIndexT1 = len(playerMovement)
            for point in reversed(playerMovement):
                firstIndexT1 -= 1
                if playerDuration >= totalDuration:
                    break
                if not point:
                    continue
                playerDuration += point.duration

            return (movementDataT0[firstIndexT0:], movementDataT1[firstIndexT1:])

    @staticmethod
    def __pauseParticlesAndEffects(isPause):
        effectsTimeScale = _SimulationTimeScale.PAUSED if isPause else _SimulationTimeScale.REAL_TIME
        BigWorld.wg_setWorldTimeScale(effectsTimeScale)
        AreaDestructibles.g_destructiblesManager.setPause(isPause)
        BigWorld.player().setProjectilesPause(isPause)
        dependency.instance(IMapActivities).setPauseVisuals(isPause)
        BigWorld.wg_setKillAllActiveEffects()
        CombatEquipmentManager.setGUIVisible(BigWorld.player(), not isPause)
        CombatEquipmentManager.setVFXVisible(BigWorld.player(), not isPause)

    def __isVehicleAnimationInProgress(self):
        for animator in self.__vehicleAnimators.itervalues():
            if animator.isInProcess():
                return True

        return False

    def __hideGameplayEntities(self):
        avatar = BigWorld.player()
        avatar.isSimulationSceneActive = True
        BigWorld.wg_withholdEntityTypes(_GAMEPLAY_ENTITIES_TO_HIDE, True)

    def __showGameplayEntities(self):
        avatar = BigWorld.player()
        avatar.isSimulationSceneActive = False
        BigWorld.wg_withholdEntityTypes(_GAMEPLAY_ENTITIES_TO_HIDE, False)
        playerVehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if playerVehicle:
            if playerVehicle.isStarted:
                self.__onSimulatedSceneEnded()
            else:
                playerVehicle.onAppearanceReady += self.__onSimulatedSceneEnded

    def __createSimulatedVehicles(self):
        self.__simulatedVictimID = self.__createSimulatedVehicle(self.__rawSimulationData.get('player', None), True)
        self.__allSimulatedVehicles.add(self.__simulatedVictimID)
        if self.__killerIsSpotted:
            self.__simulatedKillerID = self.__createSimulatedVehicle(self.__rawSimulationData.get('attacker', None))
            self.__allSimulatedVehicles.add(self.__simulatedKillerID)
        for otherVehicle in self.__rawSimulationData.get('others', None):
            otherSimID = self.__createSimulatedVehicle(otherVehicle)
            self.__allSimulatedVehicles.add(otherSimID)

        return

    def __prepareAnimations(self):
        for simVehID in self.__allSimulatedVehicles:
            animator = SimulationAnimator()
            animator.onFinished += self.__onAnimatorFinished
            self.__vehicleAnimators[simVehID] = animator

    def __onSimulatedSceneEnded(self):
        avatar = BigWorld.player()
        playerVehicle = BigWorld.entities.get(avatar.playerVehicleID)
        if playerVehicle:
            playerVehicle.onAppearanceReady -= self.__onSimulatedSceneEnded
        self.onSimulatedSceneHasEnded()

    def __isAttackerSPG(self):
        return 'vehicleType' in self.__rawSimulationData['attacker'] and VEHICLE_CLASS_NAME.SPG == self.__rawSimulationData['attacker']['vehicleType']

    def __getTurretAndGunLimits(self, simVeh):
        if simVeh.typeDescriptor:
            turretYawLimits = simVeh.typeDescriptor.gun.turretYawLimits
            gunPitchLimits = simVeh.typeDescriptor.gun.pitchLimits['absolute']
        else:
            turretYawLimits = gunPitchLimits = None
        return (turretYawLimits, gunPitchLimits)

    class _PostEffectsManager(object):

        def __init__(self, data):
            self.__killCamPostEffectSettings = PostEffectSettings(data.readFloat('contrast'), data.readFloat('saturation'), Math.Vector4(data.readVector4('vignette')))
            self.__defaultPostEffectSettings = None
            self.__getDefaultSettings()
            return

        def destroy(self):
            self.disablePostEffects()

        def __getDefaultSettings(self):
            self.__defaultPostEffectSettings = PostEffectSettings(round(BigWorld.getColorContrast(), 2), BigWorld.getColorSaturation(), BigWorld.WGRenderSettings().getVignetteSettings())

        def enablePostEffects(self):
            self.__getDefaultSettings()
            BigWorld.setColorContrast(self.__killCamPostEffectSettings.contrast)
            BigWorld.setColorSaturation(self.__killCamPostEffectSettings.saturation)
            BigWorld.WGRenderSettings().setVignetteSettings(self.__killCamPostEffectSettings.vignette)

        def disablePostEffects(self):
            BigWorld.setColorContrast(self.__defaultPostEffectSettings.contrast)
            BigWorld.setColorSaturation(self.__defaultPostEffectSettings.saturation)
            BigWorld.WGRenderSettings().setVignetteSettings(self.__defaultPostEffectSettings.vignette)


class SimulationAnimator(CallbackPauseManager, TimeDeltaMeter):
    __TIME_SCALE = ANIMATION_DURATION_BEFORE_SHOT / ANIMATION_REAL_TIME_DURATION

    def __init__(self):
        CallbackPauseManager.__init__(self)
        TimeDeltaMeter.__init__(self)
        self._pos0 = Math.Vector3()
        self._pos1 = Math.Vector3()
        self._rot0 = Math.Matrix()
        self._rot1 = Math.Matrix()
        self._tRot0 = Math.Matrix()
        self._tRot1 = Math.Matrix()
        self._duration = 0
        self._simulatedVehicle = None
        self._vehicleRadius = 0.0
        self._trackScroll = (0.0, 0.0)
        self._posError = (0, 0, 0)
        self._engineMode = (0, 0)
        self.__timeScale = _SimulationTimeScale.REAL_TIME
        self.__speed = 0.0
        self.__yawSpeed = 0.0
        self.onFinished = Event.Event()
        self.__movementData = None
        self.__section = 0
        self.__lastSection = 0
        self.__sectionDuration = 0.0
        self.__sectionElapsedTime = 0.0
        return

    def destroy(self):
        self.stop()

    def start(self, vehicle, movementData):
        self._simulatedVehicle = vehicle
        self.__movementData = movementData
        self.__lastSection = len(self.__movementData) - 1
        self.__section = 0
        self._duration = ANIMATION_DURATION_BEFORE_SHOT
        origin = self.__movementData[0]
        if self._simulatedVehicle.appearance.wheelsAnimator:
            self._simulatedVehicle.wheelsState = self._simulatedVehicle.simulationData_wheelsState
            self._simulatedVehicle.appearance.wheelsAnimator.overrideSteeringDataLink(self._simulatedVehicle.getSimulatedSteeringDataLink())
        self.__setVehiclePosition(origin.position, origin.direction, origin.turretYaw, origin.gunPitch)
        self._vehicleRadius = self._simulatedVehicle.appearance.computeFullVehicleLength() / 2
        self.__initSection(0)

    def finish(self):
        self._duration = 0.0
        self.__stopTick()
        if self.__movementData:
            endPoint = self.__movementData[-1]
            self.__setVehiclePosition(endPoint.position, endPoint.direction, endPoint.turretYaw, endPoint.gunPitch)
        self.delayCallback(0.0, self.__onFinish)

    def __onFinish(self):
        self.onFinished()
        self.stop()

    def isInProcess(self):
        return self._duration > 0

    def stop(self):
        self._duration = 0.0
        self.__sectionDuration = 0.0
        self.__section = 0
        self.__timeScale = _SimulationTimeScale.REAL_TIME
        self.__stopTick()
        if self._simulatedVehicle is not None:
            if hasattr(self._simulatedVehicle, 'speedInfo'):
                speedInfo = self._simulatedVehicle.speedInfo
                speedInfo.set(Math.Vector4(0.0, 0.0, 0.0, 0.0))
        self._simulatedVehicle = None
        return

    def pause(self, isInPause):
        if isInPause:
            self.pauseCallbacks()
            self.__updateTrackAndWheelScroll(0.0, 0.0)
        else:
            self.measureDeltaTime()
            self.resumeCallbacks()

    def setTimeScale(self, timeScale):
        self.__timeScale = timeScale

    def reset(self):
        self.stop()

    @noexcept
    def tick(self):
        deltaTime = self.measureDeltaTime()
        self.__sectionElapsedTime += deltaTime
        et = self.__sectionElapsedTime
        d = self.__sectionDuration
        progress = math_utils.clamp01(_ANIMATION_EASING_CURVE(et, 1.0, d))
        positionT = math_utils.lerp(self._pos0, self._pos1, progress)
        rotationMatrixT = Math.slerp(self._rot0, self._rot1, progress)
        rotationT = (rotationMatrixT.roll, rotationMatrixT.pitch, rotationMatrixT.yaw)
        turretRotT = Math.slerp(self._tRot0, self._tRot1, progress)
        if self._trackStates:
            trackState = self._trackStates[self.__section + 1]
            self._simulatedVehicle.updateBrokenTracks(trackState)
        self.__setVehiclePosition(positionT, rotationT, turretRotT.yaw, turretRotT.pitch)
        leftScroll, rightScroll = self._trackScroll
        self.__updateTrackAndWheelScroll(leftScroll * self.__timeScale, rightScroll * self.__timeScale)
        self._simulatedVehicle.appearance.changeEngineMode(self._engineMode)
        if et >= d:
            self.__initSection(self.__section + 1)
            return

    def __stopTick(self):
        self.clearCallbacks()
        if self._simulatedVehicle is not None:
            if hasattr(self._simulatedVehicle, 'appearance'):
                self.__updateTrackAndWheelScroll(0.0, 0.0)
        return

    def __initSection(self, section):
        self.__section = section
        nextSection = self.__section + 1
        if self.__lastSection < nextSection:
            self.finish()
            return
        self._numOfMovementData = len(self.__movementData)
        point0 = self.__movementData[self.__section]
        point1 = self.__movementData[nextSection]
        self._trackStates = [ trackState for _, _, _, _, _, trackState in self.__movementData ]
        self.__startSection(point0.position, point1.position, point0.direction, point1.direction, point0.turretYaw, point1.turretYaw, point0.gunPitch, point1.gunPitch, point1.duration)
        speedInfo = Math.Vector4(self.__speed, self.__yawSpeed, self.__speed, self.__yawSpeed)
        self._simulatedVehicle.speedInfo.set(speedInfo)

    def __startSection(self, p0, p1, r0, r1, tY0, tY1, gP0, gP1, duration):
        self._pos0 = Math.Vector3(p0)
        self._pos1 = Math.Vector3(p1)
        self._rot0 = math_utils.createRotationMatrix((r0[2], r0[1], r0[0]))
        self._rot1 = math_utils.createRotationMatrix((r1[2], r1[1], r1[0]))
        self._tRot0 = math_utils.createRotationMatrix((tY0, gP0, 0))
        self._tRot1 = math_utils.createRotationMatrix((tY1, gP1, 0))
        self.__sectionElapsedTime = 0.0
        self.__sectionDuration = duration * self.__TIME_SCALE
        self.__speed = 0.0
        self.__yawSpeed = 0.0
        if self.__sectionDuration < 0.001:
            _logger.warning('SimulationAnimator.__startSection: Too short animation, skip')
            self.__initSection(self.__section + 1)
            return
        forwardVector0 = self._rot0.applyToAxis(2)
        forwardVector1 = self._rot1.applyToAxis(2)
        rawTranslation = self._pos1 - self._pos0
        self.__speed = rawTranslation.length / duration
        self.__yawSpeed = (self._rot1.yaw - self._rot0.yaw) / duration
        speed = self.__speed
        direction = Math.Vector3(rawTranslation)
        direction.normalise()
        engineDirection = 1
        if forwardVector0.dot(direction) < 0.0:
            speed = -speed
            engineDirection = 2
        radianPerSec = math.acos(math_utils.clamp(0.0, 1.0, forwardVector0.dot(forwardVector1)))
        if radianPerSec > abs(speed) * 0.5:
            leftScroll = radianPerSec * self._vehicleRadius / duration
            if self.__yawSpeed > 0:
                engineDirection = 4
            else:
                engineDirection = 8
                leftScroll = -1 * leftScroll
            rightScroll = -leftScroll
        else:
            leftScroll = rightScroll = speed
        if abs(speed) > 0.01 or radianPerSec > 0.01:
            engineMode = 2
        else:
            engineMode = 1
            engineDirection = 0
        self._trackScroll = (leftScroll, rightScroll)
        self._engineMode = (engineMode, engineDirection)
        self.measureDeltaTime()
        self.delayCallback(0.0, self.tick)

    def __setVehiclePosition(self, position, direction, turretYaw, gunPitch):
        vehFilter = self._simulatedVehicle.filter
        vehFilter.reset()
        vehFilter.input(BigWorld.time(), self._simulatedVehicle.spaceID, 0, position, self._posError, direction)
        self._simulatedVehicle.turretMatrix.setRotateYPR((turretYaw, 0.0, 0.0))
        self._simulatedVehicle.gunMatrix.setRotateYPR((0.0, gunPitch, 0.0))

    def __updateTrackAndWheelScroll(self, leftScroll, rightScroll):
        if self._simulatedVehicle:
            if self._simulatedVehicle.appearance.typeDescriptor.isWheeledVehicle and self._simulatedVehicle.appearance.wheelsAnimator:

                def getWheelScrollLeft():
                    return leftScroll

                def getWheelScrollRight():
                    return rightScroll

                self._simulatedVehicle.appearance.wheelsAnimator.overrideScrollDataLink(getWheelScrollLeft, getWheelScrollRight)
            else:
                self._simulatedVehicle.appearance.updateTracksScroll(leftScroll, rightScroll)


def calculateWorldHitPoint(vehicle, segment):
    if not segment:
        return None
    else:
        points = segment
        decodedPoints = vehicle.decodeHitPoints(points)
        if not decodedPoints:
            return None
        decodedPoint = decodedPoints[-1]
        compoundModel = vehicle.appearance.compoundModel
        decodedPointPosition = decodedPoint.matrix.translation
        compoundMatrix = Math.Matrix(compoundModel.node(decodedPoint.componentName))
        if decodedPoint.componentName == TankPartNames.GUN:
            pitchMatrix = Math.Matrix()
            pitchMatrix.setRotateX(Math.Matrix(vehicle.appearance.gunMatrix).pitch)
            decodedPointPosition = pitchMatrix.applyPoint(decodedPointPosition)
        return compoundMatrix.applyPoint(decodedPointPosition)
