# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/chassis_mechanics.py
from __future__ import absolute_import
from gui.shared.gui_items.vehicle_mechanics.factories.base_factory import BaseMechanicFactory
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class ChassisMechanicFactory(BaseMechanicFactory):

    @classmethod
    def _getMechanicsChecks(cls, guiItem, _):
        return [(guiItem.isHydraulicWheeledChassis(), VehicleMechanic.HYDRAULIC_WHEELED_CHASSIS), (guiItem.isHydraulicChassis(), VehicleMechanic.HYDRAULIC_CHASSIS), (guiItem.isTrackWithinTrack(), VehicleMechanic.TRACK_WITHIN_TRACK)]
