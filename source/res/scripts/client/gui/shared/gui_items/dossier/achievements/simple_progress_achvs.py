# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/simple_progress_achvs.py
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from dossiers2.custom.cache import getCache as getDossiersCache
from abstract import SimpleProgressAchievement
from abstract.mixins import Deprecated, HasVehiclesList
from collections import namedtuple
from supply_shared import Supply
from items import vehicles

class BeasthunterAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(BeasthunterAchievement, self).__init__('beasthunter', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsBeast')


class BruteForceAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(BruteForceAchievement, self).__init__('bruteForceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'bruteForce')


class CrucialShotAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(CrucialShotAchievement, self).__init__('crucialShotMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'crucialShot')


class InfiltratorAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(InfiltratorAchievement, self).__init__('infiltratorMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'infiltrator')


class GeniusForWarAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(GeniusForWarAchievement, self).__init__('geniusForWarMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'geniusForWar')


class GuerrillaAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(GuerrillaAchievement, self).__init__('guerrillaMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'guerrilla')


class HeavyFireAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(HeavyFireAchievement, self).__init__('heavyFireMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'heavyFire')


class FightingReconnaissanceAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(FightingReconnaissanceAchievement, self).__init__('fightingReconnaissanceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'fightingReconnaissance')


class FireAndSteelAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(FireAndSteelAchievement, self).__init__('fireAndSteelMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'fireAndSteel')


class MousebaneAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(MousebaneAchievement, self).__init__('mousebane', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getBlock('vehTypeFrags').get(getDossiersCache()['mausTypeCompDescr'], 0)


class ReliableComradeAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(ReliableComradeAchievement, self).__init__('reliableComrade', _AB.TOTAL, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'reliableComradeSeries')


class RangerAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(RangerAchievement, self).__init__('rangerMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'ranger')


class PrematureDetonationAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PrematureDetonationAchievement, self).__init__('prematureDetonationMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'prematureDetonation')


class PromisingFighterAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PromisingFighterAchievement, self).__init__('promisingFighterMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'promisingFighter')


class PattonValleyAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PattonValleyAchievement, self).__init__('pattonValley', _AB.TOTAL, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsPatton')


class PyromaniacAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PyromaniacAchievement, self).__init__('pyromaniacMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'pyromaniac')


class SentinelAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(SentinelAchievement, self).__init__('sentinelMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'sentinel')


class SinaiAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(SinaiAchievement, self).__init__('sinai', _AB.TOTAL, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsSinai')


class TankwomenAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(TankwomenAchievement, self).__init__('tankwomen', _AB.SINGLE, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'tankwomenProgress')


class WolfAmongSheepAchievement(Deprecated, SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(WolfAmongSheepAchievement, self).__init__('wolfAmongSheepMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'wolfAmongSheep')


class SaboteurAchievement(HasVehiclesList, SimpleProgressAchievement):
    __slots__ = ()
    VehicleData = namedtuple('VehicleData', 'name icon')
    _LIST_NAME = 'vehiclesToKill'

    def __init__(self, dossier, value=None):
        self.__vehTypeCompDescrs = self._getSuppliesList(dossier)
        SimpleProgressAchievement.__init__(self, 'saboteur', _AB.EPIC_BATTLE, dossier, value)
        HasVehiclesList.__init__(self)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.EPIC_BATTLE, 'saboteurProgress')

    def _getVehiclesDescrsList(self):
        return self.__vehTypeCompDescrs

    def _getSuppliesList(self, dossier):
        suppliesList = []
        displayOrderSupplies = [Supply.PILLBOX,
         Supply.FLAMER,
         Supply.MORTAR,
         Supply.AIRSHIP]
        allSupplies = getDossiersCache()['vehiclesByTag'].get('supply', set())
        killedSupplies = set()
        if dossier:
            killedSupplies = set(dossier.getBlock('vehTypeFrags').iterkeys())
        leftKilledSupplies = allSupplies - killedSupplies
        for supplyID in displayOrderSupplies:
            for supply in leftKilledSupplies:
                if Supply.SUPPLY_ID_TO_TAG[supplyID] in vehicles.getItemByCompactDescr(supply).tags:
                    suppliesList.append(supply)
                    break

        return suppliesList

    def getVehiclesData(self):
        result = []
        for vCD in self._getVehiclesDescrsList():
            vehicle = self.itemsCache.items.getItemByCD(vCD)
            result.append(self.VehicleData(vehicle.userName, vehicle.iconSmall))

        return [ i._asdict() for i in result ]
