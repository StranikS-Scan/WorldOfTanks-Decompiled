# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/trees_display_info.py
# Compiled at: 2011-10-17 16:19:52
from debug_utils import LOG_ERROR
from gui.Scaleform.graphs import TREE_SHARED_REL_FILE_PATH, NATION_TREE_REL_FILE_PATH
from items import _xml, vehicles
import nations
import ResMgr, Math
from gui import GUI_NATIONS, GUI_NATIONS_ORDER_INDEX

class VehicleTreeDisplayInfo(object):
    __displayInfoFormat = '<row>{0:d}</row><column>{1:d}</column><position><x>{2.x:n}</x><y>{2.y:n}</y></position><connectors>{3:>s}</connectors>'
    __connectorFormat = '<connector><parent>{0:d}</parent><name>{1:>s}</name><size> <width>{2.x:n}</width> <height>{2.y:n}</height> </size><position> <x>{3.x:n}</x> <x>{3.y:n}</x> </position><operations>{4:>s}</operations></connector>'
    __operationFormat = '<operation><name>{0:>s}</name><value>{1:>s}</value></operation>'

    def __init__(self):
        super(VehicleTreeDisplayInfo, self).__init__()
        self.__loaded = False
        self.__availableNations = None
        self.__displayInfo = {}
        self.__topLevels = {}
        return

    def __readShared(self):
        shared = {'grids': {},
         'connectors': {}}
        section = ResMgr.openSection(TREE_SHARED_REL_FILE_PATH)
        if section is None:
            _xml.raiseWrongXml(None, TREE_SHARED_REL_FILE_PATH, 'can not open or read')
        xmlCtx = (None, TREE_SHARED_REL_FILE_PATH)
        precessed = _xml.getChildren(xmlCtx, section, 'grids')
        for _, gridSection in precessed:
            coordinates = []
            gridName = gridSection.asString
            rootPos = _xml.readVector2(xmlCtx, gridSection, 'root')
            coordinates.append([rootPos])
            hPosSection = _xml.getChildren(xmlCtx, gridSection, 'horizPos')
            xs = [ xSection.asFloat for _, xSection in hPosSection ]
            vPosSection = _xml.getChildren(xmlCtx, gridSection, 'vertPos')
            for _, ySection in vPosSection:
                y = ySection.asFloat
                coordinates.append([ Math.Vector2(x, y) for x in xs ])

            shared['grids'][gridName] = {'coordinates': coordinates,
             'rowCount': len(coordinates),
             'columnCount': len(xs)}

        if self.__availableNations is None:
            self.__availableNations = self.__readAvailableNations(xmlCtx, _xml.getSubsection(xmlCtx, section, 'available-nations'))
        precessed = _xml.getChildren(xmlCtx, section, 'connectors')
        for connectorName, cSection in precessed:
            inPins = dict(((gridName, gridSection.asVector2) for gridName, gridSection in _xml.getChildren(xmlCtx, cSection, 'inPin')))
            outPins = dict(((gridName, gridSection.asVector2) for gridName, gridSection in _xml.getChildren(xmlCtx, cSection, 'outPin')))
            shared['connectors'][connectorName] = {'symbol': _xml.readString(xmlCtx, cSection, 'symbol'),
             'size': _xml.readVector2(xmlCtx, cSection, 'size'),
             'scale': cSection.readBool('scale', False),
             'inPins': inPins,
             'outPins': outPins}

        return shared

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

    def __readNodeConnectors(self, xmlCtx, shared, nation, nationShared, nodeName, nodeSection):
        if nodeSection.has_key('connectors'):
            cSections = _xml.getChildren(xmlCtx, nodeSection, 'connectors')
        else:
            cSections = {}
        connectors = []
        topLevels = []
        for name, cSection in cSections:
            sharedConnector = shared['connectors'].get(name)
            if sharedConnector is None:
                LOG_ERROR('not found connector: ', name, xmlCtx)
            parent = _xml.readString(xmlCtx, cSection, 'parent')
            pUniqueName = '{0:>s}:{1:>s}'.format(nation, parent)
            ids = vehicles.g_list.getIDsByName(pUniqueName)
            pCompactDescr = vehicles.g_list.getList(ids[0]).get(ids[1]).get('compactDescr')
            topLevels.append((pUniqueName, pCompactDescr))
            if sharedConnector['scale'] and cSection.has_key('size'):
                size = _xml.readVector2(xmlCtx, cSection, 'size')
            else:
                size = sharedConnector['size']
            if cSection.has_key('position'):
                cPosition = _xml.readVector2(xmlCtx, cSection, 'position')
            elif cSection.has_key('inPin'):
                nodePosition = nationShared[nodeName]['position']
                inPin = _xml.readString(xmlCtx, cSection, 'inPin')
                pinVector = sharedConnector['inPins'].get(inPin)
                if pinVector is None:
                    raise Exception, 'Not found in pin = {0:>s} for connector = {1:>s}'.format(inPin, name)
                cPosition = Math.Vector2(nodePosition.x + pinVector.x, nodePosition.y + pinVector.y - size.y)
            elif cSection.has_key('outPin'):
                parentPosition = nationShared[parent]['position']
                outPin = _xml.readString(xmlCtx, cSection, 'outPin')
                pinVector = sharedConnector['outPins'].get(outPin)
                if pinVector is None:
                    raise Exception, 'Not found out pin = {0:>s} for connector = {1:>s}'.format(outPin, name)
                cPosition = Math.Vector2(parentPosition.x + pinVector.x, parentPosition.y + pinVector.y)
            else:
                raise Exception, 'Can not gets connector position node = %s, connector = %s' % (nodeSection.name, name)
            operations = []
            if cSection.has_key('operations'):
                opsSection = _xml.getChildren(xmlCtx, cSection, 'operations')
            else:
                opsSection = {}
            for name, opSection in opsSection:
                operations.append(self.__operationFormat.format(name, opSection.asString))

            connectors.append(self.__connectorFormat.format(pCompactDescr, sharedConnector['symbol'], size, cPosition, ''.join(operations)))

        return (''.join(connectors), topLevels)

    def __readNation(self, shared, nation, clearCache=False):
        xmlPath = NATION_TREE_REL_FILE_PATH % nation
        if clearCache:
            ResMgr.purge(xmlPath)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            LOG_ERROR('can not open or read nation tree: ', nation, xmlPath)
            return
        else:
            xmlCtx = (None, xmlPath)
            gridName = _xml.readString(xmlCtx, section, 'grid')
            grid = shared['grids'].get(gridName)
            if grid is None:
                LOG_ERROR('not found grid (<grid> tag): ', gridName, xmlPath)
            coordinates = grid['coordinates']
            rowCount = grid['rowCount']
            columnCount = grid['columnCount']
            precessed = _xml.getChildren(xmlCtx, section, 'nodes')
            nationShared = {}
            for name, nodeSection in precessed:
                uniqueName = '{0:>s}:{1:>s}'.format(nation, name)
                vehicles.g_list.getIDsByName(uniqueName)
                row = _xml.readInt(xmlCtx, nodeSection, 'row')
                column = _xml.readInt(xmlCtx, nodeSection, 'column')
                if row is 1 and column > 1:
                    raise Exception, 'In first row must be one node - root node, %s ' % uniqueName
                elif row > rowCount or column > columnCount:
                    raise Exception, 'Invalid row or column index: %s, %d, %d' % (uniqueName, row, column)
                nationShared[name] = {'uniqueName': uniqueName,
                 'row': row,
                 'column': column,
                 'position': coordinates[row - 1][column - 1]}

            for name, nodeSection in precessed:
                nodeInfo = nationShared[name]
                connectors, topLevels = self.__readNodeConnectors(xmlCtx, shared, nation, nationShared, name, nodeSection)
                self.__displayInfo[nodeInfo['uniqueName']] = self.__displayInfoFormat.format(nodeInfo['row'], nodeInfo['column'], nodeInfo['position'], connectors)
                self.__topLevels[nodeInfo['uniqueName']] = topLevels

            return

    def load(self, reload=False):
        if self.__loaded and not reload:
            return
        self.__displayInfo = {}
        self.__topLevels = {}
        shared = self.__readShared()
        for nation in self.__availableNations:
            self.__readNation(shared, nation, clearCache=reload)

        self.__loaded = True

    def getDisplayInfo(self, name):
        return self.__displayInfo.get(name)

    def getTopLevel(self, name):
        return self.__topLevels.get(name, [])

    def getAvailableNations(self):
        if self.__availableNations is None:
            section = ResMgr.openSection(TREE_SHARED_REL_FILE_PATH)
            if section is None:
                _xml.raiseWrongXml(None, TREE_SHARED_REL_FILE_PATH, 'can not open or read')
            xmlCtx = (None, TREE_SHARED_REL_FILE_PATH)
            self.__availableNations = self.__readAvailableNations(xmlCtx, section)
        return self.__availableNations[:]


g_treeDisplayInfo = VehicleTreeDisplayInfo()
