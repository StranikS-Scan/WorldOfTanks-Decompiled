# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/recruit_helper.py
import typing
from account_helpers.AccountSettings import AccountSettings, RECRUIT_NOTIFICATIONS
from helpers.i18n import makeString as _ms
from constants import ENDLESS_TOKEN_TIME
from gui.Scaleform.locale.PERSONAL_MISSIONS import PERSONAL_MISSIONS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import Tankman
from helpers import dependency
from items import tankmen, vehicles
from items.components import skills_constants
from items.components.component_constants import EMPTY_STRING
from items.components.tankmen_components import SPECIAL_CREW_TAG
from items.tankmen import TankmanDescr, MAX_SKILL_LEVEL
from nations import NONE_INDEX, INDICES, NAMES as NationNames
from shared_utils import first, findFirst
from skeletons.gui.server_events import IEventsCache
from soft_exception import SoftException
from .events_helpers import getTankmanRewardQuests
if typing.TYPE_CHECKING:
    from typing import List, Union

class RecruitGroupID(object):
    WOMEN1 = 'women1'


class RecruitSourceID(object):
    TANKWOMAN = 'tankwoman'
    TWITCH_0 = 'twitch0'
    TWITCH_1 = 'twitch1'
    TWITCH_2 = 'twitch2'
    TWITCH_3 = 'twitch3'
    TWITCH_4 = 'twitch4'
    TWITCH_5 = 'twitch5'
    TWITCH_6 = 'twitch6'
    TWITCH_7 = 'twitch7'
    TWITCH_8 = 'twitch8'
    TWITCH_9 = 'twitch9'
    TWITCH_10 = 'twitch10'
    TWITCH_11 = 'twitch11'
    TWITCH_12 = 'twitch12'
    TWITCH_13 = 'twitch13'
    TWITCH_14 = 'twitch14'
    TWITCH_15 = 'twitch15'
    TWITCH_16 = 'twitch16'
    TWITCH_17 = 'twitch17'
    TWITCH_18 = 'twitch18'
    TWITCH_19 = 'twitch19'
    TWITCH_20 = 'twitch20'
    TWITCH_21 = 'twitch21'
    TWITCH_22 = 'twitch22'
    TWITCH_23 = 'twitch23'
    TWITCH_24 = 'twitch24'
    TWITCH_25 = 'twitch25'
    TWITCH_26 = 'twitch26'
    TWITCH_27 = 'twitch27'
    TWITCH_28 = 'twitch28'
    TWITCH_29 = 'twitch29'
    TWITCH_30 = 'twitch30'
    TWITCH_31 = 'twitch31'
    TWITCH_32 = 'twitch32'
    TWITCH_33 = 'twitch33'
    TWITCH_34 = 'twitch34'
    TWITCH_35 = 'twitch35'
    TWITCH_36 = 'twitch36'
    TWITCH_37 = 'twitch37'
    TWITCH_38 = 'twitch38'
    TWITCH_39 = 'twitch39'
    TWITCH_40 = 'twitch40'
    TWITCH_41 = 'twitch41'
    TWITCH_42 = 'twitch42'
    TWITCH_43 = 'twitch43'
    TWITCH_44 = 'twitch44'
    TWITCH_45 = 'twitch45'
    TWITCH_46 = 'twitch46'
    TWITCH_47 = 'twitch47'
    TWITCH_48 = 'twitch48'
    TWITCH_49 = 'twitch49'
    TWITCH_50 = 'twitch50'
    BUFFON = 'buffon'
    LOOTBOX = 'lootbox'
    COMMANDER_MARINA = 'commander_marina'
    COMMANDER_PATRICK = 'commander_patrick'
    TWITCH_GIRL = 'twitch_girl'
    TWITCH_GUY = 'twitch_guy'
    EVENTS = (TWITCH_0,
     TWITCH_1,
     TWITCH_2,
     TWITCH_3,
     TWITCH_4,
     TWITCH_5,
     TWITCH_6,
     TWITCH_7,
     TWITCH_8,
     TWITCH_9,
     COMMANDER_MARINA,
     COMMANDER_PATRICK,
     TWITCH_10,
     TWITCH_11,
     TWITCH_12,
     TWITCH_13,
     TWITCH_14,
     TWITCH_15,
     TWITCH_16,
     TWITCH_17,
     TWITCH_18,
     TWITCH_19,
     TWITCH_20,
     TWITCH_21,
     TWITCH_22,
     TWITCH_23,
     TWITCH_24,
     TWITCH_25,
     TWITCH_26,
     TWITCH_27,
     TWITCH_28,
     TWITCH_29,
     TWITCH_30,
     TWITCH_31,
     TWITCH_32,
     TWITCH_33,
     TWITCH_34,
     TWITCH_35,
     TWITCH_36,
     TWITCH_37,
     TWITCH_38,
     TWITCH_39,
     TWITCH_40,
     TWITCH_41,
     TWITCH_42,
     TWITCH_43,
     TWITCH_44,
     TWITCH_45,
     TWITCH_46,
     TWITCH_47,
     TWITCH_48,
     TWITCH_49,
     TWITCH_50,
     TWITCH_GIRL,
     TWITCH_GUY)


_NEW_SKILL = 'new_skill'
_BASE_NAME = 'base'
_TANKWOMAN_ROLE_LEVEL = 100
_TANKWOMAN_ICON = 'girl-empty.png'
_TANKMAN_NAME = 'tankman'
_TANKMAN_ICON = 'tankman.png'
_TANKWOMAN_LEARNT_SKILLS = ['brotherhood']
_INCREASE_LIMIT_LOGIN = 5

class _BaseRecruitInfo(object):
    __slots__ = ('_recruitID', '_expiryTime', '_nations', '_freeSkills', '_learntSkills', '_freeXP', '_roleLevel', '_lastSkillLevel', '_roles', '_firstName', '_lastName', '_group', '_icon', '_sourceID', '_isPremium', '_isFemale', '_hasNewSkill', '_tankmanSkill')

    def __init__(self, recruitID, expiryTime, nations, learntSkills, freeSkills, freeXP, roleLevel, lastSkillLevel, firstName, lastName, roles, icon, group, sourceID, isPremium, isFemale, hasNewSkill):
        self._recruitID = recruitID
        self._expiryTime = expiryTime
        self._nations = nations
        self._freeSkills = freeSkills
        self._learntSkills = learntSkills
        self._freeXP = freeXP
        self._roleLevel = roleLevel
        self._lastSkillLevel = lastSkillLevel
        self._firstName = firstName
        self._lastName = lastName
        self._roles = roles
        self._icon = icon
        self._group = group
        self._sourceID = sourceID
        self._isPremium = isPremium
        self._isFemale = isFemale
        self._hasNewSkill = hasNewSkill
        self._tankmanSkill = self._getTankmanSkill()

    def __cmp__(self, other):
        return cmp(self.getExpiryTimeStamp(), other.getExpiryTimeStamp())

    def getGroupName(self):
        return self._group

    def getRecruitID(self):
        return self._recruitID

    def getEventName(self):
        return EMPTY_STRING

    def getLabel(self):
        return EMPTY_STRING

    def getDescription(self):
        return EMPTY_STRING

    def getFirstName(self):
        return self._firstName

    def getLastName(self):
        return self._lastName

    def getIsPremium(self):
        return self._isPremium

    def getRoleLevel(self):
        return self._roleLevel

    def getFreeXP(self):
        return self._freeXP

    def getEarnedSkills(self, multiplyNew=False):
        if self._hasNewSkill:
            if multiplyNew:
                skillsCount, _ = self.getNewSkillCount(onlyFull=True)
            else:
                skillsCount = 1
            return self._learntSkills + [_NEW_SKILL] * skillsCount
        return self._learntSkills

    def getAllKnownSkills(self, multiplyNew=False):
        return self.getFreeSkills() + self.getEarnedSkills(multiplyNew)

    def getFreeSkills(self):
        freeSkills = [ (skill if skill != 'any' else _NEW_SKILL) for skill in self._freeSkills ]
        freeSkills.sort(key=lambda x: x == _NEW_SKILL)
        return freeSkills

    def getLastSkillLevel(self):
        return self._lastSkillLevel

    def getExpiryTime(self):
        return backport.getShortDateFormat(self._expiryTime) if self._expiryTime and self._expiryTime < ENDLESS_TOKEN_TIME else ''

    def getExpiryTimeStamp(self):
        return self._expiryTime

    def getSmallIcon(self):
        return self._icon

    def getDynIconName(self):
        return self._icon.replace('-', '_').rsplit('.', 1)[0]

    def getBigIcon(self):
        dynAccessor = R.images.gui.maps.icons.tankmen.icons.big.dyn(self.getDynIconName())
        return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(R.images.gui.maps.icons.tankmen.icons.big.tankman())

    def getSmallIconPath(self):
        dynAccessor = R.images.gui.maps.icons.tankmen.icons.small.dyn(self.getDynIconName())
        return backport.image(dynAccessor()) if dynAccessor.isValid() else backport.image(R.images.gui.maps.icons.tankmen.icons.small.tankman())

    def getBarracksIcon(self):
        return self._icon

    def getRoles(self):
        return self._roles

    @property
    def defaultRole(self):
        return self._roles[0]

    def getNations(self):
        return self._nations

    def getFullUserName(self):
        firstName = self.getFirstName()
        lastName = self.getLastName()
        return lastName if not firstName else '{} {}'.format(firstName, lastName)

    def getRankID(self):
        return Tankman.calculateRankID(tankmen.MAX_SKILL_LEVEL, self._freeXP, skills=self._getSkillsForDescr(), freeSkills=self._getFreeSkillsForDescr(), lastSkillLevel=self._lastSkillLevel)

    def getSourceID(self):
        return self._sourceID

    def getSpecialIcon(self):
        dynAccessor = R.images.gui.maps.icons.tankmen.icons.special.dyn(self.getDynIconName())
        return backport.image(dynAccessor()) if dynAccessor.isValid() else None

    def isFemale(self):
        return self._isFemale

    def getFakeTankman(self):
        return Tankman.Tankman(self.__makeFakeDescriptor().makeCompactDescr())

    def getNewSkillCount(self, onlyFull=False):
        if self._hasNewSkill:
            tankman = self.getFakeTankman()
            count, lastSkillLevel = tankman.newSkillCount
            if onlyFull and lastSkillLevel != MAX_SKILL_LEVEL:
                count = max(count - 1, 0)
                lastSkillLevel = MAX_SKILL_LEVEL
            return (count, lastSkillLevel)

    def getTankmanSkill(self):
        return self._tankmanSkill

    def _getSkillsForDescr(self):
        return self._learntSkills

    def _getFreeSkillsForDescr(self):
        pass

    def _getTankmanSkill(self):
        return Tankman.TankmanSkill

    def __makeFakeDescriptor(self):
        vehType = vehicles.VehicleDescr(typeID=(0, 0)).type
        skills = self._getSkillsForDescr()
        freeSkills = self._getFreeSkillsForDescr()
        tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0]), vehType.id[1], vehType.crewRoles[0][0], self._roleLevel, skills=skills, freeSkills=freeSkills, lastSkillLevel=self._lastSkillLevel))
        tmanDescr.addXP(self._freeXP)
        return tmanDescr

    def _getDefaultNation(self):
        return INDICES.get(first(self._nations), NONE_INDEX)

    @property
    def defaultNation(self):
        return self._getDefaultNation()

    def _getNationGroup(self, nationID):
        groups = tankmen.getNationGroups(nationID, self._isPremium)
        group = findFirst(lambda g: g.name == self._group, groups.itervalues())
        return group

    def getSpecialVoiceTag(self, specialSoundCtrl):
        nationID = self._getDefaultNation()
        nationGroup = self._getNationGroup(nationID)
        if nationGroup is None:
            return
        else:
            for tag in nationGroup.tags:
                if specialSoundCtrl.checkTagForSpecialVoice(tag):
                    return tag

            return


class _QuestRecruitInfo(_BaseRecruitInfo):
    __slots__ = ('__operationName',)

    def __init__(self, questID, operationName):
        super(_QuestRecruitInfo, self).__init__(recruitID=questID, expiryTime=0, nations=NationNames, group=RecruitGroupID.WOMEN1, freeSkills=_TANKWOMAN_LEARNT_SKILLS, learntSkills=[], freeXP=TankmanDescr.skillUpXpCost(1), roleLevel=_TANKWOMAN_ROLE_LEVEL, lastSkillLevel=0, firstName=_ms(QUESTS.BONUSES_ITEM_TANKWOMAN), lastName=EMPTY_STRING, roles=[], icon=_TANKWOMAN_ICON, sourceID=RecruitSourceID.TANKWOMAN, isPremium=True, isFemale=True, hasNewSkill=True)
        self.__operationName = operationName

    def getEventName(self):
        return self.getLabel()

    def getLabel(self):
        return _ms(PERSONAL_MISSIONS.OPERATIONTITLE_TITLE, title=self.__operationName)

    def getDescription(self):
        return _ms(TOOLTIPS.NOTRECRUITEDTANKMAN_TANKWOMAN_DESC)

    def getHowToGetInfo(self):
        pass

    def getNewSkillCount(self, onlyFull=False):
        return (1, 0) if self._hasNewSkill else (0, 0)

    def _getFreeSkillsForDescr(self):
        return _TANKWOMAN_LEARNT_SKILLS


class _TokenRecruitInfo(_BaseRecruitInfo):
    __slots__ = ('__freeSkills',)

    def __init__(self, tokenName, expiryTime, nations, isPremium, group, freeSkills, skills, freeXP, lastSkillLevel, roleLevel, sourceID, roles):
        self._isPremium = isPremium
        self._group = group
        self.__freeSkills = freeSkills
        nationNames = [ NationNames[i] for i in nations ]
        needXP = sum((TankmanDescr.levelUpXpCost(level, len(skills) + 1) for level in xrange(0, tankmen.MAX_SKILL_LEVEL)))
        hasNewSkill = freeXP >= needXP
        nation = nations[0] if nations else NONE_INDEX
        allowedRoles, firstName, lastName, icon, isFemale = self.__parseTankmanData(nation)
        if roles:
            for role in roles:
                if skills_constants.SKILL_NAMES[role] not in allowedRoles:
                    raise SoftException('Requested role (%s) is not in the list of allowed roles (%s)' % (skills_constants.SKILL_NAMES[role], ', '.join(map(str, allowedRoles))))

            allowedRoles = [ skills_constants.SKILL_NAMES[role] for role in roles ]
        super(_TokenRecruitInfo, self).__init__(tokenName, expiryTime, nationNames, skills, freeSkills, freeXP, roleLevel, lastSkillLevel, firstName, lastName, allowedRoles, icon, group, sourceID, isPremium, isFemale, hasNewSkill)

    def getEventName(self):
        dynAccessor = R.strings.tooltips.notrecruitedtankman.dyn(self._sourceID)
        return backport.text(dynAccessor.event()) if dynAccessor.isValid() and dynAccessor.dyn('event').isValid() else backport.text(R.strings.tooltips.notrecruitedtankman.base.event())

    def getLabel(self):
        dynAccessor = R.strings.tooltips.notrecruitedtankman.dyn(self._sourceID)
        return backport.text(dynAccessor.label()) if dynAccessor.isValid() and dynAccessor.dyn('label').isValid() else backport.text(R.strings.tooltips.notrecruitedtankman.tankman.label())

    def getDescription(self):
        dynAccessor = R.strings.tooltips.notrecruitedtankman.dyn(self._sourceID)
        return backport.text(dynAccessor.desc()) if dynAccessor.isValid() and dynAccessor.dyn('desc').isValid() else backport.text(R.strings.tooltips.notrecruitedtankman.tankman.desc())

    def getHowToGetInfo(self):
        dynAccessor = R.strings.tooltips.notrecruitedtankman.dyn(self._sourceID)
        return backport.text(dynAccessor.howToGetInfo()) if dynAccessor.isValid() and dynAccessor.dyn('howToGetInfo').isValid() else backport.text(R.strings.tooltips.notrecruitedtankman.tankman.howToGetInfo())

    def getFullUserNameByNation(self, nationID=None):
        if nationID is None:
            nationID = self._getDefaultNation()
        _, firstName, lastName, _, _ = self.__parseTankmanData(nationID)
        return lastName if not firstName else '{} {}'.format(firstName, lastName)

    def getIconByNation(self, nationID):
        _, _, _, icon, _ = self.__parseTankmanData(nationID)
        return icon

    def _getSkillsForDescr(self):
        return [ skill for skill in self._learntSkills if skill not in self.__freeSkills ]

    def _getFreeSkillsForDescr(self):
        return self.__freeSkills

    def _getTankmanSkill(self):
        nationID = self._getDefaultNation()
        nationGroup = self._getNationGroup(nationID)
        if self.__hasTagInTankmenGroup(nationID, nationGroup, SPECIAL_CREW_TAG.SABATON):
            return Tankman.SabatonTankmanSkill
        if self.__hasTagInTankmenGroup(nationID, nationGroup, SPECIAL_CREW_TAG.OFFSPRING):
            return Tankman.OffspringTankmanSkill
        if self.__hasTagInTankmenGroup(nationID, nationGroup, SPECIAL_CREW_TAG.YHA):
            return Tankman.YhaTankmanSkill
        return Tankman.WitchesTankmanSkill if self.__hasTagInTankmenGroup(nationID, nationGroup, SPECIAL_CREW_TAG.WITCHES_CREW) else super(_TokenRecruitInfo, self)._getTankmanSkill()

    def __parseTankmanData(self, nationID):
        empty = ([],
         EMPTY_STRING,
         EMPTY_STRING,
         EMPTY_STRING,
         False)
        nationGroup = self._getNationGroup(nationID)
        if nationGroup is None:
            return empty
        else:
            firstNamesList = nationGroup.firstNamesList
            lastNamesList = nationGroup.lastNamesList
            iconsList = nationGroup.iconsList
            if not firstNamesList or not lastNamesList or not iconsList:
                return empty
            if len(firstNamesList) > 1 or len(lastNamesList) > 1 or len(iconsList) > 1:
                if nationGroup.isFemales:
                    return (nationGroup.rolesList,
                     _ms(QUESTS.BONUSES_ITEM_TANKWOMAN),
                     EMPTY_STRING,
                     _TANKWOMAN_ICON,
                     nationGroup.isFemales)
                return (nationGroup.rolesList,
                 _ms(QUESTS.BONUSES_ITEM_TANKMAN),
                 EMPTY_STRING,
                 _TANKMAN_ICON,
                 nationGroup.isFemales)
            firstNameId = nationGroup.firstNamesList[0]
            lastNameId = nationGroup.lastNamesList[0]
            iconId = nationGroup.iconsList[0]
            nationConfig = tankmen.getNationConfig(nationID)
            return (nationGroup.rolesList,
             nationConfig.getFirstName(firstNameId),
             nationConfig.getLastName(lastNameId),
             nationConfig.getIcon(iconId),
             nationGroup.isFemales)

    def __hasTagInTankmenGroup(self, nationID, group, tag):
        return tankmen.hasTagInTankmenGroup(nationID, group.groupID, self._isPremium, tag)


def _getRecruitInfoFromQuest(questID):
    for quest, opName in getTankmanRewardQuests():
        if questID == quest.getID():
            return _QuestRecruitInfo(questID, opName)

    return None


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def _getRecruitInfoFromToken(tokenName, eventsCache=None):
    tokenData = tankmen.getRecruitInfoFromToken(tokenName)
    expiryTime = eventsCache.questsProgress.getTokenExpiryTime(tokenName)
    return None if tokenData is None else _TokenRecruitInfo(tokenName, expiryTime, **tokenData)


def _getRecruitUniqueIDs():
    result = []
    for recruitID, count in getRecruitIDs().iteritems():
        result.extend([ str(idx) + recruitID for idx in xrange(count) ])

    return set(result)


def getRecruitInfo(recruitID):
    try:
        questID = int(recruitID)
        return _getRecruitInfoFromQuest(questID)
    except ValueError:
        return _getRecruitInfoFromToken(recruitID)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getAllRecruitsInfo(sortByExpireTime=False, eventsCache=None):
    result = []
    for tokenName in eventsCache.questsProgress.getTokenNames():
        info = _getRecruitInfoFromToken(tokenName)
        if info is not None:
            count = eventsCache.questsProgress.getTokenCount(tokenName)
            result.extend([ info for _ in range(count) ])

    if sortByExpireTime:
        result.sort()
    for quest, opName in getTankmanRewardQuests():
        result.append(_QuestRecruitInfo(quest.getID(), opName))

    return result


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getRecruitIDs(eventsCache=None):
    result = {}
    for tokenName in eventsCache.questsProgress.getTokenNames():
        info = tankmen.getRecruitInfoFromToken(tokenName)
        if info is not None:
            count = eventsCache.questsProgress.getTokenCount(tokenName)
            result[tokenName] = count

    for quest, _ in getTankmanRewardQuests():
        result[str(quest.getID())] = 1

    return result


def getSourceIdFromQuest(questID):
    sourceID = questID.split(':', 1)[0]
    return sourceID if sourceID in RecruitSourceID.EVENTS else None


def getNewRecruitsCounter():
    previous = AccountSettings.getNotifications(RECRUIT_NOTIFICATIONS)
    current = _getRecruitUniqueIDs()
    return len(current.difference(previous))


def setNewRecruitsVisited():
    AccountSettings.setNotifications(RECRUIT_NOTIFICATIONS, _getRecruitUniqueIDs())
