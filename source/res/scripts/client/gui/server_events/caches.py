# Embedded file name: scripts/client/gui/server_events/caches.py
from collections import namedtuple
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


@ReprInjector.simple('tabID', 'potapov', 'common')

class _NavigationInfo(object):
    PQInfo = namedtuple('PQInfo', 'tileID questID filters')
    CommonInfo = namedtuple('CommonInfo', 'questID')

    def __init__(self):
        self.tabID = None
        self.potapov = self.PQInfo(None, None, None)
        self.common = self.CommonInfo(None)
        return

    def selectTab(self, tabID, doResetNavInfo = False):
        if doResetNavInfo:
            if tabID == _QA.TAB_PERSONAL_QUESTS:
                self.potapov = self.__clearCache(self.potapov)
            else:
                self.common = self.__clearCache(self.potapov)
        self.tabID = tabID

    def selectPotapovQuest(self, tileID, questID = None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.potapov = self.potapov._replace(tileID=tileID, questID=questID)

    def changePQFilters(self, *args):
        self.potapov = self.potapov._replace(filters=args)

    def selectCommonQuest(self, questID):
        self.tabID = _QA.TAB_COMMON_QUESTS
        self.common = self.common._replace(questID=questID)

    @classmethod
    def __clearCache(cls, cacheTuple):
        return cacheTuple._replace(**dict(map(lambda n: (n, None), cacheTuple._fields)))


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
