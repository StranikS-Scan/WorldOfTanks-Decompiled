# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_audition_wwise.py
import math
import SoundGroups
import material_kinds
import BigWorld
import WWISE
import Math
from AvatarInputHandler.mathUtils import clamp
from constants import VEHICLE_PHYSICS_MODE
from debug_utils import LOG_ERROR
from helpers.EffectMaterialCalculation import calcEffectMaterialIndex
from helpers.ValueTracker import ValueTracker
from vehicle_systems import assembly_utility
from vehicle_systems.assembly_utility import TypedProperty, LinkDescriptor
from vehicle_systems.components.engine_state import DetailedEngineStateWWISE
from items.vehicles import HP_TO_WATTS
import CommandMapping
import collections
from vehicle_systems.tankStructure import TankPartNames

class EngineAudition(assembly_utility.Component):

    def destroy(self):
        pass

    def tick(self):
        pass

    def reattachTo(self, compoundModel):
        raise NotImplementedError()

    def stopSounds(self, stopEngine=True, stopMovement=True):
        raise NotImplementedError()

    def getGunSoundObj(self):
        return None

    def deviceDestroyed(self, deviceName):
        pass

    def deviceRepairedToCritical(self, deviceName):
        pass

    def onKeyTriggered(self, isDown, key, vehicle):
        pass


class TrackCrashAudition(assembly_utility.Component):

    def destroy(self):
        pass

    def playCrashSound(self, isLeft=True, restore=False, wheeledVehicle=False):
        pass


_EFFECT_MATERIALS_HARDNESS_RTPC = {'ground': 0.1,
 'stone': 1,
 'wood': 0.5,
 'snow': 0.3,
 'sand': 0,
 'water': 0.2}
_FRICTION_ANG_FACTOR = 0.8
_FRICTION_ANG_BOUND = 0.5
_FRICTION_STRAFE_FACTOR = 0.4
_FRICTION_STRAFE_BOUND = 1.0
_PERIODIC_TIME = 0.25
_ENABLE_SOUND_DEBUG = False

class EngineAuditionWWISE(EngineAudition):
    __vt = property(lambda self: ValueTracker.instance() if _ENABLE_SOUND_DEBUG else None)
    isUnderwaterLink = LinkDescriptor()
    isInWaterLink = LinkDescriptor()
    isFlyingLink = LinkDescriptor()
    curTerrainMatKindLink = LinkDescriptor()
    leftTrackScrollLink = LinkDescriptor()
    leftTrackScrollRelativeLink = LinkDescriptor()
    rightTrackScrollLink = LinkDescriptor()
    rightTrackScrollRelativeLink = LinkDescriptor()
    detailedEngineState = TypedProperty(DetailedEngineStateWWISE)
    vehicleFilter = TypedProperty(BigWorld.WGVehicleFilter)

    def __init__(self, physicsMode, isPlayerVehicle, compoundModel, typeDesc, vehicleId):
        self.__prevVelocity = 0
        self.__prevTime = 0.0
        self.__prevTerrSwitch = None
        self.__physicsMode = physicsMode
        self.__isPlayerVehicle = isPlayerVehicle
        self.__typeDesc = typeDesc
        self.__commonTrackScroll = 0.0
        self.__engineSound = None
        self.__movementSound = None
        self.__gunSound = None
        self.__vehicleId = vehicleId
        self.__event = None
        self.__eventC = None
        self.__cameraUnit = False
        self.__stopMotionSounds = None
        self.__initSounds(compoundModel)
        BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def __initSounds(self, compoundModel):
        vehicle = BigWorld.entity(BigWorld.player().playerVehicleID)
        if vehicle is None:
            return
        else:
            if self.__isPlayerVehicle:
                if self.__typeDesc.engine['wwsoundPC'] != '':
                    self.__event = self.__typeDesc.engine['wwsoundPC']
                else:
                    self.__event = self.__typeDesc.engine['wwsound']
                if self.__typeDesc.chassis['wwsoundPC'] != '':
                    self.__eventC = self.__typeDesc.chassis['wwsoundPC']
                else:
                    self.__eventC = self.__typeDesc.chassis['wwsound']
            else:
                if self.__typeDesc.engine['wwsoundNPC'] != '':
                    self.__event = self.__typeDesc.engine['wwsoundNPC']
                else:
                    self.__event = self.__typeDesc.engine['wwsound']
                if self.__typeDesc.chassis['wwsoundNPC'] != '':
                    self.__eventC = self.__typeDesc.chassis['wwsoundNPC']
                else:
                    self.__eventC = self.__typeDesc.chassis['wwsound']
            nodeMatrix = Math.Matrix()
            nodeMatrix.set(compoundModel.node(TankPartNames.HULL))
            vehicleMProv = compoundModel.node(TankPartNames.HULL)
            vehicleMatrix = Math.Matrix()
            vehicleMatrix.set(vehicleMProv)
            self.__engineSoundHP = 'engine' + str(self.__vehicleId)
            self.__movementSoundHP = 'tracks' + str(self.__vehicleId)
            self.__gunSoundHP = 'gun' + str(self.__vehicleId)
            nodeMatrix.set(compoundModel.node(TankPartNames.GUN))
            node = nodeMatrix.translation - vehicleMatrix.translation
            self.__gunSound = SoundGroups.g_instance.WWgetSoundObject(self.__gunSoundHP, vehicleMProv, node)
            if self.__gunSound is not None:
                weaponEnergy = vehicle.appearance.gunLength * vehicle.typeDescriptor.shot['shell']['caliber']
                self.__gunSound.setRTPC('RTPC_ext_weapon_energy', weaponEnergy)
            self.__engineSound = SoundGroups.g_instance.WWgetSoundObject(self.__engineSoundHP, vehicleMProv)
            if self.__engineSound is None:
                LOG_ERROR('!!!self.__engineSound is None')
                return
            horsePower = self.__typeDesc.physics['enginePower'] / HP_TO_WATTS
            WWISE.WW_setRTCPGlobal('RTPC_ext_engine_power', horsePower)
            self.__engineSound.setSwitch('SWITCH_ext_physics_state', 'SWITCH_ext_physics_state_off' if self.__physicsMode == VEHICLE_PHYSICS_MODE.STANDARD else 'SWITCH_ext_physics_state_on')
            nodeMatrix.set(compoundModel.node(TankPartNames.TURRET))
            node = nodeMatrix.translation - vehicleMatrix.translation
            if self.__eventC == '':
                LOG_ERROR('Tracks sound is not defined for = {0}'.format(self.__typeDesc.name))
                self.__movementSound = None
            else:
                self.__movementSound = SoundGroups.g_instance.WWgetSoundObject(self.__movementSoundHP, vehicleMProv, node)
            if self.__movementSound is not None:
                self.__movementSound.setSwitch('SWITCH_ext_physics_state', 'SWITCH_ext_physics_state_off' if self.__physicsMode == VEHICLE_PHYSICS_MODE.STANDARD else 'SWITCH_ext_physics_state_on')
                self.__movementSound.setRTPC('RTPC_ext_vehicle_weight', self.__typeDesc.physics['weight'] / 1000)
                self.__movementSound.setRTPC('RTPC_ext_engine_state', 0.0)
                self.__movementSound.setRTPC('RTPC_ext_physic_rpm_rel', 0.0)
                self.__movementSound.setRTPC('RTPC_ext_physic_rpm_abs', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_vehicle_weight', self.__typeDesc.physics['weight'] / 1000)
            self.__engineSound.setRTPC('RTPC_ext_engine_state', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_physic_rpm_rel', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_physic_rpm_abs', 0.0)
            isWheeled = 'wheeledVehicle' in vehicle.typeDescriptor.type.tags
            if isWheeled:
                self.setBigGunSwitch(False)
                soundsPair = collections.namedtuple('soundsPair', 'stop move')
                keySound = collections.namedtuple('keySound', 'key down up')
                soundSoft = 'armored_car_stop_motion_soft'
                self.__stopMotionSounds = (keySound(key=CommandMapping.CMD_MOVE_FORWARD, down=soundsPair(stop=None, move=None), up=soundsPair(stop=None, move=soundSoft)), keySound(key=CommandMapping.CMD_MOVE_BACKWARD, down=soundsPair(stop=None, move=None), up=soundsPair(stop=None, move=soundSoft)), keySound(key=CommandMapping.CMD_BLOCK_TRACKS, down=soundsPair(stop=None, move=soundSoft), up=soundsPair(stop=None, move=None)))
            return

    def reattachTo(self, compoundModel):
        hullNode = compoundModel.node(TankPartNames.HULL)
        if self.__gunSound is not None:
            self.__gunSound.matrixProvider = hullNode
        if self.__engineSound is not None:
            self.__engineSound.matrixProvider = hullNode
        if self.__movementSound is not None:
            self.__movementSound.matrixProvider = hullNode
        return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName != 'postmortem':
            return
        elif BigWorld.entity(BigWorld.player().playerVehicleID).isAlive():
            return
        elif currentVehicleId != self.__vehicleId and self.__cameraUnit:
            if self.__engineSound is not None:
                self.__engineSound.setSwitch('SWITCH_ext_postMortem', 'SWITCH_ext_postMortem_npc')
            if self.__movementSound is not None:
                self.__movementSound.setSwitch('SWITCH_ext_postMortem', 'SWITCH_ext_postMortem_npc')
            self.__cameraUnit = False
            return
        else:
            if currentVehicleId == self.__vehicleId and not self.__cameraUnit:
                if self.__engineSound is not None:
                    self.__engineSound.setSwitch('SWITCH_ext_postMortem', 'SWITCH_ext_postMortem_pc')
                if self.__movementSound is not None:
                    self.__movementSound.setSwitch('SWITCH_ext_postMortem', 'SWITCH_ext_postMortem_pc')
                self.__cameraUnit = True
            return

    def destroy(self):
        BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
        self.stopSounds()

    def onEngineStart(self):
        if SoundGroups.ENABLE_ENGINE_N_TRACKS:
            if self.__engineSound is not None and not self.__engineSound.isPlaying(self.__event):
                self.__engineSound.play(self.__event)
            if self.__movementSound is not None:
                self.__movementSound.play(self.__eventC)
        return

    def tick(self):
        if not SoundGroups.ENABLE_ENGINE_N_TRACKS:
            return
        else:
            soundEngine = self.__engineSound
            if soundEngine is None:
                return
            soundTrack = self.__movementSound
            if soundTrack is None:
                return
            vehicleAttached = BigWorld.player().getVehicleAttached()
            if vehicleAttached is None:
                return
            cameraUnit = vehicleAttached.id == self.__vehicleId
            speedInfo = vehicleAttached.speedInfo.value
            speed = speedInfo[0]
            soundEngine.setRTPC('RTPC_ext_rpm', clamp(0.0, 100.0, self.detailedEngineState.rpm))
            soundTrack.setRTPC('RTPC_ext_rpm', clamp(0.0, 100.0, self.detailedEngineState.rpm))
            soundEngine.setRTPC('RTPC_ext_engine_load', self.detailedEngineState.engineLoad)
            soundTrack.setRTPC('RTPC_ext_engine_load', self.detailedEngineState.engineLoad)
            if cameraUnit:
                WWISE.WW_setRTCPGlobal('RTPC_ext_engine_load_global', self.detailedEngineState.engineLoad)
            soundEngine.setRTPC('RTPC_ext_submersion', 1 if self.isUnderwaterLink() else 0)
            soundTrack.setRTPC('RTPC_ext_submersion', 1 if self.isUnderwaterLink() else 0)
            if cameraUnit:
                WWISE.WW_setState('STATE_underwater', 'STATE_underwater_on' if self.isUnderwaterLink() else 'STATE_underwater_off')
            soundEngine.setRTPC('RTPC_ext_speed_abs', clamp(-10, 30, speed))
            soundTrack.setRTPC('RTPC_ext_speed_abs', clamp(-10, 30, speed))
            soundEngine.setRTPC('RTPC_ext_speed_rel', clamp(-1.0, 1.0, self.detailedEngineState.relativeSpeed))
            soundTrack.setRTPC('RTPC_ext_speed_rel', clamp(-1.0, 1.0, self.detailedEngineState.relativeSpeed))
            soundEngine.setRTPC('RTPC_ext_speed_rel2', self.detailedEngineState.relativeSpeed)
            soundTrack.setRTPC('RTPC_ext_speed_rel2', self.detailedEngineState.relativeSpeed)
            soundEngine.setRTPC('RTPC_ext_rot_speed_abs', clamp(-1.0, 1.0, self.detailedEngineState.rotationSpeed))
            soundTrack.setRTPC('RTPC_ext_rot_speed_abs', clamp(-1.0, 1.0, self.detailedEngineState.rotationSpeed))
            soundEngine.setRTPC('RTPC_ext_rot_speed_rel', clamp(-1.0, 1.0, self.detailedEngineState.roatationRelSpeed))
            soundTrack.setRTPC('RTPC_ext_rot_speed_rel', clamp(-1.0, 1.0, self.detailedEngineState.roatationRelSpeed))
            if cameraUnit:
                if self.__physicsMode == VEHICLE_PHYSICS_MODE.STANDARD or not self.__isPlayerVehicle:
                    soundTrack.setRTPC('RTPC_ext_gear_2', self.detailedEngineState.gear2)
                    soundTrack.setRTPC('RTPC_ext_gear_3', self.detailedEngineState.gear3)
                    soundEngine.setRTPC('RTPC_ext_gear_2', self.detailedEngineState.gear2)
                    soundEngine.setRTPC('RTPC_ext_gear_3', self.detailedEngineState.gear3)
                    soundEngine.setRTPC('RTPC_ext_gear_num', clamp(0.0, 4.0, self.detailedEngineState.gearNum))
                    soundTrack.setRTPC('RTPC_ext_gear_num', clamp(0.0, 4.0, self.detailedEngineState.gearNum))
                else:
                    gear = self.detailedEngineState.gearNum
                    soundTrack.setRTPC('RTPC_ext_physic_rpm_rel', self.detailedEngineState.rpmPhysicRel)
                    self.__engineSound.setRTPC('RTPC_ext_physic_rpm_rel', self.detailedEngineState.rpmPhysicRel)
                    soundTrack.setRTPC('RTPC_ext_physic_rpm_abs', self.detailedEngineState.rpmPhysicAbs)
                    self.__engineSound.setRTPC('RTPC_ext_physic_rpm_abs', self.detailedEngineState.rpmPhysicAbs)
                    soundTrack.setRTPC('RTPC_ext_physic_gear', gear)
                    self.__engineSound.setRTPC('RTPC_ext_physic_gear', gear)
                    soundTrack.setRTPC('RTPC_ext_engine_state', 1.0 if gear > 0 and gear < 127 else 0.0)
                    self.__engineSound.setRTPC('RTPC_ext_engine_state', 1.0 if gear > 0 and gear < 127 else 0.0)
                    for i in range(1, 8):
                        if i != gear:
                            soundTrack.setRTPC('RTPC_ext_physic_gear_' + str(i), 0)
                            self.__engineSound.setRTPC('RTPC_ext_physic_gear_' + str(i), 0)

                    if self.detailedEngineState.gearUp:
                        soundTrack.setRTPC('RTPC_ext_physic_gear_' + str(gear), 100)
                        self.__engineSound.setRTPC('RTPC_ext_physic_gear_' + str(gear), 100)
            accelerationAbs = 0.0
            if self.__prevVelocity is not None and self.__prevTime is not None:
                accelerationAbs = (speed - self.__prevVelocity) / (BigWorld.time() - self.__prevTime)
                accelerationAbs = clamp(-1.5, 1.5, accelerationAbs)
            self.__prevVelocity = speed
            self.__prevTime = BigWorld.time()
            soundEngine.setRTPC('RTPC_ext_acc_abs', accelerationAbs)
            soundTrack.setRTPC('RTPC_ext_acc_abs', accelerationAbs)
            moveValue = 100 if math.fabs(speed) > 1.0 else 0
            soundTrack.setRTPC('RTPC_ext_move', moveValue)
            soundEngine.setRTPC('RTPC_ext_move', moveValue)
            soundEngine.setRTPC('RTPC_ext_physic_load', self.detailedEngineState.physicLoad)
            soundTrack.setRTPC('RTPC_ext_physic_load', self.detailedEngineState.physicLoad)
            if cameraUnit:
                WWISE.WW_setRTCPGlobal('RTPC_ext_physic_load_global', self.detailedEngineState.physicLoad)
                WWISE.WW_setRTCPGlobal('RTPC_ext_speed_rel_global', clamp(-1.0, 1.0, self.detailedEngineState.relativeSpeed))
                WWISE.WW_setRTCPGlobal('RTPC_ext_speed_abs_global', speed)
            soundTrack.setRTPC('RTPC_ext_flying', self.isFlyingLink())
            if not cameraUnit:
                return
            if self.__physicsMode == VEHICLE_PHYSICS_MODE.DETAILED:
                deltaR = self.rightTrackScrollRelativeLink()
                deltaL = self.leftTrackScrollRelativeLink()
                slideFriction = clamp(0.0, 1.0, max(deltaR, deltaL) / 5.0)
                soundTrack.setRTPC('RTPC_ext_slide_friction', slideFriction)
                soundEngine.setRTPC('RTPC_ext_slide_friction', slideFriction)
            matEffectsUnderTracks = dict(((effectMaterial, 0.0) for effectMaterial in _EFFECT_MATERIALS_HARDNESS_RTPC))
            currTerrainMatKind = self.curTerrainMatKindLink()
            if self.isInWaterLink():
                matEffectsUnderTracks['water'] = len(currTerrainMatKind)
            else:
                for matKind in currTerrainMatKind:
                    effectIndex = calcEffectMaterialIndex(matKind)
                    if effectIndex is not None:
                        effectMaterial = material_kinds.EFFECT_MATERIALS[effectIndex]
                        if effectMaterial in matEffectsUnderTracks:
                            matEffectsUnderTracks[effectMaterial] = matEffectsUnderTracks.get(effectMaterial, 0) + 1.0

            hardness = 0.0
            for effectMaterial, amount in matEffectsUnderTracks.iteritems():
                hardness += _EFFECT_MATERIALS_HARDNESS_RTPC.get(effectMaterial, 0) * amount

            for effectMaterial, amount in matEffectsUnderTracks.iteritems():
                if amount >= 2 and self.__prevTerrSwitch != effectMaterial:
                    soundTrack.setSwitch('SWITCH_ext_surfaceType', 'SWITCH_ext_surfaceType_' + effectMaterial)
                    self.__prevTerrSwitch = effectMaterial
                    break

            hardnessValue = hardness / len(currTerrainMatKind)
            soundTrack.setRTPC('RTPC_ext_hardness', hardnessValue)
            angPart = min(abs(self.vehicleFilter.angularSpeed) * _FRICTION_ANG_FACTOR, _FRICTION_ANG_BOUND)
            strafePart = min(abs(self.vehicleFilter.strafeSpeed) * _FRICTION_STRAFE_FACTOR, _FRICTION_STRAFE_BOUND)
            frictionValue = max(angPart, strafePart)
            soundTrack.setRTPC('RTPC_ext_friction', frictionValue)
            roughnessValue = self.detailedEngineState.roughnessValue
            if cameraUnit:
                WWISE.WW_setRTCPGlobal('RTPC_ext_roughness_global', math.fabs(roughnessValue))
            soundTrack.setRTPC('RTPC_ext_roughness_abs', math.fabs(roughnessValue))
            soundEngine.setRTPC('RTPC_ext_roughness_abs', math.fabs(roughnessValue))
            soundTrack.setRTPC('RTPC_ext_roughness2', roughnessValue)
            soundEngine.setRTPC('RTPC_ext_roughness2', roughnessValue)
            soundTrack.setRTPC('RTPC_ext_roughness_eng', roughnessValue)
            soundEngine.setRTPC('RTPC_ext_roughness_eng', roughnessValue)
            rotationSpeed = speedInfo[1]
            roatationRelSpeed = rotationSpeed / self.__typeDesc.physics['rotationSpeedLimit']
            RTPC_ext_treads_sum_affect = math.fabs(roatationRelSpeed * 0.33) + math.fabs(roughnessValue * 0.33) + (clamp(0.5, 1.0, self.detailedEngineState.physicLoad) - 0.5) * 0.66
            soundTrack.setRTPC('RTPC_ext_treads_sum_affect', RTPC_ext_treads_sum_affect)
            rightTrackScroll = math.fabs(self.rightTrackScrollLink())
            leftTrackScroll = math.fabs(self.leftTrackScrollLink())
            if rightTrackScroll > leftTrackScroll:
                trackScroll = rightTrackScroll
            else:
                trackScroll = leftTrackScroll
            if self.__physicsMode == VEHICLE_PHYSICS_MODE.DETAILED and self.__isPlayerVehicle:
                self.__commonTrackScroll += (trackScroll - self.__commonTrackScroll) * _PERIODIC_TIME / 0.2
                self.__commonTrackScroll = self.__commonTrackScroll if self.__commonTrackScroll > 0.0 else 0.0
                soundTrack.setRTPC('RTPC_ext_speed_scroll', self.__commonTrackScroll)
                soundEngine.setRTPC('RTPC_ext_speed_scroll', self.__commonTrackScroll)
            if self.__vt is not None:
                if self.__physicsMode == VEHICLE_PHYSICS_MODE.STANDARD:
                    self.__vt.addValue2('RTPC_ext_gear_2', self.detailedEngineState.gear2)
                    self.__vt.addValue2('RTPC_ext_gear_3', self.detailedEngineState.gear3)
                self.__vt.addValue2('RTPC_ext_flying', self.isFlyingLink())
                self.__vt.addValue2('RTPC_ext_hardness', hardnessValue)
                self.__vt.addValue2('RTPC_ext_friction', frictionValue)
                self.__vt.addValue2('RTPC_ext_roughness_abs', roughnessValue)
                self.__vt.addValue2('RTPC_ext_treads_sum_affect', RTPC_ext_treads_sum_affect)
                self.__vt.addValue2('speed_abs', speed)
                self.__vt.addValue2('speed_rel', self.detailedEngineState.relativeSpeed)
                self.__vt.addValue2('rot_speed_abs', rotationSpeed)
                self.__vt.addValue2('rot_speed_rel', roatationRelSpeed)
                self.__vt.addValue2('gear', self.detailedEngineState.gearNum)
                self.__vt.addValue2('acc_abs', accelerationAbs)
                self.__vt.addValue2('physic_load', self.detailedEngineState.physicLoad)
                self.__vt.addValue2('RTPC_ext_move', moveValue)
                self.__vt.addValue2('RTPC_ext_speed_scroll', self.__commonTrackScroll)
                if self.__physicsMode == VEHICLE_PHYSICS_MODE.STANDARD and cameraUnit:
                    self.__vt.addValue2('RPM', self.detailedEngineState.rpm)
                self.__vt.addValue2('engine_load', self.detailedEngineState.engineLoad)
                self.__vt.addValue2('submersion', self.isUnderwaterLink())
                if self.__physicsMode == VEHICLE_PHYSICS_MODE.DETAILED and self.__isPlayerVehicle:
                    self.__vt.addValue2('RPM', self.detailedEngineState.rpmPhysicAbs)
                    self.__vt.addValue2('RPM_REL', self.detailedEngineState.rpmPhysicRel)
            return

    def getGunSoundObj(self):
        return self.__gunSound

    def stopSounds(self, stopEngine=True, stopMovement=True):
        if self.__gunSound is not None:
            self.__gunSound.stopAll()
            self.__gunSound = None
        if self.__engineSound is not None and stopEngine:
            self.__engineSound.stopAll()
            self.__engineSound = None
        if self.__movementSound is not None and stopMovement:
            self.__movementSound.stopAll()
            self.__movementSound = None
        return

    def deviceDestroyed(self, deviceName):
        if deviceName == 'engine':
            self.__engineSound.play('eng_stopping')

    def deviceRepairedToCritical(self, deviceName):
        if deviceName == 'engine':
            self.__engineSound.play('eng_restoring')

    def onKeyTriggered(self, isDown, key, vehicle):
        if self.__stopMotionSounds is None or vehicle is None:
            return
        else:
            vehicleSpeed = vehicle.getSpeed()
            isMoving = abs(vehicleSpeed) > 0.01
            cmdMap = CommandMapping.g_instance
            sound = None
            for value in self.__stopMotionSounds:
                if cmdMap.isFired(value.key, key):
                    sounds = value.down if isDown else value.up
                    sound = sounds.move if isMoving else sounds.stop
                    break

            if sound is not None and self.__movementSound is not None:
                self.__movementSound.play(sound)
            return

    def setBigGunSwitch(self, isOn):
        if isOn:
            self.__gunSound.setSwitch('wpn_external_armored_car', 'ev_mark_big_gun_ext')
        else:
            self.__gunSound.setSwitch('wpn_external_armored_car', 'ev_mark_machine_gun_ext')


class TrackCrashAuditionWWISE(TrackCrashAudition):

    def __init__(self, trackCenterMProvs):
        """:type trackCenterMProvs: tuple """
        self.__trackCenterMProvs = trackCenterMProvs

    def destroy(self):
        self.__trackCenterMProvs = None
        return

    def playCrashSound(self, isLeft=True, restore=False, wheeledVehicle=False):
        positionMatrix = Math.Matrix(self.__trackCenterMProvs[0 if isLeft else 1])
        if wheeledVehicle:
            if restore:
                SoundGroups.g_instance.playSoundPos('gui_repair_wheel', positionMatrix.translation)
            else:
                SoundGroups.g_instance.playSoundPos('gui_brakedown_wheel', positionMatrix.translation)
            return
        if restore:
            SoundGroups.g_instance.playSoundPos('repair_treads', positionMatrix.translation)
        else:
            SoundGroups.g_instance.playSoundPos('brakedown_treads', positionMatrix.translation)
