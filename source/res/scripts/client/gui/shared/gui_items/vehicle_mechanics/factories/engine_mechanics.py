# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_mechanics/factories/engine_mechanics.py
from __future__ import absolute_import
from gui.shared.gui_items.vehicle_mechanics.factories.base_factory import BaseMechanicFactory
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import hasVehicleDescrMechanic

class EngineMechanicFactory(BaseMechanicFactory):

    @classmethod
    def _getMechanicsChecks(cls, guiItem, vehDescr):
        return [(guiItem.hasTurboshaftEngine(vehDescr), VehicleMechanic.TURBOSHAFT_ENGINE), (guiItem.hasRocketAcceleration(vehDescr), VehicleMechanic.ROCKET_ACCELERATION), (cls.__checkMechanic(vehDescr, VehicleMechanic.STAGED_JET_BOOSTERS), VehicleMechanic.STAGED_JET_BOOSTERS)]

    @staticmethod
    def __checkMechanic(vehDescr, mechanicConstant):
        return vehDescr is not None and hasVehicleDescrMechanic(vehDescr, mechanicConstant)
