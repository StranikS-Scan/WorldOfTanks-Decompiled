# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/shared.py
import functools
import operator
import typing
from account_shared import getFairPlayViolationName
from constants import DEATH_REASON_ALIVE
from debug_utils import LOG_CURRENT_EXCEPTION
from dossiers2.custom.records import DB_ID_TO_RECORD
from dossiers2.ui import achievements, layouts
from gui.battle_results.reusable import sort_keys
from gui.shared.crits_mask_parser import CRIT_MASK_SUB_TYPES, critsParserGenerator
from gui.shared.gui_items import Vehicle
from gui.shared.gui_items.dossier import getAchievementFactory
from items import vehicles as vehicles_core
from shared_utils import findFirst
import ArenaType
from gui.battle_results.settings import BATTLE_RESULTS_RECORD as _RECORD

def makeAchievementFromPersonal(results):
    popUps = results.get('dossierPopUps', [])
    for achievementID, value in popUps:
        record = DB_ID_TO_RECORD[achievementID]
        if record in layouts.IGNORED_BY_BATTLE_RESULTS or not layouts.isAchievementRegistered(record):
            continue
        factory = getAchievementFactory(record)
        if factory is not None:
            achievement = factory.create(value=value)
            if record == achievements.MARK_ON_GUN_RECORD:
                if 'typeCompDescr' in results:
                    try:
                        nationID = vehicles_core.parseIntCompactDescr(results['typeCompDescr'])[1]
                        achievement.setVehicleNationID(nationID)
                    except Exception:
                        LOG_CURRENT_EXCEPTION()

                if 'damageRating' in results:
                    achievement.setDamageRating(results['damageRating'])
            if achievement.getName() in achievements.BATTLE_ACHIEVES_RIGHT:
                yield (1, achievement)
            else:
                yield (-1, achievement)

    return


def makeMarkOfMasteryFromPersonal(results):
    markOfMastery = results.get('markOfMastery', 0)
    achievement = None
    if not markOfMastery:
        return
    else:
        factory = getAchievementFactory(('achievements', 'markOfMastery'))
        if factory is not None:
            achievement = factory.create(value=markOfMastery)
            achievement.setPrevMarkOfMastery(results.get('prevMarkOfMastery', 0))
            achievement.setCompDescr(results.get('typeCompDescr'))
        return achievement


def makeCritsInfo(value):
    rv = {CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES: [],
     CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES: [],
     CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS: []}
    critsCount = 0
    for subType, critType in critsParserGenerator(value):
        critsCount += 1
        rv[subType].append(critType)

    rv['critsCount'] = critsCount
    return rv


def unionCritsInfo(destination, source):
    rv = {CRIT_MASK_SUB_TYPES.DESTROYED_DEVICES: [],
     CRIT_MASK_SUB_TYPES.CRITICAL_DEVICES: [],
     CRIT_MASK_SUB_TYPES.DESTROYED_TANKMENS: []}
    for subType in rv.iterkeys():
        if subType not in source:
            continue
        values = source[subType]
        if subType in destination:
            toUpdate = destination[subType]
        else:
            toUpdate = destination[subType] = []
        for value in values:
            if value not in toUpdate:
                toUpdate.append(value)

    if 'critsCount' in source:
        if 'critsCount' in destination:
            destination['critsCount'] += source['critsCount']
        else:
            destination['critsCount'] = source['critsCount']


class ItemInfo(object):
    __slots__ = ('__wasInBattle',)

    def __init__(self, wasInBattle=True):
        super(ItemInfo, self).__init__()
        self.__wasInBattle = wasInBattle

    @property
    def wasInBattle(self):
        return self.__wasInBattle


class UnpackedInfo(object):
    __slots__ = ('__unpackedItemsIDs',)

    def __init__(self):
        super(UnpackedInfo, self).__init__()
        self.__unpackedItemsIDs = []

    def getNumberOfUnpackedItems(self):
        return len(self.__unpackedItemsIDs)

    def hasUnpackedItems(self):
        return self.getNumberOfUnpackedItems() > 0

    def _addUnpackedItemID(self, itemUniqueID):
        self.__unpackedItemsIDs.append(itemUniqueID)


def no_key_error(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KeyError:
            LOG_CURRENT_EXCEPTION()

    return wrapper


class _BaseInfo(object):

    @property
    def capturePoints(self):
        raise NotImplementedError

    @property
    def droppedCapturePoints(self):
        raise NotImplementedError


class TeamBasesInfo(_BaseInfo):
    __slots__ = ('__capturePoints', '__droppedCapturePoints')

    def __init__(self, capturePoints=0, droppedCapturePoints=0):
        super(TeamBasesInfo, self).__init__()
        self.__capturePoints = capturePoints
        self.__droppedCapturePoints = droppedCapturePoints

    @property
    def capturePoints(self):
        return self.__capturePoints

    @property
    def droppedCapturePoints(self):
        return self.__droppedCapturePoints


class SummarizeTeamBasesInfo(object):
    __slots__ = ('__bases', '__arenaType')

    def __init__(self, result):
        super(SummarizeTeamBasesInfo, self).__init__()
        self.__bases = []
        arenaTypeID = result[_RECORD.COMMON]['arenaTypeID']
        self.__arenaType = ArenaType.g_cache[arenaTypeID]

    @property
    def capturePoints(self):
        sm = sum((base.capturePoints for base in self.__bases))
        maxPoints = self.__arenaType.capturePointsLimit
        return min(maxPoints, sm)

    @property
    def droppedCapturePoints(self):
        return sum((base.droppedCapturePoints for base in self.__bases))

    def addBasesInfo(self, info):
        self.__bases.append(info)


class _VehicleInfo(object):
    __slots__ = ('_vehicleID', '_player', '_deathReason')

    def __init__(self, vehicleID, player, deathReason=DEATH_REASON_ALIVE):
        self._vehicleID = vehicleID
        self._player = player
        self._deathReason = deathReason

    @property
    def vehicleID(self):
        return self._vehicleID

    @property
    def player(self):
        return self._player

    @property
    def deathReason(self):
        return self._deathReason

    @property
    def vehicle(self):
        raise NotImplementedError

    @property
    def killerID(self):
        raise NotImplementedError

    @property
    def isTeamKiller(self):
        raise NotImplementedError

    @property
    def isKilledByTeamKiller(self):
        raise NotImplementedError

    @property
    def achievementsIDs(self):
        raise NotImplementedError

    @property
    def spotted(self):
        raise NotImplementedError

    @property
    def piercings(self):
        raise NotImplementedError

    @property
    def piercingEnemyHits(self):
        raise NotImplementedError

    @property
    def piercingsReceived(self):
        raise NotImplementedError

    @property
    def damageDealt(self):
        raise NotImplementedError

    @property
    def tdamageDealt(self):
        raise NotImplementedError

    @property
    def sniperDamageDealt(self):
        raise NotImplementedError

    @property
    def supplyDamageDealt(self):
        raise NotImplementedError

    @property
    def supplyDamageReceived(self):
        raise NotImplementedError

    @property
    def spottedSupplies(self):
        raise NotImplementedError

    @property
    def damagedSupplies(self):
        raise NotImplementedError

    @property
    def damagedTanks(self):
        raise NotImplementedError

    @property
    def killedSupplies(self):
        raise NotImplementedError

    @property
    def damageReceivedFromSupply(self):
        raise NotImplementedError

    @property
    def kills(self):
        raise NotImplementedError

    @property
    def tkills(self):
        raise NotImplementedError

    @property
    def targetKills(self):
        raise NotImplementedError

    @property
    def noDamageDirectHitsReceived(self):
        raise NotImplementedError

    @property
    def damageBlockedByArmor(self):
        raise NotImplementedError

    @property
    def rickochetsReceived(self):
        raise NotImplementedError

    @property
    def damageAssistedTrack(self):
        raise NotImplementedError

    @property
    def damageAssistedRadio(self):
        raise NotImplementedError

    @property
    def damageAssisted(self):
        raise NotImplementedError

    @property
    def damageAssistedStun(self):
        raise NotImplementedError

    @property
    def stunNum(self):
        raise NotImplementedError

    @property
    def stunDuration(self):
        raise NotImplementedError

    @property
    def critsInfo(self):
        raise NotImplementedError

    @property
    def critsCount(self):
        raise NotImplementedError

    @property
    def shots(self):
        raise NotImplementedError

    @property
    def explosionHits(self):
        raise NotImplementedError

    @property
    def directHits(self):
        raise NotImplementedError

    @property
    def directEnemyHits(self):
        raise NotImplementedError

    @property
    def directHitsReceived(self):
        raise NotImplementedError

    @property
    def explosionHitsReceived(self):
        raise NotImplementedError

    @property
    def damaged(self):
        raise NotImplementedError

    @property
    def mileage(self):
        raise NotImplementedError

    @property
    def capturePoints(self):
        raise NotImplementedError

    @property
    def droppedCapturePoints(self):
        raise NotImplementedError

    @property
    def xp(self):
        raise NotImplementedError

    @property
    def xpForAttack(self):
        raise NotImplementedError

    @property
    def xpForAssist(self):
        raise NotImplementedError

    @property
    def xpOther(self):
        raise NotImplementedError

    @property
    def xpPenalty(self):
        raise NotImplementedError

    @property
    def deathCount(self):
        raise NotImplementedError

    @property
    def rollouts(self):
        raise NotImplementedError

    @property
    def respawns(self):
        raise NotImplementedError

    @property
    def numDefended(self):
        raise NotImplementedError

    @property
    def numRecovered(self):
        raise NotImplementedError

    @property
    def numCaptured(self):
        raise NotImplementedError

    @property
    def numDestroyed(self):
        raise NotImplementedError

    @property
    def destructiblesDamageDealt(self):
        raise NotImplementedError

    @property
    def equipmentDamageDealt(self):
        raise NotImplementedError

    @property
    def equipmentDamageAssisted(self):
        raise NotImplementedError

    @property
    def rtsEventPoints(self):
        raise NotImplementedError

    def getOrderByClass(self):
        return Vehicle.getOrderByVehicleClass(Vehicle.getVehicleClassTag(self.vehicle.descriptor.type.tags))


class VehicleDetailedInfo(_VehicleInfo):
    __slots__ = ('_vehicle', '_killerID', '_achievementsIDs', '_critsInfo', '_spotted', '_piercings', '_piercingEnemyHits', '_piercingsReceived', '_damageDealt', '_tdamageDealt', '_sniperDamageDealt', '_supplyDamageDealt', '_damageReceivedFromSupply', '_supplyDamageReceived', '_damageBlockedByArmor', '_damageAssistedTrack', '_damageAssistedRadio', '_damageAssistedStun', '_stunNum', '_stunDuration', '_rickochetsReceived', '_noDamageDirectHitsReceived', '_targetKills', '_directHits', '_directEnemyHits', '_directHitsReceived', '_explosionHits', '_explosionHitsReceived', '_shots', '_kills', '_tkills', '_damaged', '_mileage', '_capturePoints', '_droppedCapturePoints', '_xp', '_fire', '_isTeamKiller', '_isKilledByTeamKiller', '_rollouts', '_respawns', '_deathCount', '_equipmentDamageDealt', '_equipmentDamageAssisted', '_xpForAttack', '_xpForAssist', '_xpOther', '_xpPenalty', '_numDefended', '_vehicleNumCaptured', '_numRecovered', '_destructiblesNumDestroyed', '_destructiblesDamageDealt', '_achievedLevel', '_spottedSupplies', '_damagedSupplies', '_damagedTanks', '_killedSupplies', '_rtsEventPoints')

    def __init__(self, vehicleID, vehicle, player, deathReason=DEATH_REASON_ALIVE):
        super(VehicleDetailedInfo, self).__init__(vehicleID, player, deathReason)
        self._vehicle = vehicle
        self._killerID = 0
        self._achievementsIDs = set()
        self._critsInfo = makeCritsInfo(0)
        self._spotted = 0
        self._piercings = 0
        self._piercingEnemyHits = 0
        self._piercingsReceived = 0
        self._damageBlockedByArmor = 0
        self._rickochetsReceived = 0
        self._noDamageDirectHitsReceived = 0
        self._targetKills = 0
        self._damageDealt = 0
        self._tdamageDealt = 0
        self._sniperDamageDealt = 0
        self._supplyDamageDealt = 0
        self._damageReceivedFromSupply = 0
        self._supplyDamageReceived = 0
        self._equipmentDamageDealt = 0
        self._damageAssistedTrack = 0
        self._damageAssistedRadio = 0
        self._damageAssistedStun = 0
        self._equipmentDamageAssisted = 0
        self._stunNum = 0
        self._stunDuration = 0
        self._directHits = 0
        self._directEnemyHits = 0
        self._directHitsReceived = 0
        self._explosionHits = 0
        self._explosionHitsReceived = 0
        self._shots = 0
        self._kills = 0
        self._tkills = 0
        self._damaged = 0
        self._mileage = 0
        self._capturePoints = 0
        self._droppedCapturePoints = 0
        self._xp = 0
        self._fire = 0
        self._isTeamKiller = False
        self._rollouts = 0
        self._respawns = 0
        self._deathCount = 0
        self._xpForAssist = 0
        self._xpForAttack = 0
        self._xpOther = 0
        self._xpPenalty = 0
        self._isKilledByTeamKiller = False
        self._numRecovered = 0
        self._vehicleNumCaptured = 0
        self._destructiblesNumDestroyed = 0
        self._destructiblesDamageDealt = 0
        self._numDefended = 0
        self._achievedLevel = 0
        self._spottedSupplies = 0
        self._damagedSupplies = set()
        self._damagedTanks = set()
        self._killedSupplies = 0
        self._rtsEventPoints = 0

    @property
    def vehicle(self):
        return self._vehicle

    @property
    def killerID(self):
        return self._killerID

    @property
    def achievementsIDs(self):
        return self._achievementsIDs

    @property
    def spotted(self):
        return self._spotted

    @property
    def piercings(self):
        return self._piercings

    @property
    def piercingEnemyHits(self):
        return self._piercingEnemyHits

    @property
    def piercingEnemyHitsByTanks(self):
        return self._piercingEnemyHits if not self._vehicle.isSupply else 0

    @property
    def piercingEnemyHitsBySupplies(self):
        return self._piercingEnemyHits if self._vehicle.isSupply else 0

    @property
    def piercingsReceived(self):
        return self._piercingsReceived

    @property
    def damageDealt(self):
        return self._damageDealt + self.destructiblesDamageDealt

    @property
    def damageDealtByTanks(self):
        return self.damageDealt if not self._vehicle.isSupply else 0

    @property
    def damageDealtBySupplies(self):
        return self.damageDealt if self._vehicle.isSupply else 0

    @property
    def tdamageDealt(self):
        return self._tdamageDealt

    @property
    def sniperDamageDealt(self):
        return self._sniperDamageDealt

    @property
    def sniperDamageDealtByTanks(self):
        return self._sniperDamageDealt if not self._vehicle.isSupply else 0

    @property
    def sniperDamageDealtBySupplies(self):
        return self._sniperDamageDealt if self._vehicle.isSupply else 0

    @property
    def supplyDamageDealt(self):
        return self._damageDealt if self._vehicle.isSupply else self._supplyDamageDealt

    @property
    def supplyDamageReceived(self):
        return self._supplyDamageReceived

    @property
    def damageReceivedFromSupply(self):
        return self._damageReceivedFromSupply

    @property
    def equipmentDamageDealt(self):
        return self._equipmentDamageDealt

    @property
    def targetKills(self):
        return self._targetKills

    @property
    def noDamageDirectHitsReceived(self):
        return self._noDamageDirectHitsReceived

    @property
    def damageBlockedByArmor(self):
        return self._damageBlockedByArmor

    @property
    def damageBlockedByTanks(self):
        return self._damageBlockedByArmor if not self._vehicle.isSupply else 0

    @property
    def damageBlockedBySupplies(self):
        return self._damageBlockedByArmor if self._vehicle.isSupply else 0

    @property
    def rickochetsReceived(self):
        return self._rickochetsReceived

    @property
    def damageAssistedTrack(self):
        return self._damageAssistedTrack

    @property
    def damageAssistedRadio(self):
        return self._damageAssistedRadio

    @property
    def damageAssisted(self):
        return self._damageAssistedTrack + self._damageAssistedRadio

    @property
    def damageAssistedStun(self):
        return self._damageAssistedStun

    @property
    def equipmentDamageAssisted(self):
        return self._equipmentDamageAssisted

    @property
    def stunNum(self):
        return self._stunNum

    @property
    def stunDuration(self):
        return self._stunDuration

    @property
    def critsInfo(self):
        return self._critsInfo

    @property
    def critsCount(self):
        return self.critsInfo['critsCount']

    @property
    def shots(self):
        return self._shots

    @property
    def shotsByTanks(self):
        return self._shots if not self._vehicle.isSupply else 0

    @property
    def shotsBySupplies(self):
        return self._shots if self._vehicle.isSupply else 0

    @property
    def explosionHits(self):
        return self._explosionHits

    @property
    def explosionHitsByTanks(self):
        return self._explosionHits if not self._vehicle.isSupply else 0

    @property
    def explosionHitsBySupplies(self):
        return self._explosionHits if self._vehicle.isSupply else 0

    @property
    def directHits(self):
        return self._directHits

    @property
    def directEnemyHits(self):
        return self._directEnemyHits

    @property
    def directEnemyHitsByTanks(self):
        return self._directEnemyHits if not self._vehicle.isSupply else 0

    @property
    def directEnemyHitsBySupplies(self):
        return self._directEnemyHits if self._vehicle.isSupply else 0

    @property
    def directHitsReceived(self):
        return self._directHitsReceived

    @property
    def explosionHitsReceived(self):
        return self._explosionHitsReceived

    @property
    def kills(self):
        return self._kills

    @property
    def tkills(self):
        return self._tkills

    @property
    def damaged(self):
        return self._damaged

    @property
    def mileage(self):
        return self._mileage

    @property
    def capturePoints(self):
        return self._capturePoints

    @property
    def droppedCapturePoints(self):
        return self._droppedCapturePoints

    @property
    def xp(self):
        return self._xp

    @property
    def isTeamKiller(self):
        return self._isTeamKiller

    @property
    def isKilledByTeamKiller(self):
        return self._isKilledByTeamKiller

    @property
    def deathCount(self):
        return self._deathCount

    @property
    def rollouts(self):
        return self._rollouts

    @property
    def respawns(self):
        return self._respawns

    @property
    def achievedLevel(self):
        return self._achievedLevel

    @property
    def numDefended(self):
        return self._numDefended

    @property
    def numRecovered(self):
        return self._numRecovered

    @property
    def numCaptured(self):
        return self._vehicleNumCaptured

    @property
    def numDestroyed(self):
        return self._destructiblesNumDestroyed

    @property
    def destructiblesDamageDealt(self):
        return self._destructiblesDamageDealt

    @property
    def xpForAssist(self):
        return self._xpForAssist

    @property
    def xpForAttack(self):
        return self._xpForAttack

    @property
    def xpOther(self):
        return self._xpOther

    @property
    def xpPenalty(self):
        return self._xpPenalty

    @property
    def spottedSupplies(self):
        return self._spottedSupplies

    @property
    def damagedSupplies(self):
        return self._damagedSupplies

    @property
    def damagedTanks(self):
        return self._damagedTanks

    @property
    def killedSupplies(self):
        return self._killedSupplies

    @property
    def rtsEventPoints(self):
        return self._rtsEventPoints

    def haveInteractionDetails(self):
        return self._spotted != 0 or self._deathReason > DEATH_REASON_ALIVE or self._directHits != 0 or self._directEnemyHits != 0 or self._explosionHits != 0 or self._piercings != 0 or self._piercingEnemyHits != 0 or self._damageDealt != 0 or self.damageAssisted != 0 or self.damageAssistedStun != 0 or self.stunNum != 0 or self.critsCount != 0 or self._fire != 0 or self._targetKills != 0 or self.stunDuration != 0 or self._damageBlockedByArmor != 0 or self._spottedSupplies != 0 or len(self._damagedSupplies) != 0 or len(self._damagedTanks) != 0 or self._killedSupplies != 0

    @classmethod
    @no_key_error
    def makeForEnemy(cls, vehicleID, vehicle, player, detailsRecords, deathReason=DEATH_REASON_ALIVE, isTeamKiller=False):
        info = cls(vehicleID, vehicle, player, deathReason=deathReason)
        info._critsInfo = makeCritsInfo(detailsRecords['crits'])
        info._rickochetsReceived = detailsRecords['rickochetsReceived']
        info._targetKills = detailsRecords['targetKills']
        info._fire = detailsRecords['fire']
        info._isTeamKiller = isTeamKiller
        info._isKilledByTeamKiller = False
        cls._setSharedRecords(info, detailsRecords)
        return info

    @classmethod
    @no_key_error
    def makeForVehicle(cls, vehicleID, vehicle, player, vehicleRecords, critsRecords=None):
        info = cls(vehicleID, vehicle, player)
        if critsRecords is not None:
            critsInfo = makeCritsInfo(0)
            for crits in critsRecords:
                unionCritsInfo(critsInfo, makeCritsInfo(crits))

            info._critsInfo = critsInfo
        info._killerID = vehicleRecords['killerID']
        info._achievementsIDs = set(vehicleRecords['achievements'])
        info._piercingsReceived = vehicleRecords['piercingsReceived']
        info._tdamageDealt = vehicleRecords['tdamageDealt']
        info._sniperDamageDealt = vehicleRecords['sniperDamageDealt']
        info._equipmentDamageDealt = vehicleRecords['equipmentDamageDealt']
        info._shots = vehicleRecords['shots']
        info._directHitsReceived = vehicleRecords['directHitsReceived']
        info._explosionHitsReceived = vehicleRecords['explosionHitsReceived']
        info._kills = vehicleRecords['kills']
        info._tkills = vehicleRecords['tkills']
        info._damaged = vehicleRecords['damaged']
        info._mileage = vehicleRecords['mileage']
        info._capturePoints = vehicleRecords['capturePoints']
        info._droppedCapturePoints = vehicleRecords['droppedCapturePoints']
        if 'originalXP' in vehicleRecords:
            info._xp = vehicleRecords['originalXP']
        else:
            info._xp = vehicleRecords['xp'] - vehicleRecords['achievementXP']
        info._xpOther = vehicleRecords['xp/other']
        info._xpForAssist = vehicleRecords['xp/assist']
        info._xpForAttack = vehicleRecords['xp/attack']
        info._xpPenalty = vehicleRecords['xpPenalty']
        info._isTeamKiller = vehicleRecords['isTeamKiller']
        info._isKilledByTeamKiller = vehicleRecords.get('isKilledByTeamKiller', False)
        info._rollouts = vehicleRecords['rolloutsCount']
        info._respawns = vehicleRecords['rolloutsCount'] - 1 if vehicleRecords['rolloutsCount'] > 0 else 0
        info._deathCount = vehicleRecords['deathCount']
        info._numRecovered = vehicleRecords['numRecovered']
        info._vehicleNumCaptured = vehicleRecords['vehicleNumCaptured']
        info._destructiblesNumDestroyed = vehicleRecords['destructiblesNumDestroyed']
        info._destructiblesDamageDealt = vehicleRecords['destructiblesDamageDealt']
        info._numDefended = vehicleRecords['numDefended']
        info._equipmentDamageAssisted = vehicleRecords.get('damageAssistedInspire', 0) + vehicleRecords.get('damageAssistedSmoke', 0)
        info._supplyDamageDealt = vehicleRecords.get('supplyDamageDealt', 0)
        info._damageReceivedFromSupply = vehicleRecords.get('damageReceivedFromSupply', 0)
        info._supplyDamageReceived = vehicleRecords['damageReceived'] if vehicle and vehicle.isSupply else 0
        info._achievedLevel = vehicleRecords.get('achivedLevel', 0)
        info._spottedSupplies = vehicleRecords.get('spottedSupplies', 0)
        info._damagedSupplies = set(vehicleRecords.get('damagedSupplies', set()))
        info._killedSupplies = vehicleRecords.get('killedSupplies', 0)
        info._damagedTanks = set(vehicleRecords.get('damagedTanks', set()))
        info._rtsEventPoints = vehicleRecords.get('rtsEventPoints', 0)
        cls._setSharedRecords(info, vehicleRecords)
        return info

    @classmethod
    def _setSharedRecords(cls, info, records):
        info._deathReason = max(info._deathReason, records['deathReason'])
        info._spotted = records['spotted']
        info._piercings = records['piercings']
        info._piercingEnemyHits = records['piercingEnemyHits']
        info._damageDealt = records['damageDealt']
        info._damageBlockedByArmor = records['damageBlockedByArmor']
        info._noDamageDirectHitsReceived = records['noDamageDirectHitsReceived']
        info._damageAssistedTrack = records['damageAssistedTrack']
        info._damageAssistedRadio = records['damageAssistedRadio']
        info._directHits = records['directHits']
        info._directEnemyHits = records['directEnemyHits']
        info._explosionHits = records['explosionHits']
        info._damageAssistedStun = records['damageAssistedStun']
        info._stunNum = records['stunNum']
        info._stunDuration = records['stunDuration']


class VehicleSummarizeInfo(_VehicleInfo):
    __slots__ = ('__avatar', '_vehicles')

    def __init__(self, vehicleID, player):
        super(VehicleSummarizeInfo, self).__init__(vehicleID, player)
        self.__avatar = None
        self._vehicles = []
        return

    @property
    def avatar(self):
        return self.__avatar

    @property
    def vehicle(self):
        return self._vehicles[0].vehicle if self._vehicles else None

    @property
    def vehicles(self):
        return self._vehicles if self._vehicles else []

    @property
    def isTeamKiller(self):
        return any(self._getAtrributeGenerator('isTeamKiller'))

    @property
    def isKilledByTeamKiller(self):
        return any(self._getAtrributeGenerator('isKilledByTeamKiller'))

    @property
    def killerID(self):
        return self._findFirstNoZero('killerID')

    @property
    def deathReason(self):
        return self._findMaxInt('deathReason', start=DEATH_REASON_ALIVE)

    @property
    def achievementsIDs(self):
        return self._collectToSet('achievementsIDs')

    @property
    def spotted(self):
        return self._accumulate('spotted')

    @property
    def piercings(self):
        return self._accumulate('piercings')

    @property
    def piercingEnemyHits(self):
        return self._accumulate('piercingEnemyHits')

    @property
    def piercingEnemyHitsByTanks(self):
        return self._accumulateTanks('piercingEnemyHits')

    @property
    def piercingEnemyHitsBySupplies(self):
        return self._accumulateSupplies('piercingEnemyHits')

    @property
    def piercingsReceived(self):
        return self._accumulate('piercingsReceived')

    @property
    def damageDealt(self):
        value = self._accumulate('damageDealt')
        if self.__avatar is not None:
            value += self.__avatar.avatarDamageDealt
        return value

    @property
    def tdamageDealt(self):
        return self._accumulate('tdamageDealt')

    @property
    def supplyDamageDealt(self):
        return self._accumulate('supplyDamageDealt')

    @property
    def supplyDamageReceived(self):
        return self._accumulate('supplyDamageReceived')

    @property
    def damageReceivedFromSupply(self):
        return self._accumulate('damageReceivedFromSupply')

    @property
    def sniperDamageDealt(self):
        return self._accumulate('sniperDamageDealt')

    @property
    def targetKills(self):
        return self._accumulate('targetKills')

    @property
    def noDamageDirectHitsReceived(self):
        return self._accumulate('noDamageDirectHitsReceived')

    @property
    def damageBlockedByArmor(self):
        return self._accumulate('damageBlockedByArmor')

    @property
    def rickochetsReceived(self):
        return self._accumulate('rickochetsReceived')

    @property
    def damageAssistedTrack(self):
        return self._accumulate('damageAssistedTrack')

    @property
    def damageAssistedRadio(self):
        return self._accumulate('damageAssistedRadio')

    @property
    def damageAssisted(self):
        return self._accumulate('damageAssisted')

    @property
    def damageAssistedStun(self):
        return self._accumulate('damageAssistedStun')

    @property
    def stunNum(self):
        return self._accumulate('stunNum')

    @property
    def stunDuration(self):
        return self._accumulate('stunDuration')

    @property
    def critsInfo(self):
        result = {'critsCount': 0}
        for value in self._getAtrributeGenerator('critsInfo'):
            unionCritsInfo(result, value)

        return result

    @property
    def critsCount(self):
        return self.critsInfo['critsCount']

    @property
    def shots(self):
        return self._accumulate('shots')

    @property
    def shotsBySupplies(self):
        return self._accumulateSupplies('shots')

    @property
    def shotsByTanks(self):
        return self._accumulateTanks('shots')

    @property
    def damageDealtBySupplies(self):
        return self._accumulateSupplies('damageDealt')

    @property
    def damageDealtByTanks(self):
        return self._accumulateTanks('damageDealt')

    @property
    def damageBlockedBySupplies(self):
        return self._accumulateSupplies('damageBlockedByArmor')

    @property
    def damageBlockedByTanks(self):
        return self._accumulateTanks('damageBlockedByArmor')

    @property
    def sniperDamageDealtByTanks(self):
        return self._accumulateTanks('sniperDamageDealt')

    @property
    def sniperDamageDealtBySupplies(self):
        return self._accumulateSupplies('sniperDamageDealt')

    @property
    def explosionHits(self):
        return self._accumulate('explosionHits')

    @property
    def explosionHitsByTanks(self):
        return self._accumulateTanks('explosionHits')

    @property
    def explosionHitsBySupplies(self):
        return self._accumulateSupplies('explosionHits')

    @property
    def directHits(self):
        return self._accumulate('directHits')

    @property
    def directEnemyHits(self):
        return self._accumulate('directEnemyHits')

    @property
    def directEnemyHitsByTanks(self):
        return self._accumulateTanks('directEnemyHits')

    @property
    def directEnemyHitsBySupplies(self):
        return self._accumulateSupplies('directEnemyHits')

    @property
    def directHitsReceived(self):
        return self._accumulate('directHitsReceived')

    @property
    def explosionHitsReceived(self):
        return self._accumulate('explosionHitsReceived')

    @property
    def kills(self):
        value = self._accumulate('kills')
        if self.__avatar is not None:
            value += self.__avatar.avatarKills
        return value

    @property
    def tkills(self):
        return self._accumulate('tkills')

    @property
    def damaged(self):
        return self._accumulate('damaged')

    @property
    def mileage(self):
        return self._accumulate('mileage')

    @property
    def capturePoints(self):
        return self._accumulate('capturePoints')

    @property
    def droppedCapturePoints(self):
        return self._accumulate('droppedCapturePoints')

    @property
    def xp(self):
        return self._accumulate('xp')

    @property
    def xpForAttack(self):
        return self._accumulate('xpForAttack')

    @property
    def xpForAssist(self):
        return self._accumulate('xpForAssist')

    @property
    def xpOther(self):
        return self._accumulate('xpOther')

    @property
    def xpPenalty(self):
        return self._accumulate('xpPenalty')

    @property
    def deathCount(self):
        return self._accumulate('deathCount')

    @property
    def rollouts(self):
        return self._accumulate('rollouts')

    @property
    def respawns(self):
        return self._accumulate('rollouts') - 1

    @property
    def numDefended(self):
        return self._accumulate('numDefended')

    @property
    def numRecovered(self):
        return self._accumulate('numRecovered')

    @property
    def numCaptured(self):
        return self._accumulate('numCaptured')

    @property
    def numDestroyed(self):
        return self._accumulate('numDestroyed')

    @property
    def destructiblesDamageDealt(self):
        return self._accumulate('destructiblesDamageDealt')

    @property
    def equipmentDamageDealt(self):
        return self._accumulate('equipmentDamageDealt')

    @property
    def equipmentDamageAssisted(self):
        return self._accumulate('equipmentDamageAssisted')

    @property
    def spottedSupplies(self):
        return self._accumulate('spottedSupplies')

    @property
    def damagedSupplies(self):
        return self._collectToSet('damagedSupplies')

    @property
    def damagedTanks(self):
        return self._collectToSet('damagedTanks')

    @property
    def killedSupplies(self):
        return self._accumulate('killedSupplies')

    @property
    def rtsEventPoints(self):
        return self._accumulate('rtsEventPoints')

    def addVehicleInfo(self, info):
        self._vehicles.append(info)

    def addAvatarInfo(self, avatar):
        self.__avatar = avatar

    def getVehiclesIterator(self):
        yield self
        for vehicle in self._vehicles:
            yield vehicle

    def getAchievements(self):
        result = []
        for achievementID in self.achievementsIDs:
            record = DB_ID_TO_RECORD[achievementID]
            factory = getAchievementFactory(record)
            if factory is not None and layouts.isAchievementRegistered(record):
                achievement = factory.create(value=0)
                if not achievement.isApproachable():
                    result.append((achievement, True))

        return sorted(result, key=sort_keys.AchievementSortKey)

    def _getAtrributeGenerator(self, attr):
        getter = operator.attrgetter(attr)
        for vehicle in self._vehicles:
            yield getter(vehicle)

    def _getAtrributeGeneratorForSupplies(self, attr):
        getter = operator.attrgetter(attr)
        for vehicle in self._vehicles:
            if vehicle.vehicle.isSupply:
                yield getter(vehicle)

    def _getAtrributeGeneratorForTanks(self, attr):
        getter = operator.attrgetter(attr)
        for vehicle in self._vehicles:
            if not vehicle.vehicle.isSupply:
                yield getter(vehicle)

    def _findFirstNoZero(self, attr):
        return findFirst(lambda value: value > 0, self._getAtrributeGenerator(attr), default=0)

    def _findMaxInt(self, attr, start=0):
        result = start
        for value in self._getAtrributeGenerator(attr):
            result = max(result, value)

        return result

    def _collectToSet(self, attr):
        result = set()
        for value in self._getAtrributeGenerator(attr):
            result |= value

        return result

    def _collectToDict(self, attr):
        result = {}
        for value in self._getAtrributeGenerator(attr):
            result.update(value)

        return result

    def _accumulate(self, attr):
        return sum(self._getAtrributeGenerator(attr))

    def _accumulateSupplies(self, attr):
        return sum(self._getAtrributeGeneratorForSupplies(attr))

    def _accumulateTanks(self, attr):
        return sum(self._getAtrributeGeneratorForTanks(attr))


class SupplySummarizeInfo(VehicleSummarizeInfo):

    @property
    def deathReason(self):
        return min(self._getAtrributeGenerator('deathReason'))

    @property
    def aliveCount(self):
        return len([ value for value in self._getAtrributeGenerator('deathReason') if value == DEATH_REASON_ALIVE ])


class FairplayViolationsInfo(object):
    __slots__ = ('_warningsMask', '_penaltiesMask', '_violationsMask', '_penaltiesInPercent')

    def __init__(self, warningsMask=0, penaltiesMask=0, violationsMask=0, penaltiesInPercent=-100):
        super(FairplayViolationsInfo, self).__init__()
        self._warningsMask = warningsMask
        self._penaltiesMask = penaltiesMask
        self._violationsMask = violationsMask
        self._penaltiesInPercent = penaltiesInPercent

    def hasWarnings(self):
        return self._warningsMask != 0

    def hasPenalties(self):
        return self._penaltiesMask != 0

    def hasViolations(self):
        return self._violationsMask != 0

    def getWarningName(self):
        return getFairPlayViolationName(self._warningsMask)

    def getPenaltyName(self):
        return getFairPlayViolationName(self._penaltiesMask)

    def getViolationName(self):
        return getFairPlayViolationName(self._violationsMask)

    def getPenaltyDetails(self):
        return (self.getPenaltyName(), self._penaltiesInPercent) if self.hasPenalties() else None
