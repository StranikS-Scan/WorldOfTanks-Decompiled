# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/techtree_dp.py
from collections import defaultdict, namedtuple
import operator
from constants import IS_DEVELOPMENT
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.techtree.nodes import BaseNode
from gui.Scaleform.daapi.view.lobby.techtree.settings import TREE_SHARED_REL_FILE_PATH, UnlockStats
from gui.Scaleform.daapi.view.lobby.techtree.settings import NATION_TREE_REL_FILE_PATH
from gui.Scaleform.daapi.view.lobby.techtree.settings import DEFAULT_UNLOCK_PROPS
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items import _xml, vehicles, getTypeOfCompactDescr
import nations
import ResMgr
from skeletons.gui.shared import IItemsCache

class _ConfigError(Exception):

    def __init__(self, ctx, msg):
        super(_ConfigError, self).__init__()
        self.msg = msg
        self.ctx = ctx

    def __str__(self):
        return 'Config error in {0:>s}. {1:>s}'.format(self.ctx[1], self.msg)


def _makeLines():
    return {'outLiteral': None,
     'outPin': None,
     'inPins': []}


DISPLAY_SETTINGS = {'hasRoot': 'readBool',
 'isLevelDisplayed': 'readBool',
 'nodeRendererName': 'readString'}
_VEHICLE = GUI_ITEM_TYPE.VEHICLE
_VEHICLE_TYPE_NAME = GUI_ITEM_TYPE_NAMES[_VEHICLE]
_AnnouncementInfo = namedtuple('_AnnouncementInfo', ('userString',
 'tooltip',
 'tags',
 'level',
 'icon',
 'isElite'))

class _TechTreeDataProvider(object):
    """
    Class performs following operations:
    - reads shared parameters for trees from file TREE_SHARED_REL_FILE_PATH;
    - reads node's display information from XML-files
        (specified nations.AVAILABLE_NAMES) that are specified for each tree of nation.
    
    Provides the following methods to draw nation tree:
    - getDisplayInfo.
    - getTopLevel. Gets parents: vehicles that provide access to given vehicle.
    - getNextLevel. Gets child: vehicles that available from given vehicle.
    - isNext2Unlock. Is given vehicle is next to unlock.
    - getNext2UnlockByItems. Returns list of vehicle are available to unlock.
    - getAvailableNations.
    - getAnnouncement*. These operations allow you to get announcement vehicles.
    """
    __slots__ = ('__loaded', '__availableNations', '__override', '__displayInfo', '__displaySettings', '__topLevels', '__topItems', '__nextLevels', '__unlockPrices', '__announcements', '__announcementCDToName', '__nextAnnouncements', '__nodes', '__nextTypeIDs')
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(_TechTreeDataProvider, self).__init__()
        self.__loaded = False
        self.__availableNations = None
        self.__override = ''
        self._clear()
        return

    def load(self, isReload=False):
        """ Reads node's display information from XML-files that are specified for
        each tree of nation and builds xml string for each vehicle listed in xml files.
        :param isReload: is force clear xml file cache and rebuild xml strings.
        :return: True if xml file was loaded, otherwise - False.
        """
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

            except _ConfigError as error:
                LOG_ERROR(error)

        finally:
            self.__makeAbsoluteCoordinates()
            self.__loaded = True

        return True

    def setOverride(self, override=''):
        """ If @param override is different from already set __override,
        it resets __loaded flag and sets new __override value.
        :param override: string containing new name of settings that should be overridden.
        """
        if self.__override != override:
            self.__override = override
            self.__loaded = False

    def getDisplaySettings(self, nationID):
        """ Gets display settings that defined in grid.
        :param nationID: integer containing ID of nation.
        :return: { <setting name> : <setting value>, ... }. Available settings see in tree_shared.xml.
        """
        try:
            result = self.__displaySettings[nationID]
        except KeyError:
            result = {}

        return result

    def getNationTreeIterator(self, nationID):
        """ Get iterator to get nodes and display information by specified nation.
        :param nationID: integer containing ID of nation.
        :return: generator.
        """
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
        """ Gets top level vehicles, which are parents for given vehicle.
        :param vTypeCD: int-type vehicle compact descriptor.
        :return: set( <vehicle type compact descr>, ... )
        """
        return self.__topLevels[vTypeCD]

    def getNextLevel(self, vTypeCD):
        """ Gets next level vehicles, which are children for given vehicle.
        :param vTypeCD: int-type vehicle compact descriptor.
        :return: set( <vehicle type compact descr>, ... )
        """
        return self.__nextLevels[vTypeCD].keys()

    def isNext2Unlock(self, vTypeCD, unlocked=set(), xps=None, freeXP=0):
        """ Is given vehicle is next to unlock. "next to unlock" - all required
        items are unlocked. If vehicle is available in a few vehicles, than
        returns compact descriptor for parent vehicle where min XP cost.
        NOTE: if xps is defined than searches vehicles for which enough experience
        and available.
        :param vTypeCD: compact descriptor of vehicle (int).
        :param unlocked: set of unlocked items (int compact descriptor).
        :param xps: dict of vehicles XPs { int compact descriptor : xp, ... }
        :param freeXP: value of free XP.
        :return: (<is available>, <instance of UnlockProps>).
        """
        topLevel = self.getTopLevel(vTypeCD)
        available = False
        topIDs = set()
        compare = []
        result = DEFAULT_UNLOCK_PROPS
        for parentCD in topLevel:
            nextLevel = self.__nextLevels[parentCD]
            idx, xpCost, required = nextLevel[vTypeCD]
            if required.issubset(unlocked) and parentCD in unlocked:
                topIDs.add(parentCD)
                compare.append(UnlockProps(parentCD, idx, xpCost, topIDs))
                available = True
            if not result.xpCost or result.xpCost > xpCost:
                result = UnlockProps(parentCD, idx, xpCost, set())

        if available:
            result = self._findNext2Unlock(compare, xps=xps, freeXP=freeXP)
        return (available, result)

    def getNext2UnlockByItems(self, itemCDs, unlocked=set(), xps=None, freeXP=0):
        """ Returns list of vehicle are available to unlock (all required
        items are unlocked) by unlocked items.
        NOTE: if xps is defined than searches vehicles for which enough experience
            and available.
        :param itemCDs: list of unlocked items which determine available vehicles.
        :param unlocked: set of unlocked items (int compact descriptor).
        :param xps: dict of vehicles XPs { int compact descriptor : xp, ... }
        :param freeXP: value of free XP.
        :return: dict( <vehicle compact descriptor>: <instance of UnlockProps>, ... )
        """
        filtered = filter(lambda item: item in self.__topItems, itemCDs)
        if not filtered or not unlocked:
            return {}
        available = defaultdict(list)
        parentCDs = set(filter(lambda item: getTypeOfCompactDescr(item) == _VEHICLE, itemCDs))
        for item in filtered:
            if item in unlocked:
                parentCDs |= self.__topItems[item]

        for parentCD in parentCDs:
            if parentCD not in unlocked:
                continue
            nextLevel = self.__nextLevels[parentCD]
            topIDs = set()
            for childCD, (idx, xpCost, required) in nextLevel.iteritems():
                if childCD not in unlocked and required.issubset(unlocked):
                    topIDs.add(parentCD)
                    available[childCD].append(UnlockProps(parentCD, idx, xpCost, topIDs))

        result = {}
        for childCD, compare in available.iteritems():
            result[childCD] = self._findNext2Unlock(compare, xps=xps, freeXP=freeXP)

        return result

    def getAvailableNations(self):
        """ Gets available nations in the nation's trees.
        :return: list of nations.
        """
        if self.__availableNations is None:
            section = ResMgr.openSection(TREE_SHARED_REL_FILE_PATH)
            if section is None:
                _xml.raiseWrongXml(None, TREE_SHARED_REL_FILE_PATH, 'can not open or read')
            xmlCtx = (None, TREE_SHARED_REL_FILE_PATH)
            self.__availableNations = self.__readAvailableNations(xmlCtx, section)
        return self.__availableNations[:]

    def getAvailableNationsIndices(self):
        """ Gets available IDs of nations in the nation's trees.
        :return: list of nations IDs.
        """
        return map(lambda nation: nations.INDICES[nation], self.getAvailableNations())

    def getUnlockPrices(self, compactDescr):
        """ Gets unlock prices for given item
        :param compactDescr: int-type compact descriptor.
        :return: unlock prices dict.
        """
        return self.__unlockPrices[compactDescr]

    def getAllPossibleItems2Unlock(self, vehicle, unlocked):
        """ Gets all possible items to unlocks on vehicle.
        :param vehicle: instance of vehicle gui item.
        :param unlocked: set of int-type compact descriptors.
        :return: dict(int-type compact descriptors: instance of UnlockProps).
        """
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD not in unlocked:
                items[nodeCD] = UnlockProps(vehicle.intCD, unlockIdx, xpCost, required)

        return items

    def getUnlockedVehicleItems(self, vehicle, unlocked):
        """ Gets all unlocked items on vehicle.
        :param vehicle: instance of vehicle gui item.
        :param unlocked: set of int-type compact descriptors.
        :return: dict(int-type compact descriptors: instance of UnlockProps).
        """
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD in unlocked:
                items[nodeCD] = UnlockProps(vehicle.intCD, unlockIdx, xpCost, required)

        return items

    def getAllVehiclePossibleXP(self, nodeCD, unlockStats):
        criteria = REQ_CRITERIA.VEHICLE.FULLY_ELITE | ~REQ_CRITERIA.IN_CD_LIST([nodeCD])
        eliteVehicles = self.itemsCache.items.getVehicles(criteria)
        dirtyResult = sum(map(operator.attrgetter('xp'), eliteVehicles.values()))
        exchangeRate = self.itemsCache.items.shop.freeXPConversion[0]
        result = min(int(dirtyResult / exchangeRate) * exchangeRate, self.itemsCache.items.stats.gold * exchangeRate)
        result += unlockStats.getVehTotalXP(nodeCD)
        return result

    def isVehicleAvailableToUnlock(self, nodeCD):
        unlocks = self.itemsCache.items.stats.unlocks
        xps = self.itemsCache.items.stats.vehiclesXPs
        freeXP = self.itemsCache.items.stats.actualFreeXP
        unlockProps = g_techTreeDP.getUnlockProps(nodeCD)
        parentID = unlockProps.parentID
        allPossibleXp = self.getAllVehiclePossibleXP(parentID, UnlockStats(unlocks, xps, freeXP))
        isAvailable, props = self.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=xps, freeXP=freeXP)
        return (isAvailable and allPossibleXp >= props.xpCost, props.xpCost, allPossibleXp)

    def getUnlockProps(self, vehicleCD):
        _, unlockProps = self.isNext2Unlock(vehicleCD, unlocked=self.itemsCache.items.stats.unlocks, xps=self.itemsCache.items.stats.vehiclesXPs, freeXP=self.itemsCache.items.stats.actualFreeXP)
        return unlockProps

    def getAnnouncementByName(self, name):
        """ Gets announcement vehicle by name.
            Note: this vehicle is not added to vehicles cache, it just is defined in GUI.
        :param name: name of announcement vehicle
        :return: instance of _AnnouncementInfo or None.
        """
        return self.__announcements[name] if name in self.__announcements else None

    def getAnnouncementByCD(self, intCD):
        """ Gets announcement vehicle by int-type compact descriptor.
        :param intCD: int-type compact descriptor of vehicle.
        :return: instance of _AnnouncementInfo or None.
        """
        return self.getAnnouncementByName(self.__announcementCDToName[intCD]) if intCD in self.__announcementCDToName else None

    def getNextAnnouncements(self, intCD):
        """ Gets sequence of int-type compact descriptor that are
        announcements next vehicles for specified vehicle.
        :param intCD: int-type compact descriptor of vehicle.
        :return: generator.
        """
        if intCD not in self.__nextAnnouncements:
            return
        for nodeCD in self.__nextAnnouncements[intCD]:
            yield nodeCD

    def _clear(self):
        """Clears data."""
        self.__displayInfo = [None] * len(nations.NAMES)
        self.__nextTypeIDs = [0] * len(nations.NAMES)
        self.__nodes = [None] * len(nations.NAMES)
        self.__displaySettings = {}
        self.__topLevels = defaultdict(set)
        self.__topItems = defaultdict(set)
        self.__nextLevels = defaultdict(dict)
        self.__unlockPrices = defaultdict(dict)
        self.__announcements = {}
        self.__announcementCDToName = {}
        self.__nextAnnouncements = defaultdict(list)
        return

    def _findNext2Unlock(self, compare, xps=None, freeXP=0):
        xpGetter = xps.get

        def makeItem(item):
            xp = xpGetter(item.parentID, 0)
            return (item, xp, item.xpCost - xp)

        def getMinFreeXPSpent(props):
            _, _, minDelta = min(props, key=lambda item: item[2])
            filtered = filter(lambda item: item[2] == minDelta, props)
            recommended, _, _ = min(filtered, key=lambda item: item[1])
            return recommended

        mapping = map(makeItem, compare)
        filtered = []
        recommended = None
        if xps is not None:
            filtered = filter(lambda item: item[0].xpCost <= item[1] + freeXP, mapping)
        if filtered:
            recommended = getMinFreeXPSpent(filtered)
        if recommended is None:
            if filtered:
                mapping = filtered
            recommended = getMinFreeXPSpent(mapping)
        return recommended

    def __readShared(self, clearCache=False):
        if clearCache:
            ResMgr.purge(TREE_SHARED_REL_FILE_PATH)
        shared = {'settings': {},
         'grids': {},
         'default': {},
         'lines': {}}
        section = ResMgr.openSection(TREE_SHARED_REL_FILE_PATH)
        if section is None:
            _xml.raiseWrongXml(None, TREE_SHARED_REL_FILE_PATH, 'can not open or read')
        xmlCtx = (None, TREE_SHARED_REL_FILE_PATH)
        precessed = _xml.getChildren(xmlCtx, section, 'settings-set')
        for name, settingsSec in precessed:
            settingsName = settingsSec.asString
            xPath = '{0:>s}/{1:>s}/{2:>s}'.format(TREE_SHARED_REL_FILE_PATH, name, settingsName)
            xmlCtx = (None, xPath)
            settings = {}
            for _, settingSec in settingsSec.items():
                name = _xml.readString(xmlCtx, settingSec, 'name')
                if name not in DISPLAY_SETTINGS:
                    LOG_ERROR('Setting is invalid', name)
                    continue
                reader = DISPLAY_SETTINGS[name]
                value = getattr(_xml, reader)(xmlCtx, settingSec, 'value')
                settings[name] = value

            for name in DISPLAY_SETTINGS.iterkeys():
                if name not in settings:
                    raise _ConfigError(xmlCtx, 'Setting not found')

            shared['settings'][settingsName] = settings

        if self.__availableNations is None:
            self.__availableNations = self.__readAvailableNations((None, TREE_SHARED_REL_FILE_PATH), section)
        self.__readAnnouncements((None, TREE_SHARED_REL_FILE_PATH), section)
        self.__readSharedMetrics(shared, xmlCtx, section)
        if self.__override:
            subSec = section['overrides/{0:>s}'.format(self.__override)]
            if subSec:
                xmlCtx = (None, '{0:>s}/overrides/{1:>s}'.format(TREE_SHARED_REL_FILE_PATH, '', self.__override))
                self.__readSharedMetrics(shared, xmlCtx, subSec)
        self.__readDefaultLine(shared, xmlCtx, section)
        return shared

    def __readSharedMetrics(self, shared, xmlCtx, section):
        precessed = _xml.getChildren(xmlCtx, section, 'grids')
        for name, gridSection in precessed:
            gridName = gridSection.asString
            xPath = '{0:>s}/{1:>s}/{2:>s}'.format(TREE_SHARED_REL_FILE_PATH, name, gridName)
            gridCtx = (None, xPath)
            subSec = _xml.getSubsection(xmlCtx, gridSection, 'root')
            xmlCtx = (None, '{0:>s}/root'.format(xPath))
            rootPos = {'start': _xml.readVector2(xmlCtx, subSec, 'start').tuple(),
             'step': _xml.readInt(xmlCtx, subSec, 'step')}
            subSec = _xml.getSubsection(gridCtx, gridSection, 'vertical')
            xmlCtx = (None, '{0:>s}/vertical'.format(xPath))
            vertical = (_xml.readInt(xmlCtx, subSec, 'start'), _xml.readInt(xmlCtx, subSec, 'step'))
            subSec = _xml.getSubsection(gridCtx, gridSection, 'horizontal')
            xmlCtx = (None, '{0:>s}/horizontal'.format(xPath))
            horizontal = (_xml.readInt(xmlCtx, subSec, 'start'), _xml.readInt(xmlCtx, subSec, 'step'))
            shared['grids'][gridName] = {'root': rootPos,
             'vertical': vertical,
             'horizontal': horizontal}

        precessed = _xml.getChildren(xmlCtx, section, 'lines')
        lines = shared['lines']
        for name, sub in precessed:
            xPath = '{0:>s}/{1:>s}'.format(TREE_SHARED_REL_FILE_PATH, name)
            xmlCtx = (None, xPath)
            pinsSec = _xml.getChildren(xmlCtx, sub, 'inPin')
            inPins = dict(((pName, pSec.asVector2.tuple()) for pName, pSec in pinsSec))
            pinsSec = _xml.getChildren(xmlCtx, sub, 'outPin')
            outPins = dict(((pName, pSec.asVector2.tuple()) for pName, pSec in pinsSec))
            pinsSec = _xml.getChildren(xmlCtx, sub, 'viaPin')
            viaPins = defaultdict(dict)
            for outPin, setSec in pinsSec:
                for inPin, pSec in setSec.items():
                    viaPins[outPin][inPin] = map(lambda section: section[1].asVector2.tuple(), pSec.items())

            defSec = sub['default']
            default = {}
            if defSec is not None:
                xmlCtx = (None, '{0:>s}/default'.format(xPath))
                default = {'outPin': _xml.readString(xmlCtx, defSec, 'outPin'),
                 'inPin': _xml.readString(xmlCtx, defSec, 'inPin')}
            lines[name] = {'inPins': inPins,
             'outPins': outPins,
             'viaPins': viaPins,
             'default': default}

        return

    def __readDefaultLine(self, shared, xmlCtx, section):
        defSec = _xml.getSubsection(xmlCtx, section, 'default-line')
        xPath = '{0:>s}/default-line'.format(TREE_SHARED_REL_FILE_PATH)
        xmlCtx = (None, xPath)
        name = _xml.readString(xmlCtx, defSec, 'line')
        outPin = _xml.readString(xmlCtx, defSec, 'outPin')
        inPin = _xml.readString(xmlCtx, defSec, 'inPin')
        self.__getLineInfo(xmlCtx, name, 0, outPin, inPin, shared['lines'])
        shared['default'] = {'line': name,
         'inPin': inPin,
         'outPin': outPin}
        return

    def __getLineInfo(self, xmlCtx, lineName, nodeCD, outPin, inPin, lineShared):
        if lineName not in lineShared:
            raise _ConfigError(xmlCtx, 'Line {0:>s} not found'.format(lineName))
        line = lineShared[lineName]
        if inPin not in line['inPins'].keys():
            raise _ConfigError(xmlCtx, 'Not found in pin = {0:>s} for line {1:>s}'.format(inPin, lineName))
        if outPin not in line['outPins'].keys():
            raise _ConfigError(xmlCtx, 'Not found out pin = {0:>s} for line {1:>s} line'.format(outPin, lineName))
        return (line['outPins'][outPin], {'childID': nodeCD,
          'inPin': line['inPins'][inPin],
          'viaPins': line['viaPins'].get(outPin, {}).get(inPin, [])})

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

    def __readNodeLines(self, parentCD, nation, xmlCtx, section, shared):
        linesSec = section['lines']
        if linesSec is None:
            linesSec = {}
        result = defaultdict(_makeLines)
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
            data = shared['default'].copy()
            tags = sub.keys()
            lineShared = shared['lines']
            line = data['line']
            if 'line' in tags:
                line = sub.readString('line')
                if line in lineShared:
                    data.update(lineShared[line]['default'])
            outPin = data['outPin']
            if 'outPin' in tags:
                outPin = sub.readString('outPin')
            inPin = data['inPin']
            if 'inPin' in tags:
                inPin = sub.readString('inPin')
            outPos, lineInfo = self.__getLineInfo(xmlCtx, line, node.nodeCD, outPin, inPin, lineShared)
            result[outPin]['outPin'] = outPos
            result[outPin]['outLiteral'] = outPin
            result[outPin]['inPins'].append(lineInfo)

        if IS_DEVELOPMENT and nextLevel:
            _, nationID, vTypeID = vehicles.parseIntCompactDescr(parentCD)
            pName = vehicles.g_list.getList(nationID)[vTypeID].name
            for itemCD in nextLevel:
                _, nationID, vTypeID = vehicles.parseIntCompactDescr(itemCD)
                uName = vehicles.g_list.getList(nationID)[vTypeID].name
                LOG_ERROR('Relation between {0:>s} and {1:>s} are not defined'.format(pName, uName))

        return result.values()

    def __readNation(self, shared, nation, clearCache=False):
        xmlPath = NATION_TREE_REL_FILE_PATH % nation
        if clearCache:
            ResMgr.purge(xmlPath)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            LOG_ERROR('can not open or read nation tree: ', nation, xmlPath)
            return {}
        else:
            xmlCtx = (None, xmlPath)
            settingsName = _xml.readString(xmlCtx, section, 'settings')
            if settingsName not in shared['settings']:
                LOG_ERROR('not found settings (<settings> tag): ', settingsName, xmlPath)
                return {}
            precessed = _xml.getSubsection(xmlCtx, section, 'grid')
            gridName = precessed.asString
            if gridName not in shared['grids']:
                LOG_ERROR('not found grid (<grid> tag): ', gridName, xmlPath)
                return {}
            xPath = '{0:>s}/grid'.format(xmlPath)
            xmlCtx = (None, xPath)
            grid = shared['grids'][gridName]
            settings = shared['settings'][settingsName]
            rows = _xml.readInt(xmlCtx, precessed, 'rows')
            columns = _xml.readInt(xmlCtx, precessed, 'columns')
            nationID = nations.INDICES[nation]
            self.__displaySettings[nationID] = settings
            nationIndex = self.__availableNations.index(nation)
            hasRoot = settings['hasRoot']
            if hasRoot:
                coords = self.__makeGridCoordsWithRoot(grid, nationIndex, rows, columns)
            else:
                coords = self.__makeGridCoordsWoRoot(grid, rows, columns)
            getVehicle = vehicles.g_cache.vehicle
            precessed = _xml.getChildren(xmlCtx, section, 'nodes')
            displayInfo = {}
            for name, nodeSection in precessed:
                xPath = '{0:>s}/nodes/{1:>s}'.format(xmlPath, name)
                xmlCtx = (None, xPath)
                row = _xml.readInt(xmlCtx, nodeSection, 'row')
                column = _xml.readInt(xmlCtx, nodeSection, 'column')
                node = self.__getNodeByName(name, nationID, order=column * 100 + row)
                if not node.isFound:
                    raise _ConfigError(xmlCtx, 'Unknown vehicle type name {0:>s}'.format(node.nodeName))
                if not node.isAnnouncement:
                    vType = getVehicle(node.nationID, node.itemTypeID)
                    nextLevel = filter(lambda data: getTypeOfCompactDescr(data[1][1]) == _VEHICLE, enumerate(vType.unlocksDescrs))
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

                if hasRoot and row > 1 and column is 1:
                    raise _ConfigError(xmlCtx, 'In first column must be one node - root node, {0:>s} '.format(node.nodeName))
                elif row > rows or column > columns:
                    raise _ConfigError(xmlCtx, 'Invalid row or column index: {0:>s}, {1:d}, {2:d}'.format(node.nodeName, row, column))
                lines = self.__readNodeLines(node.nodeCD, nation, xmlCtx, nodeSection, shared)
                displayInfo[node.nodeCD] = {'row': row,
                 'column': column,
                 'position': coords[column - 1][row - 1],
                 'lines': lines}

            return displayInfo

    def __makeAbsoluteCoordinates(self):
        for displayInfo in self.__displayInfo:
            if displayInfo is None:
                continue
            for info in displayInfo.itervalues():
                lines = info['lines']
                nodePos = info['position']
                for lineInfo in lines:
                    pinPos = lineInfo['outPin']
                    lineInfo['outPin'] = (pinPos[0] + nodePos[0], pinPos[1] + nodePos[1])
                    inPins = lineInfo['inPins']
                    for pin in inPins:
                        if pin['childID'] not in displayInfo:
                            continue
                        childInfo = displayInfo[pin['childID']]
                        childPos = childInfo['position']
                        pinPos = pin['inPin']
                        pin['inPin'] = (pinPos[0] + childPos[0], pinPos[1] + childPos[1])
                        pin['viaPins'] = map(lambda item, offset=nodePos: (item[0] + offset[0], item[1] + offset[1]), pin['viaPins'])

        return

    def __makeGridCoordsWithRoot(self, grid, nationIndex, rows, columns):
        start = grid['root']['start']
        step = grid['root']['step']
        coordinates = [[[start[0], start[1] + step * nationIndex]]]
        start, step = grid['horizontal']
        hRange = xrange(start, start + step * columns, step)
        start, step = grid['vertical']
        vRange = xrange(start, start + step * rows, step)
        for x in hRange:
            coordinates.append([ (x, y) for y in vRange ])

        return coordinates

    def __makeGridCoordsWoRoot(self, grid, rows, columns):
        coordinates = []
        start, step = grid['horizontal']
        hRange = xrange(start, start + step * (columns + 1), step)
        start, step = grid['vertical']
        vRange = xrange(start, start + step * (rows + 1), step)
        for x in hRange:
            coordinates.append([ (x, y) for y in vRange ])

        return coordinates


g_techTreeDP = _TechTreeDataProvider()
