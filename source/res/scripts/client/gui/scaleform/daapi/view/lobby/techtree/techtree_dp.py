# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/techtree/techtree_dp.py
from collections import defaultdict
from constants import IS_DEVELOPMENT
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import GUI_NATIONS_ORDER_INDEX
from gui.Scaleform.daapi.view.lobby.techtree.settings import TREE_SHARED_REL_FILE_PATH
from gui.Scaleform.daapi.view.lobby.techtree.settings import NATION_TREE_REL_FILE_PATH
from gui.Scaleform.daapi.view.lobby.techtree.settings import makeDefUnlockProps
from gui.Scaleform.daapi.view.lobby.techtree.settings import UnlockProps
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from items import _xml, vehicles, getTypeOfCompactDescr
import nations
import ResMgr

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

class _TechTreeDataProvider(object):

    def __init__(self):
        super(_TechTreeDataProvider, self).__init__()
        self.__loaded = False
        self.__availableNations = None
        self.__override = ''
        self._clear()
        return

    def _clear(self):
        self.__displayInfo = {}
        self.__displaySettings = {}
        self.__topLevels = defaultdict(set)
        self.__topItems = defaultdict(set)
        self.__nextLevels = defaultdict(dict)
        self.__unlockPrices = defaultdict(dict)

    def __readShared(self, clearCache = False):
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

    def __readNodeLines(self, parentCD, nation, xmlCtx, section, shared):
        linesSec = section['lines']
        if linesSec is None:
            linesSec = {}
        result = defaultdict(_makeLines)
        nextLevel = self.__nextLevels[parentCD].keys()
        _, xPath = xmlCtx
        xPath = '{0:>s}/lines'.format(xPath)
        getIDsByName = vehicles.g_list.getIDsByName
        makeIntCDByID = vehicles.makeIntCompactDescrByID
        for name, sub in linesSec.items():
            xmlCtx = (None, '{0:>s}/lines/{1:>1}'.format(xPath, name))
            uName = '{0:>s}:{1:>s}'.format(nation, name)
            try:
                nodeCD = makeIntCDByID(_VEHICLE_TYPE_NAME, *getIDsByName(uName))
            except Exception:
                raise _ConfigError(xmlCtx, 'Unknown vehicle type name {0:>s}'.format(uName))

            if IS_DEVELOPMENT:
                if nodeCD not in nextLevel:
                    _, nationID, vTypeID = vehicles.parseIntCompactDescr(parentCD)
                    pName = vehicles.g_list.getList(nationID)[vTypeID]['name']
                    LOG_ERROR('{0:>s} does not have relation with {1:>s}'.format(pName, uName))
                else:
                    nextLevel.remove(nodeCD)
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
            outPos, lineInfo = self.__getLineInfo(xmlCtx, line, nodeCD, outPin, inPin, lineShared)
            result[outPin]['outPin'] = outPos
            result[outPin]['outLiteral'] = outPin
            result[outPin]['inPins'].append(lineInfo)

        if IS_DEVELOPMENT and len(nextLevel):
            _, nationID, vTypeID = vehicles.parseIntCompactDescr(parentCD)
            pName = vehicles.g_list.getList(nationID)[vTypeID]['name']
            for itemCD in nextLevel:
                _, nationID, vTypeID = vehicles.parseIntCompactDescr(itemCD)
                uName = vehicles.g_list.getList(nationID)[vTypeID]['name']
                LOG_ERROR('Relation between {0:>s} and {1:>s} are not defined'.format(pName, uName))

        return result.values()

    def __readNation(self, shared, nation, clearCache = False):
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
            self.__displaySettings[nations.INDICES[nation]] = settings
            nationIndex = self.__availableNations.index(nation)
            hasRoot = settings['hasRoot']
            if hasRoot:
                coords = self.__makeGridCoordsWithRoot(grid, nationIndex, rows, columns)
            else:
                coords = self.__makeGridCoordsWoRoot(grid, rows, columns)
            getIDsByName = vehicles.g_list.getIDsByName
            makeIntCDByID = vehicles.makeIntCompactDescrByID
            getVehicle = vehicles.g_cache.vehicle
            precessed = _xml.getChildren(xmlCtx, section, 'nodes')
            displayInfo = {}
            for name, nodeSection in precessed:
                xPath = '{0:>s}/nodes/{1:>s}'.format(xmlPath, name)
                xmlCtx = (None, xPath)
                uName = '{0:>s}:{1:>s}'.format(nation, name)
                try:
                    nationID, vTypeID = getIDsByName(uName)
                except Exception:
                    raise _ConfigError(xmlCtx, 'Unknown vehicle type name {0:>s}'.format(uName))

                nodeCD = makeIntCDByID(_VEHICLE_TYPE_NAME, nationID, vTypeID)
                vType = getVehicle(nationID, vTypeID)
                nextLevel = filter(lambda data: getTypeOfCompactDescr(data[1][1]) == _VEHICLE, enumerate(vType.unlocksDescrs))
                for unlockDescr in vType.unlocksDescrs:
                    self.__unlockPrices[unlockDescr[1]][vType.compactDescr] = unlockDescr[0]

                for idx, data in nextLevel:
                    xpCost = data[0]
                    nextCD = data[1]
                    required = data[2:]
                    self.__nextLevels[nodeCD][nextCD] = (idx, xpCost, set(required))
                    self.__topLevels[nextCD].add(nodeCD)
                    for itemCD in required:
                        self.__topItems[itemCD].add(nodeCD)

                row = _xml.readInt(xmlCtx, nodeSection, 'row')
                column = _xml.readInt(xmlCtx, nodeSection, 'column')
                if hasRoot and row > 1 and column is 1:
                    raise _ConfigError(xmlCtx, 'In first column must be one node - root node, {0:>s} '.format(uName))
                elif row > rows or column > columns:
                    raise _ConfigError, (xmlCtx, 'Invalid row or column index: {0:>s}, {1:d}, {2:d}'.format(uName, row, column))
                lines = self.__readNodeLines(nodeCD, nation, xmlCtx, nodeSection, shared)
                displayInfo[nodeCD] = {'row': row,
                 'column': column,
                 'position': coords[column - 1][row - 1],
                 'lines': lines}

            return displayInfo

    def __makeAbsoluteCoordinates(self):
        iterator = self.__displayInfo.iteritems()
        for _, info in iterator:
            lines = info['lines']
            nodePos = info['position']
            for lineInfo in lines:
                pinPos = lineInfo['outPin']
                lineInfo['outPin'] = (pinPos[0] + nodePos[0], pinPos[1] + nodePos[1])
                inPins = lineInfo['inPins']
                for pin in inPins:
                    if pin['childID'] not in self.__displayInfo:
                        continue
                    childInfo = self.__displayInfo[pin['childID']]
                    childPos = childInfo['position']
                    pinPos = pin['inPin']
                    pin['inPin'] = (pinPos[0] + childPos[0], pinPos[1] + childPos[1])
                    pin['viaPins'] = map(lambda item: (item[0] + nodePos[0], item[1] + nodePos[1]), pin['viaPins'])

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

    def load(self, isReload = False):
        if self.__loaded and not isReload:
            return False
        LOG_DEBUG('Tech tree data is being loaded')
        self._clear()
        try:
            shared = self.__readShared(clearCache=isReload)
            for nation in self.__availableNations:
                info = self.__readNation(shared, nation, clearCache=isReload)
                self.__displayInfo.update(info)

        except _ConfigError as error:
            LOG_ERROR(error)
        finally:
            self.__makeAbsoluteCoordinates()
            self.__loaded = True

        return True

    def setOverride(self, override = ''):
        if self.__override != override:
            self.__override = override
            self.__loaded = False

    def getDisplaySettings(self, nationID):
        try:
            result = self.__displaySettings[nationID]
        except KeyError:
            result = {}

        return result

    def getDisplayInfo(self, vTypeCD):
        result = None
        if vTypeCD in self.__displayInfo:
            result = self.__displayInfo[vTypeCD].copy()
        return result

    def getTopLevel(self, vTypeCD):
        return self.__topLevels[vTypeCD]

    def getNextLevel(self, vTypeCD):
        return self.__nextLevels[vTypeCD].keys()

    def _findNext2Unlock(self, compare, xps = None, freeXP = 0):
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
        if len(filtered):
            recommended = getMinFreeXPSpent(filtered)
        if recommended is None:
            if len(filtered):
                mapping = filtered
            recommended = getMinFreeXPSpent(mapping)
        return recommended

    def isNext2Unlock(self, vTypeCD, unlocked = set(), xps = None, freeXP = 0):
        topLevel = self.getTopLevel(vTypeCD)
        available = False
        topIDs = set()
        compare = []
        result = makeDefUnlockProps()
        for parentCD in topLevel:
            nextLevel = self.__nextLevels[parentCD]
            idx, xpCost, required = nextLevel[vTypeCD]
            if required.issubset(unlocked) and parentCD in unlocked:
                topIDs.add(parentCD)
                compare.append(UnlockProps(parentCD, idx, xpCost, topIDs))
                available = True
            elif not result.xpCost or result.xpCost > xpCost:
                result = UnlockProps(parentCD, idx, xpCost, set())

        if available:
            result = self._findNext2Unlock(compare, xps=xps, freeXP=freeXP)
        return (available, result)

    def getNext2UnlockByItems(self, itemCDs, unlocked = set(), xps = None, freeXP = 0):
        filtered = filter(lambda item: item in self.__topItems, itemCDs)
        if not len(filtered) or not len(unlocked):
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
        if self.__availableNations is None:
            section = ResMgr.openSection(TREE_SHARED_REL_FILE_PATH)
            if section is None:
                _xml.raiseWrongXml(None, TREE_SHARED_REL_FILE_PATH, 'can not open or read')
            xmlCtx = (None, TREE_SHARED_REL_FILE_PATH)
            self.__availableNations = self.__readAvailableNations(xmlCtx, section)
        return self.__availableNations[:]

    def getAvailableNationsIndices(self):
        return map(lambda nation: nations.INDICES[nation], self.getAvailableNations())

    def getUnlockPrices(self, compactDescr):
        return self.__unlockPrices[compactDescr]

    def getAllPossibleItems2Unlock(self, vehicle, unlocked):
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD not in unlocked:
                items[nodeCD] = UnlockProps(vehicle.intCD, unlockIdx, xpCost, required)

        return items

    def getUnlockedVehicleItems(self, vehicle, unlocked):
        items = {}
        for unlockIdx, xpCost, nodeCD, required in vehicle.getUnlocksDescrs():
            if required.issubset(unlocked) and nodeCD in unlocked:
                items[nodeCD] = UnlockProps(vehicle.intCD, unlockIdx, xpCost, required)

        return items


g_techTreeDP = _TechTreeDataProvider()
