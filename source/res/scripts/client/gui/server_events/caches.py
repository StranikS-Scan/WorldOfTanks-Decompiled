# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/caches.py
from collections import namedtuple
from debug_utils import LOG_ERROR
from helpers import dependency
from shared_utils import first
from gui.shared.utils.decorators import ReprInjector
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES as _QA
from skeletons.gui.lobby_context import ILobbyContext
_g_sortedVehs = {}
VehiclesListProps = namedtuple('VehiclesListProps', ('disableChecker', 'nationIdx', 'vehTypeIdx', 'levelIdx', 'selectedBtn', 'sortDirect', 'checkbox'))

def getVehiclesData(listID):
    return _g_sortedVehs.get(listID)


def addVehiclesData(listID, vehs, disableChecker=None, nationIdx=-1, vehTypeIdx=-1, levelIdx=-1, selectedBtn=None, sortDirect=None, checkbox=None):
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


PQ_TABS = (_QA.SEASON_VIEW_TAB_RANDOM,)

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getEnabledPQTabs(lobbyContext=None):
    if lobbyContext is not None:
        tabs = list(PQ_TABS)
        if not lobbyContext.getServerSettings().isRegularQuestEnabled():
            tabs.remove(_QA.SEASON_VIEW_TAB_RANDOM)
    else:
        tabs = []
    return tabs


class QuestInfo(object):
    __slots__ = ('questID',)

    def __init__(self, *args):
        super(QuestInfo, self).__init__()
        for idx, fieldName in enumerate(self.__slots__):
            object.__setattr__(self, fieldName, args[idx])

    def __setattr__(self, key, value):
        raise AssertionError

    def update(self, **kwargs):
        for key, value in kwargs.iteritems():
            if key in self.__slots__:
                object.__setattr__(self, key, value)
            LOG_ERROR('Unsupported argument for object:', self, key, value)

        return self

    def clear(self):
        for field_name in self.__slots__:
            object.__setattr__(self, field_name, None)

        return


class PMInfo(QuestInfo):
    __slots__ = ('operationID', 'questID', 'filters')


@ReprInjector.simple('tabID', 'random')
class _NavigationInfo(object):

    def __init__(self):
        self.tabID = None
        self.random = PMInfo(None, None, None)
        self.__selectedPQType = _QA.SEASON_VIEW_TAB_RANDOM
        self._missionsTab = None
        self._marathonPrefix = None
        self._vehicleSelectorFilters = {}
        return

    @property
    def selectedPQ(self):
        return self.random

    @property
    def selectedPQType(self):
        if self.__selectedPQType not in getEnabledPQTabs():
            self.__selectedPQType = first(getEnabledPQTabs(), None)
        return self.__selectedPQType

    def setPQTypeByTabID(self, tabID):
        if tabID in PQ_TABS:
            self.__selectedPQType = tabID
        else:
            LOG_ERROR('Wrong tabID to set as selected PQ type')

    def selectTab(self, tabID, doResetNavInfo=False):
        if doResetNavInfo:
            if tabID == _QA.TAB_PERSONAL_QUESTS:
                self.random.clear()
        self.tabID = tabID

    def selectPersonalMission(self, operationID, questID=None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.selectedPQ.update(operationID=operationID, questID=questID)

    def selectRandomQuest(self, operationID, questID=None):
        self.tabID = _QA.TAB_PERSONAL_QUESTS
        self.__selectedPQType = _QA.SEASON_VIEW_TAB_RANDOM
        self.random = self.random.update(operationID=operationID, questID=questID, filters=None)
        return

    def changePQFilters(self, *args):
        self.selectedPQ.update(filters=args)

    def getMissionsTab(self):
        return self._missionsTab

    def getMarathonPrefix(self):
        return self._marathonPrefix

    def setMissionsTab(self, tabID):
        self._missionsTab = tabID

    def setMarathonPrefix(self, marathonPrefix):
        self._marathonPrefix = marathonPrefix

    def getVehicleSelectorFilters(self):
        return self._vehicleSelectorFilters

    def setVehicleSelectorFilters(self, filters):
        self._vehicleSelectorFilters = filters


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
