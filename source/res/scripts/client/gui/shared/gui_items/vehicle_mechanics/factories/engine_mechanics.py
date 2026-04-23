# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/engine_mechanics.py
from __future__ import absolute_import
from gui.shared.gui_items.vehicle_mechanics.factories.base_factory import BaseMechanicFactory
from vehicles.mechanics.mechanic_constants import VehicleMechanic

class EngineMechanicFactory(BaseMechanicFactory):

    @classmethod
    def _getMechanicsChecks(cls, guiItem, vehDescr):
        return [(guiItem.hasTurboshaftEngine(vehDescr), VehicleMechanic.TURBOSHAFT_ENGINE),
         (guiItem.hasRocketAcceleration(vehDescr), VehicleMechanic.ROCKET_ACCELERATION),
         (guiItem.hasWheeledDash(vehDescr), VehicleMechanic.WHEELED_DASH),
         (guiItem.hasStagedJetBoosters(vehDescr), VehicleMechanic.STAGED_JET_BOOSTERS)]
