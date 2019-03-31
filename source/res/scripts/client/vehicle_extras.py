# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_extras.py
# Compiled at: 2011-12-09 20:25:20
import BigWorld
import random
import items
import constants
from Vibroeffects.Controllers.ShootingController import ShootingController
from debug_utils import *
from helpers import i18n
from helpers.EntityExtra import EntityExtra

def reload():
    modNames = (reload.__module__,)
    from sys import modules
    import __builtin__
    for m in modNames:
        __builtin__.reload(modules[m])

    print 'vehicle_extras reloaded'


class NoneExtra(EntityExtra):

    def _start(self, data, args):
        debug_utils.LOG_CODEPOINT_WARNING()
        self.stop(data)


import Math
from functools import partial
from helpers.EffectsList import EffectsListPlayer

class ShowShooting(EntityExtra):

    def _start(self, data, burstCount):
        vehicle = data['entity']
        gunDescr = vehicle.typeDescriptor.gun
        stages, effects, _ = gunDescr['effects']
        data['_effectsListPlayer'] = EffectsListPlayer(effects, stages)
        data['_burst'] = (burstCount, gunDescr['burst'][1])
        data['_gunModel'] = vehicle.appearance.modelsDesc['gun']['model']
        if vehicle.isPlayer:
            BigWorld.addAlwaysUpdateModel(data['_gunModel'])
        self.__doShot(data)

    def _cleanup(self, data):
        data['_effectsListPlayer'].stop()
        timerID = data.get('_timerID')
        if timerID is not None:
            BigWorld.cancelCallback(timerID)
            data['_timerID'] = None
        if data['entity'].isPlayer:
            BigWorld.delAlwaysUpdateModel(data['_gunModel'])
        return

    def __doShot(self, data):
        data['_timerID'] = None
        try:
            vehicle = data['entity']
            if not vehicle.isAlive():
                self.stop(data)
                return
            burstCount, burstInterval = data['_burst']
            gunModel = data['_gunModel']
            effPlayer = data['_effectsListPlayer']
            effPlayer.stop()
            if burstCount == 1:
                effPlayer.play(gunModel, None, partial(self.stop, data))
                if data['entity'].isPlayer and burstInterval > 0.0:
                    data['_timerID'] = BigWorld.callback(0.5, partial(self.__notifyOnCompletionOfBurst, data))
            else:
                data['_burst'] = (burstCount - 1, burstInterval)
                data['_timerID'] = BigWorld.callback(burstInterval, partial(self.__doShot, data))
                effPlayer.play(gunModel)
                if data['entity'].isPlayer:
                    avatar = BigWorld.player()
                    avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, 2)
            self.__doGroundWaveEffect(data, gunModel)
            appearance = vehicle.appearance
            appearance.gunRecoil.recoil()
            appearance.receiveShotImpulse(Math.Matrix(gunModel.matrix).applyVector(Math.Vector3(0, 0, -1)), vehicle.typeDescriptor.gun['impulse'])
            appearance.executeShootingVibrations(vehicle.typeDescriptor.shot['shell']['caliber'])
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.stop(data)

        return

    def __doGroundWaveEffect(self, data, gunModel):
        vehicle = data['entity']
        gunDescr = vehicle.typeDescriptor.gun
        if gunDescr['groundWave'] is None:
            return
        else:
            node = gunModel.node('HP_gunFire')
            gunPos = Math.Matrix(node).translation
            upVec = Math.Matrix(vehicle.matrix).applyVector(Math.Vector3(0, 1, 0))
            if upVec.y != 0:
                centerToGun = gunPos - vehicle.position
                centerToGunDist = centerToGun.length
                centerToGun.normalise()
                gunHeight = centerToGunDist * centerToGun.dot(upVec) / upVec.y
                gunPos.y -= gunHeight
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, gunPos + Math.Vector3(0, 0.5, 0), gunPos - Math.Vector3(0, 1.5, 0), 128)
            if testRes is None:
                return
            position = testRes[0]
            stages, effects, _ = gunDescr['groundWave']
            BigWorld.player().terrainEffects.addNew(position, effects, stages, None, dir=testRes[1], start=position + Math.Vector3(0, 0.5, 0), end=position - Math.Vector3(0, 0.5, 0))
            return

    def __notifyOnCompletionOfBurst(self, data):
        data['_timerID'] = None
        BigWorld.player().playShotResultNotification(None, None)
        return


class DamageMarker(EntityExtra):

    def _readConfig(self, dataSection, containerName):
        self.deviceUserString = dataSection.readString('deviceUserString')
        if not self.deviceUserString:
            self._raiseWrongConfig('deviceUserString', containerName)
        self.deviceUserString = i18n.makeString(self.deviceUserString)
        soundSection = dataSection['sounds']
        self.sounds = {}
        for state in ('critical', 'destroyed', 'functional', 'fixed'):
            sound = soundSection.readString(state)
            if sound:
                self.sounds[state] = sound


class TrackHealth(DamageMarker):

    def _readConfig(self, dataSection, containerName):
        DamageMarker._readConfig(self, dataSection, containerName)
        self.__isLeft = dataSection.readBool('isLeft')
        functionalCanMoveState = 'functionalCanMove'
        self.sounds[functionalCanMoveState] = dataSection.readString('sounds/' + functionalCanMoveState)

    def _start(self, data, args):
        data['entity'].appearance.addCrashedTrack(self.__isLeft)

    def _cleanup(self, data):
        data['entity'].appearance.delCrashedTrack(self.__isLeft)


class Fire(EntityExtra):
    _SIRENE_SOUND_NAME = '/ingame_voice/notifications_VO/fire_started_FX'

    def _readConfig(self, dataSection, containerName):
        self.sounds = {}
        startSound = dataSection.readString('sounds/fireStarted')
        if startSound:
            self.sounds['critical'] = startSound
            self.sounds['destroyed'] = startSound
        else:
            self._raiseWrongConfig('sounds/fireStarted', containerName)
        stopSound = dataSection.readString('sounds/fireStopped')
        if stopSound:
            self.sounds['fixed'] = stopSound
        else:
            self._raiseWrongConfig('sounds/fireStopped', containerName)
        self.sireneSound = None
        return

    def _start(self, data, args):
        data['_isStarted'] = False
        vehicle = data['entity']
        stages, effects, _ = random.choice(vehicle.typeDescriptor.type.effects['flaming'])
        if len(stages) != 2 or stages[0][0] != 'fire' or stages[1][0] != 'noEmission':
            LOG_ERROR("Wrong stages in vehicle flaming effect. Should be 'fire' and 'noEmission'.", vehicle.typeDescriptor.name)
            self.stop(data)
            return
        data['_noEmissionTime'] = stages[1][1]
        data['_effects'] = effects
        effects.attachTo(vehicle.appearance.modelsDesc['hull']['model'], data, 'fire')
        data['_isStarted'] = True
        self.sireneSound = vehicle.appearance.modelsDesc['hull']['model'].playSound(Fire._SIRENE_SOUND_NAME)
        vehicle.appearance.switchFireVibrations(True)

    def _cleanup(self, data):
        if not data['_isStarted']:
            return
        else:
            vehicle = data['entity']
            effects = data['_effects']
            vehicle.appearance.switchFireVibrations(False)
            if vehicle.health <= 0:
                effects.detachAllFrom(data)
                return
            if self.sireneSound is not None:
                self.sireneSound.stop()
                self.sireneSound = None
            effects.detachFrom(data, 'fire')
            effects.attachTo(vehicle.appearance.modelsDesc['hull']['model'], data, 'noEmission')
            BigWorld.callback(data['_noEmissionTime'], partial(self.__stop, data))
            return

    def __stop(self, data):
        data['_effects'].detachAllFrom(data)
