# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/shared/gui_items/dossier/stats.py
import logging
import math
from collections import namedtuple
import typing
from gui.shared.gui_items.dossier.stats import AccountDossierStats, VehicleDossierStats, _BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.dossier.stats import _DossierStats
_logger = logging.getLogger(__name__)

def getComp7DossierStats(stats, archive=None, season=None):
    if isinstance(stats, AccountDossierStats):
        clazz = AccountComp7StatsBlock
    elif isinstance(stats, VehicleDossierStats):
        clazz = Comp7StatsBlock
    else:
        _logger.warning('invalid dossier stats parameter')
        return None
    if archive:
        return clazz(stats._getDossierItem(), 'Archive{}'.format(archive))
    elif season:
        return clazz(stats._getDossierItem(), 'Season{}'.format(season))
    else:
        _logger.warning('comp7 season or archive number must be specified!')
        return None


class Comp7StatsBlock(_BattleStatsBlock, _Battle2StatsBlock, _MaxStatsBlock):

    def __init__(self, dossier, statsKey):
        self._statsKey = statsKey
        _BattleStatsBlock.__init__(self, dossier)
        _Battle2StatsBlock.__init__(self, dossier)
        _MaxStatsBlock.__init__(self, dossier)

    def getBattlesCountVer2(self):
        return self.getBattlesCount()

    def getBattlesCountVer3(self):
        return self.getBattlesCount()

    def getPrestigePoints(self):
        return self._getStat('comp7PrestigePoints')

    def getPoiCaptured(self):
        return self._getStat('poiCapturable')

    def getHealthRepair(self):
        return self._getStat('healthRepair')

    def getRoleSkillUsed(self):
        return self._getStat('roleSkillUsed')

    def getSuperSquadBattlesCount(self):
        return self._getStat('superSquadBattlesCount')

    def getSuperSquadWins(self):
        return self._getStat('superSquadWins')

    def getMaxPrestigePoints(self):
        return self._getStatMax('maxComp7PrestigePoints')

    def getMaxWinSeries(self):
        return self._getStatMax('maxWinSeries')

    def getMaxSquadWinSeries(self):
        return self._getStatMax('maxSquadWinSeries')

    def getMaxEquipmentDamageDealt(self):
        return self._getStatMax('maxEquipmentDamageDealt')

    def getMaxHealthRepair(self):
        return self._getStatMax('maxHealthRepair')

    def getAvgPrestigePoints(self):
        avgValue = self._getAvgValue(self.getBattlesCount, self.getPrestigePoints)
        return math.ceil(avgValue) if avgValue is not None else None

    def getAvgPoiCaptured(self):
        avgValue = self._getAvgValue(self.getBattlesCount, self.getPoiCaptured)
        return round(avgValue) if avgValue is not None else None

    def getAvgRoleSkillUsed(self):
        avgValue = self._getAvgValue(self.getBattlesCount, self.getRoleSkillUsed)
        return round(avgValue) if avgValue is not None else None

    def getAvgHealthRepair(self):
        avgValue = self._getAvgValue(self.getBattlesCount, self.getHealthRepair)
        return math.ceil(avgValue) if avgValue is not None else None

    def _getStatsBlock(self, dossier):
        return self._getDossierBlock(dossier, 'comp7')

    def _getStats2Block(self, dossier):
        return self._getDossierBlock(dossier, 'comp7')

    def _getStatsMaxBlock(self, dossier):
        return self._getDossierBlock(dossier, 'maxComp7')

    def _getDossierBlock(self, dossier, blockPrefix):
        dossierDescr = dossier.getDossierDescr()
        blockName = '{}{}'.format(blockPrefix, self._statsKey)
        return dossierDescr[blockName] if dossierDescr.isBlockInLayout(blockName) else {}


_Comp7VehiclesDossiersCut = namedtuple('Comp7VehiclesDossiersCut', ('battlesCount', 'wins', 'xp', 'prestigePoints'))

class Comp7VehiclesDossiersCut(_Comp7VehiclesDossiersCut):

    def __mul__(self, other):
        self.battlesCount += other.battlesCount
        self.wins += other.wins
        self.xp += other.xp
        self.prestigePoints += other.prestigePoints

    def __imul__(self, other):
        return self + other


class AccountComp7StatsBlock(Comp7StatsBlock, _VehiclesStatsBlock, _MaxVehicleStatsBlock):

    def __init__(self, dossier, statsKey):
        Comp7StatsBlock.__init__(self, dossier, statsKey)
        _VehiclesStatsBlock.__init__(self, dossier)
        _MaxVehicleStatsBlock.__init__(self, dossier)

    def getMaxPrestigePointsVehicle(self):
        return self._getStatMax('maxComp7PrestigePointsVehicle')

    def getMaxEquipmentDamageDealtVehicle(self):
        return self._getStatMax('maxEquipmentDamageDealtVehicle')

    def getMaxHealthRepairVehicle(self):
        return self._getStatMax('maxHealthRepairVehicle')

    def _getVehDossiersCut(self, dossier):
        return self._getDossierBlock(dossier, 'comp7Cut')

    def _packVehicle(self, battlesCount=0, wins=0, xp=0, prestigePoints=0):
        return Comp7VehiclesDossiersCut(battlesCount, wins, xp, prestigePoints)
