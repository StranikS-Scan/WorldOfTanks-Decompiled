# Embedded file name: scripts/client/gui/shared/fortifications/fort_seqs.py
import weakref
import BigWorld
from collections import namedtuple
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from gui.prb_control.items.sortie_items import getDivisionNameByType
from gui.shared.fortifications.context import RequestSortieUnitCtx
from gui.shared.fortifications.settings import FORT_REQUEST_TYPE
from ids_generators import SequenceIDGenerator

def getDivisionSettings(name):
    import fortified_regions
    division = None
    divisions = fortified_regions.g_cache.divisions
    if name in divisions:
        division = fortified_regions.g_cache.divisions[name]
    else:
        LOG_ERROR('Name of division is not valid', name)
    return division


_SortieItemData = namedtuple('_SortieItemData', ('cmdrDBID', 'rosterTypeID', 'count', 'maxCount', 'timestamp', 'igrType', 'cmdrName'))

def makeDefSortieItemData():
    return _SortieItemData(0, 0, 0, 0, 0, 0, '')


class SortieItem(object):

    def __init__(self, sortieID, itemData):
        super(SortieItem, self).__init__()
        self._sortieID = sortieID
        self._isDirty = True
        self.itemData = self._makeItemData(itemData)

    def __repr__(self):
        return 'SortieItem(sortieID = {0!r:s}, dirty = {1!r:s}, data = {2!r:s})'.format(self._sortieID, self._isDirty, self.itemData)

    def clear(self):
        self.unitMgrID = 0
        self.itemData = None
        return

    def filter(self, rosterTypeID):
        return rosterTypeID == 0 or self.itemData.rosterTypeID == rosterTypeID

    def getIgrType(self):
        return self.itemData.igrType

    def getID(self):
        return self._sortieID

    def getDivisionName(self):
        return getDivisionNameByType(self.itemData.rosterTypeID)

    def getCommanderFullName(self):
        return self.itemData.cmdrName

    def _makeItemData(self, itemData):
        try:
            data = _SortieItemData(*itemData)
        except TypeError:
            data = makeDefSortieItemData()
            LOG_ERROR('Client can not unpack item data of sortie', itemData)

        return data

    def _updateItemData(self, itemData):
        newData = self._makeItemData(itemData)
        if self.itemData.timestamp != newData.timestamp:
            self._isDirty = True
        self.itemData = newData


class SortiesCache(object):
    __selectedID = 0
    __rosterTypeID = 0

    def __init__(self, controller):
        self.__controller = weakref.proxy(controller)
        self.__idGen = SequenceIDGenerator()
        self.__cache = {}
        self.__idToIndex = {}
        self.__indexToID = {}
        self.__isRequestInProcess = False
        self.__cooldownRequest = None
        return

    def __del__(self):
        LOG_DEBUG('Sortie cache deleted:', self)

    def clear(self):
        self.__controller = None
        self.__cache.clear()
        self.__idToIndex.clear()
        self.__indexToID.clear()
        if self.__cooldownRequest is not None:
            BigWorld.cancelCallback(self.__cooldownRequest)
            self.__cooldownRequest = None
        return

    def start(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onSortieChanged += self.__fort_onSortieChanged
            fort.onSortieRemoved += self.__fort_onSortieRemoved
            fort.onSortieUnitReceived += self.__fort_onSortieUnitReceived
            self.__cache = self.__buildCache()
        else:
            LOG_ERROR('Client fort is not found')

    def stop(self):
        fort = self.__controller.getFort()
        if fort:
            fort.onSortieChanged -= self.__fort_onSortieChanged
            fort.onSortieRemoved -= self.__fort_onSortieRemoved
            fort.onSortieUnitReceived -= self.__fort_onSortieUnitReceived
        self.clear()

    @property
    def isRequestInProcess(self):
        return self.__isRequestInProcess

    @classmethod
    def getSelectedID(cls):
        return cls.__selectedID

    def setSelectedID(self, selectedID):
        if selectedID not in self.__cache:
            LOG_WARNING('Item is not found in cache', selectedID)
            return False
        self._setSelectedID(selectedID)
        unit = self.getSelectedUnit()
        if unit and not self.__cache[selectedID]._isDirty:
            self.__controller._listeners.notify('onSortieUnitReceived', self.__getClientIdx(selectedID))
        else:
            self._requestSortieUnit(selectedID)
        return True

    @classmethod
    def getRosterTypeID(cls):
        return cls.__rosterTypeID

    def setRosterTypeID(self, rosterTypeID):
        result = self._setRosterTypeID(rosterTypeID)
        if result:
            self.__cache = self.__buildCache()
        return result

    def getItem(self, sortieID):
        try:
            item = self.__cache[sortieID]
        except KeyError:
            LOG_ERROR('Item not found in cache', sortieID)
            item = None

        return item

    def getUnitByIndex(self, index):
        unit = None
        if index in self.__indexToID:
            sortieID = self.__indexToID[index]
            unit = self.__getUnit(sortieID)
        return unit

    def getSelectedUnit(self):
        return self.__getUnit(self.getSelectedID())

    def getIterator(self):
        for item in self.__cache.itervalues():
            if item.filter(self.__rosterTypeID):
                yield item

    def _requestSortieUnit(self, selectedID):

        def requester():
            self.__cooldownRequest = None
            self.__isRequestInProcess = True
            self.__controller.request(RequestSortieUnitCtx(waitingID='', *selectedID), self.__requestCallback)
            return

        if self.__controller._cooldown.isInProcess(FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT):
            self.__cooldownRequest = BigWorld.callback(self.__controller._cooldown.getTime(FORT_REQUEST_TYPE.REQUEST_SORTIE_UNIT), requester)
        else:
            requester()

    @classmethod
    def _setSelectedID(cls, selectedID):
        result = False
        if selectedID != cls.__selectedID and len(selectedID) == 2:
            cls.__selectedID = selectedID
            result = True
        return result

    @classmethod
    def _setRosterTypeID(cls, rosterTypeID):
        result = False
        if rosterTypeID != cls.__rosterTypeID:
            cls.__rosterTypeID = rosterTypeID
            result = True
        return result

    @classmethod
    def _removeStoredData(cls):
        cls.__selectedID = (0, 0)
        cls.__rosterTypeID = 0

    def __buildCache(self):
        cache = {}
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return cache
        sorties = fort.getSorties()
        selectedID = self.getSelectedID()
        found = False
        for sortieID, sortie in sorties.iteritems():
            item = SortieItem(sortieID, sortie)
            if not found and item.getID() == selectedID:
                found = True
            cache[sortieID] = item

        if not found:
            self._setSelectedID((0, 0))
        return cache

    def __updateItem(self, sortieID, fort):
        sortie = fort.getSortieShortData(*sortieID)
        if sortie is None:
            LOG_ERROR('Sortie is not found', sortieID, fort.sorties)
            return
        else:
            if sortieID in self.__cache:
                item = self.__cache[sortieID]
                item._updateItemData(sortie)
                if item._isDirty and self.__selectedID == item.getID():
                    self._requestSortieUnit(sortieID)
            else:
                item = SortieItem(sortieID, sortie)
                self.__cache[sortieID] = item
            return item

    def __requestCallback(self, _):
        self.__isRequestInProcess = False

    def __removeItem(self, sortieID):
        result = False
        if sortieID in self.__cache:
            self.__cache.pop(sortieID)
            result = True
        if self.getSelectedID() == sortieID:
            self._setSelectedID((0, 0))
        clientIdx = self.__idToIndex.pop(sortieID, None)
        if clientIdx is not None:
            self.__indexToID.pop(clientIdx, None)
        return result

    def __getClientIdx(self, sortieID):
        if sortieID == (0, 0):
            return 0
        if sortieID not in self.__idToIndex:
            clientIdx = self.__idGen.next()
            self.__idToIndex[sortieID] = clientIdx
            self.__indexToID[clientIdx] = sortieID
        else:
            clientIdx = self.__idToIndex[sortieID]
        return clientIdx

    def __getUnit(self, sortieID):
        fort = self.__controller.getFort()
        if not fort:
            LOG_WARNING('Client fort is not found')
            return None
        else:
            return fort.getSortieUnit(*sortieID)

    def __fort_onSortieChanged(self, unitMgrID, peripheryID):
        fort = self.__controller.getFort()
        sortieID = (unitMgrID, peripheryID)
        if fort:
            item = self.__updateItem(sortieID, fort)
            if item:
                self.__controller._listeners.notify('onSortieChanged', self, item)

    def __fort_onSortieRemoved(self, unitMgrID, peripheryID):
        sortieID = (unitMgrID, peripheryID)
        if self.__removeItem(sortieID):
            self.__controller._listeners.notify('onSortieRemoved', self, sortieID)

    def __fort_onSortieUnitReceived(self, unitMgrID, peripheryID):
        fort = self.__controller.getFort()
        sortieID = (unitMgrID, peripheryID)
        if fort:
            if unitMgrID in self.__cache:
                self.__cache[sortieID]._isDirty = False
            self.__controller._listeners.notify('onSortieUnitReceived', self.__getClientIdx(sortieID))
