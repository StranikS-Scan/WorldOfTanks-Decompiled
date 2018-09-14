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
from svarog_script import auto_properties
from svarog_script.auto_properties import TypedProperty, LinkDescriptor
import svarog_script.py_component
from vehicle_systems.components.engine_state import DetailedEngineStateWWISE
from vehicle_systems.components.engine_state import EngineLoad
from items.vehicles import HP_TO_WATTS
from vehicle_systems.tankStructure import TankPartNames
from vehicle_systems.tankStructure import TankSoundObjectsIndexes

class EngineAudition(svarog_script.py_component.Component):

    def tick(self):
        pass

    def reattachTo(self, compoundModel):
        raise NotImplementedError()

    def __stopSounds(self):
        raise NotImplementedError()

    def getSoundObject(self, index):
        return None


class TrackCrashAudition(svarog_script.py_component.Component):

    def deactivate(self):
        pass

    def playCrashSound(self, isLeft=True, restore=False):
        pass


class SingleEvent(object):
    __slots__ = '__name'

    def __init__(self, name):
        self.__name = name

    def play(self, object):
        object.play(self.__name)


class MultipleEvent(object):
    __slots__ = '__names'

    def __init__(self, names):
        self.__names = names

    def play(self, object):
        for name in self.__names:
            object.play(name)


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

    def __init__(self, isPlayerVehicle, typeDesc, vehicleId):
        self.__prevVelocity = 0
        self.__prevTime = 0.0
        self.__prevTerrSwitch = None
        self.__isPlayerVehicle = isPlayerVehicle
        self.__typeDesc = typeDesc
        self.__commonTrackScroll = 0.0
        self.__engineSound = None
        self.__movementSound = None
        self.__hitSound = None
        self.__gunSound = None
        self.__vehicleId = vehicleId
        self.__event = None
        self.__eventC = None
        self.__cameraUnit = False
        self.__engineStarted = False
        self.__engineEventsTable = ((None,
          None,
          SingleEvent('eng_broken'),
          SingleEvent('eng_stopping')),
         (SingleEvent('eng_repairing_broken'),
          None,
          None,
          SingleEvent('eng_stopping')),
         (SingleEvent('eng_repairing_broken'),
          None,
          None,
          SingleEvent('eng_stopping')),
         (MultipleEvent(('eng_restoring', 'eng_repairing_broken')),
          MultipleEvent(('eng_restoring', 'eng_still_broken')),
          MultipleEvent(('eng_restoring', 'eng_still_broken')),
          None))
        self.__prepareEvents()
        return

    def __prepareEvents(self):
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
        self.__engineSoundHP = 'engine' + str(self.__vehicleId)
        self.__movementSoundHP = 'tracks' + str(self.__vehicleId)
        self.__gunSoundHP = 'gun' + str(self.__vehicleId)

    def __initSounds(self):
        self.__gunSound = SoundGroups.g_instance.WWgetSoundObject(self.__gunSoundHP, None)
        self.__engineSound = SoundGroups.g_instance.WWgetSoundObject(self.__engineSoundHP, None)
        if self.__engineSound is None:
            LOG_ERROR('!!!self.__engineSound is None')
            return
        else:
            horsePower = self.__typeDesc.physics['enginePower'] / HP_TO_WATTS
            WWISE.WW_setRTCPGlobal('RTPC_ext_engine_power', horsePower)
            self.__engineSound.setSwitch('SWITCH_ext_physics_state', 'SWITCH_ext_physics_state_on')
            if self.__eventC == '':
                LOG_ERROR('Tracks sound is not defined for = {0}'.format(self.__typeDesc.name))
                self.__movementSound = None
            else:
                self.__movementSound = SoundGroups.g_instance.WWgetSoundObject(self.__movementSoundHP, None)
            if self.__movementSound is not None:
                self.__movementSound.setSwitch('SWITCH_ext_physics_state', 'SWITCH_ext_physics_state_on')
                self.__movementSound.setRTPC('RTPC_ext_vehicle_weight', self.__typeDesc.physics['weight'] / 1000)
                self.__movementSound.setRTPC('RTPC_ext_engine_state', 0.0)
                self.__movementSound.setRTPC('RTPC_ext_physic_rpm_rel', 0.0)
                self.__movementSound.setRTPC('RTPC_ext_physic_rpm_abs', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_vehicle_weight', self.__typeDesc.physics['weight'] / 1000)
            self.__engineSound.setRTPC('RTPC_ext_engine_state', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_physic_rpm_rel', 0.0)
            self.__engineSound.setRTPC('RTPC_ext_physic_rpm_abs', 0.0)
            return

    def attachToModel(self, compoundModel, weaponEnergy):
        if self.__gunSound is not None:
            self.__gunSound.setRTPC('RTPC_ext_weapon_energy', weaponEnergy)
        hullNode = compoundModel.node(TankPartNames.HULL)
        if self.__gunSound is not None:
            self.__gunSound.matrixProvider = compoundModel.node(TankPartNames.GUN)
        if self.__engineSound is not None:
            self.__engineSound.matrixProvider = hullNode
        if self.__movementSound is not None:
            self.__movementSound.matrixProvider = hullNode
        if self.__hitSound is not None:
            self.__hitSound.matrixProvider = hullNode
        return

    def destroy(self):
        self.deactivate()
        self.__gunSound = None
        self.__movementSound = None
        self.__engineSound = None
        return

    def activate(self):
        super(EngineAuditionWWISE, self).activate()
        self.__initSounds()
        if self.detailedEngineState.mode != EngineLoad._STOPPED:
            self.onEngineStart()
        BigWorld.player().inputHandler.onCameraChanged += self.__onCameraChanged

    def deactivate(self):
        inputhandler = BigWorld.player().inputHandler
        if inputhandler is not None:
            BigWorld.player().inputHandler.onCameraChanged -= self.__onCameraChanged
        self.__stopSounds()
        self.__engineStarted = False
        super(EngineAuditionWWISE, self).deactivate()
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

    def onEngineStart(self):
        if SoundGroups.ENABLE_ENGINE_N_TRACKS:
            if not self.__engineStarted:
                if self.__engineSound is not None:
                    self.__engineStarted = True
                    self.__engineSound.play(self.__event)
                if self.__movementSound is not None:
                    self.__movementSound.play(self.__eventC)
        return

    def onStateChanged(self, prevState, newState):
        event = self.__engineEventsTable[prevState][newState]
        if event is not None:
            event.play(self.__engineSound)
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
                if not self.__isPlayerVehicle:
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
            if self.__isPlayerVehicle:
                self.__commonTrackScroll += (trackScroll - self.__commonTrackScroll) * _PERIODIC_TIME / 0.2
                self.__commonTrackScroll = self.__commonTrackScroll if self.__commonTrackScroll > 0.0 else 0.0
                soundTrack.setRTPC('RTPC_ext_speed_scroll', self.__commonTrackScroll)
                soundEngine.setRTPC('RTPC_ext_speed_scroll', self.__commonTrackScroll)
            if self.__vt is not None:
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
                self.__vt.addValue2('engine_load', self.detailedEngineState.engineLoad)
                self.__vt.addValue2('submersion', self.isUnderwaterLink())
                if self.__isPlayerVehicle:
                    self.__vt.addValue2('RPM', self.detailedEngineState.rpmPhysicAbs)
                    self.__vt.addValue2('RPM_REL', self.detailedEngineState.rpmPhysicRel)
            return

    def getSoundObject(self, index):
        if index == TankSoundObjectsIndexes.CHASSIS:
            return self.__movementSound
        elif index == TankSoundObjectsIndexes.ENGINE:
            return self.__engineSound
        elif index == TankSoundObjectsIndexes.GUN:
            return self.__gunSound
        else:
            return self.__hitSound if index == TankSoundObjectsIndexes.HIT else None

    def __stopSounds(self):
        if self.__gunSound is not None:
            self.__gunSound.stopAll()
            self.__gunSound.matrixProvider = None
        if self.__engineSound is not None:
            self.__engineSound.stopAll()
            self.__engineSound.matrixProvider = None
        if self.__movementSound is not None:
            self.__movementSound.stopAll()
            self.__movementSound.matrixProvider = None
        return


class TrackCrashAuditionWWISE(TrackCrashAudition):

    def __init__(self, trackCenterMProvs):
        """:type trackCenterMProvs: tuple """
        self.__trackCenterMProvs = trackCenterMProvs

    def deactivate(self):
        self.__trackCenterMProvs = None
        return

    def playCrashSound(self, isLeft=True, restore=False):
        if self.__trackCenterMProvs is not None:
            positionMatrix = Math.Matrix(self.__trackCenterMProvs[0 if isLeft else 1])
            if restore:
                SoundGroups.g_instance.playSoundPos('repair_treads', positionMatrix.translation)
            else:
                SoundGroups.g_instance.playSoundPos('brakedown_treads', positionMatrix.translation)
        return
