# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/common/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.parts.guns.common.custom_integrations import GunShootingCustomIntegrations
from vehicles.parts.guns.common.guns_interfaces import IGunComponent, IGunShootingEvents, IGunShootingEventsLogic, IGunShootingListener, IGunShootingListenerLogic
from vehicles.parts.guns.common.shooting_events import GunShootingEvents, GunShootingCoreIntegration, GunShootingEventsDebugger
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
__all__ = ('IGunComponent', 'IGunShootingEvents', 'IGunShootingEventsLogic', 'IGunShootingListener', 'IGunShootingListenerLogic', 'GunShootingEvents', 'GunShootingCoreIntegration', 'GunShootingEventsDebugger', 'GunShootingCustomIntegrations', 'createGunShootingEvents')

@activateEventsContainer()
def createGunShootingEvents(vehicle, component, **_):
    shootingEvents = GunShootingEvents(component)
    GunShootingCustomIntegrations(vehicle, component).subscribeTo(shootingEvents)
    return shootingEvents
