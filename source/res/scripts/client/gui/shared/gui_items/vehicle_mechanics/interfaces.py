# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/interfaces.py
from __future__ import absolute_import
import typing
from typing import Set, Optional
if typing.TYPE_CHECKING:
    from items.vehicle_mechanics_types import VehicleMechanicKey
    from items.vehicles import VehicleDescr
    VehicleModule = typing.TypeVar('VehicleModule')

class IMechanicFactory(object):

    @classmethod
    def getMechanics(cls, guiItem, vehDescr, mechanics=None, withOverrides=False):
        raise NotImplementedError
