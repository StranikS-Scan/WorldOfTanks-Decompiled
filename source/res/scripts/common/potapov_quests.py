# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/potapov_quests.py
from __future__ import absolute_import
import struct
import time
import typing
from future.utils import viewitems
from past.builtins import intern, xrange
from enum import Enum
import ResMgr
import nations
import quest_xml_source
from items import ItemsPrices, _xml, vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from constants import COMMON_ROLE, COMMON_ROLE_TO_ROLE_TYPE, EVENT_TYPE, IS_CLIENT, IS_WEB, ITEM_DEFS_PATH, PERSONAL_MISSION_2_FINAL_PAWN_COST, PERSONAL_MISSION_2_FREE_TOKEN_NAME, PERSONAL_MISSION_FINAL_PAWN_COST, PERSONAL_MISSION_FREE_TOKEN_NAME, HAS_PM1_COMPLETED_TOKEN, HAS_PM2_COMPLETED_TOKEN, HAS_PM3_COMPLETED_TOKEN, HAS_PM4_COMPLETED_TOKEN
from nations import ALLIANCES_TAGS
from personal_missions_constants import VEHICLE_RESTRICTION_MAX_LEVEL, VEHICLE_RESTRICTION_MIN_LEVEL
from soft_exception import SoftException
from debug_utils import LOG_ERROR
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import i18n
if typing.TYPE_CHECKING:
    from typing import FrozenSet, Optional
    from items.vehicles import VehicleType
POTAPOV_QUEST_XML_PATH = ITEM_DEFS_PATH + 'potapov_quests/'
_FALLOUT_BATTLE_TAGS = frozenset(('classic', 'multiteam'))
_ALLOWED_TAG_NAMES = ('initial', 'final') + tuple(_FALLOUT_BATTLE_TAGS) + tuple(VEHICLE_CLASS_TAGS) + tuple(ALLIANCES_TAGS) + tuple(COMMON_ROLE.ALL)
g_cache = None
g_tileCache = None
g_seasonCache = None

class PQ_BRANCH():

    class QUEST_GROUPS(Enum):
        GROUP_1 = 1
        GROUP_2 = 2
        GROUP_3 = 3

    REGULAR = 0
    PERSONAL_MISSION_2 = 2
    PERSONAL_MISSION_3 = 4
    PERSONAL_MISSION_4 = 8
    ALL = (REGULAR,
     PERSONAL_MISSION_2,
     PERSONAL_MISSION_3,
     PERSONAL_MISSION_4)
    PM1_NAME = 'regular'
    PM2_NAME = 'pm2'
    PM3_NAME = 'pm3'
    PM4_NAME = 'pm4'
    NAME_TO_TYPE = {PM1_NAME: REGULAR,
     PM2_NAME: PERSONAL_MISSION_2,
     PM3_NAME: PERSONAL_MISSION_3,
     PM4_NAME: PERSONAL_MISSION_4}
    ALL_NAMES = tuple(NAME_TO_TYPE.keys())
    PM_CAMPAIGNS_IDS = {REGULAR: 1,
     PERSONAL_MISSION_2: 2,
     PERSONAL_MISSION_3: 3,
     PERSONAL_MISSION_4: 4}

    @classmethod
    def convertBranchNameToSeasonID(cls, branchName):
        return cls.PM_CAMPAIGNS_IDS[cls.NAME_TO_TYPE[branchName]]

    BRANCH_TO_OPERATION_IDS = {REGULAR: (1, 2, 3, 4),
     PERSONAL_MISSION_2: (5, 6, 7),
     PERSONAL_MISSION_3: (8, 9, 10),
     PERSONAL_MISSION_4: (11,)}
    OPERATION_ID_TO_BRANCH = {operationsId:branch for branch, operationsIDs in BRANCH_TO_OPERATION_IDS.items() for operationsId in operationsIDs}
    TYPE_TO_NAME = {v:k for k, v in NAME_TO_TYPE.items()}

    @classmethod
    def convertNameToType(cls, branches):
        return [ cls.NAME_TO_TYPE[branch] for branch in branches ]

    MUTUAL_EXCLUSION_BRANCHES = {QUEST_GROUPS.GROUP_1: (PM1_NAME, PM2_NAME),
     QUEST_GROUPS.GROUP_2: (PM3_NAME,),
     QUEST_GROUPS.GROUP_3: (PM4_NAME,)}
    WITH_AWARD_LIST_BRANCHES = MUTUAL_EXCLUSION_BRANCHES[QUEST_GROUPS.GROUP_1]
    WITHOUT_AWARD_LIST_BRANCHES = MUTUAL_EXCLUSION_BRANCHES[QUEST_GROUPS.GROUP_2] + MUTUAL_EXCLUSION_BRANCHES[QUEST_GROUPS.GROUP_3]


class PQ_SWITCHES():
    IS_PM_BATTLE_PROGRESS_ENABLED = 'isPMBattleProgressEnabled'
    IS_REGULAR_QUEST_ENABLED = 'isRegularQuestEnabled'
    IS_PM2_QUEST_ENABLED = 'isPM2QuestEnabled'
    IS_PM3_QUEST_ENABLED = 'isPM3QuestEnabled'
    IS_PM4_QUEST_ENABLED = 'isPM4QuestEnabled'
    ALL = (IS_REGULAR_QUEST_ENABLED,
     IS_PM2_QUEST_ENABLED,
     IS_PM3_QUEST_ENABLED,
     IS_PM4_QUEST_ENABLED)
    DISABLED_PM_OPERATIONS = 'disabledPMOperations'
    DISABLED_PM_MISSIONS = 'disabledPersonalMissions'
    WITHOUT_AWARD_LIST_SWITCHERS = ALL[len(PQ_BRANCH.WITH_AWARD_LIST_BRANCHES):]
    MAP_BRANCH_NAME_TO_SWITCH_NAME = {PQ_BRANCH.PM1_NAME: IS_REGULAR_QUEST_ENABLED,
     PQ_BRANCH.PM2_NAME: IS_PM2_QUEST_ENABLED,
     PQ_BRANCH.PM3_NAME: IS_PM3_QUEST_ENABLED,
     PQ_BRANCH.PM4_NAME: IS_PM4_QUEST_ENABLED}


PM_BRANCH_TO_FREE_TOKEN_NAME = {PQ_BRANCH.REGULAR: PERSONAL_MISSION_FREE_TOKEN_NAME,
 PQ_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FREE_TOKEN_NAME}
PM_BRANCH_TO_FINAL_PAWN_COST = {PQ_BRANCH.REGULAR: PERSONAL_MISSION_FINAL_PAWN_COST,
 PQ_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FINAL_PAWN_COST}
MAP_BRANCH_NAME_TO_COMPLETED_TOKEN = {PQ_BRANCH.PM1_NAME: HAS_PM1_COMPLETED_TOKEN,
 PQ_BRANCH.PM2_NAME: HAS_PM2_COMPLETED_TOKEN,
 PQ_BRANCH.PM3_NAME: HAS_PM3_COMPLETED_TOKEN,
 PQ_BRANCH.PM4_NAME: HAS_PM4_COMPLETED_TOKEN}
POTAPOV_QUEST_COMPLETED_TOKENS = tuple(MAP_BRANCH_NAME_TO_COMPLETED_TOKEN.values())

def isPotapovQuestBranchEnabled(gameParams, branchName):
    switchName = PQ_SWITCHES.MAP_BRANCH_NAME_TO_SWITCH_NAME.get(branchName)
    if switchName is None:
        LOG_ERROR('Branch %d is unknown' % branchName)
        return False
    else:
        return gameParams['misc_settings'].get(switchName, False)


def isPotapovQuestTileEnabled(gameParams, pqType):
    return pqType.tileID not in gameParams['misc_settings'][PQ_SWITCHES.DISABLED_PM_OPERATIONS]


def isPotapovQuestEnabled(gameParams, questID):
    return questID not in gameParams['misc_settings'][PQ_SWITCHES.DISABLED_PM_MISSIONS]


def isPotapovQuestBranchTileAndMissionEnabled(gameParams, pqType):
    return isPotapovQuestBranchEnabled(gameParams, pqType.branchName) and isPotapovQuestTileEnabled(gameParams, pqType) and isPotapovQuestEnabled(gameParams, pqType.id)


class PQ_STATE():
    NONE = 0
    UNLOCKED = 1
    NEED_GET_MAIN_REWARD = 2
    MAIN_REWARD_GOTTEN = 3
    NEED_GET_ADD_REWARD = 4
    NEED_GET_ALL_REWARDS = 5
    ALL_REWARDS_GOTTEN = 6
    NEXT_STATE = {NONE: (UNLOCKED, NEED_GET_MAIN_REWARD, NEED_GET_ALL_REWARDS),
     UNLOCKED: (NEED_GET_MAIN_REWARD, NEED_GET_ALL_REWARDS),
     NEED_GET_MAIN_REWARD: (MAIN_REWARD_GOTTEN, ALL_REWARDS_GOTTEN),
     MAIN_REWARD_GOTTEN: (NEED_GET_ADD_REWARD,),
     NEED_GET_ADD_REWARD: (ALL_REWARDS_GOTTEN,),
     NEED_GET_ALL_REWARDS: (ALL_REWARDS_GOTTEN,)}
    NEED_GET_REWARD = (NEED_GET_MAIN_REWARD, NEED_GET_ADD_REWARD, NEED_GET_ALL_REWARDS)
    COMPLETED = (ALL_REWARDS_GOTTEN, NEED_GET_ALL_REWARDS, NEED_GET_ADD_REWARD)


class PQ_FLAG():
    NONE = 0
    PAUSE = 1


PQ_REWARD_BY_DEMAND = {1: (PQ_STATE.NEED_GET_MAIN_REWARD, PQ_STATE.NEED_GET_ALL_REWARDS),
 2: (PQ_STATE.NEED_GET_ADD_REWARD, PQ_STATE.NEED_GET_ALL_REWARDS),
 3: (PQ_STATE.NEED_GET_MAIN_REWARD, PQ_STATE.NEED_GET_ADD_REWARD, PQ_STATE.NEED_GET_ALL_REWARDS)}

def init():
    global g_cache
    global g_tileCache
    global g_seasonCache
    g_seasonCache = SeasonCache()
    g_tileCache = TileCache()
    g_cache = PQCache()


class SeasonCache():

    def __init__(self):
        self.__seasonsInfo = {}
        self.__readSeasons()

    def getSeasonInfo(self, seasonID):
        if seasonID not in self.__seasonsInfo:
            raise SoftException('Invalid season id (%s)' % (seasonID,))
        return self.__seasonsInfo[seasonID]

    def __readSeasons(self):
        xmlPath = POTAPOV_QUEST_XML_PATH + '/seasons.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__seasonsInfo = idToSeason = {}
        ids = {}
        for sname, ssection in section.items():
            ctx = (None, xmlPath)
            if sname in ids:
                _xml.raiseWrongXml(ctx, '', 'season name is not unique')
            seasonID = _xml.readInt(ctx, ssection, 'id', 0, 15)
            if seasonID in idToSeason:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            basicInfo = {'name': sname}
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(ssection.readString('userString'))
                basicInfo['description'] = i18n.makeString(ssection.readString('description'))
            ids[sname] = seasonID
            idToSeason[seasonID] = basicInfo

        return


class TileCache(object):

    def __init__(self):
        self.__tilesInfo = {}
        self.__readTiles()

    def getTileInfo(self, tileID):
        if tileID not in self.__tilesInfo:
            raise SoftException('Invalid tile id (%s)' % (tileID,))
        return self.__tilesInfo[tileID]

    def __iter__(self):
        return iter(viewitems(self.__tilesInfo))

    def __readTiles(self):
        xmlPath = POTAPOV_QUEST_XML_PATH + '/tiles.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__tilesInfo = idToTile = {}
        ids = {}
        for tname, tsection in section.items():
            if tname == 'quests':
                continue
            ctx = (None, xmlPath)
            if tname in ids:
                _xml.raiseWrongXml(ctx, '', 'tile name is not unique')
            seasonID = _xml.readInt(ctx, tsection, 'seasonID')
            g_seasonCache.getSeasonInfo(seasonID)
            tileID = _xml.readInt(ctx, tsection, 'id', 0, 15)
            if tileID in idToTile:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            chainsCount = _xml.readInt(ctx, tsection, 'chainsCount', 1, 15)
            chainsCountToUnlockNext = _xml.readInt(ctx, tsection, 'chainsCountToUnlockNext', 0, 15)
            nextTileIDs = frozenset((int(tileID) for tileID in _xml.readString(ctx, tsection, 'nextTileIDs').split()))
            achievements = {}
            basicInfo = {'name': tname,
             'chainsCount': chainsCount,
             'nextTileIDs': nextTileIDs,
             'chainsCountToUnlockNext': chainsCountToUnlockNext,
             'questsInChain': _xml.readInt(ctx, tsection, 'questsInChain', 1, 100),
             'price': ItemsPrices._tuplePrice(_xml.readPrice(ctx, tsection, 'price')),
             'achievements': achievements,
             'seasonID': seasonID,
             'tokens': set(_xml.readString(ctx, tsection, 'tokens').split())}
            if tsection.has_key('achievements'):
                for aname, asection in tsection['achievements'].items():
                    _, aid = aname.split('_')
                    achievements[int(aid)] = asection.asString

                if len(achievements) < basicInfo['chainsCount']:
                    _xml.raiseWrongXml(ctx, 'achievements', 'wrong achievement number')
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(tsection.readString('userString'))
                basicInfo['description'] = i18n.makeString(tsection.readString('description'))
                basicInfo['iconID'] = i18n.makeString(tsection.readString('iconID'))
            ids[tname] = tileID
            idToTile[tileID] = basicInfo

        return


class PQCache(object):

    def __init__(self, auxData=None):
        self.__potapovQuestIDToQuestType = {}
        self.__questUniqueIDToPotapovQuestID = {}
        self.__tileIDchainIDToPotapovQuestID = {}
        self.__tileIDchainIDToFinalPotapovQuestID = {}
        self.__tileIDchainIDToInitialPotapovQuestID = {}
        self.__readQuestList(auxData=auxData)

    def questByPotapovQuestID(self, potapovQuestID):
        if potapovQuestID not in self.__potapovQuestIDToQuestType:
            raise SoftException('Invalid potapov quest id (%s)' % (potapovQuestID,))
        return self.__potapovQuestIDToQuestType[potapovQuestID]

    def hasPotapovQuest(self, potapovQuestID):
        return potapovQuestID in self.__potapovQuestIDToQuestType

    def getPotapovQuests(self):
        return self.__potapovQuestIDToQuestType

    def questByUniqueQuestID(self, uniqueQuestID):
        return self.questByPotapovQuestID(self.getPotapovQuestIDByUniqueID(uniqueQuestID))

    def isPotapovQuest(self, uniqueQuestID):
        return uniqueQuestID in self.__questUniqueIDToPotapovQuestID

    def questListByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToPotapovQuestID[tileID, chainID]

    def finalPotapovQuestIDByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToFinalPotapovQuestID[tileID, chainID]

    def initialPotapovQuestIDByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToInitialPotapovQuestID[tileID, chainID]

    def getPotapovQuestIDByUniqueID(self, uniqueQuestID):
        if uniqueQuestID not in self.__questUniqueIDToPotapovQuestID:
            raise SoftException('Invalid potapov quest name (%s)' % (uniqueQuestID,))
        return self.__questUniqueIDToPotapovQuestID[uniqueQuestID]

    def branchByPotapovQuestID(self, potapovQuestID):
        return self.questByPotapovQuestID(potapovQuestID).branchName

    def getPotapovQuestNameByQuestID(self, questID):
        return self.questByPotapovQuestID(questID).generalQuestID

    def getPotapovQuestIDByName(self, questName):
        return self.getPotapovQuestIDByUniqueID('{}_main'.format(questName))

    def __iter__(self):
        return iter(viewitems(self.__questUniqueIDToPotapovQuestID))

    def __readQuestList(self, auxData=None):
        xmlPath = POTAPOV_QUEST_XML_PATH + '/list.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__potapovQuestIDToQuestType = idToQuest = {}
        self.__questUniqueIDToPotapovQuestID = questUniqueNameToPotapovQuestID = {}
        self.__tileIDchainIDToPotapovQuestID = tileIDchainIDToPotapovQuestID = {}
        self.__tileIDchainIDToFinalPotapovQuestID = tileIDchainIDToFinalPotapovQuestID = {}
        self.__tileIDchainIDToInitialPotapovQuestID = tileIDchainIDToInitialPotapovQuestID = {}
        ids = {}
        curTime = int(time.time())
        xmlSource = quest_xml_source.Source()
        for qname, qsection in section.items():
            splitted = qname.split('_')
            ctx = (None, xmlPath)
            if qname in ids:
                _xml.raiseWrongXml(ctx, '', 'potapov quest name is not unique')
            potapovQuestID = _xml.readInt(ctx, qsection, 'id', 0, 1023)
            if potapovQuestID in idToQuest:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            questBranchName, tileID, chainID, internalID = splitted
            isQuestBranchWithoutAwardLists = questBranchName in PQ_BRANCH.WITHOUT_AWARD_LIST_BRANCHES
            isQuestBranchWithAwardLists = questBranchName in PQ_BRANCH.WITH_AWARD_LIST_BRANCHES
            tileInfo = g_tileCache.getTileInfo(int(tileID))
            if not 1 <= int(chainID) <= tileInfo['chainsCount']:
                _xml.raiseWrongXml(ctx, '', 'quest chainID must be between 1 and %s' % tileInfo['chainsCount'])
            if not 1 <= int(internalID) <= tileInfo['questsInChain']:
                _xml.raiseWrongXml(ctx, '', 'quest internalID must be between 1 and %s' % tileInfo['chainsCount'])
            minLevel = _xml.readInt(ctx, qsection, 'minLevel', VEHICLE_RESTRICTION_MIN_LEVEL, VEHICLE_RESTRICTION_MAX_LEVEL)
            maxLevel = _xml.readInt(ctx, qsection, 'maxLevel', minLevel, VEHICLE_RESTRICTION_MAX_LEVEL)
            basicInfo = {'name': qname,
             'id': potapovQuestID,
             'branch': PQ_BRANCH.NAME_TO_TYPE[questBranchName],
             'branchName': questBranchName,
             'tileID': int(tileID),
             'chainID': int(chainID),
             'internalID': int(internalID),
             'minLevel': minLevel,
             'maxLevel': maxLevel,
             'requiredUnlocks': frozenset((int(unlock) for unlock in _xml.readString(ctx, qsection, 'requiredUnlocks').split()))}
            rewardByDemand = qsection.readInt('rewardByDemand', 0)
            if rewardByDemand != 0 and rewardByDemand not in PQ_REWARD_BY_DEMAND.keys():
                raise SoftException('Unexpected value for rewardByDemand')
            basicInfo['rewardByDemand'] = rewardByDemand
            tags = _readTags(ctx, qsection, 'tags')
            basicInfo['tags'] = tags
            if questBranchName == PQ_BRANCH.PM1_NAME and tags.isdisjoint(VEHICLE_CLASS_TAGS):
                _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle class is not specified')
            if questBranchName == PQ_BRANCH.PM2_NAME and tags.isdisjoint(ALLIANCES_TAGS):
                _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle alliance is not specified')
            if isQuestBranchWithoutAwardLists and tags.isdisjoint(COMMON_ROLE.ALL):
                _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle role is not specified')
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(qsection.readString('userString'))
                basicInfo['shortUserString'] = i18n.makeString(qsection.readString('shortUserString'))
                basicInfo['description'] = qsection.readString('description')
                basicInfo['advice'] = qsection.readString('advice')
            questPath = ''.join([POTAPOV_QUEST_XML_PATH,
             '/',
             questBranchName,
             '/tile_',
             tileID,
             '/chain_',
             chainID,
             '/',
             qname,
             '.xml'])
            questCtx = (None, questPath)
            nodes = xmlSource.readFromInternalFile(questPath, curTime, auxData)
            nodes = nodes.get(EVENT_TYPE.POTAPOV_QUEST, None)
            if nodes is None:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Potapov quests are not specified.')
            if isQuestBranchWithoutAwardLists and len(nodes) != 2 or isQuestBranchWithAwardLists and len(nodes) != 4:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Main and additional quest should be presented.')
            qinfo = nodes[0].info
            if not qinfo['id'].endswith('main'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Main quest must be first.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['mainQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['mainQuestInfo'] = qinfo['questClientData']
            if isQuestBranchWithAwardLists:
                qinfo = nodes[1].info
                if not qinfo['id'].endswith('main_award_list'):
                    _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Main award list quest must be second.')
                if qinfo['id'] in questUniqueNameToPotapovQuestID:
                    _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
                questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
                basicInfo['mainAwardListQuestID'] = qinfo['id']
                if IS_CLIENT or IS_WEB:
                    basicInfo['mainAwardListQuestInfo'] = qinfo['questClientData']
            else:
                basicInfo['mainAwardListQuestID'] = None
                basicInfo['mainAwardListQuestInfo'] = None
            qinfo = nodes[1].info if isQuestBranchWithoutAwardLists else nodes[2].info
            if not qinfo['id'].endswith('add'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Add quest must be third.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['addQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['addQuestInfo'] = qinfo['questClientData']
            if isQuestBranchWithAwardLists:
                qinfo = nodes[3].info
                if not qinfo['id'].endswith('add_award_list'):
                    _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Add award list quest must be fourth.')
                if qinfo['id'] in questUniqueNameToPotapovQuestID:
                    _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
                questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
                basicInfo['addAwardListQuestID'] = qinfo['id']
                if IS_CLIENT or IS_WEB:
                    basicInfo['addAwardListQuestInfo'] = qinfo['questClientData']
            else:
                basicInfo['addAwardListQuestID'] = None
                basicInfo['addAwardListQuestInfo'] = None
            idToQuest[potapovQuestID] = PQType(basicInfo)
            ids[qname] = potapovQuestID
            key = (int(tileID), int(chainID))
            tileIDchainIDToPotapovQuestID.setdefault(key, set()).add(potapovQuestID)
            if 'final' in tags:
                tileIDchainIDToFinalPotapovQuestID[key] = potapovQuestID
            if 'initial' in tags:
                tileIDchainIDToInitialPotapovQuestID[key] = potapovQuestID

        ResMgr.purge(xmlPath, True)
        return


class IClassifier(object):

    def __init__(self, questTags):
        pass

    @property
    def classificationAttr(self):
        raise NotImplementedError

    def matchVehicle(self, vehicleType):
        raise NotImplementedError


class ClassifierByClass(IClassifier):

    def __init__(self, questTags):
        super(ClassifierByClass, self).__init__(questTags)
        vehClasses = list(questTags & VEHICLE_CLASS_TAGS)
        if len(vehClasses) != 1:
            raise SoftException('Potapov quest with tags %s has more than one vehicle class' % str(questTags))
        self.vehClass = vehClasses[0]

    @property
    def classificationAttr(self):
        return self.vehClass

    def matchVehicle(self, vehicleType):
        vehClass = tuple(vehicles.VEHICLE_CLASS_TAGS & vehicleType.tags)[0]
        return vehClass == self.vehClass


class ClassifierByAlliance(IClassifier):

    def __init__(self, questTags):
        super(ClassifierByAlliance, self).__init__(questTags)
        alliances = list(questTags & ALLIANCES_TAGS)
        if len(alliances) != 1:
            raise SoftException('Potapov quest with tags %s has more than one alliance' % str(questTags))
        self.alliance = alliances[0]

    @property
    def classificationAttr(self):
        return self.alliance

    def matchVehicle(self, vehicleType):
        nationID = vehicleType.id[0]
        return nations.NAMES[nationID] in nations.ALLIANCE_TO_NATIONS[self.alliance]


class ClassifierByRole(IClassifier):

    def __init__(self, questTags):
        super(ClassifierByRole, self).__init__(questTags)
        commonRoles = COMMON_ROLE.ALL & questTags
        if len(commonRoles) != 1:
            raise SoftException('Potapov quest with tags %s must have exactly one common role' % str(questTags))
        self.commonRole = commonRole = next(iter(commonRoles))
        self.roles = COMMON_ROLE_TO_ROLE_TYPE[commonRole]

    @property
    def classificationAttr(self):
        return self.commonRole

    def matchVehicle(self, vehicleType):
        return vehicleType.role in self.roles


_MAP_BRANCH_TO_CLASSIFIER = {PQ_BRANCH.PM1_NAME: ClassifierByClass,
 PQ_BRANCH.PM2_NAME: ClassifierByAlliance,
 PQ_BRANCH.PM3_NAME: ClassifierByRole,
 PQ_BRANCH.PM4_NAME: ClassifierByRole}

class PQType(object):
    __slots__ = ('id', 'tags', 'isInitial', 'isFinal', 'branch', 'classifier', 'tileID', 'chainID', 'internalID', 'requiredUnlocks', 'generalQuestID', 'mainQuestID', 'mainAwardListQuestID', 'addQuestID', 'addAwardListQuestID', 'mainQuestInfo', 'addQuestInfo', 'userString', 'shortUserString', 'description', 'advice', 'minLevel', 'maxLevel', 'rewardByDemand', 'mainAwardListQuestInfo', 'addAwardListQuestInfo', 'branchName', 'isBranchWithAwardListQuests', 'isBranchWithoutAwardListQuests')

    def __init__(self, basicInfo):
        self.id = basicInfo['id']
        self.tags = tags = basicInfo['tags']
        self.isInitial = 'initial' in tags
        self.isFinal = 'final' in tags
        self.minLevel = basicInfo['minLevel']
        self.maxLevel = basicInfo['maxLevel']
        self.rewardByDemand = basicInfo['rewardByDemand']
        self.branch = basicInfo['branch']
        self.branchName = basicInfo['branchName']
        self.tileID = basicInfo['tileID']
        self.chainID = basicInfo['chainID']
        self.internalID = basicInfo['internalID']
        self.requiredUnlocks = basicInfo['requiredUnlocks']
        self.generalQuestID = basicInfo['name']
        self.mainQuestID = basicInfo['mainQuestID']
        self.mainAwardListQuestID = basicInfo['mainAwardListQuestID']
        self.addQuestID = basicInfo['addQuestID']
        self.addAwardListQuestID = basicInfo['addAwardListQuestID']
        classifierBuilder = _MAP_BRANCH_TO_CLASSIFIER.get(self.branchName)
        if classifierBuilder is None:
            raise SoftException('wrong potapov quest branch: %s' % self.branchName)
        self.classifier = classifierBuilder(self.tags)
        if IS_CLIENT or IS_WEB:
            self.mainQuestInfo = basicInfo['mainQuestInfo']
            self.mainAwardListQuestInfo = basicInfo['mainAwardListQuestInfo']
            self.addQuestInfo = basicInfo['addQuestInfo']
            self.addAwardListQuestInfo = basicInfo['addAwardListQuestInfo']
            self.userString = basicInfo['userString']
            self.shortUserString = basicInfo['shortUserString']
            self.description = basicInfo['description']
            self.advice = basicInfo['advice']
        self.isBranchWithAwardListQuests = self.branchName in PQ_BRANCH.WITH_AWARD_LIST_BRANCHES
        self.isBranchWithoutAwardListQuests = not self.isBranchWithAwardListQuests
        return

    def getMajorTag(self):
        return self.classifier.classificationAttr

    def maySelectQuest(self, unlockedQuests):
        return len(self.requiredUnlocks - frozenset(unlockedQuests)) == 0

    def areRequiredQuestsUnlockedOrSelectable(self, unlockedQuests):
        result = True
        requiredQuestIds = self.requiredUnlocks - frozenset(unlockedQuests)
        for requiredQuestId in requiredQuestIds:
            pqType = g_cache.questByPotapovQuestID(requiredQuestId)
            result &= pqType.maySelectQuest(unlockedQuests)

        return result

    def tryUnlockNextTile(self, potapovQuestsProgress):
        if not self.isFinal:
            return (False, [])
        tileInfo = g_tileCache.getTileInfo(self.tileID)
        nextTileIDs = tileInfo['nextTileIDs']
        if len(nextTileIDs) == 0:
            return (False, [])
        chainsCountToUnlockNext = tileInfo['chainsCountToUnlockNext']
        if chainsCountToUnlockNext == 0:
            return (False, [])
        completedQuestsCount = 0
        toUnlock = set()
        for chainID in xrange(1, tileInfo['chainsCount'] + 1):
            finalQuestID = g_cache.finalPotapovQuestIDByTileIDChainID(self.tileID, chainID)
            _, state = potapovQuestsProgress.get(finalQuestID)
            if state >= PQ_STATE.NEED_GET_ADD_REWARD:
                completedQuestsCount += 1
            if state == PQ_STATE.NONE:
                toUnlock.add(finalQuestID)

        return (completedQuestsCount >= chainsCountToUnlockNext, toUnlock)


class PQStorage(object):

    def __init__(self, compDescr=None, storage=None):
        if compDescr is not None:
            self.__compDescr = compDescr
            self.__quests = quests = {}
            if compDescr == '':
                return
            size = struct.unpack('<H', compDescr[:2])[0]
            lst = struct.unpack('<%sH' % size, compDescr[2:])
            for i in xrange(size):
                v = lst[i]
                quests[v >> 6 & 1023] = (v >> 3 & 7, v & 7)

        elif storage is not None:
            self.__compDescr = None
            self.__quests = storage
        return

    def keys(self):
        return list(self.__quests)

    def completedPQIDs(self):
        return [ k for k, v in viewitems(self.__quests) if v[1] >= PQ_STATE.NEED_GET_MAIN_REWARD ]

    def unlockedPQIDs(self):
        return [ k for k, v in viewitems(self.__quests) if v[1] >= PQ_STATE.UNLOCKED ]

    def __getitem__(self, id):
        return self.__quests[id]

    def __setitem__(self, id, value):
        oldValue = self.__quests.get(id, None)
        if oldValue == value:
            return
        else:
            self.__compDescr = None
            self.__quests[id] = value
            return

    def __contains__(self, id):
        return id in self.__quests

    def get(self, key, default=(PQ_FLAG.NONE, PQ_STATE.NONE)):
        return self.__quests.get(key, default)

    def pop(self, id):
        oldValue = self.__quests.get(id, None)
        if oldValue is None:
            return
        else:
            self.__compDescr = None
            self.__quests.pop(id)
            return

    def makeCompDescr(self):
        if self.__compDescr is not None:
            return self.__compDescr
        else:
            quests = self.__quests
            size = len(quests)
            packedValues = [ ((id & 1023) << 6) + ((flags & 7) << 3) + (state & 7) for id, (flags, state) in viewitems(quests) ]
            self.__compDescr = struct.pack(('<%sH' % (size + 1)), size, *packedValues)
            return self.__compDescr

    def iteritems(self):
        return iter(viewitems(self.__quests))

    def items(self):
        return viewitems(self.__quests)


def _readTags(xmlCtx, section, subsectionName):
    tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    for tagName in tagNames:
        if tagName not in _ALLOWED_TAG_NAMES:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)


def isWithoutAwardListBranchQuest(questName):
    branchName = questName.split('_', 1)[0]
    return branchName in PQ_BRANCH.WITHOUT_AWARD_LIST_BRANCHES


def getQuestBranchByQuestName(questName):
    branchName = questName.split('_', 1)[0]
    return branchName if branchName in PQ_BRANCH.ALL_NAMES else None
