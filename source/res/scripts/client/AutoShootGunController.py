# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import typing
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from constants import DEFAULT_GUN_INSTALLATION_INDEX
from vehicles.components.component_wrappers import checkStateStatus
from vehicles.components.vehicle_component import VehicleGunPrefabDynamicComponent
from vehicles.mechanics.auto_shoot_guns.custom_integrations import AutoShootCustomIntegrations
from vehicles.mechanics.auto_shoot_guns.mechanic_events import AutoShootingEvents
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getPlayerVehicleMechanic
from vehicles.parts.guns import IGunComponent
if typing.TYPE_CHECKING:
    import CGF
    from vehicles.mechanics.auto_shoot_guns.mechanic_interfaces import IAutoShootingEvents

def getPlayerVehicleAutoShootGunController():
    return getPlayerVehicleMechanic(VehicleMechanic.AUTO_SHOOT_GUN)


class AutoShootGunController(VehicleGunPrefabDynamicComponent, IGunComponent):

    def __init__(self):
        super(AutoShootGunController, self).__init__()
        self.__gunsGroupSize = 0
        self.__groupRatePerSecond = 0.0
        self.__shotRatePerSecond = 0.0
        self.__shootingEvents = AutoShootingEvents(self)
        AutoShootCustomIntegrations(self.entity, self).subscribe(self.__shootingEvents)
        self._initComponent()

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

    def getGroupShotInterval(self):
        return self.defaultShotRate

    def getGunInstallationIndex(self):
        return DEFAULT_GUN_INSTALLATION_INDEX

    def getGunRootGameObject(self):
        return self._prefabRoot

    def getShotRatePerSecond(self):
        return self.__shotRatePerSecond

    def set_defaultShotRate(self, _=None):
        self.__collectShootingRates()
        self.__updateShootingRates()

    def set_stateStatus(self, _=None):
        self._updateComponentAvatar()
        self._updateComponentAppearance()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(AutoShootGunController, self).onDestroy()

    def onDiscreteShot(self):
        self.__shootingEvents.processDiscreteShot()

    def _initComponent(self):
        self.__collectShootingRates()
        super(AutoShootGunController, self)._initComponent()

    def _onAppearanceReady(self):
        super(AutoShootGunController, self)._onAppearanceReady()
        self.__shootingEvents.processAppearanceReady()
        self.__updateShootingRates()

    def _onComponentAvatarUpdate(self, player):
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onComponentAppearanceUpdate(self):
        self.__shootingEvents.updateAutoShootingStatus(self.stateStatus)

    def _collectComponentParams(self, typeDescriptor):
        super(AutoShootGunController, self)._collectComponentParams(typeDescriptor)
        self.__gunsGroupSize = typeDescriptor.gun.autoShoot.groupSize
        self.__collectShootingRates()

    def __collectShootingRates(self):
        defaultShotRate = self.defaultShotRate
        self.__groupRatePerSecond = 1.0 / defaultShotRate if defaultShotRate else 0.0
        self.__shotRatePerSecond = self.__groupRatePerSecond * self.__gunsGroupSize

    def __updateShootingRates(self):
        self.__shootingEvents.onShotRateUpdate(self.getShotRatePerSecond())
