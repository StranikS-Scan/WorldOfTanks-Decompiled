# Embedded file name: scripts/client/gui/server_events/caches.py
from collections import namedtuple
from debug_utils import LOG_ERROR
from gui import nationCompareByIndex, getNationIndex
from gui.shared.utils.decorators import ReprInjector
from gui.shared.gui_items.Vehicle import VEHICLE_TYPES_ORDER_INDICES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES as _QA
_g_sortedVehs = {}
VehiclesListProps = namedtuple('VehiclesListProps', ['disableChecker',
 'nationIdx',
 'vehTypeIdx',
 'levelIdx',
 'selectedBtn',
 'sortDirect',
 'checkbox'])

def getVehiclesData(listID):
    return _g_sortedVehs.get(listID)


def addVehiclesData(listID, vehs, disableChecker = None, nationIdx = -1, vehTypeIdx = -1, levelIdx = -1, selectedBtn = None, sortDirect = None, checkbox = None):
    listID = str(listID)
    if listID in _g_sortedVehs:
        _, props = _g_sortedVehs[listID]
    else:
        props = VehiclesListProps(disableChecker, nationIdx, vehTypeIdx, levelIdx, selectedBtn, sortDirect, checkbox)
    _g_sortedVehs[listID] = (vehs, props)
    return props


def updateVehiclesDataProps(listID, **kwargs):
    if listID in _g_sortedVehs:
        vehs, props = _g_sortedVehs[listID]
        _g_sortedVehs[listID] = (vehs, props._replace(**kwargs))


def clearVehiclesData():
    _g_sortedVehs.clear()


PQ_TABS = (_QA.SEASON_VIEW_TAB_RANDOM, _QA.SEASON_VIEW_TAB_FALLOUT)

class QuestInfo(object):
    __slots__ = ('questID',)

    def __init__(self, *args):
        super(QuestInfo, self).__init__()
        raise len(args) == len(self.__slots__) or AssertionError
        for idx, fieldName in enumerate(self.__slots__):
            object.__setattr__(self, fieldName, args[idx])

    def __setattr__(self, key, value):
        raise AssertionError

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self.__slots__:
                object.__setattr__(self, key, value)
            else:
                LOG_ERROR('Unsupported argument for object:', self, key, value)

        return self

    def clear(self):
        for field_name in self.__slots__:
            object.__setattr__(self, field_name, None)

        return


class PQInfo(QuestInfo):
    __slots__ = ('tileID', 'questID', 'filters')


@ReprInjector.simple('tabID', 'random', 'falloutQuests', 'common', 'tutorial')

class _NavigationInfo(object):

    def __init__(self):
        self.tabID = None
        self.random = PQInfo(None, None, None)
        self.falloutQuests = PQInfo(None, None, None)
        self.common = QuestInfo(None)
        self.tutorial = QuestInfo(None)
        self.__selectedPQType = _QA.SEASON_VIEW_TAB_RANDOM
        return

    @property
    def selectedPQ(self):
        if self.__selectedPQType == _QA.SEASON_VIEW_TAB_RANDOM:
            return self.random
        else:
            return self.falloutQuests

    @property
    def selectedPQType(self):
        return self.__selectedPQType

    def setPQTypeByTabID(self, tabID):
        if tabID in PQ_TABS:
            self.__selectedPQType = tabID
        else:
            LOG_ERROR('Wrong tabID to set as selected PQ type')

    def selectTab(self, tabID, doResetNavInfo = False):
        if doResetNavInfo:
            if tabID == _QA.TAB_PERSONAL_QUESTS:
                self.random.clear()
                self.falloutQuests.clear()
            else:
                self.common.clear()
        self.tabID = tabID

    def selectPotapovQuest(self, tileID, questID = None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.selectedPQ.update(tileID=tileID, questID=questID)

    def selectRandomQuest(self, tileID, questID = None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.__selectedPQType = _QA.SEASON_VIEW_TAB_RANDOM
        self.random = self.random.update(tileID=tileID, questID=questID)

    def selectFalloutQuest(self, tileID, questID = None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.__selectedPQType = _QA.SEASON_VIEW_TAB_FALLOUT
        self.falloutQuests = self.falloutQuests.update(tileID=tileID, questID=questID)

    def changePQFilters(self, *args):
        self.selectedPQ.update(filters=args)

    def selectCommonQuest(self, questID):
        self.tabID = _QA.TAB_COMMON_QUESTS
        self.common = self.common.update(questID=questID)

    def selectTutorialQuest(self, questID):
        self.tabID = _QA.TAB_BEGINNER_QUESTS
        self.tutorial = self.tutorial.update(questID=questID)


_g_navInfo = None

def getNavInfo():
    global _g_navInfo
    if _g_navInfo is None:
        _g_navInfo = _NavigationInfo()
    return _g_navInfo


def clearNavInfo():
    global _g_navInfo
    _g_navInfo = None
    return


_SORTINGS = {'nation': lambda (veh1, _), (veh2, __): nationCompareByIndex(veh1.nationID, veh2.nationID),
 'type': lambda (veh1, _), (veh2, __): veh1._sortByType(veh2),
 'level': lambda (veh1, _), (veh2, __): veh1.level - veh2.level,
 'vName': lambda (veh1, _), (veh2, __): cmp(veh1.userName, veh2.userName),
 'notAvailable': lambda (_, vData1), (__, vData2): cmp(vData1[0], vData2[0]),
 'discount': lambda (_, vData1), (__, vData2): cmp(vData1[1], vData2[1])}

def sortVehTable(tableID, btnID, direction, nation = None, vehType = None, level = None, cbSelected = None, isAction = None):
    result = []
    vehData = getVehiclesData(tableID)
    if vehData is None:
        return result
    else:
        vehList, props = vehData
        updateVehiclesDataProps(tableID, nationIdx=nation, vehTypeIdx=vehType, levelIdx=level, selectedBtn=btnID, sortDirect=direction, checkbox=cbSelected)
        for v, data in vehList:
            if nation != -1 and getNationIndex(nation) != v.nationID:
                continue
            if vehType != -1 and vehType != VEHICLE_TYPES_ORDER_INDICES[v.type]:
                continue
            if level != -1 and level != v.level:
                continue
            if isAction and cbSelected and v.isInInventory:
                continue
            if not isAction and cbSelected and not v.isInInventory:
                continue
            result.append((v, data))

        if btnID in _SORTINGS:
            result.sort(cmp=_SORTINGS[btnID], reverse=direction == 'descending')
        return (result, props.disableChecker)
