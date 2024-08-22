# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import logging
import typing
import BigWorld
import CGF
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from gui.battle_control.controllers.auto_shoot_guns.auto_shoot_wrappers import checkStateStatus
from vehicle_systems.entity_components.vehicle_mechanic_component import getPlayerVehicleMechanic, VehicleMechanicComponent
from vehicle_systems.auto_shoot_guns.shooting_events import AutoShootingEvents
from vehicle_systems.auto_shoot_guns.custom_integrations import AutoShootCustomIntegrations
from vehicle_systems.model_assembler import loadAppearancePrefab
if typing.TYPE_CHECKING:
    from vehicle_systems.auto_shoot_guns.system_interfaces import IAutoShootingEvents
_logger = logging.getLogger(__name__)

def getPlayerVehicleAutoShootGunController():
    return getPlayerVehicleMechanic('autoShootGunController')


class AutoShootGunController(VehicleMechanicComponent):

    def __init__(self):
        super(AutoShootGunController, self).__init__()
        self.__prefabRoot = None
        self.__gunsGroupSize = 0
        self.__groupRatePerSecond = 0.0
        self.__shotRatePerSecond = 0.0
        self.__shootingPrefab = ''
        self.__shootingEvents = AutoShootingEvents(self)
        AutoShootCustomIntegrations(self.entity, self).subscribe(self.__shootingEvents)
        self._initMechanic()
        return

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

    def getShotRatePerSecond(self):
        return self.__shotRatePerSecond

    def set_defaultShotRate(self, _=None):
        self.__updateShootingRates()

    def set_stateStatus(self, _=None):
        self._updateMechanicAvatar()
        self._updateMechanicAppearance()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        if self.__prefabRoot is not None:
            _logger.debug('[AutoShoot] removeGameObject (onDestroy) for %s', self.entity.id)
            CGF.removeGameObject(self.__prefabRoot)
            self.__prefabRoot = None
        super(AutoShootGunController, self).onDestroy()
        return

    def onDiscreteShot(self):
        self.__shootingEvents.processDiscreteShot()

    def _initMechanic(self):
        self.__updateShootingRates()
        super(AutoShootGunController, self)._initMechanic()

    def _onAppearanceReady(self):
        appearance = self.entity.appearance
        typeDescriptor = self.entity.typeDescriptor
        skin = appearance.modelsSetParams.skin or 'default'
        self.__gunsGroupSize = typeDescriptor.gun.autoShoot.groupSize
        self.__shootingPrefab = typeDescriptor.gun.prefabs[skin]['main'][0]
        self.__shootingEvents.processAppearanceReady()
        self.__updateShootingRates()
        loadAppearancePrefab(self.__shootingPrefab, appearance, self.__onShootingPrefabLoaded)
        _logger.debug('[AutoShoot] loadAppearancePrefab for %s', self.entity.id)

    def _onMechanicAvatarUpdate(self, player):
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _onMechanicAppearanceUpdate(self):
        self.__shootingEvents.updateAutoShootingStatus(self.stateStatus)

    def __updateShootingRates(self):
        defaultShotRate = self.defaultShotRate
        self.__groupRatePerSecond = 1.0 / defaultShotRate if defaultShotRate else 0.0
        self.__shotRatePerSecond = self.__groupRatePerSecond * self.__gunsGroupSize
        self.__shootingEvents.onShotRateUpdate(self.getShotRatePerSecond())

    def __onShootingPrefabLoaded(self, root):
        if not root.isValid:
            _logger.error('[AutoShoot] failed to load prefab: %s', self.__shootingPrefab)
            return
        if self.isComponentDestroyed():
            _logger.debug('[AutoShoot] removeGameObject (onLoaded) for %s', self.entity.id)
            CGF.removeGameObject(root)
            return
        self.__prefabRoot = root
