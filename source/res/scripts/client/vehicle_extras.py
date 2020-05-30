# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_extras.py
import random
import weakref
from functools import partial
import BigWorld
import Math
import material_kinds
from debug_utils import LOG_CODEPOINT_WARNING, LOG_CURRENT_EXCEPTION
from items import vehicles
from helpers import i18n
from helpers.EffectsList import EffectsListPlayer
from helpers.EntityExtra import EntityExtra

def reload():
    modNames = (reload.__module__,)
    from sys import modules
    import __builtin__
    for m in modNames:
        __builtin__.reload(modules[m])

    print 'vehicle_extras reloaded'


class NoneExtra(EntityExtra):
    __slots__ = ()

    def _start(self, data, args):
        LOG_CODEPOINT_WARNING()
        self.stop(data)


class ShowShooting(EntityExtra):
    __slots__ = ()

    def _start(self, data, args):
        burstCount, _ = args
        vehicle = data['entity']
        gunDescr = vehicle.typeDescriptor.gun
        stages, effects, _ = gunDescr.effects
        data['entity_id'] = vehicle.id
        data['_effectsListPlayer'] = EffectsListPlayer(effects, stages, **data)
        data['_burst'] = (burstCount, gunDescr.burst[1])
        data['_gunModel'] = vehicle.appearance.compoundModel
        self.__doShot(data)

    def _cleanup(self, data):
        if data.get('_effectsListPlayer') is not None:
            data['_effectsListPlayer'].stop()
        timerID = data.get('_timerID')
        if timerID is not None:
            BigWorld.cancelCallback(timerID)
            data['_timerID'] = None
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
                withShot = 1
            else:
                data['_burst'] = (burstCount - 1, burstInterval)
                data['_timerID'] = BigWorld.callback(burstInterval, partial(self.__doShot, data))
                effPlayer.play(gunModel)
                withShot = 2
            avatar = BigWorld.player()
            if data['entity'].isPlayerVehicle or vehicle is avatar.getVehicleAttached():
                avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, withShot)
            groundWaveEff = effPlayer.effectsList.relatedEffects.get('groundWave')
            if groundWaveEff is not None:
                self._doGroundWaveEffect(data['entity'], groundWaveEff, gunModel)
            self.__doRecoil(vehicle, gunModel)
            if vehicle.isPlayerVehicle:
                appearance = vehicle.appearance
                appearance.executeShootingVibrations(vehicle.typeDescriptor.shot.shell.caliber)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.stop(data)

        return

    def __doRecoil(self, vehicle, gunModel):
        appearance = vehicle.appearance
        appearance.recoil()

    def _doGroundWaveEffect(self, vehicle, groundWaveEff, gunModel, gunNode=None):
        node = gunModel.node('HP_gunFire' if gunNode is None else gunNode)
        gunMatr = Math.Matrix(node)
        gunPos = gunMatr.translation
        gunDir = gunMatr.applyVector((0, 0, 1))
        upVec = Math.Matrix(vehicle.matrix).applyVector(Math.Vector3(0, 1, 0))
        if upVec.y != 0:
            centerToGun = gunPos - vehicle.position
            centerToGunDist = centerToGun.length
            centerToGun.normalise()
            gunHeight = centerToGunDist * centerToGun.dot(upVec) / upVec.y
            gunPos.y -= gunHeight
        distanceToWater = BigWorld.wg_collideWater(gunPos, gunPos + Math.Vector3(0, 1, 0), False)
        if distanceToWater > -1:
            position = gunPos - Math.Vector3(0, distanceToWater, 0)
            matKind = material_kinds.getWaterMatKind()
        else:
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, gunPos + Math.Vector3(0, 0.5, 0), gunPos - Math.Vector3(0, 1.5, 0), 128)
            if testRes is None:
                return
            position = testRes.closestPoint
            matKind = testRes.matKind
        BigWorld.player().terrainEffects.addNew(position, groundWaveEff.effectsList, groundWaveEff.keyPoints, None, dir=gunDir, surfaceMatKind=matKind, start=position + Math.Vector3(0, 0.5, 0), end=position - Math.Vector3(0, 0.5, 0), entity_id=vehicle.id)
        return


class ShowShootingMultiGun(ShowShooting):
    _SHOT_SINGLE = 1

    def _start(self, data, args):
        burstCount, gunIndex = args
        if burstCount != self._SHOT_SINGLE:
            data['_gunIndex'] = range(0, burstCount)
        else:
            data['_gunIndex'] = [gunIndex]
        vehicle = data['entity']
        gunDescr = vehicle.typeDescriptor.gun
        data['entity_id'] = vehicle.id
        effectPlayers = {}
        for gunIndex in data['_gunIndex']:
            stages, effects, _ = gunDescr.effects[gunIndex]
            effectPlayers[gunIndex] = EffectsListPlayer(effects, stages, **data)

        data['_effectsListPlayers'] = effectPlayers
        data['_burst'] = (burstCount, gunDescr.burst[1])
        data['_gunModel'] = vehicle.appearance.compoundModel
        self.__doShot(data)

    def _cleanup(self, data):
        effPlayers = data.get('_effectsListPlayers')
        if effPlayers is None:
            return
        else:
            for effPlayer in effPlayers.values():
                if effPlayer is not None:
                    effPlayer.stop()

            return

    def __doShot(self, data):
        try:
            vehicle = data['entity']
            if not vehicle.isAlive():
                self.stop(data)
                return
            self.__doGunEffect(data)
            avatar = BigWorld.player()
            if data['entity'].isPlayerVehicle or vehicle is avatar.getVehicleAttached():
                avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, withShot=1)
            self.__doRecoil(data)
            if vehicle.isPlayerVehicle:
                appearance = vehicle.appearance
                appearance.executeShootingVibrations(vehicle.typeDescriptor.shot.shell.caliber)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.stop(data)

    def __doGunEffect(self, data):
        gunModel = data['_gunModel']
        vehicle = data['entity']
        multiGun = vehicle.typeDescriptor.turret.multiGun
        for gunIndex, effPlayer in data['_effectsListPlayers'].items():
            effPlayer.stop()
            effPlayer.play(gunModel, None, partial(self.stop, data))
            groundWaveEff = effPlayer.effectsList.relatedEffects.get('groundWave')
            if groundWaveEff is not None:
                self._doGroundWaveEffect(vehicle, groundWaveEff, gunModel, gunNode=multiGun[gunIndex].gunFire)

        return

    def __doRecoil(self, data):
        vehicle = data['entity']
        appearance = vehicle.appearance
        gunIndexes = data['_gunIndex']
        appearance.multiGunRecoil(gunIndexes)


class DamageMarker(EntityExtra):
    __slots__ = ('deviceUserString', 'sounds')

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


def wheelHealths(name, index, containerName, dataSection, vehType):
    extras = []
    maxAxleCount = max((len(c[1]['axleSteeringLockAngles']) for c in vehType.xphysics['chassis'].iteritems()))
    template = vehicles.makeMultiExtraNameTemplate(name)
    for number in xrange(maxAxleCount * 2):
        extraName = template.format(number)
        wheelHealth = DamageMarker(extraName, number + index, containerName, dataSection)
        extras.append(wheelHealth)

    return extras


class TrackHealth(DamageMarker):
    __slots__ = ('__isLeft',)

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
    __slots__ = ('sounds',)

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

    def _start(self, data, args):
        data['_isStarted'] = False
        vehicle = data['entity']
        isUnderwater = vehicle.appearance.isUnderwater
        if not isUnderwater:
            self.__playEffect(data)
        data['_isStarted'] = True
        data['_invokeTime'] = BigWorld.time()
        vehicle.appearance.switchFireVibrations(True)

    def _update(self, data, args):
        if not data['_isStarted']:
            return
        else:
            currTime = BigWorld.time()
            if args and currTime - data.get('_invokeTime', currTime) > args:
                effectsListPlayer = self.__getEffectsListPlayer(data)
                if effectsListPlayer is None:
                    return
                effectsListPlayer.stop(forceCallback=True)
                data['_isStarted'] = False
                vehicle = data['entity']
                if vehicle.health > 0:
                    isUnderwater = vehicle.appearance.isUnderwater
                    if not isUnderwater:
                        self.__playEffect(data)
                    data['_isStarted'] = True
                    data['_invokeTime'] = BigWorld.time()
            return

    def _cleanup(self, data):
        if not data['_isStarted']:
            return
        else:
            vehicle = data['entity']
            vehicle.appearance.switchFireVibrations(False)
            effectsListPlayer = self.__getEffectsListPlayer(data)
            if effectsListPlayer is not None:
                if vehicle.health <= 0:
                    effectsListPlayer.stop(forceCallback=True)
                    return
                effectsListPlayer.keyOff()
            return

    def __getEffectsListPlayer(self, data):
        effectsListPlayerRef = data.get('_effectsPlayer', None)
        return effectsListPlayerRef() if effectsListPlayerRef is not None else None

    def __playEffect(self, data):
        vehicle = data['entity']
        stages, effects, _ = random.choice(vehicle.typeDescriptor.type.effects['flaming'])
        data['entity_id'] = vehicle.id
        waitForKeyOff = True
        effectListPlayer = vehicle.appearance.boundEffects.addNew(None, effects, stages, waitForKeyOff, **data)
        data['_effectsPlayer'] = weakref.ref(effectListPlayer)
        return

    def checkUnderwater(self, vehicle, isVehicleUnderwater):
        data = vehicle.extras[self.index]
        if isVehicleUnderwater:
            effectsListPlayer = self.__getEffectsListPlayer(data)
            if effectsListPlayer is not None:
                effectsListPlayer.stop(forceCallback=True)
                del data['_effectsPlayer']
        if not isVehicleUnderwater:
            self.__playEffect(data)
        return
