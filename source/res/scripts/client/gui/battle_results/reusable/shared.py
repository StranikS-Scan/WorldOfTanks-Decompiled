# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/reusable/shared.py
import functools
import operator
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
                    except:
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
    """Creates a dict with info about critical damages for one vehicle.
    :param value: value from 'crits' key for one enemy in 'details' section
    :return: a dict with results
    """
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
        """Is information about item corresponding to desired battle."""
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


class TeamBasesInfo(object):
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


class _VehicleInfo(object):
    """Abstract class that contains information about vehicle."""
    __slots__ = ('_vehicleID', '_vehicle', '_player', '_deathReason')

    def __init__(self, vehicleID, player, deathReason=DEATH_REASON_ALIVE):
        super(_VehicleInfo, self).__init__()
        self._vehicleID = vehicleID
        self._player = player
        self._deathReason = deathReason

    @property
    def vehicleID(self):
        """Gets long containing unique ID of vehicle on the arena."""
        return self._vehicleID

    @property
    def vehicle(self):
        """Get gui wrapper of vehicle."""
        raise NotImplementedError

    @property
    def killerID(self):
        """Get killer account's database ID or 0 if player wasn't killed."""
        raise NotImplementedError

    @property
    def player(self):
        """Get information about player"""
        return self._player

    @property
    def deathReason(self):
        """Gets vehicle's death reason (see ATTACK_REASONS). -1 if it wasn't killed."""
        return self._deathReason

    @property
    def achievementsIDs(self):
        """Gets received "in-battle" achievements IDs"""
        raise NotImplementedError

    @property
    def spotted(self):
        """Gets number of spotted vehicles."""
        raise NotImplementedError

    @property
    def piercings(self):
        """Gets number of direct hits vehicle made that caused damage to target's health or devices."""
        raise NotImplementedError

    @property
    def piercingsReceived(self):
        """Gets number of direct hits received that caused damage to vehicle's health or devices."""
        raise NotImplementedError

    @property
    def damageDealt(self):
        """Gets total damage dealt to the target by vehicle."""
        raise NotImplementedError

    @property
    def tdamageDealt(self):
        """Gets team damage dealt."""
        raise NotImplementedError

    @property
    def sniperDamageDealt(self):
        """Gets damage dealt from sniper distance."""
        raise NotImplementedError

    @property
    def kills(self):
        """Gets total number of kills that vehicle made."""
        raise NotImplementedError

    @property
    def tkills(self):
        """Gets number of team kills that vehicle made."""
        raise NotImplementedError

    @property
    def targetKills(self):
        """Gets number of target kills (for respawn mechanics) by actor."""
        raise NotImplementedError

    @property
    def noDamageDirectHitsReceived(self):
        """Gets number of direct hits received that caused no damage."""
        raise NotImplementedError

    @property
    def damageBlockedByArmor(self):
        """Gets damage that might be received if there were piercings."""
        raise NotImplementedError

    @property
    def rickochetsReceived(self):
        """Gets number of rickochets received."""
        raise NotImplementedError

    @property
    def damageAssistedTrack(self):
        """Gets damage dealt with the vehicle track assistant."""
        raise NotImplementedError

    @property
    def damageAssistedRadio(self):
        """Gets damage dealt with the vehicle radio assistant.."""
        raise NotImplementedError

    @property
    def damageAssisted(self):
        """Gets sum of properties damageAssistedTrack and damageAssistedRadio."""
        raise NotImplementedError

    @property
    def critsInfo(self):
        """ Gets critical information that personal vehicle(s) according to enemy."""
        raise NotImplementedError

    @property
    def critsCount(self):
        """Gets number of critical damages that personal vehicle(s) according to enemy."""
        raise NotImplementedError

    @property
    def shots(self):
        """ Gets number of shots made (may lead to direct hit, explosion hit, or miss)."""
        raise NotImplementedError

    @property
    def explosionHits(self):
        """Gets number of explosion hits received (with and without damage)."""
        raise NotImplementedError

    @property
    def directHits(self):
        """Gets number of direct hits made to another vehicles (with and without damage)."""
        raise NotImplementedError

    @property
    def directHitsReceived(self):
        """Gets number of direct hits received (with and without damage)."""
        raise NotImplementedError

    @property
    def explosionHitsReceived(self):
        """Gets number of explosion hits received (with and without damage)."""
        raise NotImplementedError

    @property
    def damaged(self):
        """Gets number of vehicle damaged."""
        raise NotImplementedError

    @property
    def mileage(self):
        """Gets mileage for the battle."""
        raise NotImplementedError

    @property
    def capturePoints(self):
        """Gets team base capture points."""
        raise NotImplementedError

    @property
    def droppedCapturePoints(self):
        """Gets dropped team base capture points."""
        raise NotImplementedError

    @property
    def fortResource(self):
        """Gets total fortified resources."""
        raise NotImplementedError

    @property
    def xp(self):
        """Gets value of total XP according to vehicles without achievements XP."""
        raise NotImplementedError

    def getOrderByClass(self):
        return Vehicle.getOrderByVehicleClass(Vehicle.getVehicleClassTag(self.vehicle.descriptor.type.tags))


class VehicleDetailedInfo(_VehicleInfo):
    """Class that contains detailed information about one vehicle.
    This class can be used for vehicle and comments of properties related to this vehicle.
    Also this class can be used for enemies in the efficiency block and
    comments of properties related to some personal vehicle."""
    __slots__ = ('_vehicle', '_killerID', '_achievementsIDs', '_critsInfo', '_spotted', '_piercings', '_piercingsReceived', '_damageDealt', '_tdamageDealt', '_sniperDamageDealt', '_damageBlockedByArmor', '_damageAssistedTrack', '_damageAssistedRadio', '_rickochetsReceived', '_noDamageDirectHitsReceived', '_targetKills', '_directHits', '_directHitsReceived', '_explosionHits', '_explosionHitsReceived', '_shots', '_kills', '_tkills', '_damaged', '_mileage', '_capturePoints', '_droppedCapturePoints', '_fortResource', '_xp', '_fire')

    def __init__(self, vehicleID, vehicle, player, deathReason=DEATH_REASON_ALIVE):
        super(VehicleDetailedInfo, self).__init__(vehicleID, player, deathReason)
        self._vehicle = vehicle
        self._killerID = 0
        self._achievementsIDs = set()
        self._critsInfo = makeCritsInfo(0)
        self._spotted = 0
        self._piercings = 0
        self._piercingsReceived = 0
        self._damageBlockedByArmor = 0
        self._rickochetsReceived = 0
        self._noDamageDirectHitsReceived = 0
        self._targetKills = 0
        self._damageDealt = 0
        self._tdamageDealt = 0
        self._sniperDamageDealt = 0
        self._damageAssistedTrack = 0
        self._damageAssistedRadio = 0
        self._directHits = 0
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
        self._fortResource = 0
        self._xp = 0
        self._fire = 0

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
    def piercingsReceived(self):
        return self._piercingsReceived

    @property
    def damageDealt(self):
        return self._damageDealt

    @property
    def tdamageDealt(self):
        return self._tdamageDealt

    @property
    def sniperDamageDealt(self):
        return self._sniperDamageDealt

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
    def critsInfo(self):
        return self._critsInfo

    @property
    def critsCount(self):
        return self.critsInfo['critsCount']

    @property
    def shots(self):
        return self._shots

    @property
    def explosionHits(self):
        return self._explosionHits

    @property
    def directHits(self):
        return self._directHits

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
    def fortResource(self):
        return self._fortResource

    @property
    def xp(self):
        return self._xp

    def haveInteractionDetails(self):
        return self._spotted != 0 or self._deathReason > DEATH_REASON_ALIVE or self._directHits != 0 or self._explosionHits != 0 or self._piercings != 0 or self._damageDealt != 0 or self.damageAssisted != 0 or self.critsCount != 0 or self._fire != 0 or self._targetKills != 0

    @classmethod
    @no_key_error
    def makeForEnemy(cls, vehicleID, vehicle, player, detailsRecords, deathReason=DEATH_REASON_ALIVE):
        info = cls(vehicleID, vehicle, player, deathReason=deathReason)
        info._critsInfo = makeCritsInfo(detailsRecords['crits'])
        info._rickochetsReceived = detailsRecords['rickochetsReceived']
        info._targetKills = detailsRecords['targetKills']
        info._fire = detailsRecords['fire']
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
        info._shots = vehicleRecords['shots']
        info._directHitsReceived = vehicleRecords['directHitsReceived']
        info._explosionHitsReceived = vehicleRecords['explosionHitsReceived']
        info._kills = vehicleRecords['kills']
        info._tkills = vehicleRecords['tkills']
        info._damaged = vehicleRecords['damaged']
        info._mileage = vehicleRecords['mileage']
        info._capturePoints = vehicleRecords['capturePoints']
        info._droppedCapturePoints = vehicleRecords['droppedCapturePoints']
        info._fortResource = vehicleRecords['fortResource']
        info._xp = vehicleRecords['xp'] - vehicleRecords['achievementXP']
        cls._setSharedRecords(info, vehicleRecords)
        return info

    @classmethod
    def _setSharedRecords(cls, info, records):
        info._deathReason = max(info._deathReason, records['deathReason'])
        info._spotted = records['spotted']
        info._piercings = records['piercings']
        info._damageDealt = records['damageDealt']
        info._damageBlockedByArmor = records['damageBlockedByArmor']
        info._noDamageDirectHitsReceived = records['noDamageDirectHitsReceived']
        info._damageAssistedTrack = records['damageAssistedTrack']
        info._damageAssistedRadio = records['damageAssistedRadio']
        info._directHits = records['directHits']
        info._explosionHits = records['explosionHits']


class VehicleSummarizeInfo(_VehicleInfo):
    """Class that contains detailed information about all vehicles that are use one player."""
    __slots__ = ('__avatar', '__vehicles')

    def __init__(self, vehicleID, player):
        super(VehicleSummarizeInfo, self).__init__(vehicleID, player)
        self.__avatar = None
        self.__vehicles = []
        return

    @property
    def vehicle(self):
        if self.__vehicles:
            return self.__vehicles[0].vehicle
        else:
            return None
            return None

    @property
    def killerID(self):
        return self.__findFirstNoZero('killerID')

    @property
    def deathReason(self):
        return self.__findMaxInt('deathReason', start=DEATH_REASON_ALIVE)

    @property
    def achievementsIDs(self):
        return self.__collectToSet('achievementsIDs')

    @property
    def spotted(self):
        return self.__accumulate('spotted')

    @property
    def piercings(self):
        return self.__accumulate('piercings')

    @property
    def piercingsReceived(self):
        return self.__accumulate('piercingsReceived')

    @property
    def damageDealt(self):
        value = self.__accumulate('damageDealt')
        if self.__avatar is not None:
            value += self.__avatar.avatarDamageDealt
        return value

    @property
    def tdamageDealt(self):
        return self.__accumulate('tdamageDealt')

    @property
    def sniperDamageDealt(self):
        return self.__accumulate('sniperDamageDealt')

    @property
    def targetKills(self):
        return self.__accumulate('targetKills')

    @property
    def noDamageDirectHitsReceived(self):
        return self.__accumulate('noDamageDirectHitsReceived')

    @property
    def damageBlockedByArmor(self):
        return self.__accumulate('damageBlockedByArmor')

    @property
    def rickochetsReceived(self):
        return self.__accumulate('rickochetsReceived')

    @property
    def damageAssistedTrack(self):
        return self.__accumulate('damageAssistedTrack')

    @property
    def damageAssistedRadio(self):
        return self.__accumulate('damageAssistedRadio')

    @property
    def damageAssisted(self):
        return self.__accumulate('damageAssisted')

    @property
    def critsInfo(self):
        result = {'critsCount': 0}
        for value in self.__getAtrributeGenerator('critsInfo'):
            unionCritsInfo(result, value)

        return result

    @property
    def critsCount(self):
        return self.critsInfo['critsCount']

    @property
    def shots(self):
        return self.__accumulate('shots')

    @property
    def explosionHits(self):
        return self.__accumulate('explosionHits')

    @property
    def directHits(self):
        return self.__accumulate('directHits')

    @property
    def directHitsReceived(self):
        return self.__accumulate('directHitsReceived')

    @property
    def explosionHitsReceived(self):
        return self.__accumulate('explosionHitsReceived')

    @property
    def kills(self):
        value = self.__accumulate('kills')
        if self.__avatar is not None:
            value += self.__avatar.avatarKills
        return value

    @property
    def tkills(self):
        return self.__accumulate('tkills')

    @property
    def damaged(self):
        return self.__accumulate('damaged')

    @property
    def mileage(self):
        return self.__accumulate('mileage')

    @property
    def capturePoints(self):
        return self.__accumulate('capturePoints')

    @property
    def droppedCapturePoints(self):
        return self.__accumulate('droppedCapturePoints')

    @property
    def fortResource(self):
        return self.__accumulate('fortResource')

    @property
    def xp(self):
        return self.__accumulate('xp')

    def addVehicleInfo(self, info):
        """Adds detailed information about vehicle.
        :param info: instance of VehicleDetailedInfo.
        """
        self.__vehicles.append(info)

    def addAvatarInfo(self, avatar):
        """Adds information about avatar.
        :param avatar: instance of AvatarInfo.
        """
        self.__avatar = avatar

    def getVehiclesIterator(self):
        """Returns generator where each item is _VehicleInfo.
        Note: first item is summarize data for all vehicles.
        
        :return: generator.
        """
        yield self
        for vehicle in self.__vehicles:
            yield vehicle

    def getAchievements(self):
        """Gets list of received "in-battle" achievements that are reviced by player's vehicles."""
        achievements = []
        for achievementID in self.achievementsIDs:
            record = DB_ID_TO_RECORD[achievementID]
            factory = getAchievementFactory(record)
            if factory is not None and layouts.isAchievementRegistered(record):
                achievement = factory.create(value=0)
                if not achievement.isApproachable():
                    achievements.append((achievement, True))

        return sorted(achievements, key=sort_keys.AchievementSortKey)

    def __getAtrributeGenerator(self, attr):
        getter = operator.attrgetter(attr)
        for vehicle in self.__vehicles:
            yield getter(vehicle)

    def __findFirstNoZero(self, attr):
        return findFirst(lambda value: value > 0, self.__getAtrributeGenerator(attr), default=0)

    def __findMaxInt(self, attr, start=0):
        result = start
        for value in self.__getAtrributeGenerator(attr):
            result = max(result, value)

        return result

    def __collectToSet(self, attr):
        result = set()
        for value in self.__getAtrributeGenerator(attr):
            result |= value

        return result

    def __collectToDict(self, attr):
        result = {}
        for value in self.__getAtrributeGenerator(attr):
            result.update(value)

        return result

    def __accumulate(self, attr):
        return sum(self.__getAtrributeGenerator(attr))


class FairplayViolationsInfo(object):
    """Class holds information about fairplay violations"""
    __slots__ = ('_warningsMask', '_penaltiesMask', '_violationsMask', '_penaltiesInPercent')

    def __init__(self, warningsMask=0, penaltiesMask=0, violationsMask=0, penaltiesInPercent=-100):
        super(FairplayViolationsInfo, self).__init__()
        self._warningsMask = warningsMask
        self._penaltiesMask = penaltiesMask
        self._violationsMask = violationsMask
        self._penaltiesInPercent = penaltiesInPercent

    def hasWarnings(self):
        """Have fairplay warnings?
        :return: bool.
        """
        return self._warningsMask != 0

    def hasPenalties(self):
        """Have fairplay penalties?
        :return: bool.
        """
        return self._penaltiesMask != 0

    def hasViolations(self):
        """Have fairplay penalties?
        :return: bool.
        """
        return self._violationsMask != 0

    def getWarningName(self):
        """Gets first name of warning.
        :return: string containing one of FAIRPLAY_VIOLATIONS_NAMES value or None.
        """
        return getFairPlayViolationName(self._warningsMask)

    def getPenaltyName(self):
        """Gets first name of penalty.
        :return: string containing one of FAIRPLAY_VIOLATIONS_NAMES value or None.
        """
        return getFairPlayViolationName(self._penaltiesMask)

    def getViolationName(self):
        """Gets first name of violations.
        :return: string containing one of FAIRPLAY_VIOLATIONS_NAMES value or None.
        """
        return getFairPlayViolationName(self._violationsMask)

    def getPenaltyDetails(self):
        """Gets penalty details if they have.
        :return: tuple(name of penalty, value in percent).
        """
        if self.hasPenalties():
            return (self.getPenaltyName(), self._penaltiesInPercent)
        else:
            return None
            return None
