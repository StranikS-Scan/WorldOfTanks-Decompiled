# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/vehicle_mechanics_blocks.py
import typing
from constants import CONCENTRATION_MODE_STATE, OVERHEAT_GAIN_STATE, POWER_MODE_STATE, RECHARGEABLE_NITRO_STATE, SECONDARY_GUN_STATE, VEHICLE_SIEGE_STATE, TARGET_DESIGNATOR_STATE, STATIONARY_RELOAD_STATE, GUN_LOCK_REASONS
from visual_script.misc import ASPECT
from visual_script.vehicle_blocks import VehicleMeta
from visual_script.type import VScriptEnum
if typing.TYPE_CHECKING:
    from typing import Type

class VehicleMechanicsMeta(VehicleMeta):

    @classmethod
    def blockCategory(cls):
        pass


class ConcentrationModeStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return CONCENTRATION_MODE_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class VehicleSiegeStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return VEHICLE_SIEGE_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class PowerModeStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return POWER_MODE_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class SecondaryGunStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return SECONDARY_GUN_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class RechargeableNitroStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return RECHARGEABLE_NITRO_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class OverheatGainStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return OVERHEAT_GAIN_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class TargetDesignatorStateEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return TARGET_DESIGNATOR_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT, ASPECT.SERVER]


class StationaryReloadEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return STATIONARY_RELOAD_STATE

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]


class StationaryReloadLockEnum(VScriptEnum):

    @classmethod
    def slotType(cls):
        pass

    @classmethod
    def vs_enum(cls):
        return GUN_LOCK_REASONS

    @classmethod
    def vs_aspects(cls):
        return [ASPECT.CLIENT]
