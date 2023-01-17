# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/tankmen.py
import random
import struct
from functools import partial
from itertools import izip
from typing import List, Dict, Any, Tuple, Optional, Union
import nations
from items import vehicles, ITEM_TYPES, parseIntCompactDescr, ITEM_ID_RANGES
from items.components import skills_components, crew_skins_constants, crew_books_constants
from items.components import skills_constants
from items.components import tankmen_components
from items.components import component_constants
from items.components.crew_skins_components import CrewSkinsCache
from items.components.crew_books_components import CrewBooksCache
from items.readers import skills_readers
from items.readers import tankmen_readers
from items.readers.crewSkins_readers import readCrewSkinsCacheFromXML
from items.readers.crewBooks_readers import readCrewBooksCacheFromXML
from items.passports import PassportCache, passport_generator, maxAttempts, distinctFrom, acceptOn
from vehicles import VEHICLE_CLASS_TAGS, EXTENDED_VEHICLE_TYPE_ID_FLAG
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG_DEV
from constants import ITEM_DEFS_PATH, IS_CLIENT
from account_shared import AmmoIterator
from soft_exception import SoftException
SKILL_NAMES = skills_constants.SKILL_NAMES
SKILL_INDICES = skills_constants.SKILL_INDICES
ROLES = skills_constants.ROLES
COMMON_SKILLS = skills_constants.COMMON_SKILLS
ROLES_AND_COMMON_SKILLS = skills_constants.ROLES_AND_COMMON_SKILLS
SKILLS_BY_ROLES = skills_constants.SKILLS_BY_ROLES
PERKS = skills_constants.PERKS
MAX_FREE_SKILLS_SIZE = 16
MAX_SKILL_LEVEL = 100
MIN_ROLE_LEVEL = 50
SKILL_LEVELS_PER_RANK = 50
COMMANDER_ADDITION_RATIO = 10
_MAX_FREE_XP = 4000000000L
_LEVELUP_K1 = 50.0
_LEVELUP_K2 = 100.0
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


def getSkillsMask(skills):
    result = 0
    for skill in skills:
        result |= 1 << SKILL_INDICES[skill]

    return result


ALL_SKILLS_MASK = getSkillsMask([ skill for skill in SKILL_NAMES if skill != 'reserved' ])

def getNationConfig(nationID):
    global _g_nationsConfig
    if _g_nationsConfig[nationID] is None:
        nationName = nations.NAMES[nationID]
        if nationName not in nations.AVAILABLE_NAMES:
            _g_nationsConfig[nationID] = tankmen_components.NationConfig('stub')
        else:
            _g_nationsConfig[nationID] = tankmen_readers.readNationConfig(ITEM_DEFS_PATH + 'tankmen/' + nationName + '.xml')
    return _g_nationsConfig[nationID]


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
    skills = []
    if skillsMask != 0:
        tankmanSkills = set()
        for i in xrange(len(role)):
            roleSkills = SKILLS_BY_ROLES[role[i]]
            if skillsMask == ALL_SKILLS_MASK:
                tankmanSkills.update(roleSkills)
            for skill, idx in SKILL_INDICES.iteritems():
                if 1 << idx & skillsMask and skill in roleSkills:
                    tankmanSkills.add(skill)

        skills.extend(tankmanSkills)
    return skills


def generateTankmen(nationID, vehicleTypeID, roles, isPremium, roleLevel, skillsMask, isPreview=False):
    tankmenList = []
    prevPassports = PassportCache()
    for i in xrange(len(roles)):
        role = roles[i]
        pg = passport_generator(nationID, isPremium, partial(crewMemberPreviewProducer, vehicleTypeID=vehicleTypeID, role=role[0]) if isPreview else passportProducer, maxAttempts(10), distinctFrom(prevPassports), acceptOn('roles', role[0]))
        passport = next(pg)
        prevPassports.append(passport)
        skills = generateSkills(role, skillsMask)
        tmanCompDescr = generateCompactDescr(passport, vehicleTypeID, role[0], roleLevel, skills)
        tankmenList.append(tmanCompDescr)

    return tankmenList if len(tankmenList) == len(roles) else []


def generateCompactDescr(passport, vehicleTypeID, role, roleLevel, skills=(), lastSkillLevel=MAX_SKILL_LEVEL, dossierCompactDescr='', freeSkills=()):
    pack = struct.pack
    nationID, isPremium, isFemale, firstNameID, lastNameID, iconID = passport
    header = ITEM_TYPES.tankman + (nationID << 4)
    ext = vehicleTypeID >> 8
    header += EXTENDED_VEHICLE_TYPE_ID_FLAG if ext else 0
    cd = pack('2B', header, vehicleTypeID & 255)
    cd += chr(ext) if ext else ''
    cd += pack('2B', SKILL_INDICES[role], roleLevel)
    numSkills = len(skills) + len(freeSkills)
    allSkills = [ SKILL_INDICES[s] for s in freeSkills ]
    for s in skills:
        allSkills.append(SKILL_INDICES[s])

    cd += pack((str(1 + numSkills) + 'B'), numSkills, *allSkills)
    cd += chr(lastSkillLevel if numSkills else 0)
    totalLevel = roleLevel - MIN_ROLE_LEVEL
    if skills:
        totalLevel += (len(skills) - 1) * MAX_SKILL_LEVEL
        totalLevel += lastSkillLevel
    rank, levelsToNextRank = divmod(totalLevel, SKILL_LEVELS_PER_RANK)
    levelsToNextRank = SKILL_LEVELS_PER_RANK - levelsToNextRank
    rankIDs = getNationConfig(nationID).getRoleRanks(role)
    maxRankIdx = len(rankIDs) - 1
    rank = min(rank, maxRankIdx)
    if rank == maxRankIdx:
        levelsToNextRank = 0
    isFemale = 1 if isFemale else 0
    isPremium = 1 if isPremium else 0
    flags = isFemale | isPremium << 1 | len(freeSkills) << 2
    cd += pack('<B4HI', flags, firstNameID, lastNameID, iconID, rank | levelsToNextRank << 5, 0)
    cd += dossierCompactDescr
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
    vehTypeOffset = 1 if ord(compactDescr[0]) & EXTENDED_VEHICLE_TYPE_ID_FLAG else 0
    return compactDescr[:6 + vehTypeOffset + ord(compactDescr[4 + vehTypeOffset]) + 1 + 6]


def parseNationSpecAndRole(compactDescr):
    vehicleTypeID = ord(compactDescr[1])
    if ord(compactDescr[0]) & EXTENDED_VEHICLE_TYPE_ID_FLAG:
        vehicleTypeID += ord(compactDescr[2]) << 8
        roleID = ord(compactDescr[3])
    else:
        roleID = ord(compactDescr[2])
    return (ord(compactDescr[0]) >> 4 & 15, vehicleTypeID, roleID)


def compareMastery(tankmanDescr1, tankmanDescr2):
    return cmp(tankmanDescr1.totalXP(), tankmanDescr2.totalXP())


def commanderTutorXpBonusFactorForCrew(crew, ammo):
    tutorLevel = component_constants.ZERO_FLOAT
    haveBrotherhood = True
    for t in crew:
        if t.role == 'commander':
            tutorLevel = t.skillLevel('commander_tutor')
            if not tutorLevel:
                return component_constants.ZERO_FLOAT
        if t.skillLevel('brotherhood') != MAX_SKILL_LEVEL:
            haveBrotherhood = False

    skillsConfig = getSkillsConfig()
    if haveBrotherhood:
        tutorLevel += skillsConfig.getSkill('brotherhood').crewLevelIncrease
    equipCrewLevelIncrease = component_constants.ZERO_FLOAT
    cache = vehicles.g_cache
    for compDescr, count in AmmoIterator(ammo):
        itemTypeIdx, _, itemIdx = vehicles.parseIntCompactDescr(compDescr)
        if itemTypeIdx == ITEM_TYPES.equipment:
            equipCrewLevelIncrease += getattr(cache.equipments()[itemIdx], 'crewLevelIncrease', component_constants.ZERO_FLOAT)

    tutorLevel += equipCrewLevelIncrease
    return tutorLevel * skillsConfig.getSkill('commander_tutor').xpBonusFactorPerLevel


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
    def tags(self):
        return getNationConfig(self.nationID).getGroups(self.isPremium)[self.gid].tags

    @property
    def skills(self):
        return list(self.__skills)

    @property
    def freeSkills(self):
        return list(self.__skills[:self.freeSkillsNumber])

    @property
    def earnedSkills(self):
        return list(self.__skills[self.freeSkillsNumber:])

    @property
    def lastSkillLevel(self):
        return self.__lastSkillLevel

    @property
    def lastSkillNumber(self):
        return len(self.__skills)

    @property
    def skillLevels(self):
        for skillName in self.__skills:
            level = MAX_SKILL_LEVEL if skillName != self.__skills[-1] else self.__lastSkillLevel
            yield (skillName, level)

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

    def efficiencyFactorOnVehicle(self, vehicleDescrType):
        _, _, vehicleTypeID = vehicles.parseIntCompactDescr(vehicleDescrType.compactDescr)
        factor = 1.0
        if vehicleTypeID != self.vehicleTypeID:
            isPremium, isSameClass = self.__paramsOnVehicle(vehicleDescrType)
            if isSameClass:
                factor = 1.0 if isPremium else 0.75
            else:
                factor = 0.75 if isPremium else 0.5
        return factor

    def efficiencyOnVehicle(self, vehicleDescr):
        _, nationID, _ = vehicles.parseIntCompactDescr(vehicleDescr.type.compactDescr)
        factor = self.efficiencyFactorOnVehicle(vehicleDescr.type)
        addition = vehicleDescr.miscAttrs['crewLevelIncrease']
        return (factor, addition)

    def getBattleXpGainFactor(self, vehicleType, tankmanHasSurvived, commanderTutorXpBonusFactor):
        factor = 1.0
        nationID, vehicleTypeID = vehicleType.id
        if vehicleTypeID != self.vehicleTypeID:
            isPremium, isSameClass = self.__paramsOnVehicle(vehicleType)
            if isPremium:
                factor *= 1.0 if isSameClass else 0.5
            else:
                factor *= 0.5 if isSameClass else 0.25
        factor *= vehicleType.crewXpFactor
        if not tankmanHasSurvived:
            factor *= 0.9
        if self.role != 'commander':
            factor *= 1.0 + commanderTutorXpBonusFactor
        return factor

    @staticmethod
    def levelUpXpCost(fromSkillLevel, skillSeqNum):
        costs = _g_levelXpCosts
        return 2 ** skillSeqNum * (costs[fromSkillLevel + 1] - costs[fromSkillLevel])

    def skillLevel(self, skillName):
        if skillName not in self.skills:
            return None
        else:
            return MAX_SKILL_LEVEL if skillName != self.__skills[-1] else self.__lastSkillLevel

    def totalXP(self):
        levelCosts = _g_levelXpCosts
        xp = self.freeXP + levelCosts[self.roleLevel]
        numSkills = self.lastSkillNumber - self.freeSkillsNumber
        if numSkills:
            xp += levelCosts[self.__lastSkillLevel] * 2 ** numSkills
            for idx in xrange(1, numSkills):
                xp += levelCosts[MAX_SKILL_LEVEL] * 2 ** idx

        return xp

    def addXP(self, xp, truncateXP=True):
        self.freeXP = self.freeXP + xp
        if truncateXP:
            self.truncateXP()
        while self.roleLevel < MAX_SKILL_LEVEL:
            xpCost = self.levelUpXpCost(self.roleLevel, 0)
            if xpCost > self.freeXP:
                break
            self.freeXP -= xpCost
            self.roleLevel += 1
            self.__updateRankAtSkillLevelUp()

        if self.roleLevel == MAX_SKILL_LEVEL:
            self.__levelUpLastSkill()

    def checkRestrictionsByVehicleTags(self):
        if 'lockCrewSkills' in self.__vehicleTags:
            raise SoftException('Changing tankmans skills is forbidden for current vehicle.')

    def addSkill(self, skillName):
        if skillName in self.skills:
            raise SoftException('Skill already leaned (%s)' % skillName)
        if skillName not in skills_constants.ACTIVE_SKILLS:
            raise SoftException('Unknown skill (%s)' % skillName)
        if skillName in skills_constants.UNLEARNABLE_SKILLS:
            raise SoftException('Skill (%s) cannot be learned' % skillName)
        if self.role != 'commander' and skillName in skills_constants.COMMANDER_SKILLS:
            raise SoftException('Cannot learn commander skill (%s) for another role (%s)' % (skillName, self.role))
        if self.roleLevel != MAX_SKILL_LEVEL:
            raise SoftException('Main role not fully leaned (%d)' % self.roleLevel)
        if self.__skills and self.__lastSkillLevel != MAX_SKILL_LEVEL:
            raise SoftException('Last skill not fully leaned (%d)' % self.__lastSkillLevel)
        self.__skills.append(skillName)
        self.__lastSkillLevel = 0
        self.__levelUpLastSkill()

    def truncateXP(self):
        self.freeXP = min(_MAX_FREE_XP, self.freeXP)

    def isFreeDropSkills(self):
        if self.lastSkillNumber < 1 + self.freeSkillsNumber:
            return True
        return True if self.lastSkillNumber == 1 + self.freeSkillsNumber and self.__lastSkillLevel == 0 else False

    def dropSkills(self, xpReuseFraction=0.0, throwIfNoChange=True, truncateXP=True):
        if len(self.__skills) == 0:
            if throwIfNoChange:
                raise SoftException('attempt to reset empty skills')
            return
        prevTotalXP = self.totalXP()
        if self.numLevelsToNextRank != 0:
            numSkills = self.lastSkillNumber - self.freeSkillsNumber
            if numSkills < 1:
                if throwIfNoChange:
                    raise SoftException('attempt to reset free skills')
                return
            self.numLevelsToNextRank += self.__lastSkillLevel
            if numSkills > 1:
                self.numLevelsToNextRank += MAX_SKILL_LEVEL * (numSkills - 1)
        del self.__skills[self.freeSkillsNumber:]
        if self.freeSkillsNumber:
            self.__lastSkillLevel = MAX_SKILL_LEVEL
        else:
            self.__lastSkillLevel = 0
        if xpReuseFraction != 0.0:
            self.addXP(int(xpReuseFraction * (prevTotalXP - self.totalXP())), truncateXP=truncateXP)

    def dropSkill(self, skillName, xpReuseFraction=0.0):
        idx = self.__skills.index(skillName)
        prevTotalXP = self.totalXP()
        numSkills = self.lastSkillNumber - self.freeSkillsNumber
        levelsDropped = MAX_SKILL_LEVEL
        if numSkills == 1:
            levelsDropped = self.__lastSkillLevel
            self.__lastSkillLevel = 0
        elif idx + 1 == numSkills:
            levelsDropped = self.__lastSkillLevel
            self.__lastSkillLevel = MAX_SKILL_LEVEL
        del self.__skills[idx]
        if self.numLevelsToNextRank != 0:
            self.numLevelsToNextRank += levelsDropped
        if xpReuseFraction != 0.0:
            self.addXP(int(xpReuseFraction * (prevTotalXP - self.totalXP())))

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
        idx = self.__skills.index(oldSkillName)
        if idx > self.freeSkillsNumber - 1:
            raise SoftException('skill is not free')
        self.__skills[idx] = newSkillName

    def respecialize(self, newVehicleTypeID, minNewRoleLevel, vehicleChangeRoleLevelLoss, classChangeRoleLevelLoss, becomesPremium):
        newVehTags = vehicles.g_list.getList(self.nationID)[newVehicleTypeID].tags
        roleLevelLoss = 0.0 if newVehicleTypeID == self.vehicleTypeID else vehicleChangeRoleLevelLoss
        isSameClass = len(self.__vehicleTags & newVehTags & vehicles.VEHICLE_CLASS_TAGS)
        if not isSameClass:
            roleLevelLoss += classChangeRoleLevelLoss
        newRoleLevel = int(round(self.roleLevel * (1.0 - roleLevelLoss)))
        newRoleLevel = max(minNewRoleLevel, newRoleLevel)
        self.vehicleTypeID = newVehicleTypeID
        self.__vehicleTags = newVehTags
        if newRoleLevel > self.roleLevel:
            self.__updateRankAtSkillLevelUp(newRoleLevel - self.roleLevel)
            self.roleLevel = newRoleLevel
        elif newRoleLevel < self.roleLevel:
            if self.numLevelsToNextRank != 0:
                self.numLevelsToNextRank += self.roleLevel - newRoleLevel
            self.roleLevel = newRoleLevel
            self.addXP(0)

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
            g = getNationConfig(self.nationID).getGroupByLastName(self.lastNameID)
            if g and self.firstNameID in g.firstNames and self.iconID in g.icons:
                self.__gid = g.groupID
            elif g and self.iconID not in g.icons and self.nationID == 5 and self.iconID in (3001, 3002, 3003, 3004):
                self.__gid = g.groupID
            else:
                self.__gid, _ = findGroupsByIDs(getNationGroups(self.nationID, self.isPremium), self.isFemale, self.firstNameID, self.lastNameID, self.iconID)[0]
        return self.__gid

    def makeCompactDescr(self):
        pack = struct.pack
        header = ITEM_TYPES.tankman + (self.nationID << 4)
        ext = self.vehicleTypeID >> 8
        header += EXTENDED_VEHICLE_TYPE_ID_FLAG if ext else 0
        cd = pack('2B', header, self.vehicleTypeID & 255)
        cd += chr(self.vehicleTypeID >> 8) if ext else ''
        cd += pack('2B', SKILL_INDICES[self.role], self.roleLevel)
        numSkills = self.lastSkillNumber
        skills = [ SKILL_INDICES[s] for s in self.__skills ]
        cd += pack((str(1 + numSkills) + 'B'), numSkills, *skills)
        cd += chr(self.__lastSkillLevel if numSkills else 0)
        isFemale = 1 if self.isFemale else 0
        isPremium = 1 if self.isPremium else 0
        flags = isFemale | isPremium << 1 | self.freeSkillsNumber << 2
        cd += pack('<B4HI', flags, self.firstNameID, self.lastNameID, self.iconID, self.__rankIdx & 31 | (self.numLevelsToNextRank & 2047) << 5, self.freeXP)
        cd += self.dossierCompactDescr
        return cd

    def isRestorable(self):
        vehicleTags = self.__vehicleTags
        return (len(self.skills) > 0 and self.skillLevel(self.skills[0]) == MAX_SKILL_LEVEL or self.roleLevel == MAX_SKILL_LEVEL and self.freeXP >= _g_totalFirstSkillXpCost) and not ('lockCrew' in vehicleTags and 'unrecoverable' in vehicleTags)

    def __initFromCompactDescr(self, compactDescr, battleOnly):
        cd = compactDescr
        unpack = struct.unpack
        try:
            header, self.vehicleTypeID = unpack('2B', cd[:2])
            is_ext = ord(cd[0]) & EXTENDED_VEHICLE_TYPE_ID_FLAG
            cd = cd[2:]
            self.vehicleTypeID += ord(cd[0]) << 8 if is_ext else 0
            cd = cd[1:] if is_ext else cd
            roleID, self.roleLevel, numSkills = unpack('3B', cd[:3])
            cd = cd[3:]
            nationID = header >> 4 & 15
            nations.NAMES[nationID]
            self.nationID = nationID
            self.__vehicleTags = vehicles.g_list.getList(nationID)[self.vehicleTypeID].tags
            self.role = SKILL_NAMES[roleID]
            if self.role not in ROLES:
                raise SoftException('Incorrect tankman role', self.role)
            if self.roleLevel > MAX_SKILL_LEVEL:
                raise SoftException('Incorrect role level', self.roleLevel)
            self.__skills = []
            if numSkills == 0:
                self.__lastSkillLevel = 0
            else:
                for skillID in unpack(str(numSkills) + 'B', cd[:numSkills]):
                    skillName = SKILL_NAMES[skillID]
                    if skillName not in skills_constants.ACTIVE_FREE_SKILLS:
                        raise SoftException('Incorrect skill name', skillName)
                    self.__skills.append(skillName)

                self.__lastSkillLevel = ord(cd[numSkills])
                if self.__lastSkillLevel > MAX_SKILL_LEVEL:
                    raise SoftException('Incorrect last skill level', self.__lastSkillLevel)
            cd = cd[numSkills + 1:]
            flags = unpack('<B', cd[:1])[0]
            self.isFemale = bool(flags & 1)
            self.isPremium = bool(flags & 2)
            self.freeSkillsNumber = flags >> 2
            if self.freeSkillsNumber == len(self.__skills) and self.freeSkillsNumber:
                self.__lastSkillLevel = MAX_SKILL_LEVEL
            cd = cd[1:]
            nationConfig = getNationConfig(nationID)
            self.firstNameID, self.lastNameID, self.iconID, rank, self.freeXP = unpack('<4HI', cd[:12].ljust(12, '\x00'))
            self.__gid = None
            if battleOnly:
                del self.freeXP
                return
            cd = cd[12:]
            self.dossierCompactDescr = cd
            self.__rankIdx = rank & 31
            self.numLevelsToNextRank = rank >> 5
            self.rankID = nationConfig.getRoleRanks(self.role)[self.__rankIdx]
            if not nationConfig.hasFirstName(self.firstNameID):
                raise SoftException('Incorrect firstNameID', self.firstNameID)
            if not nationConfig.hasLastName(self.lastNameID):
                raise SoftException('Incorrect lastNameID', self.lastNameID)
            if not nationConfig.hasIcon(self.iconID):
                raise SoftException('Incorrect iconID', self.iconID)
        except Exception:
            LOG_ERROR('(compact description to XML mismatch?)', compactDescr)
            raise

        return

    def __paramsOnVehicle(self, vehicleType):
        isPremium = 'premium' in vehicleType.tags or 'premiumIGR' in vehicleType.tags
        isSameClass = len(VEHICLE_CLASS_TAGS & vehicleType.tags & self.__vehicleTags)
        return (isPremium, isSameClass)

    def __updateRankAtSkillLevelUp(self, numLevels=1):
        if numLevels < self.numLevelsToNextRank:
            self.numLevelsToNextRank -= numLevels
            return
        rankIDs = getNationConfig(self.nationID).getRoleRanks(self.role)
        maxRankIdx = len(rankIDs) - 1
        while numLevels >= self.numLevelsToNextRank > 0:
            numLevels -= self.numLevelsToNextRank
            self.__rankIdx = min(self.__rankIdx + 1, maxRankIdx)
            self.rankID = rankIDs[self.__rankIdx]
            self.numLevelsToNextRank = SKILL_LEVELS_PER_RANK if self.__rankIdx < maxRankIdx else 0

    def __levelUpLastSkill(self):
        numSkills = self.lastSkillNumber - self.freeSkillsNumber
        if numSkills <= 0:
            return
        while self.__lastSkillLevel < MAX_SKILL_LEVEL:
            xpCost = self.levelUpXpCost(self.__lastSkillLevel, numSkills)
            if xpCost > self.freeXP:
                break
            self.freeXP -= xpCost
            self.__lastSkillLevel += 1
            self.__updateRankAtSkillLevelUp()


class NoneGroupSelection(object):

    def matches(self, tankmanDescr):
        return False


class TankmanGroupSelection(NoneGroupSelection):
    ANY = ('', '*')
    PTYPE = {'premium': True,
     'normal': False}

    def __init__(self, ns=(), premiumFlags=None, gid=(), tags=()):
        self.__nations = {nations.INDICES[n] for n in ns} if ns else nations.INDICES.values()
        self.__tags = frozenset(tags)
        self.__premiumFlags = (True, False) if premiumFlags is None else premiumFlags
        self.__gids = gid
        return

    def matches(self, tankmanDescr):
        tman = TankmanDescr(tankmanDescr) if type(tankmanDescr) is str else tankmanDescr
        return tman.nationID in self.__nations and tman.isPremium in self.__premiumFlags and (tman.gid in self.__gids if self.__gids else True) and (not self.__tags.isdisjoint(tman.tags) if self.__tags else True)

    def __str__(self):
        return ':'.join(('|'.join((nations.MAP[i] for i in self.__nations)),
         '|'.join((('premium' if p else 'normal') for p in self.__premiumFlags)),
         '|'.join((str(i) for i in self.__gids or '*')),
         '|'.join(self.__tags or '*')))

    @staticmethod
    def fromString(tstr):
        tstr += '::::'
        try:
            ns, premium, gid, tags, _ = tstr.split(':', 4)
            ns = {n for n in ns.split('|') if n in nations.NAMES} if ns not in TankmanGroupSelection.ANY else ()
            premium = {TankmanGroupSelection.PTYPE[p] for p in premium.split('|')} if premium not in TankmanGroupSelection.ANY else None
            gid = {int(g) for g in gid.split('|')} if gid not in TankmanGroupSelection.ANY else ()
            tags = {t for t in tags.split('|')} if tags not in TankmanGroupSelection.ANY else ()
            return TankmanGroupSelection(ns=ns, premiumFlags=premium, gid=gid, tags=tags)
        except:
            LOG_CURRENT_EXCEPTION()
            return NoneGroupSelection()

        return


class TankmanGroupWoT(NoneGroupSelection):

    def matches(self, tankmanDescr):
        tman = TankmanDescr(tankmanDescr) if type(tankmanDescr) is str else tankmanDescr
        return tman.gid in ITEM_ID_RANGES.WOT


class TankmanGroupMT(NoneGroupSelection):

    def matches(self, tankmanDescr):
        tman = TankmanDescr(tankmanDescr) if type(tankmanDescr) is str else tankmanDescr
        return tman.gid in ITEM_ID_RANGES.MT


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
    roleLevel = tmanData.get('roleLevel', 50)
    if not 50 <= roleLevel <= MAX_SKILL_LEVEL:
        raise SoftException('Wrong tankman level')
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
    tankmanCompDescr = generateCompactDescr(passport, vehicleTypeID, role, roleLevel, skills, lastSkillLevel=lastSkillLevel, freeSkills=freeSkills)
    freeXP = tmanData.get('freeXP', 0)
    if freeXP != 0:
        tankmanDescr = TankmanDescr(tankmanCompDescr)
        tankmanDescr.addXP(freeXP)
        tankmanCompDescr = tankmanDescr.makeCompactDescr()
    return tankmanCompDescr


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


def getNationGroupByTmanDescr(tankmanDescr):
    td = TankmanDescr(tankmanDescr)
    return getNationConfig(td.nationID).getGroups(td.isPremium).get(td.gid)


def __validateSkills(skills):
    if len(set(skills)) != len(skills):
        raise SoftException('Duplicate tankman skills')
    for skill in skills:
        if skill not in SKILL_INDICES:
            raise SoftException('Wrong tankman skill')


_g_skillsConfig = None
_g_crewSkinsConfig = None
_g_nationsConfig = [ None for x in xrange(len(nations.NAMES)) ]

def _makeLevelXpCosts():
    costs = [0] * (MAX_SKILL_LEVEL + 1)
    prevCost = 0
    for level in xrange(1, len(costs)):
        prevCost += int(round(_LEVELUP_K1 * pow(_LEVELUP_K2, float(level - 1) / MAX_SKILL_LEVEL)))
        costs[level] = prevCost

    return costs


_g_levelXpCosts = _makeLevelXpCosts()

def _calcFirstSkillXpCost():
    result = 0
    for level in range(MAX_SKILL_LEVEL):
        result += TankmanDescr.levelUpXpCost(level, 1)

    return result


_g_totalFirstSkillXpCost = _calcFirstSkillXpCost()

def getRecruitInfoFromToken(tokenName):
    parts = tokenName.split(':')
    if len(parts) != 11:
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
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: nation duplicates'.format(tokenName))
                    return None
                for nation in nationNames:
                    if nation not in nations.AVAILABLE_NAMES:
                        LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: unknown nation name "{}"'.format(tokenName, nation))
                        return None
                    result['nations'].append(nations.INDICES[nation])

            if parts[2] == '' or parts[2] == 'true':
                result['isPremium'] = True
            elif parts[2] != 'false':
                LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: wrong "isPremium" value "{}'.format(tokenName, parts[2]))
                return None
            for nation in result['nations']:
                if len(filter(lambda g: g.name == parts[3], getNationGroups(nation, result['isPremium']).itervalues())) != 1:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: wrong group name'.format(tokenName))
                    return None

            result['group'] = parts[3]
            if parts[4] != '':
                freeXP = int(parts[4])
                if freeXP < 0 or freeXP > _MAX_FREE_XP:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: XP out of bounds'.format(tokenName))
                    return None
                result['freeXP'] = freeXP
            earnedSkillsSet = set()
            if parts[5] != '':
                skills = parts[5].split('!')
                if len(skills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: too many earned skills'.format(tokenName))
                    return None
                earnedSkillsSet = set(skills)
                if len(skills) != len(earnedSkillsSet):
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: earned skills are duplicated'.format(tokenName))
                    return None
                for skill in skills:
                    if skill not in skills_constants.ACTIVE_SKILLS:
                        LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: earned skill "{}" is not active'.format(tokenName, skill))
                        return None
                    result['skills'].append(skill)

            if parts[6] != '':
                lastSkillLevel = int(parts[6])
                if lastSkillLevel < 0 or lastSkillLevel > MAX_SKILL_LEVEL:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: lastSkillLevel out of bounds'.format(tokenName))
                    return None
                result['lastSkillLevel'] = lastSkillLevel
            freeSkillsSet = set()
            if parts[7] != '':
                freeSkills = parts[7].split('!')
                if len(freeSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: too many free skills'.format(tokenName))
                    return None
                chosenFreeSkills = [ s for s in freeSkills if s != 'any' ]
                freeSkillsSet = set(chosenFreeSkills)
                if len(chosenFreeSkills) != len(freeSkillsSet):
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: free skills are duplicated'.format(tokenName))
                    return None
                for skill in freeSkills:
                    if skill not in skills_constants.ACTIVE_FREE_SKILLS:
                        LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: free skill "{}" is not active'.format(tokenName, skill))
                        return None
                    result['freeSkills'].append(skill)

            if len(earnedSkillsSet) + len(freeSkillsSet) != len(earnedSkillsSet | freeSkillsSet):
                LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: free and earned skills are duplicated'.format(tokenName))
                return None
            if parts[8] != '':
                roleLevel = int(parts[8])
                if roleLevel < MIN_ROLE_LEVEL or roleLevel > MAX_SKILL_LEVEL:
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: roleLevel out of bounds'.format(tokenName))
                    return None
                result['roleLevel'] = roleLevel
            sourceID = parts[9]
            if sourceID == '':
                LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: empty sourceID'.format(tokenName))
                return None
            result['sourceID'] = sourceID
            if parts[10] != '':
                roles = parts[10].split('!')
                if len(roles) != len(set(roles)):
                    LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: roles are duplicated'.format(tokenName))
                    return None
                for role in roles:
                    if role not in skills_constants.ROLES:
                        LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: unknown role name "{}"'.format(tokenName, role))
                        return None
                    result['roles'].append(SKILL_INDICES[role])

        except ValueError:
            LOG_DEBUG_DEV('getRecruitInfoFromToken({}) error: value error'.format(tokenName))
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
            if recruitRole not in skills_constants.SKILL_NAMES:
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
    for slotID, tmanCompDescr in enumerate(crew):
        if tmanCompDescr is None:
            if not resultMask & crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW:
                resultMsg += 'Vehicle has not full crew; '
            resultMask = resultMask | crew_books_constants.CREW_BOOK_PROPERTIES_MASKS.FULL_CREW
            continue
        tmanDescr = TankmanDescr(tmanCompDescr)
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
