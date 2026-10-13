# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/fitting_item.py
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.shared.tooltips.advanced import BaseAdvancedTooltip, GunAltKeyData, ChassisAltKeyData, TurretAltKeyData, OptionalDeviceAltKeyData, EquipmentAltKeyData, BattleBoosterKeyData, ShellKeyData, DefaultAltKeyData

class FittingItemAdvanced(BaseAdvancedTooltip):
    MECHANIC_DATA_FACTORY = {FITTING_TYPES.VEHICLE_GUN: GunAltKeyData,
     FITTING_TYPES.VEHICLE_CHASSIS: ChassisAltKeyData,
     FITTING_TYPES.VEHICLE_TURRET: TurretAltKeyData,
     FITTING_TYPES.OPTIONAL_DEVICE: OptionalDeviceAltKeyData,
     FITTING_TYPES.EQUIPMENT: EquipmentAltKeyData,
     FITTING_TYPES.BOOSTER: BattleBoosterKeyData,
     FITTING_TYPES.SHELL: ShellKeyData}

    def _getTooltipData(self, *args, **kwargs):
        fittingItemDataClass = self.MECHANIC_DATA_FACTORY.get(self._item.fittingType, DefaultAltKeyData)
        result = fittingItemDataClass.getData(self._item)
        return result
