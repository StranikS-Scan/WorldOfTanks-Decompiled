# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/parts/guns/auto_shoot/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.parts.guns.auto_shoot.custom_integrations import AutoShootCustomIntegrations
from vehicles.parts.guns.auto_shoot.guns_interfaces import IAutoShootDispersionState, IAutoShootGunComponentState, IAutoShootGunComponent, IAutoShootingEvents, IAutoShootingListener
from vehicles.parts.guns.auto_shoot.shooting_events import AutoShootingEvents
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
__all__ = ('IAutoShootDispersionState', 'IAutoShootGunComponentState', 'IAutoShootGunComponent', 'IAutoShootingEvents', 'IAutoShootingListener', 'createAutoShootingEvents')

@activateEventsContainer()
def createAutoShootingEvents(vehicle, component, **_):
    shootingEvents = AutoShootingEvents(component)
    AutoShootCustomIntegrations(vehicle, component).subscribeTo(shootingEvents)
    return shootingEvents
