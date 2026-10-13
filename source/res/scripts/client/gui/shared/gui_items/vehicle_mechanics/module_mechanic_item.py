# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/module_mechanic_item.py
from __future__ import absolute_import
import typing
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsEnum
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.gui_items.vehicle_mechanics.constants import VEHICLE_MECHANICS_GUI_MAP
from gui.shared.utils.decorators import ReprInjector
from items.vehicle_mechanics_types import VehicleMechanicKey, VehicleMechanicKeys
if typing.TYPE_CHECKING:
    VehicleModule = typing.TypeVar('VehicleModule')

@ReprInjector.simple('mechanic', 'guiName')
class ModuleMechanicItem(GUIItem):
    __slots__ = ('_mechanic',)
    _GUI_SUPPORTED_MECHANICS = {}
    _EXTRA_STATUSES = {}

    def __init__(self, mechanic, *args, **kwargs):
        super(ModuleMechanicItem, self).__init__()
        self._mechanic = mechanic

    @property
    def isHidden(self):
        return self._mechanic not in self._GUI_SUPPORTED_MECHANICS

    @property
    def guiName(self):
        return VEHICLE_MECHANICS_GUI_MAP.get(self._mechanic, MechanicsEnum.UNKNOWN)

    @property
    def mechanic(self):
        return self._mechanic

    def getExtraStatuses(self, _):
        return self.guiName.value if self._mechanic in self._EXTRA_STATUSES else None


class GunMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanicKeys.AUTO_LOADER_GUN,
     VehicleMechanicKeys.AUTO_LOADER_GUN_BOOST,
     VehicleMechanicKeys.AUTO_SHOOT_GUN,
     VehicleMechanicKeys.DAMAGE_MUTABLE,
     VehicleMechanicKeys.DUAL_ACCURACY,
     VehicleMechanicKeys.DUAL_GUN,
     VehicleMechanicKeys.HEATING_ZONES_GUN,
     VehicleMechanicKeys.LOW_CHARGE_SHOT,
     VehicleMechanicKeys.MAGAZINE_GUN,
     VehicleMechanicKeys.OVERHEAT_GUN,
     VehicleMechanicKeys.PROPELLANT_GUN,
     VehicleMechanicKeys.SHELL_PARAMS_SWITCHER,
     VehicleMechanicKeys.STUN,
     VehicleMechanicKeys.TWIN_GUN}
    _EXTRA_STATUSES = {VehicleMechanicKeys.AUTO_LOADER_GUN,
     VehicleMechanicKeys.AUTO_LOADER_GUN_BOOST,
     VehicleMechanicKeys.AUTO_SHOOT_GUN,
     VehicleMechanicKeys.DAMAGE_MUTABLE,
     VehicleMechanicKeys.DUAL_ACCURACY,
     VehicleMechanicKeys.DUAL_GUN,
     VehicleMechanicKeys.HEATING_ZONES_GUN,
     VehicleMechanicKeys.LOW_CHARGE_SHOT,
     VehicleMechanicKeys.MAGAZINE_GUN,
     VehicleMechanicKeys.OVERHEAT_GUN,
     VehicleMechanicKeys.PROPELLANT_GUN,
     VehicleMechanicKeys.SHELL_PARAMS_SWITCHER,
     VehicleMechanicKeys.TWIN_GUN}


class EngineMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanicKeys.COMBAT_THROTTLE,
     VehicleMechanicKeys.ROCKET_ACCELERATION,
     VehicleMechanicKeys.STAGED_JET_BOOSTERS,
     VehicleMechanicKeys.TURBOSHAFT_ENGINE,
     VehicleMechanicKeys.WHEELED_DASH}
    _EXTRA_STATUSES = {VehicleMechanicKeys.COMBAT_THROTTLE,
     VehicleMechanicKeys.ROCKET_ACCELERATION,
     VehicleMechanicKeys.STAGED_JET_BOOSTERS,
     VehicleMechanicKeys.TURBOSHAFT_ENGINE,
     VehicleMechanicKeys.WHEELED_DASH}


class ChassisMechanicItem(ModuleMechanicItem):
    _GUI_SUPPORTED_MECHANICS = {VehicleMechanicKeys.HYDRAULIC_WHEELED_CHASSIS, VehicleMechanicKeys.HYDRAULIC_CHASSIS, VehicleMechanicKeys.TRACK_WITHIN_TRACK}
    _EXTRA_STATUSES = {VehicleMechanicKeys.HYDRAULIC_WHEELED_CHASSIS, VehicleMechanicKeys.HYDRAULIC_CHASSIS, VehicleMechanicKeys.TRACK_WITHIN_TRACK}

    def getExtraStatuses(self, module):
        return 'hydroAutoSiegeChassis' if self._mechanic == VehicleMechanicKeys.HYDRAULIC_CHASSIS and module.hasAutoSiege() else super(ChassisMechanicItem, self).getExtraStatuses(module)
