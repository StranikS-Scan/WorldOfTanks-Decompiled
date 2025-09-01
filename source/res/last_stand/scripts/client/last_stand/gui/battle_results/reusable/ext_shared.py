# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/battle_results/reusable/ext_shared.py
from gui.battle_results.reusable.shared import VehicleSummarizeInfo, VehicleDetailedInfo, no_key_error

class LSVehicleDetailedInfo(VehicleDetailedInfo):
    __slots__ = ('_phase', '_phasesCount', '_effectivenessKeys', '_totalKeys', '_teamFightPlace', '_respawnsCount', '_prevBestMissionsCount', '_completedDifficultyMissions')

    @classmethod
    @no_key_error
    def makeForVehicle(cls, vehicleID, vehicle, player, vehicleRecords, critsRecords=None):
        info = super(LSVehicleDetailedInfo, cls).makeForVehicle(vehicleID, vehicle, player, vehicleRecords, critsRecords=critsRecords)
        info._phase = vehicleRecords['ls_phase']
        info._phasesCount = vehicleRecords['ls_phasesCount']
        info._effectivenessKeys = info._totalKeys = vehicleRecords['ls_artefactKeys']
        info._teamFightPlace = vehicleRecords['ls_teamFightPlace']
        info._respawnsCount = vehicleRecords['ls_respawnCount']
        info._prevBestMissionsCount = vehicleRecords.get('ls_prevBestMissionsCount', 0)
        info._completedDifficultyMissions = vehicleRecords.get('ls_completedDifficultyMissions', [])
        return info

    @property
    def prevBestMissionsCount(self):
        return self._prevBestMissionsCount

    @property
    def phase(self):
        return self._phase

    @property
    def phasesCount(self):
        return self._phasesCount

    @property
    def effectivenessKeys(self):
        return self._effectivenessKeys

    @property
    def totalKeys(self):
        return self._totalKeys

    @property
    def teamContribution(self):
        return max(1, self._damageDealt)

    @property
    def teamFightPlace(self):
        return self._teamFightPlace

    @property
    def respawnsCount(self):
        return self._respawnsCount

    @property
    def completedDifficultyMissions(self):
        return self._completedDifficultyMissions


class LSVehicleSummarizeInfo(VehicleSummarizeInfo):

    @property
    def prevBestMissionsCount(self):
        return min(self._getAtrributeGenerator('prevBestMissionsCount'))

    @property
    def phase(self):
        return self._accumulate('phase')

    @property
    def phasesCount(self):
        return self._accumulate('phasesCount')

    @property
    def effectivenessKeys(self):
        return self._accumulate('effectivenessKeys')

    @property
    def totalKeys(self):
        return self._accumulate('totalKeys')

    @property
    def teamContribution(self):
        return self._accumulate('teamContribution')

    @property
    def teamFightPlace(self):
        return self._accumulate('teamFightPlace')

    @property
    def respawnsCount(self):
        return self._accumulate('respawnsCount')

    @property
    def completedDifficultyMissions(self):
        return next(self._getAtrributeGenerator('completedDifficultyMissions'), [])
