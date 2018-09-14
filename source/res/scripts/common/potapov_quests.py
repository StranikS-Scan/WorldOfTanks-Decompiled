# Embedded file name: scripts/common/potapov_quests.py
import time
import ResMgr
import struct
import quest_xml_source
from items import _xml
from items.vehicles import VEHICLE_CLASS_TAGS
from constants import ITEM_DEFS_PATH, IS_CLIENT, IS_WEB, EVENT_TYPE
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import *
_POTAPOV_QUEST_XML_PATH = ITEM_DEFS_PATH + 'potapov_quests/'
_ALLOWED_TAG_NAMES = ('initial', 'final') + tuple(VEHICLE_CLASS_TAGS)
g_cache = None

def init():
    global g_cache
    g_cache = PQCache()


class PQCache(object):

    def __init__(self):
        self.__potapovQuestIDToQuestType = {}
        self.questUniqueNameToPotapovQuestID = {}
        self.__readQuestList()

    def questByPotapovQuestID(self, potapovQuestID):
        if potapovQuestID not in self.__potapovQuestIDToQuestType:
            raise Exception, 'Invalid potapov quest id (%s)' % (potapovQuestID,)
        return self.__potapovQuestIDToQuestType[potapovQuestID]

    def questByUniqueQuestID(self, uniqueQuestID):
        if uniqueQuestID not in self.__questUniqueIDToPotapovQuestID:
            raise Exception, 'Invalid potapov quest name (%s)' % (uniqueQuestID,)
        return self.questByPotapovQuestID(self.__questUniqueIDToPotapovQuestID[uniqueQuestID])

    def isPotapovQuest(self, uniqueQuestID):
        return uniqueQuestID in self.__questUniqueIDToPotapovQuestID

    def __readQuestList(self):
        xmlPath = _POTAPOV_QUEST_XML_PATH + '/list.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        self.__potapovQuestIDToQuestType = idToQuest = {}
        self.__questUniqueIDToPotapovQuestID = questUniqueNameToPotapovQuestID = {}
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
            _, difficulty, internalID = splitted
            if 1 <= difficulty <= 4:
                _xml.raiseWrongXml(ctx, '', 'quest difficulty must be between 1 and 4')
            if 1 <= internalID <= 15:
                _xml.raiseWrongXml(ctx, '', 'quest internalID must be between 1 and 15')
            ids[qname] = potapovQuestID
            basicInfo = {'name': qname,
             'id': potapovQuestID,
             'difficulty': int(difficulty),
             'internalID': int(internalID),
             'requiredUnlocks': frozenset(map(int, _xml.readString(ctx, qsection, 'requiredUnlocks').split()))}
            tags = _readTags(ctx, qsection, 'tags')
            if 0 == len(tags & VEHICLE_CLASS_TAGS):
                _xml.raiseWrongXml(ctx, 'tags', 'quest vehicle class tag is not specified')
            basicInfo['tags'] = tags
            if IS_CLIENT or IS_WEB:
                basicInfo['userString'] = i18n.makeString(qsection.readString('userString'))
                basicInfo['description'] = i18n.makeString(qsection.readString('description'))
            questPath = _POTAPOV_QUEST_XML_PATH + '/'.join(splitted[:2]) + '/' + qname + '.xml'
            questCtx = (None, questPath)
            nodes = xmlSource.readFromInternalFile(questPath, curTime)
            nodes = nodes.get(EVENT_TYPE.POTAPOV_QUEST, None)
            if nodes is None:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Potapov quests are not specified.')
            if len(nodes) != 2:
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
            if not qinfo['id'].endswith('add'):
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Add quest must be second.')
            if qinfo['id'] in questUniqueNameToPotapovQuestID:
                _xml.raiseWrongXml(questCtx, 'potapovQuest', 'Duplicate name detected.')
            questUniqueNameToPotapovQuestID[qinfo['id']] = potapovQuestID
            basicInfo['addQuestID'] = qinfo['id']
            if IS_CLIENT or IS_WEB:
                basicInfo['addQuestInfo'] = qinfo['questClientData']
            idToQuest[potapovQuestID] = PQType(basicInfo)

        ResMgr.purge(xmlPath, True)
        return


class PQType(object):
    __slots__ = ('id', 'tags', 'isInitial', 'isFinal', 'vehClasses', 'difficulty', 'internalID', 'requiredUnlocks', 'mainQuestID', 'addQuestID', 'mainQuestInfo', 'addQuestInfo', 'userString', 'description')

    def __init__(self, basicInfo):
        self.id = basicInfo['id']
        self.tags = tags = basicInfo['tags']
        self.isInitial = 'initial' in tags
        self.isFinal = 'final' in tags
        vehClasses = list(tags & VEHICLE_CLASS_TAGS)
        vehClasses.sort()
        self.vehClasses = tuple(vehClasses)
        self.difficulty = basicInfo['difficulty']
        self.internalID = basicInfo['internalID']
        self.requiredUnlocks = basicInfo['requiredUnlocks']
        self.mainQuestID = basicInfo['mainQuestID']
        self.addQuestID = basicInfo['addQuestID']
        if IS_CLIENT or IS_WEB:
            self.mainQuestInfo = basicInfo['mainQuestInfo']
            self.addQuestInfo = basicInfo['addQuestInfo']
            self.userString = basicInfo['userString']
            self.description = basicInfo['description']

    def maySelectQuest(self, unlockedQuests):
        return len(self.requiredUnlocks - frozenset(unlockedQuests)) == 0


class PQStorage(object):

    def __init__(self, compDescr = None, storage = None):
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
        else:
            raise False or AssertionError
        return

    def keys(self):
        return self.__quests.keys()

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


class PQ_STATE:
    MAIN_COND_COMPLETED = 1
    TWO_COND_COMPLETED = 2


def _readTags(xmlCtx, section, subsectionName):
    tagNames = _xml.readString(xmlCtx, section, subsectionName).split()
    res = set()
    for tagName in tagNames:
        if tagName not in _ALLOWED_TAG_NAMES:
            _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown tag '%s'" % tagName)
        res.add(intern(tagName))

    return frozenset(res)
