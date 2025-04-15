# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_results/reusable/fall_tanks_shared.py
from constants import DEATH_REASON_ALIVE
from gui.battle_results.reusable.shared import VehicleSummarizeInfo, VehicleDetailedInfo

class FallTanksVehicleDetailedInfo(VehicleDetailedInfo):
    __slots__ = ('_finishTime', '_finishPosition', '_checkpointsPassed')

    def __init__(self, vehicleID, vehicle, player, deathReason=DEATH_REASON_ALIVE):
        super(FallTanksVehicleDetailedInfo, self).__init__(vehicleID, vehicle, player, deathReason)
        self._finishPosition = 0
        self._finishTime = 0
        self._checkpointsPassed = 0

    @property
    def finishTime(self):
        return self._finishTime

    @property
    def finishPosition(self):
        return self._finishPosition

    @property
    def checkpointsPassed(self):
        return self._checkpointsPassed

    @classmethod
    def _setSharedRecords(cls, info, records):
        super(FallTanksVehicleDetailedInfo, cls)._setSharedRecords(info, records)
        info._finishTime = records.get('fallTanksFinishTime', 0)
        info._finishPosition = records.get('fallTanksPosition', 0)
        info._checkpointsPassed = records.get('fallTanksCheckpointsPassed', 0)


class FallTanksVehicleSummarizeInfo(VehicleSummarizeInfo):

    @property
    def finishTime(self):
        return self._accumulate('finishTime')

    @property
    def finishPosition(self):
        return self._accumulate('finishPosition')

    @property
    def checkpointsPassed(self):
        return self._accumulate('checkpointsPassed')
