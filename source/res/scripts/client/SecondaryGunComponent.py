# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/SecondaryGunComponent.py
import typing
from gui.shared.utils.decorators import ReprInjector
from vehicles.components.vehicle_component import VehicleDynamicComponent
from vehicles.parts.guns.common import IGunComponent, createGunShootingEvents
if typing.TYPE_CHECKING:
    from vehicles.parts.guns.common import IGunShootingEvents

@ReprInjector.withParent()
class SecondaryGunComponent(VehicleDynamicComponent, IGunComponent):

    def __init__(self):
        super(SecondaryGunComponent, self).__init__()
        self.__shootingEvents = createGunShootingEvents(self.entity, self)
        self._initComponent()

    @property
    def shootingEvents(self):
        return self.__shootingEvents

    def getGunInstallationIndex(self):
        return self.gunInstallationIndex

    def onDestroy(self):
        self.__shootingEvents.destroy()
        super(SecondaryGunComponent, self).onDestroy()

    def onDiscreteShot(self, gunIndex):
        self.__shootingEvents.processDiscreteShot(gunIndex)

    def onMultiShot(self, gunIndexes):
        self.__shootingEvents.processMultiShot(gunIndexes)

    def _onAppearanceReady(self):
        super(SecondaryGunComponent, self)._onAppearanceReady()
        self.__shootingEvents.processAppearanceReady()
