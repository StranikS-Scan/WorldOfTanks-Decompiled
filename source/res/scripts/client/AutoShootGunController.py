# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import typing
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from vehicle_systems.entity_components.vehicle_mechanic_component import getPlayerVehicleMechanic, checkStateStatus, initOnce, VehicleMechanicGunPrefabComponent
from vehicle_systems.auto_shoot_guns.shooting_events import AutoShootingEvents
from vehicle_systems.auto_shoot_guns.custom_integrations import AutoShootCustomIntegrations
if typing.TYPE_CHECKING:
    from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingEvents

def getPlayerVehicleAutoShootGunController():
    return getPlayerVehicleMechanic('autoShootGunController')


class AutoShootGunController(VehicleMechanicGunPrefabComponent):

    @initOnce
    def __init__(self):
        super(AutoShootGunController, self).__init__()
        self.__gunsGroupSize = 0
        self.__defaultShotRatePerSecond = 0.0
        self.__shootingEvents = AutoShootingEvents(self)
        AutoShootCustomIntegrations(self.entity, self).subscribe(self.__shootingEvents)
        self._initMechanic()

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def isShooting(self):
        return self.stateStatus is not None and self.stateStatus.state in AutoShootGunState.SHOOTING_STATES

    @checkStateStatus(states=AutoShootGunState.SHOOTING_STATES, defReturn=0.0)
    def getCurrentDispersionFactor(self, stateStatus=None):
        dt = max(BigWorld.serverTime() - stateStatus.updateTime, 0.0)
        currDispersionFactor = stateStatus.dispersionFactor + dt * stateStatus.shotDispersionPerSec
        return min(currDispersionFactor, stateStatus.maxShotDispersion)

    def getDefaultShotRatePerSecond(self):
        return self.__defaultShotRatePerSecond

    def getGroupShotInterval(self):
        spinningRateFactor = self.__getSpinningRateFactor()
        temperatureFactor = self.__getTemperatureFactor()
        temperatureIntervalFactor = 1.0 / temperatureFactor if temperatureFactor > 0.0 else 1.0
        spinningIntervalFactor = 1.0 / spinningRateFactor if spinningRateFactor > 0.0 else 1.0
        return self.defaultShotRate * spinningIntervalFactor * temperatureIntervalFactor

    def getShotRatePerSecond(self):
        return self.__defaultShotRatePerSecond * self.__getSpinningRateFactor() * self.__getTemperatureFactor()

    def set_defaultShotRate(self, _=None):
        self.__updateShootingRates()

    def set_stateStatus(self, _=None):
        self._updateMechanicAvatar()
        self._updateMechanicAppearance()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(AutoShootGunController, self).onDestroy()

    def onDiscreteShot(self):
        self.__shootingEvents.processDiscreteShot()

    def _initMechanic(self):
        self.__updateShootingRates()
        super(AutoShootGunController, self)._initMechanic()

    def _onAppearanceReady(self):
        typeDescriptor = self.entity.typeDescriptor
        self.__gunsGroupSize = typeDescriptor.gun.autoShoot.groupSize
        self.__shootingEvents.processAppearanceReady()
        self.__updateShootingRates()
        super(AutoShootGunController, self)._onAppearanceReady()

    def _onMechanicAvatarUpdate(self, player):
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onMechanicAppearanceUpdate(self):
        self.__shootingEvents.updateAutoShootingStatus(self.stateStatus)

    def __getSpinningRateFactor(self):
        spinningCtrl = self.entity.dynamicComponents.get('spinGunController', None)
        return spinningCtrl.getSpinningValue() if spinningCtrl is not None else 1.0

    def __getTemperatureFactor(self):
        temperatureCtrl = self.entity.dynamicComponents.get('temperatureGunController', None)
        return temperatureCtrl.getAutoShootRateFactor() if temperatureCtrl is not None else 1.0

    def __updateShootingRates(self):
        defaultShotRate = self.defaultShotRate
        self.__defaultShotRatePerSecond = self.__gunsGroupSize / defaultShotRate if defaultShotRate else 0.0
        self.__shootingEvents.onShotRateUpdate(self.getShotRatePerSecond())
