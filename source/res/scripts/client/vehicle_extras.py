# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_extras.py
import random
import weakref
from functools import partial
import BigWorld
import Math
import ArenaType
from helpers.EffectsList import EffectsListPlayer, effectsFromSection
from helpers import newFakeModel
from debug_utils import LOG_CODEPOINT_WARNING, LOG_CURRENT_EXCEPTION
from helpers import i18n, dependency
from helpers.EntityExtra import EntityExtra
from helpers.CallbackDelayer import CallbackDelayer
import material_kinds
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.tankStructure import TankPartNames

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

    def _start(self, data, burstCount):
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
                self.__doGroundWaveEffect(data['entity'], groundWaveEff, gunModel)
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

    def __doGroundWaveEffect(self, vehicle, groundWaveEff, gunModel):
        node = gunModel.node('HP_gunFire')
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
            matKind = material_kinds.WATER_MATERIAL_KIND
        else:
            testRes = BigWorld.wg_collideSegment(BigWorld.player().spaceID, gunPos + Math.Vector3(0, 0.5, 0), gunPos - Math.Vector3(0, 1.5, 0), 128)
            if testRes is None:
                return
            position = testRes.closestPoint
            matKind = testRes.matKind
        BigWorld.player().terrainEffects.addNew(position, groundWaveEff.effectsList, groundWaveEff.keyPoints, None, dir=gunDir, surfaceMatKind=matKind, start=position + Math.Vector3(0, 0.5, 0), end=position - Math.Vector3(0, 0.5, 0), entity_id=vehicle.id)
        return


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
        vehicle.appearance.switchFireVibrations(True)

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


class HalloweenVehicleEffects(EntityExtra):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _ZOMBIE_IDLE_EFFECT_OFFSET = Math.Vector3(0.0, 1.0, 0.0)
    _SOULS_COLLECTOR_SMALL_EFFECT_OFFSET = Math.Vector3(0.0, 0.47, -2.84)
    _ZOMBIE_VEHICLE_IDLE_LARGE = 'ZombieVehicleIdleLargeEffect'
    _SMALL_GHOST_COLLECTOR = 'PlayerSmallGhostCollector'
    _PLAYER_SOUL_PICKUP_EFFECT = 'PlayerSoulPickupEffect'

    def _start(self, data, _):
        if not data['entity'].isAlive() or data['entity'].health <= 0:
            return
        else:
            self._pickupSettings = ArenaType.g_cache[BigWorld.player().arenaTypeID].eventPointsPickupSettings
            data['fakeModel'] = self._prepareModel()
            data['callbackDelayer'] = CallbackDelayer()
            data['eventPointsCountPrev'] = 0
            self.__updateHullPosition(data)
            effectName, modelOffset = self.__getModelName(data['entity'].botKind)
            translationMatrix = Math.Matrix()
            translationMatrix.setTranslate(modelOffset)
            refinedMatrixProvider = Math.MatrixProduct()
            refinedMatrixProvider.a = translationMatrix
            refinedMatrixProvider.b = data['hull']
            data['servo'] = BigWorld.Servo(refinedMatrixProvider)
            effect = effectsFromSection(self._pickupSettings.epEffects[effectName])
            pickupEffect = effectsFromSection(self._pickupSettings.epEffects[HalloweenVehicleEffects._PLAYER_SOUL_PICKUP_EFFECT])
            data['effectsListPlayer'] = EffectsListPlayer(effect.effectsList, effect.keyPoints)
            data['pickupEffectsListPlayer'] = EffectsListPlayer(pickupEffect.effectsList, pickupEffect.keyPoints)
            data['effectsListPlayer'].play(data['fakeModel'])
            if data['servo'] not in data['fakeModel'].motors:
                data['fakeModel'].addMotor(data['servo'])
            if not data['entity'].botKind:
                componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
                eventPointsComp = getattr(componentSystem, 'eventPointsComponent', None)
                if eventPointsComp is not None:
                    data['cb'] = partial(self.__onCurrentEventPointsUpdated, data=data)
                    eventPointsComp.onCurrentEventPointsUpdated += data['cb']
            return

    def _cleanup(self, data):
        if not data['entity'].botKind and data.get('cb', None) is not None:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            eventPointsComp = getattr(componentSystem, 'eventPointsComponent', None)
            if eventPointsComp is not None and data.get('cb', None) is not None:
                eventPointsComp.onCurrentEventPointsUpdated -= data['cb']
                del data['cb']
        if data.get('effectsListPlayer', None) is not None:
            data['effectsListPlayer'].stop(keepPosteffects=True)
            del data['effectsListPlayer']
        if data.get('pickupEffectsListPlayer', None) is not None:
            data['pickupEffectsListPlayer'].stop(keepPosteffects=True)
            del data['pickupEffectsListPlayer']
        if data.get('fakeModel', None) is not None:
            if data.get('servo', None) is not None and data['servo'] in data['fakeModel'].motors:
                data['fakeModel'].delMotor(data['servo'])
            if data['fakeModel'].inWorld is True:
                BigWorld.player().delModel(data['fakeModel'])
            del data['fakeModel']
        if data.get('servo', None) is not None:
            data['servo'].signal = None
            del data['servo']
        if data.get('callbackDelayer', None) is not None:
            data['callbackDelayer'].destroy()
            del data['callbackDelayer']
        del data['eventPointsCountPrev']
        return

    def _prepareModel(self):
        model = newFakeModel()
        BigWorld.player().addModel(model)
        return model

    def __getModelName(self, botKind):
        if botKind:
            modelOffset = HalloweenVehicleEffects._ZOMBIE_IDLE_EFFECT_OFFSET
            effectName = HalloweenVehicleEffects._ZOMBIE_VEHICLE_IDLE_LARGE
        else:
            modelOffset = HalloweenVehicleEffects._SOULS_COLLECTOR_SMALL_EFFECT_OFFSET
            effectName = HalloweenVehicleEffects._SMALL_GHOST_COLLECTOR
        return (effectName, modelOffset)

    def __onCurrentEventPointsUpdated(self, eventPoints, data):
        avatar = BigWorld.player()
        eventPointsCount = eventPoints[avatar.team].get(data['entity'].id, 0)
        player = data.get('pickupEffectsListPlayer', None)
        fakeModel = data.get('fakeModel', None)
        if eventPointsCount != data['eventPointsCountPrev'] and player is not None and not player.isPlaying and fakeModel is not None:
            player.play(fakeModel)
            data['eventPointsCountPrev'] = eventPointsCount
        return

    def __updateHullPosition(self, data):
        if data.get('hull', None) is None:
            data['hull'] = Math.Matrix()
        data['hull'].set(data['entity'].model.node(TankPartNames.HULL))
        callbackDelayer = data.get('callbackDelayer', None)
        if callbackDelayer is not None:
            callbackDelayer.delayCallback(0, partial(self.__updateHullPosition, data))
        return
