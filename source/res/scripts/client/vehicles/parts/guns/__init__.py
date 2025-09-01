# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/__init__.py
import typing
from vehicles.parts.guns.custom_integrations import GunShootingCustomIntegrations
from vehicles.parts.guns.guns_interfaces import IGunComponent, IGunShootingEvents, IGunShootingListener, IGunShootingListenerLogic
from vehicles.parts.guns.shooting_events import GunShootingEvents
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
__all__ = ('IGunComponent', 'IGunShootingEvents', 'IGunShootingListener', 'IGunShootingListenerLogic', 'createGunShootingEvents')

def createGunShootingEvents(vehicle, component):
    shootingEvents = GunShootingEvents(component)
    GunShootingCustomIntegrations(vehicle, component).subscribeTo(shootingEvents)
    return shootingEvents
