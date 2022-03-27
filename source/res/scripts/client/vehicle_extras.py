# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_extras.py
from functools import partial
from vehicle_systems.stricted_loading import makeCallbackWeak
import BigWorld
import Math
import material_kinds
import AnimationSequence
from debug_utils import LOG_CODEPOINT_WARNING, LOG_CURRENT_EXCEPTION
from gui.impl import backport
from gui.impl.gen import R
from items import vehicles
from items.components.component_constants import MAIN_TRACK_PAIR_IDX
from common_tank_appearance import MAX_DISTANCE
from helpers import i18n
from helpers.EffectsList import EffectsListPlayer
from helpers.EntityExtra import EntityExtra
from helpers.laser_sight_matrix_provider import LaserSightMatrixProvider
from constants import IS_EDITOR, CollisionFlags
import Projectiles
from vehicle_extras_battle_royale import AfterburningBattleRoyale

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
            shotsDone = vehicle.appearance.findComponentByType(Projectiles.ShotsDoneComponent)
            if shotsDone is None:
                vehicle.appearance.createComponent(Projectiles.ShotsDoneComponent)
            else:
                shotsDone.addShot()
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
            self.__doRecoil(vehicle, gunModel)
            if not IS_EDITOR:
                avatar = BigWorld.player()
                if data['entity'].isPlayerVehicle or vehicle is avatar.getVehicleAttached():
                    avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, withShot)
                groundWaveEff = effPlayer.effectsList.relatedEffects.get('groundWave')
                if groundWaveEff is not None:
                    self._doGroundWaveEffect(data['entity'], groundWaveEff, gunModel)
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
            shotsDone = vehicle.appearance.findComponentByType(Projectiles.ShotsDoneComponent)
            if shotsDone is not None:
                shotsDone.addShot()
            else:
                vehicle.appearance.createComponent(Projectiles.ShotsDoneComponent)
            self.__doGunEffect(data)
            self.__doRecoil(data)
            if not IS_EDITOR:
                avatar = BigWorld.player()
                if data['entity'].isPlayerVehicle or vehicle is avatar.getVehicleAttached():
                    avatar.getOwnVehicleShotDispersionAngle(avatar.gunRotator.turretRotationSpeed, withShot=1)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.stop(data)

        return

    def __doGunEffect(self, data):
        gunModel = data['_gunModel']
        vehicle = data['entity']
        multiGun = vehicle.typeDescriptor.turret.multiGun
        for gunIndex, effPlayer in data['_effectsListPlayers'].items():
            effPlayer.stop()
            effPlayer.play(gunModel, None, partial(self.stop, data))
            if not IS_EDITOR:
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
        deviceUserString = self._getDeviceUserString(dataSection, containerName)
        self.deviceUserString = deviceUserString
        soundSection = dataSection['sounds']
        self.sounds = {}
        for state in ('critical', 'destroyed', 'functional', 'fixed'):
            sound = soundSection.readString(state)
            if sound:
                self.sounds[state] = sound

    def _getDeviceUserString(self, dataSection, containerName):
        return i18n.makeString(dataSection.readString('deviceUserString'))

    @property
    def isTankman(self):
        return False


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
    __slots__ = ('__isLeft', '_trackPairIndex')

    def _readConfig(self, dataSection, containerName):
        self.__isLeft = dataSection.readBool('isLeft')
        self._trackPairIndex = dataSection.readInt('trackPairIdx', 0)
        DamageMarker._readConfig(self, dataSection, containerName)
        functionalCanMoveState = 'functionalCanMove'
        self.sounds[functionalCanMoveState] = dataSection.readString('sounds/' + functionalCanMoveState)

    def _getDeviceUserString(self, dataSection, _):
        resource = R.strings.ingame_gui.devices.track
        typeTxt = backport.text(resource.left() if self.__isLeft else resource.right())
        return backport.text(resource(), type=typeTxt)

    def _start(self, data, args):
        data['entity'].appearance.addCrashedTrack(self.__isLeft, self._trackPairIndex)

    def _cleanup(self, data):
        data['entity'].appearance.delCrashedTrack(self.__isLeft, self._trackPairIndex)


class TrackWithinTrackHealth(TrackHealth):

    def _getDeviceUserString(self, dataSection, _):
        resource = R.strings.ingame_gui.devices.track
        typeTxt = backport.text(resource.main() if self._trackPairIndex == MAIN_TRACK_PAIR_IDX else resource.outer())
        return backport.text(resource(), type=typeTxt)


class TankmanHealth(DamageMarker):

    @property
    def isTankman(self):
        return True


class BlinkingLaserSight(EntityExtra):
    __slots__ = ('_isEnabledBlinking', '_shouldCollideTarget', '_beamLength', '_bindNode', '_beamSeqs')
    _SEQUENCE_NAMES = ('beamStaticSeq', 'beamReloadStartSeq', 'beamReloadFininshSeq')

    def _readConfig(self, dataSection, containerName):
        self._isEnabledBlinking = dataSection.readBool('isEnabledBlinking')
        self._shouldCollideTarget = dataSection.readBool('shouldCollideTarget')
        self._beamLength = dataSection.readFloat('beamLength', 1.0)
        self._bindNode = dataSection.readString('bindNode')
        self._beamSeqs = dict(((name, dataSection.readString(name)) for name in self._SEQUENCE_NAMES if self._isEnabledBlinking or name == 'beamStaticSeq'))

    def _newData(self, entity):
        data = super(BlinkingLaserSight, self)._newData(entity)
        data.update({'beamModelRef': None,
         'bindNodeRef': None,
         'beamMP': None,
         'animatorRefs': {},
         'currSeq': None,
         'isVehicleTakenAtGunPoint': False})
        return data

    def _start(self, data, args):
        data['bindNodeRef'] = data['entity'].model.node(self._bindNode)
        if data['bindNodeRef'] is not None:
            data['beamMP'] = LaserSightMatrixProvider()
            data['beamMP'].beamMatrix = data['bindNodeRef']
            data['beamModelRef'] = BigWorld.Model('')
            data['beamModelRef'].addMotor(BigWorld.Servo(data['beamMP'].beamMatrix))
            player = BigWorld.player()
            player.addModel(data['beamModelRef'])
            for beamSeq in self._beamSeqs.itervalues():
                loader = AnimationSequence.Loader(beamSeq, player.spaceID)
                data['animatorRefs'][beamSeq] = loader.loadSync()
                BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onSequenceLoaded, beamSeq, data))

        return

    def _update(self, data, args):
        vehicle = data['entity']
        if not (vehicle.health > 0 and vehicle.isCrewActive):
            self.stop(data)
            return
        elif args is None or data['bindNodeRef'] is None:
            return
        else:
            gunMatr = Math.Matrix(data['bindNodeRef'])
            gunPos = gunMatr.applyToOrigin()
            gunDir = gunMatr.applyToAxis(2)
            endPos = gunPos + gunDir * MAX_DISTANCE
            collidePos = BigWorld.wg_collideDynamicStatic(vehicle.spaceID, gunPos, endPos, CollisionFlags.TRIANGLE_PROJECTILENOCOLLIDE, vehicle.id, -1)
            data['isVehicleTakenAtGunPoint'] = args['isTakesAim'] or not self._shouldCollideTarget or collidePos[1]
            distanceToTarget = gunPos.distTo(collidePos[0]) if collidePos is not None else MAX_DISTANCE
            beamMode = args['beamMode']
            if beamMode not in self._beamSeqs:
                beamMode = 'beamStaticSeq'
            requestedSeq = self._beamSeqs[beamMode]
            if data['isVehicleTakenAtGunPoint']:
                data['beamMP'].beamLength = distanceToTarget / self._beamLength
                if data['currSeq'] != requestedSeq:
                    self.__stopAnimator(data)
                data['currSeq'] = requestedSeq
                data['animatorRefs'][data['currSeq']].setEnabled(True)
                data['animatorRefs'][data['currSeq']].start()
            elif data['currSeq'] is not None:
                self.__stopAnimator(data)
            return

    def _cleanup(self, data):
        self.__stopAnimator(data)
        self.__stopModel(data)
        data['bindNodeRef'] = None
        data['beamMP'] = None
        for animator in data['animatorRefs'].itervalues():
            animator.unbind()

        data['animatorRefs'] = {}
        return

    @staticmethod
    def __onSequenceLoaded(seqName, data, resourceRefs):
        if seqName not in resourceRefs.failedIDs and data['beamModelRef'] is not None:
            data['animatorRefs'][seqName].bindTo(AnimationSequence.ModelWrapperContainer(data['beamModelRef'], BigWorld.player().spaceID))
        return

    @staticmethod
    def __stopAnimator(data):
        if data['currSeq'] is None:
            return
        else:
            data['animatorRefs'][data['currSeq']].stop()
            data['animatorRefs'][data['currSeq']].setEnabled(False)
            data['currSeq'] = None
            return

    @staticmethod
    def __stopModel(data):
        if data['beamModelRef'] is None:
            return
        else:
            BigWorld.player().delModel(data['beamModelRef'])
            data['beamModelRef'] = None
            return
