# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/battle_results/reusable/shared.py
from gui.battle_results.reusable.shared import VehicleDetailedInfo, VehicleSummarizeInfo, no_key_error
from constants import DEATH_REASON_ALIVE

class Comp7VehicleDetailedInfo(VehicleDetailedInfo):
    __slots__ = ('_prestigePoints', '_roleSkillUsed', '_healthRepair', '_alliedHealthRepair', '_entityCaptured')

    def __init__(self, vehicleID, vehicle, player, deathReason=DEATH_REASON_ALIVE):
        super(Comp7VehicleDetailedInfo, self).__init__(vehicleID, vehicle, player, deathReason)
        self._prestigePoints = 0
        self._roleSkillUsed = 0
        self._healthRepair = 0
        self._alliedHealthRepair = 0
        self._entityCaptured = {}

    @property
    def prestigePoints(self):
        return self._prestigePoints

    @property
    def roleSkillUsed(self):
        return self._roleSkillUsed

    @property
    def healthRepair(self):
        return self._healthRepair

    @property
    def alliedHealthRepair(self):
        return self._alliedHealthRepair

    @property
    def entityCaptured(self):
        return self._entityCaptured

    @classmethod
    @no_key_error
    def makeForVehicle(cls, vehicleID, vehicle, player, vehicleRecords, critsRecords=None):
        info = super(Comp7VehicleDetailedInfo, cls).makeForVehicle(vehicleID, vehicle, player, vehicleRecords, critsRecords)
        info._prestigePoints = vehicleRecords.get('comp7PrestigePoints', 0)
        info._roleSkillUsed = vehicleRecords.get('roleSkillUsed', 0)
        info._healthRepair = vehicleRecords.get('healthRepair', 0)
        info._alliedHealthRepair = vehicleRecords.get('alliedHealthRepair', 0)
        info._entityCaptured = vehicleRecords.get('entityCaptured', {})
        return info


class Comp7VehicleSummarizeInfo(VehicleSummarizeInfo):

    @property
    def prestigePoints(self):
        return self._accumulate('prestigePoints')

    @property
    def roleSkillUsed(self):
        return self._accumulate('roleSkillUsed')

    @property
    def healthRepair(self):
        return self._accumulate('healthRepair')

    @property
    def alliedHealthRepair(self):
        return self._accumulate('alliedHealthRepair')

    @property
    def entityCaptured(self):
        return self._collectToDict('entityCaptured')
