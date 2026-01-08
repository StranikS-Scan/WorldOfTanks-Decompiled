# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/gun_mechanics.py
from __future__ import absolute_import
from gui.shared.gui_items.vehicle_mechanics.factories.base_factory import BaseMechanicFactory
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class GunMechanicFactory(BaseMechanicFactory):

    @classmethod
    def _getMechanicsChecks(cls, guiItem, vehDescr):
        return [(guiItem.isAutoShoot(vehDescr), VehicleMechanic.AUTO_SHOOT_GUN),
         (guiItem.isDualGun(vehDescr), VehicleMechanic.DUAL_GUN),
         (guiItem.hasDualAccuracy(vehDescr), VehicleMechanic.DUAL_ACCURACY),
         (guiItem.isTwinGun(vehDescr), VehicleMechanic.TWIN_GUN),
         (guiItem.isClipGun(vehDescr), VehicleMechanic.MAGAZINE_GUN),
         (guiItem.isAutoReloadableWithBoost(vehDescr), VehicleMechanic.AUTO_LOADER_GUN_BOOST),
         (guiItem.isAutoReloadable(vehDescr) and not guiItem.isAutoReloadableWithBoost(vehDescr), VehicleMechanic.AUTO_LOADER_GUN),
         (guiItem.isDamageMutable(), VehicleMechanic.DAMAGE_MUTABLE),
         (any((shell.descriptor.hasStun for shell in guiItem.defaultAmmo)), VehicleMechanic.STUN)]

    @classmethod
    def _getMechanicsParams(cls, guiItem, vehDescr):
        return guiItem.getDescriptor(vehDescr).mechanicsParams
