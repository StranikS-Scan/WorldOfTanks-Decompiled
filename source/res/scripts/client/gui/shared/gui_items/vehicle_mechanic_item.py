# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanic_item.py
import typing
from itertools import chain
from gui import GUI_SETTINGS
from gui.impl.gen.view_models.common.vehicle_mechanic_model import MechanicsEnum
from gui.shared.gui_items.gui_item import GUIItem
from gui.shared.utils.decorators import ReprInjector
from items import vehicles
from vehicles.mechanics.mechanic_constants import VehicleMechanic, VEHICLE_PARAMS_TO_MECHANIC
VEHICLE_MECHANICS_GUI_MAP = {VehicleMechanic.MAGAZINE_GUN: MechanicsEnum.MAGAZINE_GUN,
 VehicleMechanic.AUTO_LOADER_GUN: MechanicsEnum.AUTO_LOADER_GUN,
 VehicleMechanic.AUTO_LOADER_GUN_BOOST: MechanicsEnum.AUTO_LOADER_GUN_BOOST,
 VehicleMechanic.DAMAGE_MUTABLE: MechanicsEnum.DAMAGE_MUTABLE,
 VehicleMechanic.DUAL_GUN: MechanicsEnum.DUAL_GUN,
 VehicleMechanic.HYDRAULIC_CHASSIS: MechanicsEnum.HYDRAULIC_CHASSIS,
 VehicleMechanic.TRACK_WITHIN_TRACK: MechanicsEnum.TRACK_WITHIN_TRACK,
 VehicleMechanic.SIEGE_MODE: MechanicsEnum.SIEGE_MODE,
 VehicleMechanic.STUN: MechanicsEnum.STUN,
 VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS: MechanicsEnum.HYDRAULIC_WHEELED_CHASSIS,
 VehicleMechanic.TURBOSHAFT_ENGINE: MechanicsEnum.TURBOSHAFT_ENGINE,
 VehicleMechanic.ROCKET_ACCELERATION: MechanicsEnum.ROCKET_ACCELERATION,
 VehicleMechanic.DUAL_ACCURACY: MechanicsEnum.DUAL_ACCURACY,
 VehicleMechanic.AUTO_SHOOT_GUN: MechanicsEnum.AUTO_SHOOT_GUN,
 VehicleMechanic.TWIN_GUN: MechanicsEnum.TWIN_GUN,
 VehicleMechanic.IMPROVED_RAMMING: MechanicsEnum.IMPROVED_RAMMING,
 VehicleMechanic.CONCENTRATION_MODE: MechanicsEnum.CONCENTRATION_MODE,
 VehicleMechanic.BATTLE_FURY: MechanicsEnum.BATTLE_FURY,
 VehicleMechanic.EXTRA_SHOT_CLIP: MechanicsEnum.EXTRA_SHOT_CLIP,
 VehicleMechanic.POWER_MODE: MechanicsEnum.POWER_MODE,
 VehicleMechanic.ACCURACY_STACKS: MechanicsEnum.ACCURACY_STACKS,
 VehicleMechanic.SUPPORT_WEAPON: MechanicsEnum.SUPPORT_WEAPON,
 VehicleMechanic.PILLBOX_SIEGE_MODE: MechanicsEnum.PILLBOX_SIEGE_MODE,
 VehicleMechanic.CHARGEABLE_BURST: MechanicsEnum.CHARGEABLE_BURST,
 VehicleMechanic.RECHARGEABLE_NITRO: MechanicsEnum.RECHARGEABLE_NITRO,
 VehicleMechanic.CHARGE_SHOT: MechanicsEnum.CHARGE_SHOT,
 VehicleMechanic.OVERHEAT_STACKS: MechanicsEnum.OVERHEAT_STACKS,
 VehicleMechanic.STANCE_DANCE: MechanicsEnum.STANCE_DANCE,
 VehicleMechanic.STATIONARY_RELOAD: MechanicsEnum.STATIONARY_RELOAD,
 VehicleMechanic.TARGET_DESIGNATOR: MechanicsEnum.TARGET_DESIGNATOR}
VEHICLE_MECHANICS_OVERRIDES = {VehicleMechanic.TURBOSHAFT_ENGINE: {VehicleMechanic.SIEGE_MODE},
 VehicleMechanic.DUAL_GUN: {VehicleMechanic.SIEGE_MODE},
 VehicleMechanic.DUAL_ACCURACY: {VehicleMechanic.SIEGE_MODE},
 VehicleMechanic.TWIN_GUN: {VehicleMechanic.SIEGE_MODE},
 VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS: {VehicleMechanic.SIEGE_MODE}}
GUN_MECHANICS_OVERRIDES = {VehicleMechanic.AUTO_LOADER_GUN_BOOST: {VehicleMechanic.AUTO_LOADER_GUN, VehicleMechanic.MAGAZINE_GUN},
 VehicleMechanic.AUTO_LOADER_GUN: {VehicleMechanic.MAGAZINE_GUN},
 VehicleMechanic.AUTO_SHOOT_GUN: {VehicleMechanic.MAGAZINE_GUN}}
CHASSIS_MECHANICS_OVERRIDES = {VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS: {VehicleMechanic.HYDRAULIC_CHASSIS}}
ENGINE_MECHANICS_OVERRIDES = {}

def extendMechanics(mechanics, mechanicsParams, checkers, overrides):
    mechanics.update((mechanic for condition, mechanic in checkers if condition))
    mechanics.update((VEHICLE_PARAMS_TO_MECHANIC[p] for p in mechanicsParams if p in VEHICLE_PARAMS_TO_MECHANIC))
    for excluded in chain(*(override for mechanic, override in overrides.iteritems() if mechanic in mechanics)):
        mechanics.discard(excluded)


@ReprInjector.simple(('guiName', 'guiName'), ('isSpecial', 'isSpecial'))
class VehicleMechanicItem(GUIItem):
    __slots__ = ('__mechanic', '__vehIntCD')

    def __init__(self, mechanic, vehIntCD):
        super(VehicleMechanicItem, self).__init__()
        self.__mechanic = mechanic
        self.__vehIntCD = vehIntCD

    @property
    def isSpecial(self):
        return self.__mechanic.value in vehicles.g_cache.vehicleMechanics.get(self.__vehIntCD, {})

    @property
    def hasVideo(self):
        urlDict = GUI_SETTINGS.lookup('mechanicsVideoUrls')
        return urlDict and self.__mechanic.value in urlDict

    @property
    def guiName(self):
        return VEHICLE_MECHANICS_GUI_MAP[self.__mechanic]

    @property
    def staticParams(self):
        return vehicles.g_cache.vehicleMechanics.get(self.__vehIntCD, {}).get(self.__mechanic.value, ())
