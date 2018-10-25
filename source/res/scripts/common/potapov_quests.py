# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/potapov_quests.py
import time
import ResMgr
import struct
import quest_xml_source
import nations
from items import _xml, ItemsPrices, vehicles
from items.vehicles import VEHICLE_CLASS_TAGS
from constants import ITEM_DEFS_PATH, IS_CLIENT, IS_WEB, EVENT_TYPE, PERSONAL_MISSION_FREE_TOKEN_NAME, PERSONAL_MISSION_2_FREE_TOKEN_NAME, PERSONAL_MISSION_FINAL_PAWN_COST, PERSONAL_MISSION_2_FINAL_PAWN_COST
from nations import ALLIANCES_TAGS
from soft_exception import SoftException
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import *
POTAPOV_QUEST_XML_PATH = ITEM_DEFS_PATH + 'potapov_quests/'
_FALLOUT_BATTLE_TAGS = frozenset(('classic', 'multiteam'))
_ALLOWED_TAG_NAMES = ('initial', 'final') + tuple(_FALLOUT_BATTLE_TAGS) + tuple(VEHICLE_CLASS_TAGS) + tuple(ALLIANCES_TAGS)
g_cache = None
g_tileCache = None
g_seasonCache = None

class PQ_BRANCH():
    REGULAR = 0
    PERSONAL_MISSION_2 = 2
    NAME_TO_TYPE = {'regular': REGULAR,
     'pm2': PERSONAL_MISSION_2}
    TYPE_TO_NAME = dict(zip(NAME_TO_TYPE.values(), NAME_TO_TYPE.keys()))


PM_BRANCH_TO_FREE_TOKEN_NAME = {PQ_BRANCH.REGULAR: PERSONAL_MISSION_FREE_TOKEN_NAME,
 PQ_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FREE_TOKEN_NAME}
PM_BRANCH_TO_FINAL_PAWN_COST = {PQ_BRANCH.REGULAR: PERSONAL_MISSION_FINAL_PAWN_COST,
 PQ_BRANCH.PERSONAL_MISSION_2: PERSONAL_MISSION_2_FINAL_PAWN_COST}

def isPotapovQuestBranchEnabled(gameParams, branch):
    if branch == PQ_BRANCH.REGULAR:
        return gameParams['misc_settings']['isRegularQuestEnabled']
    return gameParams['misc_settings']['isPM2QuestEnabled'] if branch == PQ_BRANCH.PERSONAL_MISSION_2 else False


def isPotapovQuestTileEnabled(gameParams, pqType):
    return pqType.tileID not in gameParams['misc_settings']['disabledPMOperations']


def isPotapovQuestEnabled(gameParams, questID):
    return questID not in gameParams['misc_settings']['disabledPersonalMissions']


def isPotapovQuestBranchTileAndMissionEnabled(gameParams, pqType):
    return isPotapovQuestBranchEnabled(gameParams, pqType.branch) and isPotapovQuestTileEnabled(gameParams, pqType) and isPotapovQuestEnabled(gameParams, pqType.id)


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
     NEED_GET_MAIN_REWARD: (MAIN_REWARD_GOTTEN,),
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
        return self.__tilesInfo.iteritems()

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
            nextTileIDs = frozenset(map(int, _xml.readString(ctx, tsection, 'nextTileIDs').split()))
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

    def __init__(self):
        self.__potapovQuestIDToQuestType = {}
        self.__questUniqueIDToPotapovQuestID = {}
        self.__tileIDchainIDToPotapovQuestID = {}
        self.__tileIDchainIDToFinalPotapovQuestID = {}
        self.__tileIDchainIDToInitialPotapovQuestID = {}
        self.__readQuestList()

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
        return PQ_BRANCH.TYPE_TO_NAME[self.questByPotapovQuestID(potapovQuestID).branch]

    def __iter__(self):
        return self.__questUniqueIDToPotapovQuestID.iteritems()

    def __readQuestList(self):
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
            tileInfo = g_tileCache.getTileInfo(int(tileID))
            if 1 <= chainID <= tileInfo['chainsCount']:
                _xml.raiseWrongXml(ctx, '', 'quest chainID must be between 1 and %s' % tileInfo['chainsCount'])
            if 1 <= internalID <= tileInfo['questsInChain']:
                _xml.raiseWrongXml(ctx, '', 'quest internalID must be between 1 and %s' % tileInfo['chainsCount'])
            minLevel = _xml.readInt(ctx, qsection, 'minLevel', 1, 10)
            maxLevel = _xml.readInt(ctx, qsection, 'maxLevel', minLevel, 10)
            basicInfo = {'name': qname,
             'id': potapovQuestID,
             'branch': PQ_BRANCH.NAME_TO_TYPE[questBranchName],
             'tileID': int(tileID),
             'chainID': int(chainID),
             'internalID': int(internalID),
             'minLevel': minLevel,
             'maxLevel': maxLevel,
             'requiredUnlocks': frozenset(map(int, _xml.readString(ctx, qsection, 'requiredUnlocks').split()))}
            rewardByDemand = qsection.readInt('rewardByDemand', 0)
            if rewardByDemand != 0 and rewardByDemand not in PQ_REWARD_BY_DEMAND.keys():
                raise SoftException('Unexpected value for rewardByDemand')
            basicInfo['rewardByDemand'] = rewardByDemand
            tags = _readTags(ctx, qsection, 'tags')
            basicInfo['tags'] = tags
            if questBranchName == 'regular':
                if 0 == len(tags & VEHICLE_CLASS_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle class is not specified')
            if questBranchName == 'fallout':
                if 0 == len(tags & _FALLOUT_BATTLE_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest fallout type is not specified')
            if questBranchName == 'pm2':
                if 0 == len(tags & ALLIANCES_TAGS):
                    _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle class is not specified')
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(qsection.readString('userString'))
                basicInfo['shortUserString'] = i18n.makeString(qsection.readString('shortUserString'))
                basicInfo['description'] = i18n.makeString(qsection.readString('description'))
                basicInfo['advice'] = i18n.makeString(qsection.readString('advice'))
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
            nodes = xmlSource.readFromInternalFile(questPath, curTime)
            nodes = nodes.get(EVENT_TYPE.POTAPOV_QUEST, None)
            if nodes is None:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Potapov quests are not specified.')
            if len(nodes) != 4:
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
            qinfo = nodes[1].info
            if not qinfo['id'].endswith('main_award_list'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Main award list quest must be second.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['mainAwardListQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['mainAwardListQuestInfo'] = qinfo['questClientData']
            qinfo = nodes[2].info
            if not qinfo['id'].endswith('add'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Add quest must be third.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['addQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['addQuestInfo'] = qinfo['questClientData']
            qinfo = nodes[3].info
            if not qinfo['id'].endswith('add_award_list'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Add award list quest must be fourth.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['addAwardListQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['addAwardListQuestInfo'] = qinfo['questClientData']
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


class ClassifierByClass(object):

    def __init__(self, questTags):
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


class ClassifierByAlliance(object):

    def __init__(self, questTags):
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


class PQType(object):
    __slots__ = ('id', 'tags', 'isInitial', 'isFinal', 'branch', 'classifier', 'tileID', 'chainID', 'internalID', 'requiredUnlocks', 'generalQuestID', 'mainQuestID', 'mainAwardListQuestID', 'addQuestID', 'addAwardListQuestID', 'mainQuestInfo', 'addQuestInfo', 'userString', 'shortUserString', 'description', 'advice', 'minLevel', 'maxLevel', 'rewardByDemand', 'mainAwardListQuestInfo', 'addAwardListQuestInfo')

    def __init__(self, basicInfo):
        self.id = basicInfo['id']
        self.tags = tags = basicInfo['tags']
        self.isInitial = 'initial' in tags
        self.isFinal = 'final' in tags
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
        self.mainAwardListQuestID = basicInfo['mainAwardListQuestID']
        self.addQuestID = basicInfo['addQuestID']
        self.addAwardListQuestID = basicInfo['addAwardListQuestID']
        if self.branch == PQ_BRANCH.REGULAR:
            self.classifier = ClassifierByClass(self.tags)
        elif self.branch == PQ_BRANCH.PERSONAL_MISSION_2:
            self.classifier = ClassifierByAlliance(self.tags)
        else:
            raise SoftException('wrong potapov quest branch: %i' % self.branch)
        if IS_CLIENT or IS_WEB:
            self.mainQuestInfo = basicInfo['mainQuestInfo']
            self.mainAwardListQuestInfo = basicInfo['mainAwardListQuestInfo']
            self.addQuestInfo = basicInfo['addQuestInfo']
            self.addAwardListQuestInfo = basicInfo['addAwardListQuestInfo']
            self.userString = basicInfo['userString']
            self.shortUserString = basicInfo['shortUserString']
            self.description = basicInfo['description']
            self.advice = basicInfo['advice']

    def getMajorTag(self):
        return self.classifier.classificationAttr

    def maySelectQuest(self, unlockedQuests):
        return len(self.requiredUnlocks - frozenset(unlockedQuests)) == 0

    def maySelectQuestToPawn(self, unlockedQuests):
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
            flags, state = potapovQuestsProgress.get(finalQuestID)
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
        return self.__quests.keys()

    def completedPQIDs(self):
        return [ k for k, v in self.__quests.iteritems() if v[1] >= PQ_STATE.NEED_GET_MAIN_REWARD ]

    def unlockedPQIDs(self):
        return [ k for k, v in self.__quests.iteritems() if v[1] >= PQ_STATE.UNLOCKED ]

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
