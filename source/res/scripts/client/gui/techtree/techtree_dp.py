# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/techtree/techtree_dp.py
import operator
from collections import defaultdict, namedtuple
from copy import copy
import ResMgr
import nations
import section2dict
from constants import IS_DEVELOPMENT
from debug_utils import LOG_ERROR, LOG_DEBUG
from dict2model import models, schemas, fields
from gui import GUI_NATIONS_ORDER_INDEX
from gui.techtree.nodes import BaseNode
from gui.techtree.settings import NATION_TREE_REL_FILE_PATH, TreeDataFilesPath
from gui.techtree.settings import NATION_TREE_REL_PREMIUM_FILE_PATH
from gui.techtree.settings import NODE_ORDER_PREFIX_COMMON, NODE_ORDER_PREFIX_PREMIUM
from gui.techtree.settings import TREE_SHARED_REL_FILE_PATH, UnlockStats
from gui.techtree.settings import UNKNOWN_VEHICLE_LEVEL
from gui.techtree.settings import UnlockProps, DEFAULT_UNLOCK_PROPS
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items import _xml, vehicles, getTypeOfCompactDescr
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.techtree_events import ITechTreeEventsListener
from soft_exception import SoftException

class _ConfigError(SoftException):

    def __init__(self, ctx, msg):
        super(_ConfigError, self).__init__()
        self.msg = msg
        self.ctx = ctx

    def __str__(self):
        return 'Config error in {0:>s}. {1:>s}'.format(self.ctx[1], self.msg)


class DisplaySettingsModel(models.Model):
    __slots__ = ('rowsNumber', 'columnsNumber', 'premiumRowsNumber')

    def __init__(self, rowsNumber, columnsNumber, premiumRowsNumber):
        super(DisplaySettingsModel, self).__init__()
        self.rowsNumber = rowsNumber
        self.columnsNumber = columnsNumber
        self.premiumRowsNumber = premiumRowsNumber


displaySettingsSchema = schemas.Schema(fields={'rowsNumber': fields.Integer(required=True),
 'columnsNumber': fields.Integer(required=True),
 'premiumRowsNumber': fields.Integer(required=True)}, modelClass=DisplaySettingsModel, checkUnknown=True)
SUPPORTED_LINES = {'horizontal', 'vertical', 'H_V'}
_VEHICLE = GUI_ITEM_TYPE.VEHICLE
_VEHICLE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[_VEHICLE]
_AnnouncementInfo = namedtuple('_AnnouncementInfo', ('userString',
 'tooltip',
 'tags',
 'level',
 'icon',
 'isElite'))

class TechTreeDataProvider(object):
    __slots__ = ('__loaded', '__availableNations', '__displayInfo', '__topLevels', '__topItems', '__nextLevels', '__settings', '__unlockPrices', '__announcements', '__announcementCDToName', '__nextAnnouncements', '__nodes', '__nextTypeIDs', '__source')
    itemsCache = dependency.descriptor(IItemsCache)
    techTreeEventsListener = dependency.descriptor(ITechTreeEventsListener)
    earlyAccessController = dependency.descriptor(IEarlyAccessController)

    def __init__(self, source=None):
        super(TechTreeDataProvider, self).__init__()
        self.__loaded = False
        self.__availableNations = None
        self.__settings = None
        self._clear()
        self.__source = source if source is not None else TreeDataFilesPath(shared=TREE_SHARED_REL_FILE_PATH, nation=NATION_TREE_REL_FILE_PATH, nationPremium=NATION_TREE_REL_PREMIUM_FILE_PATH)
        return

    def load(self, isReload=False):
        if self.__loaded and not isReload:
            return False
        LOG_DEBUG('Tech tree data is being loaded')
        self._clear()
        try:
            try:
                shared = self.__readShared(clearCache=isReload)
                for nation in self.__availableNations:
                    info = self.__readNation(shared, nation, clearCache=isReload)
                    self.__displayInfo[nations.INDICES[nation]] = info

                self.__settings = shared['settings']
            except _ConfigError as error:
                LOG_ERROR(error)

        finally:
            self.__loaded = True

        _xml.clearCaches()
        return True

    def getDisplaySettings(self):
        return copy(self.__settings)

    def getNationTreeIterator(self, nationID):
        if nationID >= len(self.__nodes):
            LOG_ERROR('Nation ID is out of range', nationID)
            return
        else:
            nodes = self.__nodes[nationID]
            if nodes is None:
                LOG_ERROR('Nodes is not found', nationID)
                return
            displayInfo = self.__displayInfo[nationID]
            if displayInfo is None:
                LOG_ERROR('Display info is not found', nationID)
                return
            for node in sorted(nodes.itervalues(), key=lambda item: item.order):
                yield (node, displayInfo[node.nodeCD].copy())

            return

    def getTopLevel(self, vTypeCD):
        return self.__topLevels[vTypeCD]

    def getNextLevel(self, vTypeCD):
        return set(self.__nextLevels[vTypeCD].keys())

    def isNext2Unlock(self, vTypeCD, unlocked=None, xps=None, freeXP=0, level=UNKNOWN_VEHICLE_LEVEL):
        unlocked = unlocked or set()
        topLevel = self.getTopLevel(vTypeCD)
        isEarlyAccess = self.itemsCache.items.getItemByCD(vTypeCD).isEarlyAccess
        available = False
        topIDs = set()
        compare = []
        result = DEFAULT_UNLOCK_PROPS
        for parentCD in topLevel:
            nextLevel = self.__nextLevels[parentCD]
            idx, xpCost, required = nextLevel[vTypeCD]
            discount, newCost = self.getBlueprintDiscountData(vTypeCD, level, xpCost)
            isEarlyAccessUnlock = isEarlyAccess and vTypeCD not in self.earlyAccessController.getBlockedVehicles() and (parentCD in unlocked or vTypeCD == self.earlyAccessController.getFirstVehicleCD())
            if required.issubset(unlocked) and parentCD in unlocked or isEarlyAccessUnlock:
                topIDs.add(parentCD)
                compare.append(UnlockProps(parentCD, idx, newCost, topIDs, discount, xpCost))
                available = True
            if not result.xpCost or result.xpCost > xpCost:
                result = UnlockProps(parentCD, idx, newCost, set(), discount, xpCost)

        if available:
            result = self._findNext2Unlock(compare, xps=xps, freeXP=freeXP)
        return (available, result)

    def getNext2UnlockByItems(self, itemCDs, unlocked=None, xps=None, freeXP=0):
        unlocked = unlocked or set()
        filtered = [ item for item in itemCDs if item in self.__topItems ]
        if not filtered or not unlocked:
            return {}
        available = defaultdict(list)
        parentCDs = {item for item in itemCDs if getTypeOfCompactDescr(item) == _VEHICLE}
        for item in filtered:
            if item in unlocked:
                parentCDs |= self.__topItems[item]

        for parentCD in parentCDs:
            if parentCD not in unlocked:
                continue
            nextLevel = self.__nextLevels[parentCD]
            topIDs = set()
            for childCD, (idx, xpCost, required) in nextLevel.iteritems():
                if required.issubset(unlocked):
                    topIDs.add(parentCD)
                    available[childCD].append(UnlockProps(parentCD, idx, xpCost, topIDs, 0, xpCost))

        result = {}
        for childCD, compare in available.iteritems():
            result[childCD] = self._findNext2Unlock(compare, xps=xps, freeXP=freeXP)

        return result

    def getAvailableNations(self):
        if self.__availableNations is None:
            section = ResMgr.openSection(self.__source.shared)
            if section is None:
                _xml.raiseWrongXml(None, self.__source.shared, 'can not open or read')
            xmlCtx = (None, self.__source.shared)
            self.__availableNations = self.__readAvailableNations(xmlCtx, section)
        return self.__availableNations[:]

    def getAvailableNationsIndices(self):
        return [ nations.INDICES[nation] for nation in self.getAvailableNations() ]

    def getUnlockPrices(self, compactDescr):
        return self.__unlockPrices[compactDescr]

    def getAllPossibleItems2Unlock(self, vehicle, unlocked):
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD not in unlocked:
                level = self.itemsCache.items.getItemByCD(nodeCD).level
                discount, newCost = self.getBlueprintDiscountData(nodeCD, level, xpCost)
                items[nodeCD] = UnlockProps(parentID=vehicle.intCD, unlockIdx=unlockIdx, xpCost=newCost, required=required, discount=discount, xpFullCost=xpCost)

        return items

    def getUnlockedVehicleItems(self, vehicle, unlocked):
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD in unlocked:
                discountData = self.getBlueprintDiscountData(vehicle.intCD, vehicle.level, xpCost)
                items[nodeCD] = UnlockProps(vehicle.intCD, unlockIdx, discountData[1], required, discountData[0], xpCost)

        return items

    def getAllVehiclePossibleXP(self, nodeCD, unlockStats):
        criteria = REQ_CRITERIA.VEHICLE.FULLY_ELITE | ~REQ_CRITERIA.IN_CD_LIST([nodeCD])
        eliteVehicles = self.itemsCache.items.getVehicles(criteria)
        dirtyResult = sum(map(operator.attrgetter('xp'), eliteVehicles.values()))
        exchangeRate = self.itemsCache.items.shop.freeXPConversion[0]
        result = min(int(dirtyResult / exchangeRate) * exchangeRate, self.itemsCache.items.stats.gold * exchangeRate)
        result += unlockStats.getVehTotalXP(nodeCD)
        return result

    def isVehicleAvailableToUnlock(self, nodeCD, vehicleLevel=UNKNOWN_VEHICLE_LEVEL):
        unlocks = self.itemsCache.items.stats.unlocks
        xps = self.itemsCache.items.stats.vehiclesXPs
        freeXP = self.itemsCache.items.stats.actualFreeXP
        unlockProps = self.getUnlockProps(nodeCD, vehicleLevel)
        parentID = unlockProps.parentID
        allPossibleXp = self.getAllVehiclePossibleXP(parentID, UnlockStats(unlocks, xps, freeXP))
        isNextToUnlock, props = self.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=xps, freeXP=freeXP, level=vehicleLevel)
        return (isNextToUnlock, allPossibleXp >= props.xpCost)

    def getUnlockProps(self, vehicleCD, vehicleLevel=UNKNOWN_VEHICLE_LEVEL):
        _, unlockProps = self.isNext2Unlock(vehicleCD, unlocked=self.itemsCache.items.stats.unlocks, xps=self.itemsCache.items.stats.vehiclesXPs, freeXP=self.itemsCache.items.stats.actualFreeXP, level=vehicleLevel)
        return unlockProps

    def getOldAndNewCost(self, vehicleCD, vehicleLevel):
        self.load()
        unlockProps = self.getUnlockProps(vehicleCD, vehicleLevel)
        return (unlockProps.xpCost, unlockProps.discount, unlockProps.xpFullCost) if unlockProps is not None else (0, 0, 0)

    def getBlueprintDiscountData(self, vehicleCD, level, xpCost, blueprintCount=0):
        blueprints = self.itemsCache.items.blueprints
        discount = blueprints.getBlueprintDiscount(vehicleCD, level, blueprintCount)
        newCost = blueprints.calculateCost(xpCost, discount)
        return (discount, newCost)

    def getAnnouncementByName(self, name):
        return self.__announcements[name] if name in self.__announcements else None

    def getAnnouncementByCD(self, intCD):
        return self.getAnnouncementByName(self.__announcementCDToName[intCD]) if intCD in self.__announcementCDToName else None

    def getNextAnnouncements(self, intCD):
        if intCD not in self.__nextAnnouncements:
            return
        for nodeCD in self.__nextAnnouncements[intCD]:
            yield nodeCD

    def isActionEndNode(self, nodeCD, nationID):
        return self.__isBoundActionNode(nodeCD, nationID, self.getNextLevel(nodeCD))

    def isActionStartNode(self, nodeCD, nationID):
        return self.__isBoundActionNode(nodeCD, nationID, self.getTopLevel(nodeCD))

    def _clear(self):
        self.__displayInfo = [None] * len(nations.NAMES)
        self.__nextTypeIDs = [0] * len(nations.NAMES)
        self.__nodes = [None] * len(nations.NAMES)
        self.__topLevels = defaultdict(set)
        self.__topItems = defaultdict(set)
        self.__nextLevels = defaultdict(dict)
        self.__unlockPrices = defaultdict(dict)
        self.__announcements = {}
        self.__announcementCDToName = {}
        self.__nextAnnouncements = defaultdict(list)
        self.__settings = None
        return

    def _findNext2Unlock(self, compare, xps=None, freeXP=0):
        xpGetter = xps.get

        def makeItem(item):
            xp = xpGetter(item.parentID, 0)
            return (item, xp, item.xpCost - xp)

        def getMinFreeXPSpent(props):
            _, _, minDelta = min(props, key=lambda item: item[2])
            filtered = (prop for prop in props if prop[2] == minDelta)
            recommended, _, _ = min(filtered, key=lambda item: item[1])
            return recommended

        mapping = [ makeItem(unlockProps) for unlockProps in compare ]
        filtered = []
        recommended = None
        if xps is not None:
            filtered = [ item for item in mapping if item[0].xpCost <= item[1] + freeXP ]
        if filtered:
            recommended = getMinFreeXPSpent(filtered)
        if recommended is None:
            if filtered:
                mapping = filtered
            recommended = getMinFreeXPSpent(mapping)
        return recommended

    def __readShared(self, clearCache=False):
        if clearCache:
            ResMgr.purge(self.__source.shared)
        shared = {'settings': {},
         'default': {}}
        section = ResMgr.openSection(self.__source.shared)
        if section is None:
            _xml.raiseWrongXml(None, self.__source.shared, 'can not open or read')
        xmlCtx = (None, self.__source.shared)
        shared['settings'] = self.__readSettings(xmlCtx, section)
        if self.__availableNations is None:
            self.__availableNations = self.__readAvailableNations((None, self.__source.shared), section)
        self.__readAnnouncements((None, self.__source.shared), section)
        self.__readDefaultLine(shared, xmlCtx, section)
        return shared

    def __readDefaultLine(self, shared, xmlCtx, section):
        defSec = _xml.getSubsection(xmlCtx, section, 'default-line')
        xPath = '{0:>s}/default-line'.format(self.__source.shared)
        xmlCtx = (None, xPath)
        name = _xml.readString(xmlCtx, defSec, 'line')
        if name not in SUPPORTED_LINES:
            raise _ConfigError(xmlCtx, 'line is not supported {}'.format(name))
        shared['default'] = {'line': name}
        return

    def __readAvailableNations(self, xmlCtx, root):
        names = []
        indices = nations.INDICES
        for _, section in _xml.getChildren(xmlCtx, root, 'available-nations'):
            name = section.asString
            if name not in indices:
                _xml.raiseWrongXml(xmlCtx, 'available-nations', 'Nation {0:>s} not found'.format(name))
            if name not in nations.AVAILABLE_NAMES:
                LOG_ERROR('Nation ignored, it not found in nations.AVAILABLE_NAMES', name)
                continue
            names.append(name)

        names = sorted(names, cmp=lambda item, other: cmp(GUI_NATIONS_ORDER_INDEX.get(item), GUI_NATIONS_ORDER_INDEX.get(other)))
        return names

    def __readAnnouncements(self, xmlCtx, root):
        for name, section in _xml.getChildren(xmlCtx, root, 'announcements'):
            if name in self.__announcements:
                _xml.raiseWrongXml(xmlCtx, 'announcements', 'Announcement vehicles {0:>s} is already added'.format(name))
            tags = _xml.readNonEmptyString(xmlCtx, section, 'tags')
            if tags:
                tags = frozenset(tags.split(' '))
            else:
                tags = frozenset()
            self.__announcements[name] = _AnnouncementInfo(_xml.readNonEmptyString(xmlCtx, section, 'user-string'), _xml.readNonEmptyString(xmlCtx, section, 'tooltip'), tags, _xml.readInt(xmlCtx, section, 'level'), _xml.readNonEmptyString(xmlCtx, section, 'icon'), _xml.readBool(xmlCtx, section, 'is-elite'))

    def __getNextTypeID(self, nationID):
        nextTypeID = self.__nextTypeIDs[nationID]
        if not nextTypeID:
            nextTypeID = max(vehicles.g_list.getList(nationID).keys())
        nextTypeID += 1
        self.__nextTypeIDs[nationID] = nextTypeID
        return nextTypeID

    def __getNodeByName(self, nodeName, nationID, order=0):
        nodes = self.__nodes[nationID]
        if nodes is None:
            nodes = self.__nodes[nationID] = {}
        if nodeName in nodes:
            node = nodes[nodeName]
            if order:
                node.order = order
            return node
        else:
            isFound = True
            isAnnouncement = False
            if nodeName in self.__announcements:
                isAnnouncement = True
                vehicleTypeID = self.__getNextTypeID(nationID)
            else:
                _, vehicleTypeID = vehicles.g_list.getIDsByName('{0:>s}:{1:>s}'.format(nations.NAMES[nationID], nodeName))
            try:
                nodeCD = vehicles.makeIntCompactDescrByID(_VEHICLE_TYPE_NAME, nationID, vehicleTypeID)
            except AssertionError:
                nodeCD = 0
                isFound = False

            if isAnnouncement:
                self.__announcementCDToName[nodeCD] = nodeName
            node = BaseNode(nodeName, nationID, vehicleTypeID, nodeCD, isFound=isFound, isAnnouncement=isAnnouncement, order=order)
            nodes[nodeName] = node
            return node

    def __isBoundActionNode(self, nodeCD, nationID, boundNodes):
        if nationID not in self.techTreeEventsListener.getNations(unviewed=True):
            return False
        hasAction = self.techTreeEventsListener.hasActiveAction
        return not any((hasAction(boundCD, nationID) for boundCD in boundNodes)) if hasAction(nodeCD, nationID) else False

    def __readNodeLines(self, parentCD, nation, xmlCtx, section, shared):
        linesSec = section['lines']
        if linesSec is None:
            linesSec = {}
        result = []
        nextLevel = self.__nextLevels[parentCD].keys()
        _, xPath = xmlCtx
        xPath = '{0:>s}/lines'.format(xPath)
        nationID = nations.INDICES[nation]
        for name, sub in linesSec.items():
            xmlCtx = (None, '{0:>s}/lines/{1:>1}'.format(xPath, name))
            node = self.__getNodeByName(name, nationID)
            if not node.isFound:
                raise _ConfigError(xmlCtx, 'Unknown vehicle type name {0:>s}'.format(name))
            if IS_DEVELOPMENT and not node.isAnnouncement:
                if node.nodeCD not in nextLevel:
                    _, nationID, vTypeID = vehicles.parseIntCompactDescr(parentCD)
                    pName = vehicles.g_list.getList(nationID)[vTypeID].name
                    LOG_ERROR('{0:>s} does not have relation with {1:>s}'.format(pName, name))
                else:
                    nextLevel.remove(node.nodeCD)
            if node.isAnnouncement:
                self.__nextAnnouncements[parentCD].append(node.nodeCD)
            lineName = sub.readString('line') if 'line' in sub.keys() else shared['default']['line']
            if lineName not in SUPPORTED_LINES:
                raise _ConfigError(xmlCtx, 'line is not supported {}'.format(lineName))
            result.append({'lineName': lineName,
             'childID': node.nodeCD})

        if IS_DEVELOPMENT and nextLevel:
            _, nationID, vTypeID = vehicles.parseIntCompactDescr(parentCD)
            pName = vehicles.g_list.getList(nationID)[vTypeID].name
            for itemCD in nextLevel:
                _, nationID, vTypeID = vehicles.parseIntCompactDescr(itemCD)
                uName = vehicles.g_list.getList(nationID)[vTypeID].name
                LOG_ERROR('Relation between {0:>s} and {1:>s} are not defined'.format(pName, uName))

        return result

    def __readNation(self, shared, nation, clearCache=False):
        xmlPath = self.__source.nation.format(nation)
        displayInfo = self.__readNodeList(shared, nation, xmlPath, clearCache, NODE_ORDER_PREFIX_COMMON)
        xmlPath = self.__source.nationPremium.format(nation)
        premDisplayInfo = self.__readNodeList(shared, nation, xmlPath, clearCache, NODE_ORDER_PREFIX_PREMIUM)
        displayInfo.update(premDisplayInfo)
        return displayInfo

    def __readNodeList(self, shared, nation, xmlPath, clearCache=False, orderPrefix=0):
        if clearCache:
            ResMgr.purge(xmlPath)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            LOG_ERROR('can not open or read nation tree: ', nation, xmlPath)
            return ({}, {}, {})
        else:
            xPath = '{0:>s}/grid'.format(xmlPath)
            xmlCtx = (None, xPath)
            nationID = nations.INDICES[nation]
            getVehicle = vehicles.g_cache.vehicle
            precessed = _xml.getChildren(xmlCtx, section, 'nodes')
            displayInfo = {}
            for name, nodeSection in precessed:
                xPath = '{0:>s}/nodes/{1:>s}'.format(xmlPath, name)
                xmlCtx = (None, xPath)
                row = _xml.readInt(xmlCtx, nodeSection, 'row')
                column = _xml.readInt(xmlCtx, nodeSection, 'column')
                node = self.__getNodeByName(name, nationID, order=column * 1000 + orderPrefix * 100 + row)
                if not node.isFound:
                    raise _ConfigError(xmlCtx, 'Unknown vehicle type name {0:>s}'.format(node.nodeName))
                if not node.isAnnouncement:
                    vType = getVehicle(node.nationID, node.itemTypeID)
                    nextLevel = [ (idx, descr) for idx, descr in enumerate(vType.unlocksDescrs) if getTypeOfCompactDescr(descr[1]) == _VEHICLE ]
                    for unlockDescr in vType.unlocksDescrs:
                        self.__unlockPrices[unlockDescr[1]][vType.compactDescr] = unlockDescr[0]

                    for idx, data in nextLevel:
                        xpCost = data[0]
                        nextCD = data[1]
                        required = data[2:]
                        self.__nextLevels[node.nodeCD][nextCD] = (idx, xpCost, set(required))
                        self.__topLevels[nextCD].add(node.nodeCD)
                        for itemCD in required:
                            self.__topItems[itemCD].add(node.nodeCD)

                lines = self.__readNodeLines(node.nodeCD, nation, xmlCtx, nodeSection, shared)
                displayInfo[node.nodeCD] = {'row': row,
                 'column': column,
                 'lines': lines}

            return displayInfo

    def __readSettings(self, _, root):
        rawData = section2dict.parse(root['settings'])
        return displaySettingsSchema.deserialize(rawData)


g_techTreeDP = TechTreeDataProvider()
