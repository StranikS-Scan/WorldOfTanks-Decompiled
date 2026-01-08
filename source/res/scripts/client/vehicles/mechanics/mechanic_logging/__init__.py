# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_logging/__init__.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.mechanic_logging.mechanic_input_logger import MechanicInputLogger
from vehicles.mechanics.mechanic_logging.mechanic_interfaces import IMechanicInputLoggingComponent
if typing.TYPE_CHECKING:
    from events_containers.components.life_cycle import ILifeCycleComponent
__all__ = ('IMechanicInputLoggingComponent', 'createMechanicInputLogger')

def createMechanicInputLogger(mechanicComponent, *commands):
    return MechanicInputLogger(mechanicComponent, *commands)
