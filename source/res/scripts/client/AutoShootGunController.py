# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import logging
import typing
import weakref
import BigWorld
import CGF
import Math
from aih_constants import ShakeReason
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState, CLIP_MIN_RATE
from constants import SERVER_TICK_LENGTH
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import checkStateStatus
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
from vehicle_systems.tankStructure import TankNodeNames
if typing.TYPE_CHECKING:
    from cgf_components.auto_shoot_guns_component import AutoShootingGunBurstPixie
    from GenericComponents import ParticleComponent
    from Vehicular import GunRecoilAnimator
_logger = logging.getLogger(__name__)

def getPlayerVehicleAutoShootGunController():
    vehicle = BigWorld.player().getVehicleAttached()
    return vehicle.dynamicComponents.get('autoShootGunController', None) if vehicle is not None and vehicle.isPlayerVehicle and vehicle.isAlive() else None


class AutoShootGunShootingAnimator(CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicle, controller):
        super(AutoShootGunShootingAnimator, self).__init__()
        self.__vehicle = weakref.proxy(vehicle)
        self.__controller = weakref.proxy(controller)
        self.__activationSound = self.__deactivationSound = ''
        self.__burstParticles = dict()
        self.__recoilAnimators = set()
        self.__shotObjects = set()

    def initSoundParams(self, isPlayerVehicle, activationSounds, deactivationSounds):
        self.__activationSound = activationSounds.getEvents()[0 if isPlayerVehicle else 1]
        self.__deactivationSound = deactivationSounds.getEvents()[0 if isPlayerVehicle else 1]

    def destroy(self):
        self.__vehicle = None
        self.__controller = None
        self.__shotObjects.clear()
        self.__burstParticles.clear()
        self.__recoilAnimators.clear()
        self.__activationSound = self.__deactivationSound = ''
        super(AutoShootGunShootingAnimator, self).destroy()
        return

    def addBurstParticleComponent(self, particleConfig, particleComponent):
        self.__burstParticles[particleConfig] = particleComponent
        particleComponent.setEmissionRate(particleConfig.rateFactor * self.__controller.getShootRatePerSecond())

    def addRecoilAnimator(self, recoilAnimator):
        self.__recoilAnimators.add(recoilAnimator)
        burstRate = self.__controller.getShootRatePerSecond()
        if burstRate > 0.0:
            recoilAnimator.shotsPerSec = burstRate
            recoilAnimator.enableLoop()

    def addShotGameObject(self, shotGameObject):
        self.__shotObjects.add(shotGameObject)

    def removeBurstParticleComponent(self, particleConfig, particleComponent):
        self.__burstParticles.pop(particleConfig, particleComponent)

    def removeRecoilAnimator(self, recoilAnimator):
        self.__recoilAnimators.discard(recoilAnimator)

    def removeShotGameObject(self, shotGameObject):
        self.__shotObjects.discard(shotGameObject)

    def receiveShotsImpulse(self, dt):
        appearance = self.__vehicle.appearance
        if appearance is None or appearance.compoundModel is None:
            return
        else:
            shootRatePerSecond = self.__controller.getShootRatePerSecond()
            if shootRatePerSecond == 0.0:
                return
            gunNode = appearance.compoundModel.node(TankNodeNames.GUN_INCLINATION)
            appearance.receiveShotImpulse(Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), appearance.typeDescriptor.gun.impulse * shootRatePerSecond * dt)
            return

    def updateAutoShootingStatus(self, stateStatus):
        burstInProgress = self.hasDelayedCallback(self.__updateBurst)
        if stateStatus is None or stateStatus.state != AutoShootGunState.SHOOT:
            self.stopCallback(self.__updateBurst)
            self.__deactivateBurst(burstInProgress)
            return
        elif not burstInProgress:
            self.delayCallback(SERVER_TICK_LENGTH, self.__updateBurst)
            self.__activateBurst()
            return
        else:
            self.__updateBurst()
            return

    def __activateBurst(self):
        gunSoundObject = getGunSoundObject(self.__vehicle)
        self.__showBurstStart()
        self.__updateBurst(gunSoundObject=gunSoundObject)
        gunSoundObject.play(self.__activationSound)

    def __deactivateBurst(self, burstInProgress):
        self.__playGunObjectSound(self.__deactivationSound if burstInProgress else '')
        self.__updateBurstParticles(0.0)
        for recoilAnimator in self.__recoilAnimators:
            recoilAnimator.disableLoop()

    def __playGunObjectSound(self, soundName):
        if soundName:
            getGunSoundObject(self.__vehicle).play(soundName)

    def __showBurstStart(self):
        for shotGameObject in self.__shotObjects:
            shotGameObject.deactivate()
            shotGameObject.activate()

        for recoilAnimator in self.__recoilAnimators:
            recoilAnimator.enableLoop()

    def __shakePlayerCamera(self):
        appearance = self.__vehicle.appearance
        if appearance is None or appearance.compoundModel is None:
            return
        else:
            gunFireNode = appearance.compoundModel.node('HP_gunFire')
            gunNode = appearance.compoundModel.node(TankNodeNames.GUN_INCLINATION)
            if gunFireNode is None or gunNode is None:
                return
            BigWorld.player().inputHandler.onVehicleShaken(self.__vehicle, Math.Matrix(gunFireNode).translation, Math.Matrix(gunNode).applyVector(Math.Vector3(0, 0, -1)), self.__vehicle.typeDescriptor.shot.shell.caliber, ShakeReason.OWN_SHOT)
            return

    def __updateBurst(self, gunSoundObject=None):
        burstRate = self.__controller.getShootRatePerSecond()
        self.__shakePlayerCamera()
        self.__updateBurstRecoil(burstRate)
        self.__updateBurstParticles(burstRate)
        self.__updateBurstSounds(gunSoundObject)
        return SERVER_TICK_LENGTH

    def __updateBurstParticles(self, rate):
        for particleConfig, particleComponent in self.__burstParticles.iteritems():
            particleComponent.setEmissionRate(rate * particleConfig.rateFactor)

    def __updateBurstRecoil(self, rate):
        for recoilAnimator in self.__recoilAnimators:
            recoilAnimator.shotsPerSec = rate

    def __updateBurstSounds(self, gunSoundObject=None):
        if self.__vehicle.isPlayerVehicle:
            gunSoundObject = gunSoundObject or getGunSoundObject(self.__vehicle)
            clipPercent = self.__sessionProvider.shared.ammo.getClipPercentLeft()
            gunSoundObject.setRTPC('RTPC_ext_acann_shell_remain', clipPercent * 100)


class AutoShootGunController(BigWorld.DynamicScriptComponent):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(AutoShootGunController, self).__init__()
        self.__prefabRoot = None
        self.__appearanceInited = False
        self.__componentDestroyed = False
        self.__shootingPrefab = ''
        self.__shootingAnimator = AutoShootGunShootingAnimator(self.entity, self)
        self.__defaultShootRate = 0.0
        self.__initAutoShootingAppearance()
        self.__initAutoShootingAvatar()
        return

    @property
    def shootingAnimator(self):
        return self.__shootingAnimator

    def isShooting(self):
        return self.stateStatus is not None and self.stateStatus.state == AutoShootGunState.SHOOT

    @checkStateStatus(states=(AutoShootGunState.SHOOT,), defReturn=0.0)
    def getShootDispersionFactor(self, stateStatus=None):
        dt = max(BigWorld.serverTime() - stateStatus.updateTime, 0.0)
        currDispersionFactor = stateStatus.dispersionFactor + dt * stateStatus.shotDispersionPerSec
        return min(currDispersionFactor, stateStatus.maxShotDispersion)

    @checkStateStatus(states=(AutoShootGunState.SHOOT,), defReturn=0.0)
    def getShootDuration(self, stateStatus):
        return max(BigWorld.serverTime() - stateStatus.stateActivationTime, 0.0)

    @checkStateStatus(states=(AutoShootGunState.SHOOT,), defReturn=0.0)
    def getShootRatePerSecond(self, _):
        spinningCtrl = self.entity.dynamicComponents.get('spinGunController', None)
        spinningFactor = spinningCtrl.getSpinningValue() if spinningCtrl is not None else 1.0
        temperatureCtrl = self.entity.dynamicComponents.get('temperatureGunController', None)
        temperatureFactor = temperatureCtrl.getAutoShootRateFactor() if temperatureCtrl is not None else 1.0
        return max(self.__defaultShootRate * spinningFactor * temperatureFactor, CLIP_MIN_RATE)

    def set_stateStatus(self, _=None):
        if self.__isAvatarReady():
            self.__updateAutoShootingAvatar()
        if self.__appearanceInited and self.__isAppearanceReady():
            self.__updateAutoShootingAppearance()

    def onDestroy(self):
        self.entity.onAppearanceReady -= self.__onAppearanceReady
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        self.__shootingAnimator.destroy()
        if self.__prefabRoot is not None:
            _logger.debug('QFG: removeGameObject (onDestroy) for %s', self.entity.id)
            CGF.removeGameObject(self.__prefabRoot)
            self.__prefabRoot = None
        self.__appearanceInited = False
        self.__componentDestroyed = True
        return

    def onLeaveWorld(self):
        self.onDestroy()

    def __isAvatarReady(self):
        player = BigWorld.player()
        return player is not None and player.userSeesWorld()

    def __isAppearanceReady(self):
        appearance = self.entity.appearance
        return appearance is not None and appearance.isConstructed

    def __isPlayerVehicle(self, player=None):
        player = player or BigWorld.player()
        return player is not None and player.playerVehicleID == self.entity.id

    def __onAvatarReady(self):
        self.__updateAutoShootingAvatar()

    def __onAppearanceReady(self):
        if self.__appearanceInited:
            return
        params = self.entity.typeDescriptor.gun
        _, effects, _ = params.effects
        autoShootEffect = effects.relatedEffects['autoShoot'].effectsList.descriptors()[0]
        self.__defaultShootRate = 1.0 / params.clip[1]
        self.__shootingPrefab = autoShootEffect.effectsPrefab
        self.__shootingAnimator.initSoundParams(self.entity.isPlayerVehicle, autoShootEffect.activationSound, autoShootEffect.deactivationSound)
        appearance = self.entity.appearance
        loadAppearancePrefab(self.__shootingPrefab, appearance, self.__onShootingPrefabLoaded)
        _logger.debug('QFG: loadAppearancePrefab for %s', self.entity.id)
        self.__updateAutoShootingAppearance()
        self.__appearanceInited = True

    def __onShootingPrefabLoaded(self, root):
        if not root.isValid:
            _logger.error('QFG: failed to load prefab: %s', self.__effectsPrefab)
            return
        if self.__componentDestroyed:
            _logger.debug('QFG: removeGameObject (onLoaded) for %s', self.entity.id)
            CGF.removeGameObject(root)
            return
        self.__prefabRoot = root

    def __initAutoShootingAvatar(self):
        if self.__isAvatarReady():
            self.__onAvatarReady()
        else:
            g_playerEvents.onAvatarReady += self.__onAvatarReady

    def __initAutoShootingAppearance(self):
        if self.__isAppearanceReady():
            self.__onAppearanceReady()
        else:
            self.entity.onAppearanceReady += self.__onAppearanceReady

    def __updateAutoShootingAvatar(self):
        player = BigWorld.player()
        if not self.__isPlayerVehicle(player):
            return
        else:
            player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)
            autoShootGunCtrl = self.__sessionProvider.shared.autoShootGunCtrl
            if autoShootGunCtrl is not None and self.stateStatus is not None:
                autoShootGunCtrl.burstPredictor.synchronizeShooting(self.stateStatus.state)
            return

    def __updateAutoShootingAppearance(self):
        self.__shootingAnimator.updateAutoShootingStatus(self.stateStatus)
