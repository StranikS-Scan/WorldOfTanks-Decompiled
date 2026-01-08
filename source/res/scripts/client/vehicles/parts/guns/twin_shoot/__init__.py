# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/twin_shoot/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.parts.guns.twin_shoot.custom_integrations import TwinShootCustomIntegrations
from vehicles.parts.guns.twin_shoot.guns_interfaces import ITwinShootGunComponent, ITwinShootingEvents, ITwinShootingListener
from vehicles.parts.guns.twin_shoot.shooting_events import TwinShootingEvents
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
__all__ = ('ITwinShootGunComponent', 'ITwinShootingEvents', 'ITwinShootingListener', 'createTwinShootingEvents')

@activateEventsContainer()
def createTwinShootingEvents(vehicle, component, **_):
    shootingEvents = TwinShootingEvents(component)
    TwinShootCustomIntegrations(vehicle, component).subscribeTo(shootingEvents)
    return shootingEvents
