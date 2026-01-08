# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AutoShootGunController.py
import typing
import BigWorld
from auto_shoot_guns.auto_shoot_guns_common import AutoShootGunState
from constants import UNKNOWN_GUN_INDEX
from gui.shared.utils.decorators import ReprInjector
from items.components.component_constants import DEFAULT_GUN_AUTOSHOOT
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponentLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.parts.guns.auto_shoot import IAutoShootDispersionState, IAutoShootGunComponentState, IAutoShootGunComponent, createAutoShootingEvents
if typing.TYPE_CHECKING:
    from items.components.component_constants import AutoShoot
    from vehicles.parts.guns.auto_shoot import IAutoShootingEvents

class AutoShootDispersionState(IAutoShootDispersionState):

    def __init__(self, updateTime, dispersionFactor, shotDispersionPerSec, maxShotDispersion):
        self.__updateTime = updateTime
        self.__dispersionFactor = dispersionFactor
        self.__shotDispersionPerSec = shotDispersionPerSec
        self.__maxShotDispersion = maxShotDispersion

    @classmethod
    def fromDispersionStatus(cls, status):
        return cls(status.updateTime, status.dispersionFactor, status.shotDispersionPerSec, status.maxShotDispersion)

    def getCurrentDispersionFactor(self):
        dt = max(BigWorld.serverTime() - self.__updateTime, 0.0)
        currDispersionFactor = self.__dispersionFactor + dt * self.__shotDispersionPerSec
        return min(currDispersionFactor, self.__maxShotDispersion)


class AutoShootGunComponentState(IAutoShootGunComponentState):

    def __init__(self, state, defaultShotRatePerSecond, groupShotInterval, shotRatePerSecond):
        self.__state = state
        self.__defaultShotRatePerSecond = defaultShotRatePerSecond
        self.__groupShotInterval = groupShotInterval
        self.__shotRatePerSecond = shotRatePerSecond

    @classmethod
    def fromComponentStatus(cls, status, defaultShotRate, params):
        defaultShotRatePerSecond = params.groupSize / defaultShotRate if defaultShotRate > 0.0 else 0.0
        return cls(status.state, defaultShotRatePerSecond, defaultShotRate * status.rateMultFactor, defaultShotRatePerSecond / status.rateMultFactor if status.rateMultFactor > 0.0 else 0.0)

    def isShooting(self):
        return self.__state in AutoShootGunState.SHOOTING_STATES

    def isContinuousShooting(self):
        return self.__state == AutoShootGunState.CONTINUOUS_SHOOTING

    def getDefaultShotRatePerSecond(self):
        return self.__defaultShotRatePerSecond

    def getGroupShotInterval(self):
        return self.__groupShotInterval

    def getShotRatePerSecond(self):
        return self.__shotRatePerSecond


@ReprInjector.withParent()
class AutoShootGunController(VehicleDynamicComponent, IAutoShootGunComponent, IMechanicComponentLogic):
    DEFAULT_COMPONENT_STATE = AutoShootGunComponentState(AutoShootGunState.NONE, 0.0, 0.0, 0.0)
    DEFAULT_DISPERSION_STATE = AutoShootDispersionState(0.0, 0.0, 0.0, 0.0)

    def __init__(self):
        super(AutoShootGunController, self).__init__()
        self.__componentParams = DEFAULT_GUN_AUTOSHOOT
        self.__componentState = self.DEFAULT_COMPONENT_STATE
        self.__dispersionState = self.DEFAULT_DISPERSION_STATE
        self.__shootingEvents = createAutoShootingEvents(self.entity, self)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.AUTO_SHOOT_GUN

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def getComponentState(self):
        return self.__componentState

    def getDispersionState(self):
        return self.__dispersionState

    def set_defaultShotRate(self, _=None):
        self._updateComponentAppearance()

    def set_stateStatus(self, _=None):
        self._updateComponentAppearance()

    def set_dispersionStatus(self, _=None):
        self._updateComponentAvatar()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(AutoShootGunController, self).onDestroy()

    def onDiscreteShot(self):
        self.__shootingEvents.processDiscreteShot(UNKNOWN_GUN_INDEX)

    def _onAppearanceReady(self):
        super(AutoShootGunController, self)._onAppearanceReady()
        self.__updateComponentState()
        self.__shootingEvents.processAppearanceReady()

    def _onAvatarReady(self, player):
        super(AutoShootGunController, self)._onAvatarReady(player)
        self.__updateDispersionState()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(AutoShootGunController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateComponentState()
        self.__shootingEvents.updateAutoShootingState(self.__componentState)

    def _onComponentAvatarUpdate(self, player):
        super(AutoShootGunController, self)._onComponentAvatarUpdate(player)
        self.__updateDispersionState()
        player.getOwnVehicleShotDispersionAngle(player.gunRotator.turretRotationSpeed)

    def _collectComponentParams(self, typeDescriptor):
        super(AutoShootGunController, self)._collectComponentParams(typeDescriptor)
        self.__componentParams = typeDescriptor.gun.autoShoot

    def __updateComponentState(self):
        self.__componentState = AutoShootGunComponentState.fromComponentStatus(self.stateStatus, self.defaultShotRate, self.__componentParams) if self.stateStatus is not None else self.DEFAULT_COMPONENT_STATE
        return

    def __updateDispersionState(self):
        self.__dispersionState = AutoShootDispersionState.fromDispersionStatus(self.dispersionStatus) if self.dispersionStatus is not None else self.DEFAULT_DISPERSION_STATE
        return
