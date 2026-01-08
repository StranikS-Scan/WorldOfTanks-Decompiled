# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/simple_progress_achvs.py
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.requesters import REQ_CRITERIA
from dossiers2.ui.achievements import ACHIEVEMENT_BLOCK as _AB
from dossiers2.custom.cache import getCache as getDossiersCache
from dossiers2.custom.collector20 import getCollector20Config
from dossiers2.custom.helpers import getCollector20Requirements
from abstract import SimpleProgressAchievement
from abstract.mixins import Deprecated, HasVehiclesList

class BeasthunterAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(BeasthunterAchievement, self).__init__('beasthunter', _AB.TOTAL, dossier, value)

    def getNextLevelInfo(self):
        return ('vehiclesLeft', self._lvlUpValue)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TOTAL, 'fragsBeast')


class BruteForceAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(BruteForceAchievement, self).__init__('bruteForceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'bruteForce')


class CrucialShotAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(CrucialShotAchievement, self).__init__('crucialShotMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'crucialShot')


class InfiltratorAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(InfiltratorAchievement, self).__init__('infiltratorMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'infiltrator')


class GeniusForWarAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(GeniusForWarAchievement, self).__init__('geniusForWarMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'geniusForWar')


class GuerrillaAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(GuerrillaAchievement, self).__init__('guerrillaMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'guerrilla')


class HeavyFireAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(HeavyFireAchievement, self).__init__('heavyFireMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'heavyFire')


class FightingReconnaissanceAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(FightingReconnaissanceAchievement, self).__init__('fightingReconnaissanceMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'fightingReconnaissance')


class FireAndSteelAchievement(SimpleProgressAchievement):
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


class RangerAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(RangerAchievement, self).__init__('rangerMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'ranger')


class PrematureDetonationAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PrematureDetonationAchievement, self).__init__('prematureDetonationMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'prematureDetonation')


class PromisingFighterAchievement(SimpleProgressAchievement):
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


class PyromaniacAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(PyromaniacAchievement, self).__init__('pyromaniacMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'pyromaniac')


class SentinelAchievement(SimpleProgressAchievement):
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


class WolfAmongSheepAchievement(SimpleProgressAchievement):
    __slots__ = ()

    def __init__(self, dossier, value=None):
        super(WolfAmongSheepAchievement, self).__init__('wolfAmongSheepMedal', _AB.TEAM_7X7, dossier, value)

    def _readProgressValue(self, dossier):
        return dossier.getRecordValue(_AB.TEAM_7X7, 'wolfAmongSheep')


class Collector20Achievement(HasVehiclesList, SimpleProgressAchievement):
    __itemsCache = dependency.descriptor(IItemsCache)
    _LIST_NAME = 'vehiclesToHaveInGarage'

    def __init__(self, name, block, dossier, value=None):
        if not self.checkIsInDossier(block, name, dossier):
            inventoryVehsCDs = set(self.__itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.SECRET | ~REQ_CRITERIA.HIDDEN))
            self._vehTypeCompDescrs = getCollector20Requirements(inventoryVehsCDs)
        else:
            self._vehTypeCompDescrs = set()
        SimpleProgressAchievement.__init__(self, name, block, dossier, value)
        HasVehiclesList.__init__(self)

    def _getVehiclesDescrsList(self):
        return self._vehTypeCompDescrs

    def _readLevelUpTotalValue(self, dossier):
        return len(getCollector20Config())

    def _readLevelUpValue(self, dossier):
        return len(self._vehTypeCompDescrs)

    @classmethod
    def _sortFunc(cls, i1, i2):
        return i1.level - i2.level or i1.innationID - i2.innationID or i1.nation - i2.nation
