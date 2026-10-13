# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/gun_alt_key_data.py
import typing
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.shared.gui_items.vehicle_modules import VehicleGun

class GunAltKeyData(DefaultAltKeyData):
    AUTO_SHOOT_FLAME_GUN = 'vehicleAutoShootFlameGun'
    AUTO_SHOOT_GUN = 'vehicleAutoShootGun'
    CLIP_GUN = 'vehicleClipGun'

    @staticmethod
    def _getHeader(item, mechanicName):
        if mechanicName == GunAltKeyData.CLIP_GUN:
            return backport.text(R.strings.tooltips.advanced.vehicleClipGunHeader())
        return backport.text(R.strings.tooltips.advanced.gunCoolingHeader()) if mechanicName == FITTING_TYPES.VEHICLE_GUN_COOLING else super(GunAltKeyData, GunAltKeyData)._getHeader(item, mechanicName)

    @classmethod
    def _getMechanicKeys(cls, item):
        result = []
        if item.hasDualGunDualAccuracy():
            result.append(FITTING_TYPES.VEHICLE_DUAL_GUN_COOLING)
        if item.hasDualAccuracy():
            result.append(FITTING_TYPES.VEHICLE_GUN_COOLING)
        if item.isDualGun():
            result.append(FITTING_TYPES.VEHICLE_DUAL_GUN)
        if item.isAutoShootFlameGun():
            result.append(GunAltKeyData.AUTO_SHOOT_FLAME_GUN)
        if item.isAutoShootGun():
            result.append(GunAltKeyData.AUTO_SHOOT_GUN)
        if item.isClipGun():
            result.append(cls.CLIP_GUN)
        if item.isClipGunDualAccuracy():
            result.append(cls.CLIP_GUN)
            result.append(FITTING_TYPES.VEHICLE_GUN_COOLING)
        return tuple(result) if result else (item.getGUIEmblemID(),)
