# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/pm_quests.py
import time
import ResMgr
import struct
import quest_xml_source
import nations
from items import _xml, ItemsPrices, vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from constants import ARENA_BONUS_TYPE, ITEM_DEFS_PATH, IS_CLIENT, IS_WEB, EVENT_TYPE, PERSONAL_MISSION_FREE_TOKEN_NAME, PERSONAL_MISSION_2_FREE_TOKEN_NAME, PERSONAL_MISSION_FINAL_PAWN_COST, PERSONAL_MISSION_2_FINAL_PAWN_COST, PM3_LEVEL_TAGS, MAX_VEHICLE_LEVEL, PERSONAL_MISSION_3_FREE_TOKEN_NAME, PERSONAL_MISSION_3_FINAL_PAWN_COST, MIN_VEHICLE_LEVEL
from nations import ALLIANCES_TAGS
from soft_exception import SoftException
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import *
PM_QUEST_XML_PATH = ITEM_DEFS_PATH + 'personal_missions/'
_FALLOUT_BATTLE_TAGS = frozenset(('classic', 'multiteam'))
_ALLOWED_TAG_NAMES = ('initial',
 'final',
 'withoutAdd',
 'withoutPawn') + tuple(_FALLOUT_BATTLE_TAGS) + tuple(VEHICLE_CLASS_TAGS) + tuple(ALLIANCES_TAGS) + tuple(PM3_LEVEL_TAGS)
g_cache = None
g_tileCache = None
g_seasonCache = None

class PM_BRANCH():
    REGULAR = 0
    PERSONAL_MISSION_2 = 2
    PERSONAL_MISSION_3 = 3
    NAME_TO_TYPE = {'regular': REGULAR,
     'pm2': PERSONAL_MISSION_2,
     'pm3': PERSONAL_MISSION_3}
    TYPE_TO_NAME = dict(zip(NAME_TO_TYPE.values(), NAME_TO_TYPE.keys()))


BONUS_TYPE_TO_BRANCH = {ARENA_BONUS_TYPE.REGULAR: (PM_BRANCH.REGULAR, PM_BRANCH.PERSONAL_MISSION_2, PM_BRANCH.PERSONAL_MISSION_3),
 ARENA_BONUS_TYPE.EPIC_RANDOM: (PM_BRANCH.REGULAR, PM_BRANCH.PERSONAL_MISSION_2, PM_BRANCH.PERSONAL_MISSION_3)}
PM_BRANCH_TO_FREE_TOKEN_NAME = {PM_BRANCH.REGULAR: PERSONAL_MISSION_FREE_TOKEN_NAME,
 PM_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FREE_TOKEN_NAME,
 PM_BRANCH.PERSONAL_MISSION_3: PERSONAL_MISSION_3_FREE_TOKEN_NAME}
PM_BRANCH_TO_FINAL_PAWN_COST = {PM_BRANCH.REGULAR: PERSONAL_MISSION_FINAL_PAWN_COST,
 PM_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FINAL_PAWN_COST,
 PM_BRANCH.PERSONAL_MISSION_3: PERSONAL_MISSION_3_FINAL_PAWN_COST}

def isPMQuestBranchEnabled(gameParams, branch):
    if branch == PM_BRANCH.REGULAR:
        return gameParams['misc_settings']['isRegularQuestEnabled']
    if branch == PM_BRANCH.PERSONAL_MISSION_2:
        return gameParams['misc_settings']['isPM2QuestEnabled']
    return gameParams['misc_settings']['isPM3QuestEnabled'] if branch == PM_BRANCH.PERSONAL_MISSION_3 else False


def isPMQuestTileEnabled(gameParams, pmQuestType):
    return pmQuestType.tileID not in gameParams['misc_settings']['disabledPMOperations']


def isPMQuestEnabled(gameParams, questID):
    return questID not in gameParams['misc_settings']['disabledPersonalMissions']


def isPMQuestBranchTileAndMissionEnabled(gameParams, pmQuestType):
    return isPMQuestBranchEnabled(gameParams, pmQuestType.branch) and isPMQuestTileEnabled(gameParams, pmQuestType) and isPMQuestEnabled(gameParams, pmQuestType.id)


def isResetEnabled(gameParams, branch):
    return gameParams['misc_settings']['isPM3ResetEnabled'] if branch == PM_BRANCH.PERSONAL_MISSION_3 else True


class PM_STATE():
    NONE = 0
    UNLOCKED = 1
    NEED_GET_MAIN_REWARD = 2
    MAIN_REWARD_GOTTEN = 3
    NEED_GET_ADD_REWARD = 4
    NEED_GET_ALL_REWARDS = 5
    ALL_REWARDS_GOTTEN = 6
    NEXT_STATE = {NONE: (UNLOCKED, NEED_GET_MAIN_REWARD, NEED_GET_ALL_REWARDS),
     UNLOCKED: (NEED_GET_MAIN_REWARD, NEED_GET_ALL_REWARDS),
     NEED_GET_MAIN_REWARD: (MAIN_REWARD_GOTTEN,),
     MAIN_REWARD_GOTTEN: (NEED_GET_ADD_REWARD,),
     NEED_GET_ADD_REWARD: (ALL_REWARDS_GOTTEN,),
     NEED_GET_ALL_REWARDS: (ALL_REWARDS_GOTTEN,)}
    NEED_GET_REWARD = (NEED_GET_MAIN_REWARD, NEED_GET_ADD_REWARD, NEED_GET_ALL_REWARDS)
    COMPLETED = (ALL_REWARDS_GOTTEN, NEED_GET_ALL_REWARDS, NEED_GET_ADD_REWARD)


class PM_FLAG():
    NONE = 0
    PAUSE = 1


PM_REWARD_BY_DEMAND = {1: (PM_STATE.NEED_GET_MAIN_REWARD, PM_STATE.NEED_GET_ALL_REWARDS),
 2: (PM_STATE.NEED_GET_ADD_REWARD, PM_STATE.NEED_GET_ALL_REWARDS),
 3: (PM_STATE.NEED_GET_MAIN_REWARD, PM_STATE.NEED_GET_ADD_REWARD, PM_STATE.NEED_GET_ALL_REWARDS)}

def init():
    global g_cache
    global g_tileCache
    global g_seasonCache
    g_seasonCache = SeasonCache()
    g_tileCache = TileCache()
    g_cache = PMCache()


class SeasonCache():

    def __init__(self):
        self.__seasonsInfo = {}
        self.__readSeasons()

    def getSeasonInfo(self, seasonID):
        if seasonID not in self.__seasonsInfo:
            raise SoftException('Invalid season id (%s)' % (seasonID,))
        return self.__seasonsInfo[seasonID]

    def __readSeasons(self):
        xmlPath = PM_QUEST_XML_PATH + '/seasons.xml'
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
        return self.__tilesInfo.iteritems()

    def __readTiles(self):
        xmlPath = PM_QUEST_XML_PATH + '/tiles.xml'
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
            tileID = _xml.readInt(ctx, tsection, 'id', 0)
            if tileID in idToTile:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            chainsCount = _xml.readInt(ctx, tsection, 'chainsCount', 1)
            chainsCountToUnlockNext = _xml.readInt(ctx, tsection, 'chainsCountToUnlockNext', 0, chainsCount)
            nextTileIDs = frozenset(map(int, _xml.readString(ctx, tsection, 'nextTileIDs').split()))
            achievements = {}
            basicInfo = {'name': tname,
             'chainsCount': chainsCount,
             'nextTileIDs': nextTileIDs,
             'chainsCountToUnlockNext': chainsCountToUnlockNext,
             'questsInChain': _xml.readInt(ctx, tsection, 'questsInChain', 1),
             'completeChainWithoutAdd': _xml.readBool(ctx, tsection, 'completeChainWithoutAdd', False),
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


class PMCache(object):

    def __init__(self):
        self.__pmQuestIDToQuestType = {}
        self.__questUniqueIDToPMQuestID = {}
        self.__tileIDchainIDToPMQuestID = {}
        self.__tileIDchainIDToFinalpmQuestsIDs = {}
        self.__tileIDchainIDToInitialpmQuestsIDs = {}
        self.__readQuestList()

    def questByPMQuestID(self, pmQuestID):
        if pmQuestID not in self.__pmQuestIDToQuestType:
            raise SoftException('Invalid personal mission quest id (%s)' % (pmQuestID,))
        return self.__pmQuestIDToQuestType[pmQuestID]

    def hasPMQuest(self, pmQuestID):
        return pmQuestID in self.__pmQuestIDToQuestType

    def getPMQuests(self):
        return self.__pmQuestIDToQuestType

    def questByUniqueQuestID(self, uniqueQuestID):
        return self.questByPMQuestID(self.getPMQuestIDByUniqueID(uniqueQuestID))

    def isPMQuest(self, uniqueQuestID):
        return uniqueQuestID in self.__questUniqueIDToPMQuestID

    def questListByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToPMQuestID[tileID, chainID]

    def finalpmQuestsIDsByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToFinalpmQuestsIDs[tileID, chainID]

    def initialpmQuestsIDsByTileIDChainID(self, tileID, chainID):
        return self.__tileIDchainIDToInitialpmQuestsIDs[tileID, chainID]

    def getPMQuestIDByUniqueID(self, uniqueQuestID):
        if uniqueQuestID not in self.__questUniqueIDToPMQuestID:
            raise SoftException('Invalid personal mission quest name (%s)' % (uniqueQuestID,))
        return self.__questUniqueIDToPMQuestID[uniqueQuestID]

    def branchByPMQuestID(self, pmQuestID):
        return PM_BRANCH.TYPE_TO_NAME[self.questByPMQuestID(pmQuestID).branch]

    def __iter__(self):
        return self.__questUniqueIDToPMQuestID.iteritems()

    def __readQuestList(self):
        xmlPath = PM_QUEST_XML_PATH + '/list.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__pmQuestIDToQuestType = idToQuest = {}
        self.__questUniqueIDToPMQuestID = questUniqueNameToPMQuestID = {}
        self.__tileIDchainIDToPMQuestID = tileIDchainIDToPMQuestID = {}
        self.__tileIDchainIDToFinalpmQuestsIDs = tileIDchainIDToFinalpmQuestsIDs = {}
        self.__tileIDchainIDToInitialpmQuestsIDs = tileIDchainIDToInitialpmQuestsIDs = {}
        ids = {}
        curTime = int(time.time())
        xmlSource = quest_xml_source.Source()
        for qname, qsection in section.items():
            splitted = qname.split('_')
            ctx = (None, xmlPath)
            if qname in ids:
                _xml.raiseWrongXml(ctx, '', 'personal mission quest name is not unique')
            pmQuestID = _xml.readInt(ctx, qsection, 'id', 0, 1023)
            if pmQuestID in idToQuest:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            questBranchName, tileID, chainID, internalID = splitted
            tileInfo = g_tileCache.getTileInfo(int(tileID))
            if not 1 <= int(chainID) <= tileInfo['chainsCount']:
                _xml.raiseWrongXml(ctx, '', 'quest chainID must be between 1 and %s' % tileInfo['chainsCount'])
            if not 1 <= int(internalID) <= tileInfo['questsInChain']:
                _xml.raiseWrongXml(ctx, '', 'quest internalID must be between 1 and %s' % tileInfo['chainsCount'])
            minLevel = _xml.readInt(ctx, qsection, 'minLevel', MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL)
            maxLevel = _xml.readInt(ctx, qsection, 'maxLevel', minLevel, MAX_VEHICLE_LEVEL)
            basicInfo = {'name': qname,
             'id': pmQuestID,
             'branch': PM_BRANCH.NAME_TO_TYPE[questBranchName],
             'tileID': int(tileID),
             'chainID': int(chainID),
             'internalID': int(internalID),
             'minLevel': minLevel,
             'maxLevel': maxLevel,
             'requiredUnlocks': frozenset(map(int, _xml.readString(ctx, qsection, 'requiredUnlocks').split()))}
            rewardByDemand = qsection.readInt('rewardByDemand', 0)
            if rewardByDemand != 0 and rewardByDemand not in PM_REWARD_BY_DEMAND.keys():
                raise SoftException('Unexpected value for rewardByDemand')
            basicInfo['rewardByDemand'] = rewardByDemand
            tags = _readTags(ctx, qsection, 'tags')
            basicInfo['tags'] = tags
            if questBranchName == 'regular':
                if 0 == len(tags & VEHICLE_CLASS_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle class is not specified')
            elif questBranchName == 'fallout':
                if 0 == len(tags & _FALLOUT_BATTLE_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest fallout type is not specified')
            elif questBranchName == 'pm2':
                if 0 == len(tags & ALLIANCES_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest alliance is not specified')
            elif questBranchName == 'pm3':
                if 0 == len(tags & PM3_LEVEL_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest branch is not specified')
            else:
                raise SoftException('Unknown personal mission quest branch - %s' % questBranchName)
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(qsection.readString('userString'))
                basicInfo['shortUserString'] = i18n.makeString(qsection.readString('shortUserString'))
                basicInfo['description'] = qsection.readString('description')
                basicInfo['advice'] = qsection.readString('advice')
            questPath = ''.join([PM_QUEST_XML_PATH,
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
            nodes = xmlSource.readFromInternalFile(questPath, curTime)
            nodes = nodes.get(EVENT_TYPE.PERSONAL_MISSION, None)
            if nodes is None:
                _xml.raiseWrongXml(questCtx, 'personalMissionQuest', 'Personal Missions quests are not specified.')
            withoutAdd = 'withoutAdd' in tags
            withoutPawn = 'withoutPawn' in tags
            if withoutAdd and not withoutPawn:
                _xml.raiseWrongXml(questCtx, 'personalMissionQuest', 'We dont support quests with pawn, but without add')
            questsOrder = (('_main',
              'mainQuestID',
              'mainQuestInfo',
              True),
             ('_main_award_list',
              'mainAwardListQuestID',
              'mainAwardListQuestInfo',
              not withoutPawn),
             ('_add',
              'addQuestID',
              'addQuestInfo',
              not withoutAdd or not withoutPawn),
             ('_add_award_list',
              'addAwardListQuestID',
              'addAwardListQuestInfo',
              not withoutPawn))
            count = 0
            for postfix, internalQuestName, clientInfoName, isExist in questsOrder:
                if isExist:
                    qInfo = nodes[count].info
                    questName = qInfo['id']
                    if questName != qname + postfix:
                        _xml.raiseWrongXml(questCtx, 'personalMissionQuest', 'Unknown quest {}(place {})'.format(questName, count))
                    if questName in questUniqueNameToPMQuestID:
                        _xml.raiseWrongXml(questCtx, 'personalMissionQuest', 'Duplicate name detected({}).'.format(questName))
                    questUniqueNameToPMQuestID[questName] = pmQuestID
                    basicInfo[internalQuestName] = questName
                    if IS_CLIENT or IS_WEB:
                        basicInfo[clientInfoName] = qInfo['questClientData']
                    count += 1

            if len(nodes) != count:
                _xml.raiseWrongXml(questCtx, 'personalMissionQuest', 'Must be presented {} quests.'.format(count))
            idToQuest[pmQuestID] = PMQuestType(basicInfo)
            ids[qname] = pmQuestID
            key = (int(tileID), int(chainID))
            tileIDchainIDToPMQuestID.setdefault(key, []).append(pmQuestID)
            if 'final' in tags:
                tileIDchainIDToFinalpmQuestsIDs.setdefault(key, []).append(pmQuestID)
            if 'initial' in tags:
                tileIDchainIDToInitialpmQuestsIDs.setdefault(key, []).append(pmQuestID)

        if len(idToQuest) != sum((tileInfo['chainsCount'] * tileInfo['questsInChain'] for _, tileInfo in g_tileCache)):
            _xml.raiseWrongXml(None, xmlPath, 'Exists chains with missed quests')
        for tileID, tileInfo in g_tileCache:
            for chainID in xrange(1, tileInfo['chainsCount'] + 1):
                key = (int(tileID), int(chainID))
                quests = tileIDchainIDToPMQuestID.get(key)
                initialQuests = tileIDchainIDToInitialpmQuestsIDs.get(key)
                finalQuests = tileIDchainIDToFinalpmQuestsIDs.get(key)
                if len(initialQuests) != len(finalQuests):
                    _xml.raiseWrongXml(None, xmlPath, 'Initial quests count != final quests count')
                quests.sort()
                initialQuests.sort()
                finalQuests.sort()
                if quests[-1] - quests[0] + 1 != tileInfo['questsInChain']:
                    _xml.raiseWrongXml(None, xmlPath, 'Quests must be placed sequentially in chain')
                questsCount = 0
                lastFinalQuestIdx = -1
                for initialQuest, finalQuest in zip(initialQuests, finalQuests):
                    questsCount += finalQuest - initialQuest + 1
                    if lastFinalQuestIdx >= initialQuest:
                        _xml.raiseWrongXml(None, xmlPath, 'Different initial and final quests have intersection')
                    lastFinalQuestIdx = finalQuest

                if questsCount != tileInfo['questsInChain']:
                    _xml.raiseWrongXml(None, xmlPath, 'All quests must be between initial and final quest')

        ResMgr.purge(xmlPath, True)
        return


class IClassifier(object):

    @property
    def classificationAttr(self):
        raise NotImplementedError

    def matchVehicle(self, vehicleType):
        raise NotImplementedError

    def getAllClassificationAttrs(self):
        raise NotImplementedError


class BaseClassifier(IClassifier):
    CLASSIFIER_ALIAS = None

    def getAllClassificationAttrs(self):
        return {self.CLASSIFIER_ALIAS: self.classificationAttr}


class CompositeClassifier(IClassifier):

    def __init__(self, classifiers):
        if len(classifiers) < 2:
            raise SoftException('Attempted to build composite classifier with less than 2 classifiers')
        self.__classifiers = classifiers

    @property
    def classificationAttr(self):
        return self.__classifiers[0].classificationAttr

    def getAllClassificationAttrs(self):
        return {classifier.CLASSIFIER_ALIAS:classifier.classificationAttr for classifier in self.__classifiers}

    def matchVehicle(self, vehicleType):
        return all((classifier.matchVehicle(vehicleType) for classifier in self.__classifiers))


class ClassifierByClass(BaseClassifier):
    CLASSIFIER_ALIAS = 'vehType'

    def __init__(self, classTags):
        classTags = tuple(classTags)
        if len(classTags) != 1:
            raise SoftException('Personal Mission quest with tags %s has more than one vehicle class' % str(classTags))
        self.vehClass = classTags[0]

    @property
    def classificationAttr(self):
        return self.vehClass

    def matchVehicle(self, vehicleType):
        vehClass = tuple(vehicles.VEHICLE_CLASS_TAGS & vehicleType.tags)[0]
        return vehClass == self.vehClass


class ClassifierByAlliance(BaseClassifier):
    CLASSIFIER_ALIAS = 'alliance'

    def __init__(self, allianceTags):
        allianceTags = tuple(allianceTags)
        if len(allianceTags) != 1:
            raise SoftException('Personal Mission quest with tags %s has more than one alliance' % str(allianceTags))
        self.alliance = allianceTags[0]

    @property
    def classificationAttr(self):
        return self.alliance

    def matchVehicle(self, vehicleType):
        nationID = vehicleType.id[0]
        return nations.NAMES[nationID] in nations.ALLIANCE_TO_NATIONS[self.alliance]


class ClassifierByLevel(BaseClassifier):
    CLASSIFIER_ALIAS = 'levelGroup'

    def __init__(self, levelTags):
        levelTags = tuple(levelTags)
        if len(levelTags) != 1:
            raise SoftException('Personal Mission quest with tags %s has more than one branch' % str(levelTags))
        self.level = levelTags[0]

    @property
    def classificationAttr(self):
        return self.level

    def matchVehicle(self, vehicleType):
        return True


class PMQuestType(object):
    __slots__ = ('id', 'tags', 'isInitial', 'isFinal', 'withAdd', 'withPawn', 'branch', 'classifier', 'tileID', 'chainID', 'internalID', 'requiredUnlocks', 'generalQuestID', 'mainQuestID', 'mainAwardListQuestID', 'addQuestID', 'addAwardListQuestID', 'mainQuestInfo', 'addQuestInfo', 'userString', 'shortUserString', 'description', 'advice', 'minLevel', 'maxLevel', 'rewardByDemand', 'mainAwardListQuestInfo', 'addAwardListQuestInfo')

    def __init__(self, basicInfo):
        self.id = basicInfo['id']
        self.tags = tags = basicInfo['tags']
        self.isInitial = 'initial' in tags
        self.isFinal = 'final' in tags
        self.withAdd = 'withoutAdd' not in tags
        self.withPawn = 'withoutPawn' not in tags
        self.minLevel = basicInfo['minLevel']
        self.maxLevel = basicInfo['maxLevel']
        self.rewardByDemand = basicInfo['rewardByDemand']
        self.branch = basicInfo['branch']
        self.tileID = basicInfo['tileID']
        self.chainID = basicInfo['chainID']
        self.internalID = basicInfo['internalID']
        self.requiredUnlocks = basicInfo['requiredUnlocks']
        self.generalQuestID = basicInfo['name']
        self.mainQuestID = basicInfo['mainQuestID']
        self.mainAwardListQuestID = basicInfo.get('mainAwardListQuestID', None)
        self.addQuestID = basicInfo.get('addQuestID', None)
        self.addAwardListQuestID = basicInfo.get('addAwardListQuestID', None)
        self.classifier = _buildClassifier(self.tags)
        if self.classifier is None:
            raise SoftException('wrong personal mission quest branch: %i' % self.branch)
        if IS_CLIENT or IS_WEB:
            self.mainQuestInfo = basicInfo['mainQuestInfo']
            self.mainAwardListQuestInfo = basicInfo.get('mainAwardListQuestInfo')
            self.addQuestInfo = basicInfo.get('addQuestInfo')
            self.addAwardListQuestInfo = basicInfo.get('addAwardListQuestInfo')
            self.userString = basicInfo['userString']
            self.shortUserString = basicInfo['shortUserString']
            self.description = basicInfo['description']
            self.advice = basicInfo['advice']
        return

    def getMajorTag(self):
        return self.classifier.classificationAttr

    def maySelectQuest(self, unlockedQuests):
        return len(self.requiredUnlocks - frozenset(unlockedQuests)) == 0

    def maySelectQuestToPawn(self, unlockedQuests):
        requiredQuestIds = self.requiredUnlocks - frozenset(unlockedQuests)
        for requiredQuestId in requiredQuestIds:
            pmQuestType = g_cache.questByPMQuestID(requiredQuestId)
            if not pmQuestType.maySelectQuest(unlockedQuests):
                return False

        return True

    def tryUnlockNextTile(self, pmQuestsProgress):
        if not self.isFinal:
            return (False, [])
        tileInfo = g_tileCache.getTileInfo(self.tileID)
        nextTileIDs = tileInfo['nextTileIDs']
        if len(nextTileIDs) == 0:
            return (False, [])
        chainsCountToUnlockNext = tileInfo['chainsCountToUnlockNext']
        if chainsCountToUnlockNext == 0:
            return (False, [])
        completedChainsCount = 0
        toUnlock = set()
        minimalState = PM_STATE.NEED_GET_ADD_REWARD
        if tileInfo['completeChainWithoutAdd']:
            minimalState = PM_STATE.NEED_GET_MAIN_REWARD
        for chainID in xrange(1, tileInfo['chainsCount'] + 1):
            isChainCompleted = True
            finalQuestIDs = g_cache.finalpmQuestsIDsByTileIDChainID(self.tileID, chainID)
            for finalQuestID in finalQuestIDs:
                _, state = pmQuestsProgress.get(finalQuestID)
                if state < minimalState:
                    isChainCompleted = False
                    if state == PM_STATE.NONE:
                        toUnlock.add(finalQuestID)

            completedChainsCount += isChainCompleted

        return (completedChainsCount >= chainsCountToUnlockNext, toUnlock)

    def getQuestsToExecute(self, pmQuestsProgress):
        result = []
        _, state = pmQuestsProgress.get(self.id)
        if state < PM_STATE.NEED_GET_ADD_REWARD:
            if state < PM_STATE.NEED_GET_MAIN_REWARD:
                result.append(self.mainQuestID)
                if self.withPawn:
                    result.append(self.mainAwardListQuestID)
            if self.withAdd:
                result.append(self.addQuestID)
                if self.withPawn:
                    result.append(self.addAwardListQuestID)
        return result

    def canBeCompleted(self, pmQuestsProgress):
        _, state = pmQuestsProgress.get(self.id)
        if state < PM_STATE.NEED_GET_ADD_REWARD:
            if state < PM_STATE.NEED_GET_MAIN_REWARD:
                return True
            if self.withAdd:
                return True
        return False


class PMStorage(object):

    def __init__(self, compDescr=None, storage=None, storageW=None):
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

            self.__questsW = lambda : quests
        elif storage is not None:
            self.__compDescr = None
            self.__quests = storage
            self.__questsW = storageW or (lambda : storage)
        return

    def keys(self):
        return self.__quests.keys()

    def completedPMQuestsIDs(self):
        return [ k for k, v in self.__quests.iteritems() if v[1] >= PM_STATE.NEED_GET_MAIN_REWARD ]

    def unlockedPMQuestsIDs(self):
        return [ k for k, v in self.__quests.iteritems() if v[1] >= PM_STATE.UNLOCKED ]

    def __getitem__(self, id):
        return self.__quests[id]

    def __setitem__(self, id, value):
        oldValue = self.__quests.get(id, None)
        if oldValue == value:
            return
        else:
            self.__compDescr = None
            self.__questsW()[id] = value
            return

    def __contains__(self, id):
        return id in self.__quests

    def get(self, key, default=(PM_FLAG.NONE, PM_STATE.NONE)):
        return self.__quests.get(key, default)

    def pop(self, id):
        oldValue = self.__quests.get(id, None)
        if oldValue is None:
            return
        else:
            self.__compDescr = None
            self.__questsW().pop(id)
            return

    def makeCompDescr(self):
        if self.__compDescr is not None:
            return self.__compDescr
        else:
            quests = self.__quests
            size = len(quests)
            packedValues = [ ((id & 1023) << 6) + ((flags & 7) << 3) + (state & 7) for id, (flags, state) in quests.iteritems() ]
            self.__compDescr = struct.pack(('<%sH' % (size + 1)), size, *packedValues)
            return self.__compDescr

    def iteritems(self):
        return self.__quests.iteritems()


def _readTags(xmlCtx, section, subsectionName):
    tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    for tagName in tagNames:
        if tagName not in _ALLOWED_TAG_NAMES:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)


def _buildClassifier(tags):
    classTags = tuple(tags & VEHICLE_CLASS_TAGS)
    allianceTags = tuple(tags & ALLIANCES_TAGS)
    levelTags = tuple(tags & PM3_LEVEL_TAGS)
    if not classTags and not allianceTags and not levelTags:
        raise SoftException('Personal Mission quest with tags %s has no tags defined' % str(tags))
    if classTags and allianceTags:
        return CompositeClassifier((ClassifierByAlliance(allianceTags), ClassifierByClass(classTags)))
    if classTags:
        return ClassifierByClass(classTags)
    if allianceTags:
        return ClassifierByAlliance(allianceTags)
    return ClassifierByLevel(levelTags) if levelTags else None
