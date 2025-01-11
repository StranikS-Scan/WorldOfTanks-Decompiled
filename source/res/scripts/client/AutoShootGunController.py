# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import logging
import typing
import weakref
import BigWorld
import CGF
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from constants import SERVER_TICK_LENGTH
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_helpers import getGunSoundObject
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import checkStateStatus
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from vehicle_systems.model_assembler import loadAppearancePrefab
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
        self.__updateBurstParticles(self.__controller.getShootRatePerSecond())
        gunSoundObject.play(self.__activationSound)

    def __deactivateBurst(self, burstInProgress):
        getGunSoundObject(self.__vehicle).play(self.__deactivationSound if burstInProgress else '')
        self.__updateBurstParticles(0.0)

    def __showBurstStart(self):
        for shotGameObject in self.__shotObjects:
            shotGameObject.deactivate()
            shotGameObject.activate()

    @staticmethod
    def __updateBurst():
        return SERVER_TICK_LENGTH

    def __updateBurstParticles(self, rate):
        for particleConfig, particleComponent in self.__burstParticles.iteritems():
            particleComponent.setEmissionRate(rate * particleConfig.rateFactor)


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
        return self.__defaultShootRate

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
        player = BigWorld.player()
        if player is None or player.isDisableRespawnMode:
            return False
        elif not self.entity.typeDescriptor.gun.autoShoot.shotInterval:
            return False
        else:
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
        else:
            params = self.entity.typeDescriptor.gun
            shotInterval = params.autoShoot.shotInterval
            self.__defaultShootRate = 1.0 / shotInterval
            _, effects, _ = params.effects
            autoShootEffect = effects.relatedEffects.get('autoShoot', None)
            if autoShootEffect is not None:
                autoShootEffectDescr = autoShootEffect.effectsList.descriptors()[0]
                self.__shootingPrefab = autoShootEffectDescr.effectsPrefab
                self.__shootingAnimator.initSoundParams(self.entity.isPlayerVehicle, autoShootEffectDescr.activationSound, autoShootEffectDescr.deactivationSound)
                appearance = self.entity.appearance
                loadAppearancePrefab(self.__shootingPrefab, appearance, self.__onShootingPrefabLoaded)
                _logger.debug('QFG: loadAppearancePrefab for %s', self.entity.id)
            self.__updateAutoShootingAppearance()
            self.__appearanceInited = True
            return

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
