# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/tankmen.py
import random
import struct
from functools import partial
import nations
from items import vehicles, ITEM_TYPES
from items.components import skills_components
from items.components import skills_constants
from items.components import tankmen_components
from items.components import component_constants
from items.readers import skills_readers
from items.readers import tankmen_readers
from items.passports import PassportCache, passport_generator, maxAttempts, distinctFrom, acceptOn
from vehicles import VEHICLE_CLASS_TAGS
from debug_utils import LOG_ERROR, LOG_WARNING
from constants import ITEM_DEFS_PATH
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
_MAX_FREE_XP = 2000000000
_LEVELUP_K1 = 50.0
_LEVELUP_K2 = 100.0
RECRUIT_TMAN_TOKEN_PREFIX = 'tman_template'
MAX_SKILLS_IN_RECRUIT_TOKEN = 10

def init(preloadEverything):
    if preloadEverything:
        getSkillsConfig()
        for nationID in xrange(len(nations.NAMES)):
            getNationConfig(nationID)


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
    for group in groups:
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
    nationalGroups = getNationGroups(nationID, isPremium)
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
    cd = pack('4B', header, vehicleTypeID, SKILL_INDICES[role], roleLevel)
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
    cd += pack('<B4Hi', flags, firstNameID, lastNameID, iconID, rank | levelsToNextRank << 5, 0)
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
    return compactDescr[:6 + ord(compactDescr[4]) + 1 + 6]


def parseNationSpecAndRole(compactDescr):
    return (ord(compactDescr[0]) >> 4 & 15, ord(compactDescr[1]), ord(compactDescr[2]))


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
    nationID = header >> 4 & 15
    conf = getNationConfig(nationID)
    namesOffset = ord(cd[4]) + 7
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
        return list(self.__skills)

    @property
    def freeSkills(self):
        return list(self.__skills[:self.freeSkillsNumber])

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
        if 0 <= self.gid < len(groups):
            return groups[self.gid].isUnique
        else:
            return False

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

    def battleXpGain(self, xp, vehicleType, tankmanHasSurvived, commanderTutorXpBonusFactor):
        nationID, vehicleTypeID = vehicleType.id
        if vehicleTypeID != self.vehicleTypeID:
            isPremium, isSameClass = self.__paramsOnVehicle(vehicleType)
            if isPremium:
                xp *= 1.0 if isSameClass else 0.5
            else:
                xp *= 0.5 if isSameClass else 0.25
        xp *= vehicleType.crewXpFactor
        if not tankmanHasSurvived:
            xp *= 0.9
        if self.role != 'commander':
            xp *= 1.0 + commanderTutorXpBonusFactor
        return int(xp)

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

    def addXP(self, xp):
        self.freeXP = min(_MAX_FREE_XP, self.freeXP + xp)
        while self.roleLevel < MAX_SKILL_LEVEL:
            xpCost = self.levelUpXpCost(self.roleLevel, 0)
            if xpCost > self.freeXP:
                break
            self.freeXP -= xpCost
            self.roleLevel += 1
            self.__updateRankAtSkillLevelUp()

        if self.roleLevel == MAX_SKILL_LEVEL and self.__skills:
            self.__levelUpLastSkill()

    def addSkill(self, skillName):
        if skillName in self.skills:
            raise SoftException('Skill already leaned (%s)' % skillName)
        if skillName not in skills_constants.ACTIVE_SKILLS:
            raise SoftException('Unknown skill (%s)' % skillName)
        if self.role != 'commander' and skillName in skills_constants.COMMANDER_SKILLS:
            raise SoftException('Cannot learn commander skill (%s) for another role (%s)' % (skillName, self.role))
        if self.roleLevel != MAX_SKILL_LEVEL:
            raise SoftException('Main role not fully leaned (%d)' % self.roleLevel)
        if self.__skills and self.__lastSkillLevel != MAX_SKILL_LEVEL:
            raise SoftException('Last skill not fully leaned (%d)' % self.__lastSkillLevel)
        self.__skills.append(skillName)
        self.__lastSkillLevel = 0
        self.__levelUpLastSkill()

    def isFreeDropSkills(self):
        if self.lastSkillNumber < 1 + self.freeSkillsNumber:
            return True
        return True if self.lastSkillNumber == 1 + self.freeSkillsNumber and self.__lastSkillLevel == 0 else False

    def dropSkills(self, xpReuseFraction=0.0, throwIfNoChange=True):
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
            self.addXP(int(xpReuseFraction * (prevTotalXP - self.totalXP())))

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
            if fnGroupID >= len(groups):
                return (False, 'Invalid fn group', None)
            group = groups[fnGroupID]
            if group.notInShop:
                return (False, 'Not in shop', None)
            if bool(group.isFemales) != bool(isFemale):
                return (False, 'Invalid group sex', None)
            if firstNameID not in group.firstNames:
                return (False, 'Invalid first name', None)
        if lastNameID is not None:
            if lnGroupID >= len(groups):
                return (False, 'Invalid ln group', None)
            group = groups[lnGroupID]
            if group.notInShop:
                return (False, 'Not in shop', None)
            if bool(group.isFemales) != bool(isFemale):
                return (False, 'Invalid group sex', None)
            if lastNameID not in group.lastNames:
                return (False, 'Invalid last name', None)
        if iconID is not None:
            if iGroupID >= len(groups):
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

    def makeCompactDescr(self):
        pack = struct.pack
        header = ITEM_TYPES.tankman + (self.nationID << 4)
        cd = pack('4B', header, self.vehicleTypeID, SKILL_INDICES[self.role], self.roleLevel)
        numSkills = self.lastSkillNumber
        skills = [ SKILL_INDICES[s] for s in self.__skills ]
        cd += pack((str(1 + numSkills) + 'B'), numSkills, *skills)
        cd += chr(self.__lastSkillLevel if numSkills else 0)
        isFemale = 1 if self.isFemale else 0
        isPremium = 1 if self.isPremium else 0
        flags = isFemale | isPremium << 1 | self.freeSkillsNumber << 2
        cd += pack('<B4Hi', flags, self.firstNameID, self.lastNameID, self.iconID, self.__rankIdx & 31 | (self.numLevelsToNextRank & 2047) << 5, self.freeXP)
        cd += self.dossierCompactDescr
        return cd

    def isRestorable(self):
        vehicleTags = self.__vehicleTags
        return (len(self.skills) > 0 and self.skillLevel(self.skills[0]) == MAX_SKILL_LEVEL or self.roleLevel == MAX_SKILL_LEVEL and self.freeXP >= _g_totalFirstSkillXpCost) and not ('lockCrew' in vehicleTags and 'unrecoverable' in vehicleTags)

    def __initFromCompactDescr(self, compactDescr, battleOnly):
        cd = compactDescr
        unpack = struct.unpack
        try:
            header, self.vehicleTypeID, roleID, self.roleLevel, numSkills = unpack('5B', cd[:5])
            cd = cd[5:]
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
                    if skillName not in skills_constants.ACTIVE_SKILLS:
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
            self.firstNameID, self.lastNameID, self.iconID, rank, self.freeXP = unpack('<4Hi', cd[:12].ljust(12, '\x00'))
            self.gid, _ = findGroupsByIDs(getNationGroups(nationID, self.isPremium), self.isFemale, self.firstNameID, self.lastNameID, self.iconID).pop(0)
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
        while self.__lastSkillLevel < MAX_SKILL_LEVEL:
            xpCost = self.levelUpXpCost(self.__lastSkillLevel, numSkills)
            if xpCost > self.freeXP:
                break
            self.freeXP -= xpCost
            self.__lastSkillLevel += 1
            self.__updateRankAtSkillLevelUp()


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
    if fnGroupID >= len(groups):
        raise SoftException('Invalid group fn ID')
    group = groups[fnGroupID]
    if bool(group.isFemales) != bool(isFemale):
        raise SoftException('Invalid group sex')
    if firstNameID is not None:
        if firstNameID not in group.firstNamesList:
            raise SoftException('firstNameID is not in valid group')
    else:
        firstNameID = random.choice(group.firstNamesList)
    if lnGroupID >= len(groups):
        raise SoftException('Invalid group ln ID')
    group = groups[lnGroupID]
    if bool(group.isFemales) != bool(isFemale):
        raise SoftException('Invalid group sex')
    if lastNameID is not None:
        if lastNameID not in group.lastNamesList:
            raise SoftException('lastNameID is not in valid group')
    else:
        lastNameID = random.choice(group.lastNamesList)
    if iGroupID >= len(groups):
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
    tankmanCompDescr = generateCompactDescr(passport, vehicleTypeID, role, roleLevel, skills, freeSkills=freeSkills)
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
    if groupID < 0 or groupID >= len(nationGroups):
        LOG_WARNING('tankmen.hasTagInTankmenGroup: wrong value of the groupID (index out of range)', groupID)
        return False
    return tag in nationGroups[groupID].tags


def unpackCrewParams(crewGroup):
    groupID = crewGroup >> 2
    isFemale = bool(crewGroup & 1)
    isPremium = bool(crewGroup & 2)
    return (groupID, isFemale, isPremium)


def tankmenGroupHasRole(nationID, groupID, isPremium, role):
    nationGroups = getNationGroups(nationID, isPremium)
    if 0 <= groupID < len(nationGroups):
        return role in nationGroups[groupID].roles
    else:
        return False


def tankmenGroupCanChangeRole(nationID, groupID, isPremium):
    nationGroups = getNationGroups(nationID, isPremium)
    if 0 <= groupID < len(nationGroups):
        return len(nationGroups[groupID].roles) > 1
    else:
        return True


def getNationGroups(nationID, isPremium):
    return getNationConfig(nationID).getGroups(isPremium)


def findGroupsByIDs(groups, isFemale, firstNameID, secondNameID, iconID):
    found = [(-1, 0)]
    for groupID, group in enumerate(groups):
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
    if len(parts) != 10:
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
             'sourceID': ''}
            if parts[1] == '':
                result['nations'] = nations.INDICES.values()
            else:
                nationNames = parts[1].split('!')
                if len(nationNames) != len(set(nationNames)):
                    return None
                for nation in nationNames:
                    if nation not in nations.AVAILABLE_NAMES:
                        return None
                    result['nations'].append(nations.INDICES[nation])

            if parts[2] == '' or parts[2] == 'true':
                result['isPremium'] = True
            elif parts[2] != 'false':
                return None
            for nation in result['nations']:
                if len(filter(lambda g: g.name == parts[3], getNationGroups(nation, result['isPremium']))) != 1:
                    return None

            result['group'] = parts[3]
            if parts[4] != '':
                freeXP = int(parts[4])
                if freeXP < 0 or freeXP > _MAX_FREE_XP:
                    return None
                result['freeXP'] = freeXP
            if parts[5] != '':
                skills = parts[5].split('!')
                if len(skills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    return None
                if len(skills) != len(set(skills)):
                    return None
                for skill in skills:
                    if skill not in skills_constants.ACTIVE_SKILLS:
                        return None
                    result['skills'].append(skill)

            if parts[6] != '':
                lastSkillLevel = int(parts[6])
                if lastSkillLevel < 0 or lastSkillLevel > MAX_SKILL_LEVEL:
                    return None
                result['lastSkillLevel'] = lastSkillLevel
            if parts[7] != '':
                freeSkills = parts[7].split('!')
                if len(freeSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
                    return None
                if len(freeSkills) != len(set(freeSkills)):
                    return None
                for skill in freeSkills:
                    if skill not in skills_constants.ACTIVE_SKILLS:
                        return None
                    result['freeSkills'].append(skill)

            if parts[8] != '':
                roleLevel = int(parts[8])
                if roleLevel < MIN_ROLE_LEVEL or roleLevel > MAX_SKILL_LEVEL:
                    return None
                result['roleLevel'] = roleLevel
            sourceID = parts[9]
            if sourceID == '':
                return None
            result['sourceID'] = sourceID
        except ValueError:
            return None

        return result


def generateRecruitToken(group, sourceID, nationList=(), isPremium=True, freeXP=0, skills=(), lastSkillLevel=MAX_SKILL_LEVEL, freeSkills=(), roleLevel=MAX_SKILL_LEVEL):
    tokenParts = [RECRUIT_TMAN_TOKEN_PREFIX]
    selectedNations = set()
    if len(nationList) == 0:
        selectedNations = set(nations.AVAILABLE_NAMES)
    else:
        for nation in nationList:
            if nation not in nations.AVAILABLE_NAMES:
                return None
            selectedNations.add(nation)

    if len(selectedNations) == len(nations.AVAILABLE_NAMES):
        tokenParts.append('')
    else:
        tokenParts.append('!'.join(selectedNations))
    tokenParts.append('' if isPremium else 'false')
    for nation in selectedNations:
        if len(filter(lambda g: g.name == group, getNationGroups(nations.INDICES[nation], isPremium))) != 1:
            return None

    tokenParts.append(group)
    if freeXP < 0 or freeXP > _MAX_FREE_XP:
        return None
    else:
        tokenParts.append('' if freeXP == 0 else str(freeXP))
        selectedSkills = set()
        for skill in skills:
            if skill not in skills_constants.ACTIVE_SKILLS:
                return None
            selectedSkills.add(skill)

        if len(selectedSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
            return None
        tokenParts.append('!'.join(selectedSkills))
        if lastSkillLevel < 0 or lastSkillLevel > MAX_SKILL_LEVEL:
            return None
        tokenParts.append('' if lastSkillLevel == MAX_SKILL_LEVEL else str(lastSkillLevel))
        selectedFreeSkills = set()
        for skill in freeSkills:
            if skill not in skills_constants.ACTIVE_SKILLS:
                return None
            selectedFreeSkills.add(skill)

        if len(selectedFreeSkills) > MAX_SKILLS_IN_RECRUIT_TOKEN:
            return None
        tokenParts.append('!'.join(selectedFreeSkills))
        if roleLevel < MIN_ROLE_LEVEL or roleLevel > MAX_SKILL_LEVEL:
            return None
        tokenParts.append('' if roleLevel == MAX_SKILL_LEVEL else str(roleLevel))
        tokenParts.append(sourceID)
        return ':'.join(tokenParts)
