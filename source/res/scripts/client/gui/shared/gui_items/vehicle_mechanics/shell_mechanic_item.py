# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/shell_mechanic_item.py
from __future__ import absolute_import
from gui.shared.gui_items.vehicle_mechanics.module_mechanic_item import ModuleMechanicItem
from gui.shared.utils.decorators import ReprInjector
from items import vehicles
from vehicles.mechanics.mechanic_constants import VehicleMechanic
_SHELL_MECHANIC_PRIORITY = {VehicleMechanic.SHELL_PARAMS_SWITCHER: 1,
 VehicleMechanic.SHELL_CALIBRATION: 1,
 VehicleMechanic.LOW_CHARGE_SHOT: 1,
 VehicleMechanic.BUSTLE_FEED: 1}

@ReprInjector.withParent('rank', 'mechanicSubtype')
class ShellMechanicItem(ModuleMechanicItem):
    __slots__ = ('__rank', '__mechanicSubtype')
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanic.SHELL_PARAMS_SWITCHER,
     VehicleMechanic.LOW_CHARGE_SHOT,
     VehicleMechanic.SHELL_CALIBRATION,
     VehicleMechanic.BUSTLE_FEED}

    def __init__(self, mechanic, *args, **kwargs):
        super(ShellMechanicItem, self).__init__(mechanic)
        vehIntCD = kwargs['vehIntCD']
        vehicleMechanicItem = self.itemsFactory.createVehicleMechanicItem(mechanic, vehIntCD)
        self.__rank = vehicleMechanicItem.rank
        shellCD = kwargs.get('shellCD')
        mechanicCache = vehicles.g_cache.vehicleMechanics.get(vehIntCD, {}).get(mechanic.value, {})
        self.__mechanicSubtype = mechanicCache.get('mechanicSubtypes', {}).get(shellCD, {})

    @property
    def hasVideo(self):
        return False

    @property
    def priority(self):
        return _SHELL_MECHANIC_PRIORITY.get(self._mechanic, 0)

    @property
    def rank(self):
        return self.__rank

    @property
    def mechanicSubtype(self):
        return self.__mechanicSubtype
