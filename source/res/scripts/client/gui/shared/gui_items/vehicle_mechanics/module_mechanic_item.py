# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/module_mechanic_item.py
from __future__ import absolute_import
import typing
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsEnum
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.gui_items.vehicle_mechanics.constants import VEHICLE_MECHANICS_GUI_MAP
from gui.shared.utils.decorators import ReprInjector
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    VehicleModule = typing.TypeVar('VehicleModule')

@ReprInjector.simple('guiName')
class ModuleMechanicItem(GUIItem):
    __slots__ = ('_mechanic',)
    _GUI_SUPPORTED_MECHANICS = {}
    _EXTRA_STATUSES = {}

    def __init__(self, mechanic, _=None):
        super(ModuleMechanicItem, self).__init__()
        self._mechanic = mechanic

    @property
    def isHidden(self):
        return self._mechanic not in self._GUI_SUPPORTED_MECHANICS

    @property
    def guiName(self):
        return VEHICLE_MECHANICS_GUI_MAP.get(self._mechanic, MechanicsEnum.UNKNOWN)

    def getExtraStatuses(self, _):
        return self.guiName.value if self._mechanic in self._EXTRA_STATUSES else None


class GunMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanic.AUTO_LOADER_GUN,
     VehicleMechanic.AUTO_LOADER_GUN_BOOST,
     VehicleMechanic.AUTO_SHOOT_GUN,
     VehicleMechanic.DAMAGE_MUTABLE,
     VehicleMechanic.DUAL_ACCURACY,
     VehicleMechanic.DUAL_GUN,
     VehicleMechanic.HEATING_ZONES_GUN,
     VehicleMechanic.MAGAZINE_GUN,
     VehicleMechanic.OVERHEAT_GUN,
     VehicleMechanic.STUN,
     VehicleMechanic.TWIN_GUN}
    _EXTRA_STATUSES = {VehicleMechanic.AUTO_LOADER_GUN,
     VehicleMechanic.AUTO_LOADER_GUN_BOOST,
     VehicleMechanic.AUTO_SHOOT_GUN,
     VehicleMechanic.DAMAGE_MUTABLE,
     VehicleMechanic.DUAL_ACCURACY,
     VehicleMechanic.DUAL_GUN,
     VehicleMechanic.HEATING_ZONES_GUN,
     VehicleMechanic.MAGAZINE_GUN,
     VehicleMechanic.OVERHEAT_GUN,
     VehicleMechanic.TWIN_GUN}


class EngineMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanic.TURBOSHAFT_ENGINE, VehicleMechanic.ROCKET_ACCELERATION, VehicleMechanic.STAGED_JET_BOOSTERS}
    _EXTRA_STATUSES = {VehicleMechanic.TURBOSHAFT_ENGINE, VehicleMechanic.ROCKET_ACCELERATION, VehicleMechanic.STAGED_JET_BOOSTERS}


class ChassisMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS, VehicleMechanic.HYDRAULIC_CHASSIS, VehicleMechanic.TRACK_WITHIN_TRACK}
    _EXTRA_STATUSES = {VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS, VehicleMechanic.HYDRAULIC_CHASSIS, VehicleMechanic.TRACK_WITHIN_TRACK}

    def getExtraStatuses(self, module):
        return 'hydroAutoSiegeChassis' if self._mechanic == VehicleMechanic.HYDRAULIC_CHASSIS and module.hasAutoSiege() else super(ChassisMechanicItem, self).getExtraStatuses(module)
