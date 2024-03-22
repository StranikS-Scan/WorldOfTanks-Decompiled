# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/tankmen.py
import random
import struct
from functools import partial
from itertools import izip
from typing import TYPE_CHECKING, List, Dict, Any, Tuple, Optional, Set
import nations
from constants import ITEM_DEFS_PATH, VEHICLE_NO_CREW_TRANSFER_PENALTY_TAG, VEHICLE_WOT_PLUS_TAG
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG_DEV
from helpers_common import bisectLE
from items import vehicles, ITEM_TYPES, parseIntCompactDescr
from items.components import skills_components, crew_skins_constants, crew_books_constants
from items.components import skills_constants
from items.components import tankmen_components
from items.components.crew_books_components import CrewBooksCache
from items.components.crew_skins_components import CrewSkinsCache
from items.passports import PassportCache, passport_generator, maxAttempts, distinctFrom, acceptOn
from items.readers import skills_readers
from items.readers import tankmen_readers
from items.readers.crewBooks_readers import readCrewBooksCacheFromXML
from items.readers.crewSkins_readers import readCrewSkinsCacheFromXML
from items.tankman_flags import TankmanFlags
from soft_exception import SoftException
from vehicles import VEHICLE_CLASS_TAGS, EXTENDED_VEHICLE_TYPE_ID_FLAG
if TYPE_CHECKING:
    from items.vehicles import VehicleType
SKILL_NAMES = skills_constants.SKILL_NAMES
SKILL_INDICES = skills_constants.SKILL_INDICES
ROLES = skills_constants.ROLES
COMMON_SKILL_ROLE_TYPE = skills_constants.COMMON_SKILL_ROLE_TYPE
COMMON_SKILLS = skills_constants.COMMON_SKILLS
COMMON_SKILLS_ORDERED = skills_constants.COMMON_SKILLS_ORDERED
SEPARATE_SKILLS = skills_constants.SEPARATE_SKILLS
ROLES_AND_COMMON_SKILLS = skills_constants.ROLES_AND_COMMON_SKILLS
LEARNABLE_ACTIVE_SKILLS = skills_constants.LEARNABLE_ACTIVE_SKILLS
UNLEARNABLE_SKILLS = skills_constants.UNLEARNABLE_SKILLS
SKILLS_BY_ROLES = skills_constants.SKILLS_BY_ROLES
SKILLS_BY_ROLES_ORDERED = skills_constants.SKILLS_BY_ROLES_ORDERED
MAX_FREE_SKILLS_SIZE = 16
NO_SKILL = -1
MAX_SKILL_LEVEL = 100
MAX_SKILLS_EFFICIENCY = 1.0
MAX_SKILLS_EFFICIENCY_XP = 100000
MIN_ROLE_LEVEL = 50
SKILL_LEVELS_PER_RANK = 50
COMMANDER_ADDITION_RATIO = 10
_MAX_FREE_XP = 4000000000L
MIN_XP_REUSE_FRACTION = 0.0
MAX_XP_REUSE_FRACTION = 1.0
_LEVELUP_K1 = 50.0
_LEVELUP_K2 = 100.0
RECRUIT_TMAN_TOKEN_TOTAL_PARTS = 11
RECRUIT_TMAN_TOKEN_PREFIX = 'tman_template'
MAX_SKILLS_IN_RECRUIT_TOKEN = 10
_CREW_SKINS_XML_PATH = ITEM_DEFS_PATH + 'crewSkins/'
_CREW_BOOKS_XML_PATH = ITEM_DEFS_PATH + 'crewBooks/'
g_cache = None

def init(preloadEverything, pricesToCollect):
    global g_cache
    g_cache = Cache()
    if preloadEverything:
        getSkillsConfig()
        for nationID in xrange(len(nations.NAMES)):
            getNationConfig(nationID)

        g_cache.initCrewSkins(pricesToCollect)
        g_cache.initCrewBooks(pricesToCollect)


def getSkillsConfig():
    global _g_skillsConfig
    if _g_skillsConfig is None:
        _g_skillsConfig = skills_readers.readSkillsConfig(ITEM_DEFS_PATH + 'tankmen/tankmen.xml')
    return _g_skillsConfig


def getLoreConfig():
    global _g_loreConfig
    if _g_loreConfig is None:
        _g_loreConfig = tankmen_readers.readLoreConfig(ITEM_DEFS_PATH + 'tankmen/lore.xml')
    return _g_loreConfig


def getSkillsMask(skills):
    result = 0
    for skill in skills:
        result |= 1 << SKILL_INDICES[skill]

    return result


ALL_SKILLS_MASK = getSkillsMask([ skill for skill in LEARNABLE_ACTIVE_SKILLS if skill != 'reserved' ])

def getNationConfig(nationID):
    global _g_nationsConfig
    if _g_nationsConfig[nationID] is None:
        nationName = nations.NAMES[nationID]
        if nationName not in nations.AVAILABLE_NAMES:
            _g_nationsConfig[nationID] = tankmen_components.NationConfig('stub')
        else:
            _g_nationsConfig[nationID] = tankmen_readers.readNationConfig(ITEM_DEFS_PATH + 'tankmen/' + nationName + '.xml')
    return _g_nationsConfig[nationID]


def getTankmenGroupNames():
    global _g_tankmenGroupNames
    if _g_tankmenGroupNames is None:
        _g_tankmenGroupNames = []
        for nationID in xrange(len(nations.AVAILABLE_NAMES)):
            _g_tankmenGroupNames.extend([ g.name for g in getNationGroups(nationID, False).itervalues() ])
            _g_tankmenGroupNames.extend([ g.name for g in getNationGroups(nationID, True).itervalues() ])

        _g_tankmenGroupNames = set(_g_tankmenGroupNames)
    return _g_tankmenGroupNames


def generatePassport(nationID, isPremium=False):
    return passportProducer(nationID, isPremium)[1]


def passportProducer(nationID, isPremium=False):
    isPremium = False
    groups = getNationGroups(nationID, isPremium)
    w = random.random()
    summWeight = 0.0
    group = None
    for group in groups.itervalues():
        weight = group.weight
        if summWeight <= w < summWeight + weight:
            break
        summWeight += weight

    return (group, (nationID,
      isPremium,
      group.isFemales,
      random.choice(group.firstNamesList),
      random.choice(group.lastNamesList),
      random.choice(group.iconsList)))


def crewMemberPreviewProducer(nationID, isPremium=False, vehicleTypeID=None, role=None):
    vehicleName = vehicles.g_cache.vehicle(nationID, vehicleTypeID).name if vehicleTypeID else None
    nationalGroups = getNationGroups(nationID, isPremium).values()
    groups = [ g for g in nationalGroups if vehicleName in g.tags and role in g.tags ]
    if not groups:
        groups = [ g for g in nationalGroups if vehicleName in g.tags ]
    if not groups:
        groups = [ g for g in nationalGroups if role in g.tags ]
    if not groups:
        groups = nationalGroups
    group = random.choice(groups)
    pos = random.randint(0, min(map(len, (group.firstNamesList, group.lastNamesList, group.iconsList))) - 1)
    return (group, (nationID,
      isPremium,
      group.isFemales,
      group.firstNamesList[pos],
      group.lastNamesList[pos],
      group.iconsList[pos]))


def generateSkills(role, skillsMask):
    tankmanSkills = set()
    if skillsMask != 0:
        for i in xrange(len(role)):
            roleSkills = SKILLS_BY_ROLES[role[i]]
            if skillsMask == ALL_SKILLS_MASK:
                tankmanSkills.update(roleSkills)
            for skill, idx in SKILL_INDICES.iteritems():
                if 1 << idx & skillsMask and skill in roleSkills:
                    tankmanSkills.add(skill)

    return [ skill for skill in tankmanSkills if skill not in UNLEARNABLE_SKILLS ]


def generateTankmen(nationID, vehicleTypeID, roles, isPremium, roleLevel, skillsMask, isPreview=False, freeXP=0):
    tankmenList = []
    prevPassports = PassportCache()
    for i in xrange(len(roles)):
        role = roles[i]
        pg = passport_generator(nationID, isPremium, partial(crewMemberPreviewProducer, vehicleTypeID=vehicleTypeID, role=role[0]) if isPreview else passportProducer, maxAttempts(10), distinctFrom(prevPassports), acceptOn('roles', role[0]))
        passport = next(pg)
        prevPassports.append(passport)
        skills = generateSkills(role, skillsMask)
        tmanCompDescr = generateCompactDescr(passport, vehicleTypeID, role[0], roleLevel, skills, initialXP=freeXP)
        tankmenList.append(tmanCompDescr)

    return tankmenList if len(tankmenList) == len(roles) else []


def generateCompactDescr(passport, vehicleTypeID, role, roleLevel=MAX_SKILL_LEVEL, skills=(), lastSkillLevel=MAX_SKILL_LEVEL, dossierCompactDescr='', freeSkills=(), initialXP=0, skillsEfficiencyXP=MAX_SKILLS_EFFICIENCY_XP):
    pack = struct.pack
    nationID, isPremium, isFemale, firstNameID, lastNameID, iconID = passport
    header = ITEM_TYPES.tankman + (nationID << 4)
    cd = pack('B', header)
    tf = TankmanFlags()
    tf.extendedVehicleTypeID = vehicleTypeID > 255
    tf.hasFreeSkills = len(freeSkills) > 0
    tf.isFemale = isFemale
    tf.isPremium = isPremium
    cd += tf.pack()
    fmt = '>H' if tf.extendedVehicleTypeID else 'B'
    cd += pack(fmt, vehicleTypeID)
    sef = skillsEfficiencyXP
    cd += chr((SKILL_INDICES[role] << 1) + (sef >> 16 & 1)) + chr(sef >> 8 & 255) + chr(sef & 255)
    numSkills = len(skills) + len(freeSkills)
    allSkills = [ SKILL_INDICES[s] for s in freeSkills ]
    for s in skills:
        allSkills.append(SKILL_INDICES[s])

    cd += pack((str(1 + numSkills) + 'B'), numSkills, *allSkills)
    cd += chr(lastSkillLevel if numSkills else 0)
    if tf.hasFreeSkills:
        cd += pack('B', len(freeSkills))
    freeXP = 0
    cd += pack('>3HI', firstNameID, lastNameID, iconID, freeXP)
    cd += dossierCompactDescr
    if initialXP > 0:
        tmanDescr = TankmanDescr(compactDescr=cd)
        tmanDescr.addXP(initialXP)
        cd = tmanDescr.makeCompactDescr()
    return cd


def getNextUniqueIDs(databaseID, lastFirstNameID, lastLastNameID, lastIconID, nationID, isPremium, fnGroupID, lnGroupID, iGroupID):
    return (getNextUniqueID(databaseID, lastFirstNameID, nationID, isPremium, fnGroupID, 'firstNamesList'), getNextUniqueID(databaseID, lastLastNameID, nationID, isPremium, lnGroupID, 'lastNamesList'), getNextUniqueID(databaseID, lastIconID, nationID, isPremium, iGroupID, 'iconsList'))


def getNextUniqueID(databaseID, lastID, nationID, isPremium, groupID, name):
    group = getNationConfig(nationID).getGroups(isPremium)[groupID]
    ids = getattr(group, name)
    groupSize = len(ids)
    if groupSize == 0:
        return (-1, None)
    else:
        for n in (5, 7, 11, 13, 17, 19, 23, 29, 31):
            if groupSize % n != 0:
                step = n
                break
        else:
            step = 37

        nextID = lastID
        if lastID == -1:
            nextID = databaseID % min(7, groupSize)
        else:
            nextID += step
        if nextID >= groupSize:
            nextID -= max(groupSize, step)
        return (nextID, ids[nextID])


def stripNonBattle(compactDescr):
    l = 1
    tf = TankmanFlags.fromCD(compactDescr[l:])
    l += tf.len
    l += 2 if tf.extendedVehicleTypeID else 1
    l += 3
    numSkills = ord(compactDescr[l])
    l += 2 + numSkills
    l += 1 if tf.hasFreeSkills else 0
    l += 6
    return compactDescr[:l]


def parseNationSpecAndRole(compactDescr):
    cd = compactDescr
    nationID = ord(compactDescr[0]) >> 4
    cd = cd[1:]
    tf = TankmanFlags.fromCD(cd)
    cd = cd[tf.len:]
    if tf.extendedVehicleTypeID:
        vehicleTypeID = struct.unpack('>H', cd[:2])
        cd = cd[2:]
    else:
        vehicleTypeID = struct.unpack('B', cd[:1])
        cd = cd[1:]
    roleID = ord(cd[0]) >> 1
    return (nationID, vehicleTypeID, roleID)


def fixObsoleteNames(compactDescr):
    cd = compactDescr
    header = ord(cd[0])
    vehTypeOffset = 1 if header & EXTENDED_VEHICLE_TYPE_ID_FLAG else 0
    nationID = header >> 4 & 15
    conf = getNationConfig(nationID)
    namesOffset = ord(cd[4 + vehTypeOffset]) + 7 + vehTypeOffset
    firstNameID, lastNameID = struct.unpack('<2H', cd[namesOffset:namesOffset + 4])
    hasChanges = False
    if not conf.hasFirstName(firstNameID):
        hasChanges = True
        firstNameID = generatePassport(nationID)[3]
    if not conf.hasLastName(lastNameID):
        hasChanges = True
        lastNameID = generatePassport(nationID)[4]
    return cd if not hasChanges else cd[:namesOffset] + struct.pack('<2H', firstNameID, lastNameID) + cd[namesOffset + 4:]


class OperationsRestrictions(object):
    __slots__ = ('__groupTags',)

    def __init__(self, tags=None):
        super(OperationsRestrictions, self).__init__()
        self.__groupTags = tags or frozenset()

    def isPassportReplacementForbidden(self):
        return tankmen_components.GROUP_TAG.PASSPORT_REPLACEMENT_FORBIDDEN in self.__groupTags


class TankmanDescr(object):

    def __init__(self, compactDescr, battleOnly=False):
        self.__initFromCompactDescr(compactDescr, battleOnly)

    @property
    def skills(self):
        return list(self._skills)

    @property
    def kpi(self):
        kpi = []
        skillsConfig = getSkillsConfig()
        for skill_name in self.skills:
            kpi += skillsConfig.getSkill(skill_name).kpi

        return kpi

    @property
    def freeSkills(self):
        return list(self._skills[:self.freeSkillsNumber])

    @property
    def earnedSkills(self):
        return list(self._skills[self.freeSkillsNumber:])

    @property
    def lastSkillLevel(self):
        return self.__lastSkillLevel

    @property
    def lastSkillNumber(self):
        return len(self._skills)

    @property
    def earnedSkillsNumber(self):
        return len(self._skills) - self.freeSkillsNumber

    @property
    def skillLevels(self):
        for skillName in self._skills:
            level = MAX_SKILL_LEVEL if skillName != self._skills[-1] else self.__lastSkillLevel
            yield (skillName, level)

    @property
    def nativeRoles(self):
        groups = getNationGroups(self.nationID, self.isPremium)
        return tuple(groups[self.gid].roles) if self.gid in groups else ()

    @property
    def isUnique(self):
        groups = getNationGroups(self.nationID, self.isPremium)
        if self.gid in groups:
            return groups[self.gid].isUnique
        else:
            return False

    @property
    def vehicleTypeCompDescr(self):
        return vehicles.makeIntCompactDescrByID('vehicle', self.nationID, self.vehicleTypeID)

    def canUseSkills(self, vehicleDescrType):
        isPremium, _ = self.__paramsOnVehicle(vehicleDescrType)
        if isPremium:
            return True
        tagList = [VEHICLE_NO_CREW_TRANSFER_PENALTY_TAG, VEHICLE_WOT_PLUS_TAG]
        return any((tag in vehicleDescrType.tags for tag in tagList))

    def isOwnVehicleOrPremium(self, vehicleDescrType, isCheckWotPlus=True):
        tagList = [VEHICLE_NO_CREW_TRANSFER_PENALTY_TAG]
        if isCheckWotPlus:
            tagList.append(VEHICLE_WOT_PLUS_TAG)
        if any((tag in vehicleDescrType.tags for tag in tagList)):
            return True
        if vehicleDescrType.innationID != self.vehicleTypeID:
            isPremium, isSameClass = self.__paramsOnVehicle(vehicleDescrType)
            return isPremium and isSameClass
        return True

    def getBattleXpGainFactor(self, vehicleType, commanderTutorXpBonusFactor):
        factor = 1.0
        nationID, _ = vehicleType.id
        factor *= vehicleType.crewXpFactor
        factor *= 1.0 + commanderTutorXpBonusFactor
        return factor

    @staticmethod
    def levelUpXpCost(fromSkillLevel, skillSeqNum):
        costs = _g_levelXpCosts
        return 2 ** skillSeqNum * (costs[fromSkillLevel + 1] - costs[fromSkillLevel])

    @staticmethod
    def skillUpXpCost(lastSkillSeqNum):
        if not lastSkillSeqNum:
            return 0
        costs = _g_skillXpCosts
        return costs[lastSkillSeqNum] - costs[lastSkillSeqNum - 1]

    @staticmethod
    def getXpCostForSkillsLevels(lastSkillLevel, lastSkillSeqNum):
        if not lastSkillSeqNum:
            return _g_levelXpCosts[lastSkillLevel]
        return _g_skillXpCosts[lastSkillSeqNum] if lastSkillLevel == MAX_SKILL_LEVEL else _g_skillXpCosts[lastSkillSeqNum - 1] + 2 ** lastSkillSeqNum * _g_levelXpCosts[lastSkillLevel]

    @staticmethod
    def getSkillsCountFromXp(availableXp):
        return 0 if availableXp < 0 else bisectLE(_g_skillXpCosts, availableXp) + 1

    @staticmethod
    def getSkillLevelFromXp(skillsNum, availableXp):
        if skillsNum:
            residualXp = int(float(availableXp - _g_skillXpCosts[skillsNum - 1]) / 2 ** skillsNum)
            if residualXp > 0:
                return bisectLE(_g_levelXpCosts, residualXp)

    def getTotalSkillProgress(self, withFree=False):
        xp = self.totalXP()
        fullSkillsNumber = bisectLE(_g_skillXpCosts, xp)
        lastSkillXP = xp - _g_skillXpCosts[fullSkillsNumber]
        lastSkillLevel = bisectLE(_g_levelXpCosts, lastSkillXP >> fullSkillsNumber + 1)
        if withFree:
            fullSkillsNumber += self.freeSkillsNumber
        return fullSkillsNumber * MAX_SKILL_LEVEL + lastSkillLevel

    def getFullSkillsCount(self, withFree=True):
        xp = self.totalXP()
        skillsNum = bisectLE(_g_skillXpCosts, xp)
        if withFree:
            skillsNum += self.freeSkillsNumber
        return skillsNum

    def skillLevel(self, skillName):
        if skillName not in self.skills:
            return None
        else:
            return MAX_SKILL_LEVEL if skillName != self._skills[-1] else self.__lastSkillLevel

    def totalXP(self):
        numFullSkills = max(self.earnedSkillsNumber - 1, 0)
        lastEarnedSkillLevel = self.__lastSkillLevel if self.earnedSkillsNumber > 0 else 0
        lastEarnedSkillXP = _g_levelXpCosts[lastEarnedSkillLevel] << self.earnedSkillsNumber
        return _g_skillXpCosts[numFullSkills] + lastEarnedSkillXP + self.freeXP

    def addXP(self, xp, truncateXP=True):
        tmpXP = xp
        if self.skillsEfficiencyXP < MAX_SKILLS_EFFICIENCY_XP:
            xpToAdd = min(tmpXP, MAX_SKILLS_EFFICIENCY_XP - self.skillsEfficiencyXP)
            self.skillsEfficiencyXP += xpToAdd
            tmpXP -= xpToAdd
        if tmpXP <= 0:
            return
        self.freeXP = self.freeXP + tmpXP
        if truncateXP:
            self.truncateXP()
        self.__levelUpLastSkill()

    def checkRestrictionsByVehicleTags(self):
        if 'lockCrewSkills' in self.__vehicleTags:
            raise SoftException('Changing tankmans skills is forbidden for current vehicle.')

    @property
    def roleLevel(self):
        return MAX_SKILL_LEVEL

    def addSkill(self, skillName):
        if skillName in self.skills:
            raise SoftException('Skill already leaned (%s)' % skillName)
        if skillName not in skills_constants.ACTIVE_SKILLS:
            raise SoftException('Unknown skill (%s)' % skillName)
        if skillName in skills_constants.UNLEARNABLE_SKILLS:
            raise SoftException('Skill (%s) cannot be learned' % skillName)
        if self.role != 'commander' and skillName in skills_constants.COMMANDER_SKILLS:
            raise SoftException('Cannot learn commander skill (%s) for another role (%s)' % (skillName, self.role))
        if self._skills and self.__lastSkillLevel != MAX_SKILL_LEVEL:
            raise SoftException('Last skill not fully leaned (%d)' % self.__lastSkillLevel)
        self._skills.append(skillName)
        self.__lastSkillLevel = 0
        self.__levelUpLastSkill()

    def truncateXP(self):
        self.freeXP = min(_MAX_FREE_XP, self.freeXP)

    def isFreeDropSkills(self):
        if self.lastSkillNumber < 1 + self.freeSkillsNumber:
            return True
        return True if self.lastSkillNumber == 1 + self.freeSkillsNumber and self.__lastSkillLevel == 0 else False

    def dropSkills(self, xpReuseFraction=MIN_XP_REUSE_FRACTION, throwIfNoChange=True, truncateXP=True):
        if len(self._skills) == 0:
            if throwIfNoChange:
                raise SoftException('attempt to reset empty skills')
            return
        prevTotalXP = self.totalXP()
        numSkills = self.earnedSkillsNumber
        if numSkills < 1:
            if throwIfNoChange:
                raise SoftException('attempt to reset free skills')
            return
        del self._skills[self.freeSkillsNumber:]
        if self.freeSkillsNumber:
            self.__lastSkillLevel = MAX_SKILL_LEVEL
        else:
            self.__lastSkillLevel = 0
        if xpReuseFraction > MIN_XP_REUSE_FRACTION:
            tmpXP = int(xpReuseFraction * (prevTotalXP - self.totalXP()))
            self.freeXP = self.freeXP + tmpXP
            if truncateXP:
                self.truncateXP()
            self.__levelUpLastSkill()
        self._updateRank()

    def dropSkill(self, skillName, xpReuseFraction=MIN_XP_REUSE_FRACTION, truncateXP=True):
        idx = self._skills.index(skillName)
        prevTotalXP = self.totalXP()
        numSkills = self.earnedSkillsNumber
        if numSkills == 1:
            self.__lastSkillLevel = MAX_SKILL_LEVEL if self.freeSkillsNumber else 0
        elif idx + 1 == numSkills:
            self.__lastSkillLevel = MAX_SKILL_LEVEL
        del self._skills[idx]
        if xpReuseFraction > MIN_XP_REUSE_FRACTION:
            self.addXP(int(xpReuseFraction * (prevTotalXP - self.totalXP())), truncateXP=truncateXP)
        self._updateRank()

    def validateLearningFreeSkill(self, skillName):
        if 'any' not in self.freeSkills:
            return (False, 'no free skill slots available', False)
        if skillName in self.freeSkills:
            return (False, 'free skill (%s) is already learned' % skillName, False)
        if skillName not in skills_constants.ACTIVE_SKILLS:
            return (False, 'Unknown skill (%s)' % skillName, False)
        if skillName in skills_constants.UNLEARNABLE_SKILLS:
            return (False, 'Skill (%s) cannot be learned' % skillName, False)
        return (False, 'Cannot learn free skill (%s) for this tankman' % skillName, False) if skillName not in COMMON_SKILLS and skillName not in SKILLS_BY_ROLES[self.role] else (True, '', skillName in self.earnedSkills)

    def replaceFreeSkill(self, oldSkillName, newSkillName):
        idx = self._skills.index(oldSkillName)
        if idx > self.freeSkillsNumber - 1:
            raise SoftException('skill is not free')
        self._skills[idx] = newSkillName

    @property
    def skillsEfficiency(self):
        return float(self.skillsEfficiencyXP) / MAX_SKILLS_EFFICIENCY_XP

    def respecialize(self, newVehicleTypeID, newSkillsEfficiency):
        newVehTags = vehicles.g_list.getList(self.nationID)[newVehicleTypeID].tags
        self.skillsEfficiencyXP = int(MAX_SKILLS_EFFICIENCY_XP * newSkillsEfficiency)
        self.vehicleTypeID = newVehicleTypeID
        self.__vehicleTags = newVehTags

    def validatePassport(self, isPremium, isFemale, fnGroupID, firstNameID, lnGroupID, lastNameID, iGroupID, iconID):
        if isFemale is None:
            isFemale = self.isFemale
        config = getNationConfig(self.nationID)
        groups = config.getGroups(isPremium)
        if firstNameID is not None:
            if fnGroupID not in groups:
                return (False, 'Invalid fn group', None)
            group = groups[fnGroupID]
            if group.notInShop:
                return (False, 'Not in shop', None)
            if bool(group.isFemales) != bool(isFemale):
                return (False, 'Invalid group sex', None)
            if firstNameID not in group.firstNames:
                return (False, 'Invalid first name', None)
        if lastNameID is not None:
            if lnGroupID not in groups:
                return (False, 'Invalid ln group', None)
            group = groups[lnGroupID]
            if group.notInShop:
                return (False, 'Not in shop', None)
            if bool(group.isFemales) != bool(isFemale):
                return (False, 'Invalid group sex', None)
            if lastNameID not in group.lastNames:
                return (False, 'Invalid last name', None)
        if iconID is not None:
            if iGroupID not in groups:
                return (False, 'Invalid i group', None)
            group = groups[iGroupID]
            if group.notInShop:
                return (False, 'Not in shop', None)
            if bool(group.isFemales) != bool(isFemale):
                return (False, 'Invalid group sex', None)
            if iconID not in group.icons:
                return (False, 'Invalid icon id', None)
        if firstNameID is None:
            firstNameID = self.firstNameID
        if lastNameID is None:
            lastNameID = self.lastNameID
        if iconID is None:
            iconID = self.iconID
        return (True, '', (isFemale,
          firstNameID,
          lastNameID,
          iconID))

    def replacePassport(self, ctx):
        isFemale, firstNameID, lastNameID, iconID = ctx
        self.isFemale = isFemale
        self.firstNameID = firstNameID
        self.lastNameID = lastNameID
        self.iconID = iconID

    def getPassport(self):
        return (self.nationID,
         self.isPremium,
         self.isFemale,
         self.firstNameID,
         self.lastNameID,
         self.iconID)

    def getRestrictions(self):
        return OperationsRestrictions(getGroupTags(*self.getPassport()))

    @property
    def group(self):
        return int(self.isFemale) | int(self.isPremium) << 1 | int(self.gid) << 2

    @property
    def gid(self):
        if self.__gid is None:
            self.__gid, _ = findGroupsByIDs(getNationGroups(self.nationID, self.isPremium), self.isFemale, self.firstNameID, self.lastNameID, self.iconID)[0]
        return self.__gid

    def makeCompactDescr(self):
        pack = struct.pack
        header = ITEM_TYPES.tankman + (self.nationID << 4)
        cd = pack('B', header)
        flags = TankmanFlags()
        flags.extendedVehicleTypeID = self.vehicleTypeID > 255
        flags.hasFreeSkills = self.freeSkillsNumber > 0
        flags.isFemale = self.isFemale
        flags.isPremium = self.isPremium
        cd += flags.pack()
        fmt = '>H' if flags.extendedVehicleTypeID else 'B'
        cd += pack(fmt, self.vehicleTypeID)
        rs = (SKILL_INDICES[self.role] << 17) + self.skillsEfficiencyXP
        cd += chr(rs >> 16 & 255) + chr(rs >> 8 & 255) + chr(rs & 255)
        numSkills = self.lastSkillNumber
        skills = [ SKILL_INDICES[s] for s in self._skills ]
        cd += pack((str(1 + numSkills) + 'B'), numSkills, *skills)
        cd += chr(self.__lastSkillLevel if numSkills else 0)
        if flags.hasFreeSkills:
            cd += chr(self.freeSkillsNumber)
        cd += pack('>3HI', self.firstNameID, self.lastNameID, self.iconID, self.freeXP)
        cd += self.dossierCompactDescr
        return cd

    def isRestorable(self):
        res = self.freeSkillsNumber > 0 or self.getFullSkillsCount() >= 2
        res &= not ('lockCrew' in self.__vehicleTags and 'unrecoverable' in self.__vehicleTags)
        return res

    def __initFromCompactDescr(self, compactDescr, battleOnly):
        cd = compactDescr
        unpack = struct.unpack
        try:
            header = unpack('B', cd[0])
            nationID = header >> 4 & 15
            nations.NAMES[nationID]
            self.nationID = nationID
            cd = cd[1:]
            flags = TankmanFlags.fromCD(cd)
            self.isPremium = flags.isPremium
            self.isFemale = flags.isFemale
            cd = cd[flags.len:]
            if flags.extendedVehicleTypeID:
                self.vehicleTypeID = unpack('>H', cd[:2])
                cd = cd[2:]
            else:
                self.vehicleTypeID = unpack('B', cd[0])
                cd = cd[1:]
            self.__vehicleTags = vehicles.g_list.getList(nationID)[self.vehicleTypeID].tags
            roleID, xp1, xp2, numSkills = unpack('4B', cd[:4])
            self.role = SKILL_NAMES[roleID >> 1]
            if self.role not in ROLES:
                raise SoftException('Incorrect tankman role', self.role)
            self.skillsEfficiencyXP = ((roleID & 1) << 16) + (xp1 << 8) + xp2
            cd = cd[4:]
            self._skills = []
            if numSkills == 0:
                self.__lastSkillLevel = 0
            else:
                for skillID in unpack(str(numSkills) + 'B', cd[:numSkills]):
                    skillName = SKILL_NAMES[skillID]
                    if skillName not in skills_constants.ACTIVE_FREE_SKILLS:
                        raise SoftException('Incorrect skill name', skillName)
                    self._skills.append(skillName)

                self.__lastSkillLevel = ord(cd[numSkills])
                if self.__lastSkillLevel > MAX_SKILL_LEVEL:
                    raise SoftException('Incorrect last skill level', self.__lastSkillLevel)
            cd = cd[numSkills + 1:]
            self.freeSkillsNumber = 0
            if flags.hasFreeSkills:
                self.freeSkillsNumber = unpack('B', cd[0])
                cd = cd[1:]
            if self.freeSkillsNumber == len(self._skills) and self.freeSkillsNumber > 0:
                self.__lastSkillLevel = MAX_SKILL_LEVEL
            nationConfig = getNationConfig(nationID)
            self.firstNameID, self.lastNameID, self.iconID, self.freeXP = unpack('>3HI', cd[:10].ljust(10, '\x00'))
            cd = cd[10:]
            self.__gid = None
            if battleOnly:
                del self.freeXP
                return
            self.dossierCompactDescr = cd
            if not nationConfig.hasFirstName(self.firstNameID):
                raise SoftException('Incorrect firstNameID', self.firstNameID)
            if not nationConfig.hasLastName(self.lastNameID):
                raise SoftException('Incorrect lastNameID', self.lastNameID)
            if not nationConfig.hasIcon(self.iconID):
                raise SoftException('Incorrect iconID', self.iconID)
            self._updateRank()
        except Exception:
            LOG_ERROR('(compact description to XML mismatch?)', compactDescr)
            raise

        return

    def _updateRank(self):
        lastSkillLevel = self.lastSkillLevel if self.earnedSkillsNumber > 0 else 0
        absLvl = max(0, self.earnedSkillsNumber - 1) * MAX_SKILL_LEVEL + lastSkillLevel
        self._rankIdx = 1 + absLvl / SKILL_LEVELS_PER_RANK
        rr = getNationConfig(self.nationID).getRoleRanks(self.role)
        self.rankID = rr[min(self._rankIdx, len(rr) - 1)]

    def __paramsOnVehicle(self, vehicleType):
        isPremium = 'premium' in vehicleType.tags or 'premiumIGR' in vehicleType.tags
        isSameClass = len(VEHICLE_CLASS_TAGS & vehicleType.tags & self.__vehicleTags)
        return (isPremium, isSameClass)

    def __levelUpLastSkill(self):
        numSkills = self.earnedSkillsNumber
        if numSkills <= 0:
            return
        canLevelUp, newLevel, xpCost = self.__findAffordableLevel(self.__lastSkillLevel, numSkills)
        if canLevelUp:
            self.freeXP -= xpCost
            self.__lastSkillLevel = newLevel
            self._updateRank()

    def __findAffordableLevel(self, currentLevel, skillNum):
        canLevelUp = False
        newLevel = currentLevel
        xpCost = 0
        normXP = _g_levelXpCosts[currentLevel] + (self.freeXP >> skillNum)
        if normXP >= _g_levelXpCosts[MAX_SKILL_LEVEL]:
            canLevelUp = True
            newLevel = MAX_SKILL_LEVEL
            xpCost = _g_levelXpCosts[MAX_SKILL_LEVEL] - _g_levelXpCosts[currentLevel] << skillNum
        else:
            foundLevel = bisectLE(_g_levelXpCosts, normXP, lo=currentLevel, hi=MAX_SKILL_LEVEL)
            if foundLevel > currentLevel:
                canLevelUp = True
                newLevel = foundLevel
                xpCost = _g_levelXpCosts[foundLevel] - _g_levelXpCosts[currentLevel] << skillNum
        return (canLevelUp, newLevel, xpCost)


def makeTmanDescrByTmanData(tmanData):
    nationID = tmanData['nationID']
    if not 0 <= nationID < len(nations.AVAILABLE_NAMES):
        raise SoftException('Invalid nation')
    vehicleTypeID = tmanData['vehicleTypeID']
    if vehicleTypeID not in vehicles.g_list.getList(nationID):
        raise SoftException('Invalid vehicle')
    role = tmanData['role']
    if role not in ROLES:
        raise SoftException('Invalid role')
    lastSkillLevel = tmanData.get('lastSkillLevel', MAX_SKILL_LEVEL)
    skills = tmanData.get('skills', [])
    freeSkills = tmanData.get('freeSkills', [])
    if skills is None:
        skills = []
    if freeSkills is None:
        freeSkills = []
    __validateSkills(skills)
    __validateSkills(freeSkills)
    if not set(skills).isdisjoint(set(freeSkills)):
        raise SoftException('Free skills and skills must be disjoint.')
    if len(freeSkills) > MAX_FREE_SKILLS_SIZE:
        raise SoftException('Free skills count is too big.')
    isFemale = tmanData.get('isFemale', False)
    isPremium = tmanData.get('isPremium', False)
    fnGroupID = tmanData.get('fnGroupID', 0)
    firstNameID = tmanData.get('firstNameID', None)
    lnGroupID = tmanData.get('lnGroupID', 0)
    lastNameID = tmanData.get('lastNameID', None)
    iGroupID = tmanData.get('iGroupID', 0)
    iconID = tmanData.get('iconID', None)
    skillsEfficiencyXP = tmanData.get('skillsEfficiencyXP', MAX_SKILLS_EFFICIENCY_XP)
    groups = getNationConfig(nationID).getGroups(isPremium)
    if fnGroupID not in groups:
        raise SoftException('Invalid group fn ID')
    group = groups[fnGroupID]
    if bool(group.isFemales) != bool(isFemale):
        raise SoftException('Invalid group sex')
    if firstNameID is not None:
        if firstNameID not in group.firstNamesList:
            raise SoftException('firstNameID is not in valid group')
    else:
        firstNameID = random.choice(group.firstNamesList)
    if lnGroupID not in groups:
        raise SoftException('Invalid group ln ID')
    group = groups[lnGroupID]
    if bool(group.isFemales) != bool(isFemale):
        raise SoftException('Invalid group sex')
    if lastNameID is not None:
        if lastNameID not in group.lastNamesList:
            raise SoftException('lastNameID is not in valid group')
    else:
        lastNameID = random.choice(group.lastNamesList)
    if iGroupID not in groups:
        raise SoftException('Invalid group ln ID')
    group = groups[iGroupID]
    if bool(group.isFemales) != bool(isFemale):
        raise SoftException('Invalid group sex')
    if iconID is not None:
        if iconID not in group.iconsList:
            raise SoftException('iconID is not in valid group')
    else:
        iconID = random.choice(group.iconsList)
    passport = (nationID,
     isPremium,
     isFemale,
     firstNameID,
     lastNameID,
     iconID)
    tmanCompDescr = generateCompactDescr(passport, vehicleTypeID, role, skills=skills, lastSkillLevel=lastSkillLevel, freeSkills=freeSkills, initialXP=tmanData.get('freeXP', 0), skillsEfficiencyXP=skillsEfficiencyXP)
    return tmanCompDescr


def isRestorable(tankmanCD):
    tankmanDescr = TankmanDescr(tankmanCD)
    return tankmanDescr.isRestorable()


def ownVehicleHasTags(tankmanCD, tags=()):
    nation, vehTypeID, _ = parseNationSpecAndRole(tankmanCD)
    vehicleType = vehicles.g_cache.vehicle(nation, vehTypeID)
    return bool(vehicleType.tags.intersection(tags))


def hasTagInTankmenGroup(nationID, groupID, isPremium, tag):
    nationGroups = getNationGroups(nationID, isPremium)
    if groupID not in nationGroups:
        LOG_WARNING('tankmen.hasTagInTankmenGroup: wrong value of the groupID (unknown groupID)', groupID)
        return False
    return tag in nationGroups[groupID].tags


def unpackCrewParams(crewGroup):
    groupID = crewGroup >> 2
    isFemale = bool(crewGroup & 1)
    isPremium = bool(crewGroup & 2)
    return (groupID, isFemale, isPremium)


def getCommanderInfo(crewDescrs, crewInvIDs):
    for compDescr, invID in izip(crewDescrs, crewInvIDs):
        crewDescr = TankmanDescr(compDescr, True)
        if crewDescr.role == 'commander':
            return (crewDescr, invID)

    return (None, None)


def getCommanderGroup(crewDescrs):
    commanderDecr, _ = getCommanderInfo(crewDescrs, [None] * len(crewDescrs))
    return getTankmanGroup(commanderDecr)


def getCrewGroups(crewDescrs):
    crewDescrs = sorted([ TankmanDescr(descr, battleOnly=True) for descr, invID in izip(crewDescrs, [None] * len(crewDescrs)) ], key=lambda descr: skills_constants.ORDERED_ROLES.index(descr.role))
    return [ getTankmanGroup(crewDescr) for crewDescr in crewDescrs ]


def getTankmanGroup(tankmanDescr):
    return tankmanDescr.group if tankmanDescr is not None else 0


def getCommanderSkinID(crewDescs, crewIDs, crewSkins):
    commanderDescr, commanderInvID = getCommanderInfo(crewDescs, crewIDs)
    return crewSkins.get(commanderInvID, crew_skins_constants.NO_CREW_SKIN_ID)


def getTankmenWithTag(nationID, isPremium, tag):
    nationGroups = getNationGroups(nationID, isPremium)
    return set([ group.groupID for group in nationGroups.itervalues() if tag in group.tags ])


def getSpecialVoiceTag(tankman, specialSoundCtrl):
    nationGroups = getNationGroups(tankman.nationID, tankman.descriptor.isPremium)
    nationGroup = nationGroups.get(tankman.descriptor.gid)
    if nationGroup is None:
        return
    else:
        for tag in nationGroup.tags:
            if specialSoundCtrl.checkTagForSpecialVoice(tag):
                return tag

        return


def tankmenGroupHasRole(nationID, groupID, isPremium, role):
    nationGroups = getNationGroups(nationID, isPremium)
    if groupID in nationGroups:
        return role in nationGroups[groupID].roles
    else:
        return False


def tankmenGroupCanChangeRole(nationID, groupID, isPremium):
    nationGroups = getNationGroups(nationID, isPremium)
    if groupID in nationGroups:
        return len(nationGroups[groupID].roles) > 1
    else:
        return True


def getNationGroups(nationID, isPremium):
    return getNationConfig(nationID).getGroups(isPremium)


def findGroupsByIDs(groups, isFemale, firstNameID, secondNameID, iconID):
    found = [(-1, 0)]
    for groupID, group in groups.iteritems():
        if isFemale != group.isFemales:
            continue
        overlap = 0
        if firstNameID in group.firstNames:
            overlap += 1
        if secondNameID in group.lastNames:
            overlap += 1
        if iconID in group.icons:
            overlap += 1
        if overlap:
            found.append((groupID, overlap))

    found.sort(key=lambda item: item[1], reverse=True)
    return found


def getGroupTags(nationID, isPremium, isFemale, firstNameID, secondNameID, iconID):
    groups = getNationGroups(nationID, isPremium)
    found = findGroupsByIDs(groups, isFemale, firstNameID, secondNameID, iconID)
    if found:
        groupID, overlap = found[0]
        if overlap == 3:
            return groups[groupID].tags
    return frozenset()


def __validateSkills(skills):
    if len(set(skills)) != len(skills):
        raise SoftException('Duplicate tankman skills')
    for skill in skills:
        if skill not in SKILL_INDICES:
            raise SoftException('Wrong tankman skill')


_g_skillsConfig = None
_g_loreConfig = None
_g_crewSkinsConfig = None
_g_nationsConfig = [ None for x in xrange(len(nations.NAMES)) ]
_g_tankmenGroupNames = None

def _makeLevelXpCosts():
    costs = [0] * (MAX_SKILL_LEVEL + 1)
    prevCost = 0
    for level in xrange(1, len(costs)):
        prevCost += int(round(_LEVELUP_K1 * pow(_LEVELUP_K2, float(level - 1) / MAX_SKILL_LEVEL)))
        costs[level] = prevCost

    return costs


_g_levelXpCosts = _makeLevelXpCosts()

def _makeSkillXpCosts():
    costs = [0] * len(SKILL_NAMES)
    for level in xrange(1, len(costs)):
        costs[level] = 2 * (2 ** level - 1) * _g_levelXpCosts[MAX_SKILL_LEVEL]

    return costs


_g_skillXpCosts = _makeSkillXpCosts()
_g_totalFirstSkillXpCost = _g_skillXpCosts[1]

def getRecruitInfoFromToken(tokenName):
    parts = tokenName.split(':')
    if len(parts) != RECRUIT_TMAN_TOKEN_TOTAL_PARTS:
        return None
    elif parts[0] != RECRUIT_TMAN_TOKEN_PREFIX:
        return None
    else:
        try:
            result = {'nations': [],
             'isPremium': False,
             'group': '',
             'freeSkills': [],
             'skills': [],
             'freeXP': 0,
             'lastSkillLevel': MAX_SKILL_LEVEL,
             'roleLevel': MAX_SKILL_LEVEL,
             'sourceID': '',
             'roles': []}
            if parts[1] == '':
                result['nations'] = nations.INDICES.values()
            else:
                nationNames = parts[1].split('!')
                if len(nationNames) != len(set(nationNames)):
                    raise SoftException('nation duplicates')
                for nation in nationNames:
                    if nation not in nations.AVAILABLE_NAMES:
                        raise SoftException('unknown nation name "{}"'.format(nation))
                    result['nations'].append(nations.INDICES[nation])

            if parts[2] == '' or parts[2] == 'true':
                result['isPremium'] = True
            elif parts[2] != 'false':
                raise SoftException('wrong "isPremium" value "{}"'.format(tokenName, parts[2]))
            for nation in result['nations']:
                if len(filter(lambda g: g.name == parts[3], getNationGroups(nation, result['isPremium']).itervalues())) != 1:
                    raise SoftException('wrong group name')

            result['group'] = parts[3]
            if parts[4] != '':
                freeXP = int(parts[4])
                if freeXP < 0 or freeXP > _MAX_FREE_XP:
                    raise SoftException('XP out of bounds')
                result['freeXP'] = freeXP
            earnedSkillsSet = set()
            if parts[5] != '':
                skills = parts[5].split('!')
                if len(skills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    raise SoftException('too many earned skills')
                earnedSkillsSet = set(skills)
                if len(skills) != len(earnedSkillsSet):
                    raise SoftException('earned skills are duplicated')
                for skill in skills:
                    if skill not in skills_constants.ACTIVE_SKILLS:
                        raise SoftException('earned skill "{}" is not active'.format(skill))
                    result['skills'].append(skill)

            if parts[6] != '':
                lastSkillLevel = int(parts[6])
                if lastSkillLevel < 0 or lastSkillLevel > MAX_SKILL_LEVEL:
                    raise SoftException('lastSkillLevel out of bounds')
                result['lastSkillLevel'] = lastSkillLevel
            freeSkillsSet = set()
            if parts[7] != '':
                freeSkills = parts[7].split('!')
                if len(freeSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    raise SoftException('too many free skills')
                chosenFreeSkills = [ s for s in freeSkills if s != 'any' ]
                freeSkillsSet = set(chosenFreeSkills)
                if len(chosenFreeSkills) != len(freeSkillsSet):
                    raise SoftException('free skills are duplicated')
                for skill in freeSkills:
                    if skill not in skills_constants.ACTIVE_FREE_SKILLS:
                        raise SoftException('free skill "{}" is not active'.format(skill))
                    result['freeSkills'].append(skill)

            if len(earnedSkillsSet) + len(freeSkillsSet) != len(earnedSkillsSet | freeSkillsSet):
                raise SoftException('free and earned skills are duplicated')
            if parts[8] != '':
                roleLevel = int(parts[8])
                if roleLevel < MIN_ROLE_LEVEL or roleLevel > MAX_SKILL_LEVEL:
                    raise SoftException('roleLevel out of bounds')
                result['roleLevel'] = roleLevel
            sourceID = parts[9]
            if sourceID == '':
                raise SoftException('empty sourceID')
            result['sourceID'] = sourceID
            if parts[10] != '':
                roles = parts[10].split('!')
                if len(roles) != len(set(roles)):
                    raise SoftException('roles are duplicated')
                for role in roles:
                    if role not in skills_constants.ROLES:
                        raise SoftException('unknown role name "{}"'.format(role))
                    result['roles'].append(SKILL_INDICES[role])

        except (ValueError, SoftException) as e:
            LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: {}'.format(tokenName, e))
            return None

        return result


def generateRecruitToken(group, sourceID, nationList=(), isPremium=True, freeXP=0, skills=(), lastSkillLevel=MAX_SKILL_LEVEL, freeSkills=(), roleLevel=MAX_SKILL_LEVEL, roles=()):
    tokenParts = [RECRUIT_TMAN_TOKEN_PREFIX]
    selectedNations = []
    if len(nationList) == 0:
        selectedNations = set(nations.AVAILABLE_NAMES)
    else:
        for nation in nationList:
            if nation not in nations.AVAILABLE_NAMES:
                return None
            selectedNations.append(nation)

    if len(selectedNations) == len(nations.AVAILABLE_NAMES):
        tokenParts.append('')
    else:
        tokenParts.append('!'.join(selectedNations))
    tokenParts.append('' if isPremium else 'false')
    for nation in selectedNations:
        if len(filter(lambda g: g.name == group, getNationGroups(nations.INDICES[nation], isPremium).itervalues())) != 1:
            return None

    tokenParts.append(group)
    if freeXP < 0 or freeXP > _MAX_FREE_XP:
        return None
    else:
        tokenParts.append('' if freeXP == 0 else str(freeXP))
        selectedSkills = []
        for skill in skills:
            if skill not in skills_constants.ACTIVE_SKILLS:
                return None
            selectedSkills.append(skill)

        if len(selectedSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
            return None
        tokenParts.append('!'.join(selectedSkills))
        if lastSkillLevel < 0 or lastSkillLevel > MAX_SKILL_LEVEL:
            return None
        tokenParts.append('' if lastSkillLevel == MAX_SKILL_LEVEL else str(lastSkillLevel))
        selectedFreeSkills = []
        for skill in freeSkills:
            if skill not in skills_constants.ACTIVE_FREE_SKILLS:
                return None
            selectedFreeSkills.append(skill)

        if len(selectedFreeSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
            return None
        tokenParts.append('!'.join(selectedFreeSkills))
        if roleLevel < MIN_ROLE_LEVEL or roleLevel > MAX_SKILL_LEVEL:
            return None
        tokenParts.append('' if roleLevel == MAX_SKILL_LEVEL else str(roleLevel))
        tokenParts.append(sourceID)
        selectedRecruitRoles = []
        for recruitRole in roles:
            if recruitRole not in skills_constants.ROLES:
                return None
            selectedRecruitRoles.append(recruitRole)

        tokenParts.append('!'.join(selectedRecruitRoles))
        return ':'.join(tokenParts)


def getTokenFromRecruitInfo(recruit):
    return generateRecruitToken(group=recruit['group'], sourceID=recruit['sourceID'], nationList=[ nations.NAMES[nationID] for nationID in recruit['nations'] ], isPremium=recruit['isPremium'], freeXP=recruit['freeXP'], skills=recruit['skills'], lastSkillLevel=recruit['lastSkillLevel'], freeSkills=recruit['freeSkills'], roleLevel=recruit['roleLevel'], roles=[ skills_constants.SKILL_NAMES[roleID] for roleID in recruit['roles'] ])


def validateCrewToLearnCrewBook(crew, vehTypeCompDescr):
    resultMask = crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.EMPTY_MASK
    resultMsg = ''
    crewLists = {mask:[] for mask in crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ALL}
    if None in crew:
        resultMsg += 'Vehicle has not full crew; '
        resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW
    _, _, vehicleID = vehicles.parseIntCompactDescr(vehTypeCompDescr)
    for slotID, tmanDescr in enumerate(crew):
        if tmanDescr is None:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW:
                resultMsg += 'Vehicle has not full crew; '
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW
            continue
        if tmanDescr.roleLevel < MAX_SKILL_LEVEL:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL:
                resultMsg += 'One of crew members has not enough level of specialization; '
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL
            crewLists[crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.ROLE_LEVEL].append(slotID)
        if vehicleID != tmanDescr.vehicleTypeID:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION:
                resultMsg += 'One of crew members has specialization not compatible with current vehicle;'
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION
            crewLists[crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.SPECIALIZATION].append(slotID)

    return (resultMask == 0,
     resultMask,
     resultMsg,
     crewLists)


def getTankmanDeviceNameByIdxInCrew(idxInCrew, vehicle):
    crewRoles = vehicle.typeDescriptor.type.crewRoles
    targetRole = crewRoles[idxInCrew][0]
    idxInRole = 0
    for i, tankmanRoles in enumerate(crewRoles):
        if i != idxInCrew:
            if tankmanRoles[0] == targetRole:
                idxInRole += 1
            continue
        return vehicles.DEVICE_TANKMAN_NAMES_TO_VEHICLE_EXTRA_NAMES[targetRole][idxInRole]

    raise SoftException('Did not find device name by tankman index {} in vehicle {}'.format(idxInCrew, vehicle.typeDescriptor.type.name))


def _getItemByCompactDescr(compactDescr):
    itemTypeID, nationID, compTypeID = parseIntCompactDescr(compactDescr)
    items = None
    if itemTypeID == ITEM_TYPES.crewSkin:
        items = g_cache.crewSkins().skins
    elif itemTypeID == ITEM_TYPES.crewBook:
        items = g_cache.crewBooks().books
    return items[compTypeID]


def getItemByCompactDescr(compactDescr):
    try:
        return _getItemByCompactDescr(compactDescr)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_ERROR('(compact description to XML mismatch?)', compactDescr)
        raise


def isItemWithCompactDescrExist(compactDescr):
    try:
        return _getItemByCompactDescr(compactDescr) is not None
    except Exception:
        return False

    return None


class Cache(object):
    __slots__ = ('__crewSkins', '__crewBooks')

    def __init__(self):
        self.__crewSkins = None
        self.__crewBooks = None
        return

    def initCrewSkins(self, pricesCache):
        if self.__crewSkins is None:
            self.__crewSkins = CrewSkinsCache()
            readCrewSkinsCacheFromXML(pricesCache, self.__crewSkins, _CREW_SKINS_XML_PATH)
        return

    def initCrewBooks(self, pricesCache):
        if self.__crewBooks is None:
            self.__crewBooks = CrewBooksCache()
            readCrewBooksCacheFromXML(pricesCache, self.__crewBooks, _CREW_BOOKS_XML_PATH)
        return

    def crewSkins(self):
        return self.__crewSkins

    def crewBooks(self):
        return self.__crewBooks


def getSkillRoleType(skillName):
    if skillName in COMMON_SKILLS:
        return COMMON_SKILL_ROLE_TYPE
    else:
        for role, skills in SKILLS_BY_ROLES.iteritems():
            if skillName in skills:
                return role

        return None


def compareMastery(tankmanDescr1, tankmanDescr2):
    if tankmanDescr1.skillsEfficiencyXP < MAX_SKILLS_EFFICIENCY_XP or tankmanDescr2.skillsEfficiencyXP < MAX_SKILLS_EFFICIENCY_XP:
        return cmp(tankmanDescr1.skillsEfficiencyXP, tankmanDescr2.skillsEfficiencyXP)
    else:
        return cmp(tankmanDescr1.totalXP(), tankmanDescr2.totalXP())
