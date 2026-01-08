# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/base_factory.py
from __future__ import absolute_import
from itertools import chain
import typing
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.vehicle_mechanics.constants import MECHANIC_OVERRIDES
from gui.shared.gui_items.vehicle_mechanics.interfaces import IMechanicFactory
from vehicles.mechanics.mechanic_constants import VEHICLE_PARAMS_TO_MECHANIC
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleDescr
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    VehicleModule = typing.TypeVar('VehicleModule')
    MechanicsParams = typing.TypeVar('MechanicsParams')

class BaseMechanicFactory(IMechanicFactory):

    @classmethod
    def getMechanics(cls, guiItem, vehDescr, mechanics=None, withOverrides=False):
        mechanics = mechanics if mechanics is not None else set()
        mechanicChecks = cls._getMechanicsChecks(guiItem, vehDescr)
        mechanics.update((mechanic for hasMechanic, mechanic in mechanicChecks if hasMechanic))
        mechanicParams = cls._getMechanicsParams(guiItem, vehDescr)
        mechanics.update((VEHICLE_PARAMS_TO_MECHANIC[p] for p in mechanicParams if p in VEHICLE_PARAMS_TO_MECHANIC))
        if withOverrides:
            overrides = MECHANIC_OVERRIDES.get(guiItem.itemTypeID, {}) if guiItem.itemTypeID == GUI_ITEM_TYPE.VEHICLE else {k:v for d in MECHANIC_OVERRIDES.values() for k, v in d.items()}
            for excluded in chain(*(override for mechanic, override in overrides.items() if mechanic in mechanics)):
                mechanics.discard(excluded)

        return mechanics

    @classmethod
    def _getMechanicsChecks(cls, guiItem, vehDescr):
        return []

    @classmethod
    def _getMechanicsParams(cls, _, __):
        return {}
