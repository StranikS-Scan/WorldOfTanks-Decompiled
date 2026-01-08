# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/TwinGunController.py
import typing
from constants import DUPLET_GUN_INDEXES_TUPLE
from events_handler import eventHandler
from gui.shared.utils.decorators import ReprInjector
from gui.battle_control.components_states.ammo import DefaultComponentAmmoState
from vehicles.components.component_wrappers import ifAppearanceReady
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.mechanics.common import IMechanicComponentLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.parts.guns.twin_shoot import ITwinShootGunComponent, createTwinShootingEvents
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.twin_shoot import ITwinShootingEvents

class TwinGunAmmoState(DefaultComponentAmmoState):

    def __init__(self, shotsAmount):
        super(TwinGunAmmoState, self).__init__()
        self.__shotsAmount = shotsAmount

    def getShotsAmount(self):
        return self.__shotsAmount


@ReprInjector.withParent()
class TwinGunController(VehicleDynamicComponent, ITwinShootGunComponent, IMechanicComponentLogic):

    def __init__(self):
        super(TwinGunController, self).__init__()
        self.__afterShotDelay = 0.0
        self.__shootingEvents = createTwinShootingEvents(self.entity, self)
        self._initComponent()

    @property
    def vehicleMechanic(self):
        return VehicleMechanic.TWIN_GUN

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def isDoubleBarrelMode(self):
        return len(self.getActiveGunIndexes()) > 1

    def getActiveGunIndexes(self):
        return tuple(self.activeGunIndexes)

    def getAfterShotDelay(self):
        return self.__afterShotDelay

    def getComponentParams(self):
        return self.getAfterShotDelay()

    def getNextGunIndexes(self):
        return tuple(self.nextGunIndexes or self.activeGunIndexes)

    @ifAppearanceReady
    def set_activeGunIndexes(self, _=None):
        self.__updateActiveGunIndexes()

    @ifAppearanceReady
    def set_nextGunIndexes(self, _=None):
        self.__updateNextGunIndexes()

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(TwinGunController, self).onDestroy()

    def onDiscreteShot(self, gunIndex):
        self.__shootingEvents.processDiscreteShot(gunIndex)

    def onDoubleShot(self):
        self.__shootingEvents.processMultiShot(DUPLET_GUN_INDEXES_TUPLE)

    @eventHandler
    def onCollectAmmoStates(self, ammoStates):
        ammoStates[self.vehicleMechanic.value] = TwinGunAmmoState(self.shotsCount)

    def _onAppearanceReady(self):
        super(TwinGunController, self)._onAppearanceReady()
        self.__shootingEvents.processAppearanceReady()

    def _onComponentAppearanceUpdate(self, **kwargs):
        super(TwinGunController, self)._onComponentAppearanceUpdate(**kwargs)
        self.__updateActiveGunIndexes()
        self.__updateNextGunIndexes()

    def _collectComponentParams(self, typeDescriptor):
        super(TwinGunController, self)._collectComponentParams(typeDescriptor)
        self.__afterShotDelay = typeDescriptor.gun.twinGun.afterShotDelay

    def __updateActiveGunIndexes(self):
        self.__shootingEvents.onActiveGunsUpdate(self.getActiveGunIndexes())

    def __updateNextGunIndexes(self):
        self.__shootingEvents.processNextGunsUpdate(self.getNextGunIndexes())
