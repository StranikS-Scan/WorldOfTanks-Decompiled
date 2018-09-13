# Embedded file name: scripts/client/ClientFortifiedRegion.py
import struct
import itertools
import operator
import BigWorld
from ClientUnit import ClientUnit
from constants import FORT_BUILDING_TYPE, FORT_BUILDING_TYPE_NAMES
import Event
from FortifiedRegionBase import FortifiedRegionBase, FORT_STATE, FORT_EVENT_TYPE
from debug_utils import LOG_ERROR
import fortified_regions
from gui.shared.fortifications.FortBuilding import FortBuilding
from gui.shared.fortifications.FortOrder import FortOrder
from gui.shared.gui_items.dossier import FortDossier
from gui.shared.utils import CONST_CONTAINER, findFirst
UNIT_MGR_ID_CHR = '<qH'

class ClientFortifiedRegion(FortifiedRegionBase):
    DEF_RES_STEP = 1

    class BUILDING_UPDATE_REASON(CONST_CONTAINER):
        ADDED = 1
        UPDATED = 2
        COMPLETED = 3

    def __init__(self, *args, **kwargs):
        self.__eManager = Event.EventManager()
        self.onSortieChanged = Event.Event(self.__eManager)
        self.onSortieRemoved = Event.Event(self.__eManager)
        self.onSortieUnitReceived = Event.Event(self.__eManager)
        self.onResponseReceived = Event.Event(self.__eManager)
        self.onBuildingChanged = Event.Event(self.__eManager)
        self.onBuildingRemoved = Event.Event(self.__eManager)
        self.onTransport = Event.Event(self.__eManager)
        self.onDirectionOpened = Event.Event(self.__eManager)
        self.onDirectionClosed = Event.Event(self.__eManager)
        self.onStateChanged = Event.Event(self.__eManager)
        self.onOrderReady = Event.Event(self.__eManager)
        self.onDossierChanged = Event.Event(self.__eManager)
        self.onPlayerAttached = Event.Event(self.__eManager)
        FortifiedRegionBase.__init__(self, *args, **kwargs)

    def clear(self):
        self.__eManager.clear()

    def getBuildings(self):
        result = {}
        for buildingID, bcd in self.buildings.iteritems():
            result[buildingID] = FortBuilding(bcd)

        return result

    def getBuilding(self, buildingID, default = None):
        return self.getBuildings().get(buildingID, default)

    def isBuildingBuilt(self, buildingID):
        return self.getBuilding(buildingID) is not None

    def getOpenedDirections(self):
        result = []
        for direction in range(1, fortified_regions.g_cache.maxDirections + 1):
            if self.isDirectionOpened(direction):
                result.append(direction)

        return result

    def getBuildingsByDirections(self):
        result = {}
        for direction in self.getOpenedDirections():
            buildings = []
            for dirPos, typeID in self._dirPosToBuildType.iteritems():
                if self.getDirectionFromDirPos(dirPos) == direction:
                    buildings.append(typeID)

            buildingsData = [None, None]
            for buildingId in buildings:
                buildingDescr = self.getBuilding(buildingId)
                if buildingDescr is not None:
                    buildingsData[buildingDescr.position] = buildingDescr

            result[direction] = buildingsData

        return result

    def isPositionAvailable(self, dir, pos):
        for building in self.getBuildingsByDirections().get(dir, []):
            if building is not None and building.position == pos:
                return False

        return True

    def isDirectionOpened(self, direction):
        return self.dirMask & 1 << direction

    def getPositionFromDirPos(self, dirPos):
        return dirPos & 15

    def getDirectionFromDirPos(self, dirPos):
        return dirPos >> 4 & 15

    def getDefResStep(self):
        return self.DEF_RES_STEP

    def getBuildingState(self, buildingTypeID):
        building = self.getBuilding(buildingTypeID)
        return (building.isExportAvailable(), building.isImportAvailable())

    def getOrderData(self, orderID, level = None):
        orderBuildingID = None
        for buildingID, building in fortified_regions.g_cache.buildings.iteritems():
            if building.orderType == orderID:
                orderBuildingID = buildingID

        orderLevel = 0
        orderCount = 0
        orderData = None
        if orderBuildingID is not None:
            if level is None:
                orderBuilding = self.getBuilding(orderBuildingID)
                buildingLevel = orderBuilding.level if orderBuilding is not None else 0
                orderLevel = max(buildingLevel, 1)
            else:
                orderLevel = level
            orderData = fortified_regions.g_cache.orders[orderID].levels.get(orderLevel)
            orderCount, _ = self.orders.get(orderID, (0, 0))
        return (orderBuildingID,
         orderCount,
         orderLevel,
         orderData)

    def getOrder(self, orderID):
        return FortOrder(orderID, self)

    def hasActivatedOrders(self):
        inCooldown = False
        for simpleOrder in self.orders:
            checkingOrder = self.getOrder(simpleOrder)
            if checkingOrder.inCooldown:
                inCooldown = True
                break

        return inCooldown

    def getBuildingOrder(self, buildingID):
        return fortified_regions.g_cache.buildings[buildingID].orderType

    def allBuildingsAreDone(self):
        for buildingDescr in self.getBuildings().itervalues():
            if not buildingDescr.level:
                return False

        return True

    def getBuildingsAvailableForImport(self, buildingTypeID = None):
        return set(self.__getBuildingsFor('isImportAvailable', buildingTypeID))

    def getBuildingsAvailableForExport(self, buildingTypeID = None):
        return set(self.__getBuildingsFor('isExportAvailable', buildingTypeID))

    def getBuildingsOnCooldown(self, buildingTypeID = None):
        return set(self.__getBuildingsFor('hasTimer', buildingTypeID))

    def __getBuildingsFor(self, method, buildingTypeID):

        def filter(item):
            return getattr(item, method)() and (buildingTypeID is None or item.typeID != buildingTypeID)

        return map(operator.attrgetter('typeID'), itertools.ifilter(filter, self.getBuildings().itervalues()))

    def isTransportationAvailable(self):
        forImport = self.getBuildingsAvailableForImport()

        def filter(item):
            return len(self.getBuildingsAvailableForExport(item)) > 0

        return findFirst(filter, forImport) is not None

    def getFortDossier(self):
        return FortDossier(self.statistics, True)

    def getAssignedBuildingID(self, dbID):
        for building in self.getBuildings().itervalues():
            if dbID in building.attachedPlayers:
                return building.typeID

        return 0

    def getTransportationLevel(self):
        base = self.getBuilding(FORT_BUILDING_TYPE.MILITARY_BASE)
        return fortified_regions.g_cache.transportLevels[base.level]

    def getSorties(self):
        if self.isEmpty():
            return {}
        return self.sorties

    def getSortieShortData(self, unitMgrID, peripheryID):
        sortieKey = (unitMgrID, peripheryID)
        return self.getSorties().get(sortieKey, None)

    def getSortieUnit(self, unitMgrID, peripheryID):
        sortieKey = (unitMgrID, peripheryID)
        unit = None
        if not self.isEmpty() and sortieKey in self._sortieUnits:
            unit = ClientUnit()
            unit.unpack(self._sortieUnits[sortieKey])
        return unit

    def getState(self):
        if self.isEmpty():
            return 0
        return self.state

    def isStartingScriptDone(self):
        return self.getState() & FORT_STATE.FIRST_BUILD_DONE > 0

    def isStartingScriptNotStarted(self):
        return self.getState() & FORT_STATE.FIRST_DIR_OPEN == 0

    def getTotalDefRes(self):
        outcome = 0
        for building in self.getBuildings().itervalues():
            outcome += building.storage

        return outcome

    def recalculateOrder(self, orderTypeID, prevCount, prevLevel, newLevel):
        newCount, resLeft = self._recalcOrders(orderTypeID, prevCount, prevLevel, newLevel)
        return (newCount, resLeft)

    def _setSortie(self, unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType, cmdrName):
        result = FortifiedRegionBase._setSortie(self, unitMgrID, cmdrDBID, rosterTypeID, peripheryID, count, maxCount, timestamp, igrType, cmdrName)
        self.onSortieChanged(unitMgrID, peripheryID)
        return result

    def _removeSortie(self, unitMgrID, peripheryID):
        FortifiedRegionBase._removeSortie(self, unitMgrID, peripheryID)
        self.onSortieRemoved(unitMgrID, peripheryID)

    def _unpackSortieUnit(self, unpacking):
        result = FortifiedRegionBase._unpackSortieUnit(self, unpacking)
        try:
            unitMgrID, peripheryID = struct.unpack_from(UNIT_MGR_ID_CHR, unpacking)
            self.onSortieUnitReceived(unitMgrID, peripheryID)
        except struct.error as e:
            LOG_ERROR(e)

        return result

    def _processRequest(self, reqID, callerDBID):
        FortifiedRegionBase._processRequest(self, reqID, callerDBID)
        self.onResponseReceived(reqID, callerDBID)

    def _addBuilding(self, buildingTypeID, dir, pos):
        FortifiedRegionBase._addBuilding(self, buildingTypeID, dir, pos)
        self.onBuildingChanged(buildingTypeID, self.BUILDING_UPDATE_REASON.ADDED, {'dir': dir,
         'pos': pos})

    def _upgrade(self, buildTypeID, level, decStorage):
        FortifiedRegionBase._upgrade(self, buildTypeID, level, decStorage)
        self.onBuildingChanged(buildTypeID, self.BUILDING_UPDATE_REASON.UPDATED)

    def _delBuilding(self, buildingTypeID):
        ressignPlayer = BigWorld.player().databaseID in self.getBuilding(buildingTypeID).attachedPlayers
        FortifiedRegionBase._delBuilding(self, buildingTypeID)
        self.onBuildingRemoved(buildingTypeID)
        if ressignPlayer:
            self.onPlayerAttached(FORT_BUILDING_TYPE.MILITARY_BASE)

    def _addOrders(self, buildingTypeID, count, timeFinish, initiatorDBID):
        FortifiedRegionBase._addOrders(self, buildingTypeID, count, timeFinish, initiatorDBID)
        self.onBuildingChanged(buildingTypeID, self.BUILDING_UPDATE_REASON.UPDATED)

    def _transport(self, fromBuildTypeID, toBuildTypeID, resCount, timeCooldown):
        reason = self.BUILDING_UPDATE_REASON.UPDATED
        previousState = self.getBuilding(toBuildTypeID)
        FortifiedRegionBase._transport(self, fromBuildTypeID, toBuildTypeID, resCount, timeCooldown)
        newState = self.getBuilding(toBuildTypeID)
        self.onBuildingChanged(fromBuildTypeID, self.BUILDING_UPDATE_REASON.UPDATED)
        if previousState.level == 0 and newState.level > 0:
            reason = self.BUILDING_UPDATE_REASON.COMPLETED
        self.onBuildingChanged(toBuildTypeID, reason)
        self.onTransport()

    def _contribute(self, accDBID, buildingTypeID, resCount, dateStamp):
        reason = self.BUILDING_UPDATE_REASON.UPDATED
        previousState = self.getBuilding(buildingTypeID)
        FortifiedRegionBase._contribute(self, accDBID, buildingTypeID, resCount, dateStamp)
        newState = self.getBuilding(buildingTypeID)
        if previousState.level == 0 and newState.level > 0:
            reason = self.BUILDING_UPDATE_REASON.COMPLETED
        self.onBuildingChanged(buildingTypeID, reason)

    def _openDir(self, dir):
        FortifiedRegionBase._openDir(self, dir)
        self.onDirectionOpened(dir)

    def _closeDir(self, dir):
        FortifiedRegionBase._closeDir(self, dir)
        self.onDirectionClosed(dir)

    def _setState(self, newState):
        FortifiedRegionBase._setState(self, newState)
        self.onStateChanged(newState)

    def _expireEvent(self, eventTypeID, value):
        buildingTypeID = eventTypeID - FORT_EVENT_TYPE.PRODUCT_ORDERS_BASE
        orderTypeID = 0
        orderCount = 0
        isOrder = buildingTypeID in FORT_BUILDING_TYPE_NAMES
        if isOrder:
            building = self.getBuilding(buildingTypeID)
            orderTypeID = self.getBuildingOrder(buildingTypeID)
            orderCount = building.orderInProduction.get('count')
        FortifiedRegionBase._expireEvent(self, eventTypeID, value)
        if isOrder:
            self.onOrderReady(orderTypeID, orderCount)

    def _syncFortDossier(self, compDossierDescr):
        FortifiedRegionBase._syncFortDossier(self, compDossierDescr)
        self.onDossierChanged(compDossierDescr)

    def _attach(self, buildTypeID, accDBID):
        FortifiedRegionBase._attach(self, buildTypeID, accDBID)
        self.onPlayerAttached(buildTypeID)
