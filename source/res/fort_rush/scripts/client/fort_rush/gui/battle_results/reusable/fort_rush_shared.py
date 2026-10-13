# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/battle_results/reusable/fort_rush_shared.py
from __future__ import absolute_import
from gui.battle_results.reusable.shared import VehicleSummarizeInfo, VehicleDetailedInfo, no_key_error

class FortRushVehicleDetailedInfo(VehicleDetailedInfo):
    __slots__ = ('_fortRushScore',)

    @classmethod
    @no_key_error
    def makeForVehicle(cls, vehicleID, vehicle, player, vehicleRecords, critsRecords=None):
        info = super(FortRushVehicleDetailedInfo, cls).makeForVehicle(vehicleID, vehicle, player, vehicleRecords, critsRecords=critsRecords)
        info._fortRushScore = vehicleRecords['fortRush/scorePoints']
        return info

    @property
    def fortRushScore(self):
        return self._fortRushScore


class FortRushVehicleSummarizeInfo(VehicleSummarizeInfo):

    @property
    def fortRushScore(self):
        return self._accumulate('fortRushScore')
