# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/veh_modules_config_cmp.py
import logging
from gui.Scaleform.daapi.view.meta.VehModulesConfiguratorCmpMeta import VehModulesConfiguratorCmpMeta
from gui.doc_loaders.battle_royale_settings_loader import getTreeModuleIcon
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.gui_items import GUI_ITEM_TYPE, isItemVehicleHull
from helpers import int2roman
_logger = logging.getLogger(__name__)
_GAP_BETWEEN_COLUMNS = 100
_GAP_BETWEEN_MODULES = 60
_ITEM_TYPE_TO_HEADER_ICON = {GUI_ITEM_TYPE.TURRET: backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.tower()),
 GUI_ITEM_TYPE.GUN: backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.gun()),
 GUI_ITEM_TYPE.ENGINE: backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.engine()),
 GUI_ITEM_TYPE.RADIO: backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.radio()),
 GUI_ITEM_TYPE.CHASSIS: backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.chassis()),
 'hull': backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.hull()),
 'vehicle': backport.image(R.images.gui.maps.icons.battleRoyale.tree.header.vehicle())}

def getVehicleNationIcon(vehicle):
    nation = R.images.gui.maps.icons.battleRoyale.emblems.dyn(vehicle.nationName, None)
    return backport.image(nation()) if nation else ''


def _makeItemVO(intCD, icon, selected):
    return {'intCD': intCD,
     'icon': icon,
     'potentialLinks': [],
     'activeLink': -1,
     'selected': selected,
     'selectable': False,
     'gap': _GAP_BETWEEN_MODULES}


def _makeModuleVO(item, selected):
    itemIntCD = item.intCD
    return _makeItemVO(itemIntCD, getTreeModuleIcon(item.descriptor.id), selected)


def _makeColumnVO(index, modules, headerIcon, selected=False):
    return {'index': index,
     'headerIcon': headerIcon,
     'headerText': int2roman(index + 1),
     'selected': selected,
     'highlighted': False,
     'availableForSelection': False,
     'modules': modules,
     'gap': _GAP_BETWEEN_COLUMNS}


def _makeFirstColumnVO(vehicle):
    return _makeColumnVO(0, [_makeItemVO(vehicle.intCD, 'vehicle', selected=True)], _ITEM_TYPE_TO_HEADER_ICON['vehicle'], selected=True)


def _getHeaderIcon(item, vehicle):
    return _ITEM_TYPE_TO_HEADER_ICON['hull'] if item.itemTypeID == GUI_ITEM_TYPE.CHASSIS and isItemVehicleHull(item.intCD, vehicle) else _ITEM_TYPE_TO_HEADER_ICON[item.itemTypeID]


class VehicleModulesConfiguratorCmp(VehModulesConfiguratorCmpMeta):

    def __init__(self):
        super(VehicleModulesConfiguratorCmp, self).__init__()
        self.__inited = False
        self.__availableLevel = None
        self.__currentLevel = 0
        self._columnsVOs = None
        self.__moduleIntCdToPosition = None
        self._vehicle = None
        return

    def setVehicle(self, vehicle):
        self._vehicle = vehicle

    def setAvailableLevel(self, level):
        if self.__availableLevel != level:
            self.__availableLevel = level
            if self.__inited:
                updatedIndexes = self._updateColumns()
                if updatedIndexes:
                    self.__sendUpdate(updatedIndexes)
            else:
                self._refresh()
                self.__inited = True
        else:
            _logger.warning('Attempt to set the same level %s', level)

    def getAvailableLevel(self):
        return self.__availableLevel

    def onClick(self, intCD, columnIdx, moduleIdx):
        module = self._getItem(intCD)
        success = self._installModule(module)
        if success:
            column = self._columnsVOs[columnIdx]
            updatedIndexes = set()
            moduleVO = column['modules'][moduleIdx]
            if not moduleVO['selected']:
                moduleVO['selected'] = True
                column['selected'] = True
                for prevModule in self._columnsVOs[columnIdx - 1]['modules']:
                    if prevModule['selected']:
                        moduleVO['activeLink'] = prevModule['intCD']
                        break

                module = self._getItem(intCD)
                self._setCurrentLevel(module.level)
                updatedIndexes.add(columnIdx)
                self.__sendUpdate(updatedIndexes | self._updateColumns())
        else:
            _logger.warning('Attempt to select unsuitable module %s !', intCD)
        return success

    def _syncVehicle(self, changedModuleIntCD):
        colID, modID = self.__moduleIntCdToPosition[changedModuleIntCD]
        if not self._columnsVOs[colID]['modules'][modID]['selected']:
            self._recreate()
            _logger.info('Module has been changed outside current view.')

    def _recreate(self):
        self._init()
        self.as_updateItemsS(self._columnsVOs)

    def _refresh(self):
        self._init()
        self.as_setItemsS(self._columnsVOs)

    def _getHighlightedModules(self):
        result = []
        for column in self._columnsVOs:
            if column['highlighted']:
                for module in column['modules']:
                    if module['selectable']:
                        result.append((module['intCD'], module['icon'], len(result)))

                break

        return result

    def _init(self):
        self.__moduleIntCdToPosition = {}
        vehicle = self._vehicle
        self._columnsVOs = [_makeFirstColumnVO(vehicle)]
        currentLevel = 1
        for _, _, intCD, _ in vehicle.getUnlocksDescrs():
            item = self._getItem(intCD)
            level = item.level
            columnIndex = level - 1
            while len(self._columnsVOs) <= columnIndex:
                self._columnsVOs.append(None)

            moduleSelected = False
            if not self._columnsVOs[columnIndex]:
                moduleSelected = self._isModuleSelected(item, vehicle)
                self._columnsVOs[columnIndex] = _makeColumnVO(columnIndex, [_makeModuleVO(item, moduleSelected)], _getHeaderIcon(item, vehicle))
                self.__moduleIntCdToPosition[item.intCD] = (columnIndex, 0)
            else:
                modules = self._columnsVOs[columnIndex]['modules']
                for m in modules:
                    if m['intCD'] == intCD:
                        break
                else:
                    self.__moduleIntCdToPosition[item.intCD] = (columnIndex, len(modules))
                    moduleSelected = self._isModuleSelected(item, vehicle)
                    modules.append(_makeModuleVO(item, moduleSelected))

            if moduleSelected:
                self._columnsVOs[columnIndex]['selected'] = True
                if level > currentLevel:
                    currentLevel = level

        self.__currentLevel = currentLevel
        self._updateLinks(vehicle)
        self._updateColumns()
        return

    def _isModuleSelected(self, item, vehicle):
        return item.isInstalled(vehicle)

    def _mayInstallModule(self, mItem):
        vehicle = self._vehicle
        sucess, _ = mItem.mayInstall(vehicle)
        return sucess

    def _installModule(self, moduleItem):
        return False

    def _dispose(self):
        self._vehicle = None
        self._columnsVOs = None
        super(VehicleModulesConfiguratorCmp, self)._dispose()
        return

    def _setCurrentLevel(self, moduleLevel):
        if moduleLevel > self.__currentLevel:
            self.__currentLevel = moduleLevel

    def _updateColumns(self):
        changedColumns = set()
        currentColumn = self.__currentLevel - 1
        i = currentColumn - 1
        while i >= 0:
            columnVO = self._columnsVOs[i]
            if columnVO is not None:
                for mVO in columnVO['modules']:
                    if mVO['selectable']:
                        mVO['selectable'] = False
                        changedColumns.add(i)

                if columnVO['availableForSelection']:
                    columnVO['availableForSelection'] = False
                    changedColumns.add(i)
            i = i - 1

        j = currentColumn
        totalColumns = len(self._columnsVOs)
        availableColumn = self.__availableLevel - 1
        alreadyHasHighlight = False
        while j <= availableColumn and j < totalColumns:
            columnVO = self._columnsVOs[j]
            availableForSelection = j <= availableColumn and j > currentColumn
            if columnVO['availableForSelection'] != availableForSelection:
                columnVO['availableForSelection'] = availableForSelection
                changedColumns.add(j)
            columnHighlighted = not alreadyHasHighlight and availableForSelection
            if columnVO['highlighted'] != columnHighlighted:
                columnVO['highlighted'] = columnHighlighted
                for mVO in columnVO['modules']:
                    if columnHighlighted:
                        moduleItem = self._getItem(mVO['intCD'])
                        success = self._mayInstallModule(moduleItem)
                        mVO['selectable'] = success
                    mVO['selectable'] = False

                changedColumns.add(j)
            if columnVO['highlighted']:
                alreadyHasHighlight = True
            j = j + 1

        return changedColumns

    def _updateLinks(self, vehicle):
        for i in reversed(range(1, len(self._columnsVOs))):
            currentColumn = self._columnsVOs[i]
            for moduleVO in currentColumn['modules']:
                for itemsCDs in vehicle.descriptor.type.unlocksDescrs:
                    intCD = itemsCDs[1]
                    if intCD == moduleVO['intCD']:
                        hasDirectLinks = False
                        for j in range(1, len(itemsCDs)):
                            unlockIntCD = itemsCDs[j]
                            if unlockIntCD in self.__moduleIntCdToPosition:
                                unlockColumnIdx, unlockModuleIdx = self.__moduleIntCdToPosition[unlockIntCD]
                                if unlockColumnIdx == i - 1:
                                    if unlockIntCD not in moduleVO['potentialLinks']:
                                        moduleVO['potentialLinks'].append(unlockIntCD)
                                    hasDirectLinks = True
                                    unlockModuleVO = self._columnsVOs[unlockColumnIdx]['modules'][unlockModuleIdx]
                                    if moduleVO['selected'] and unlockModuleVO['selected']:
                                        moduleVO['activeLink'] = unlockIntCD

                        if not hasDirectLinks:
                            for prevModuleVO in self._columnsVOs[i - 1]['modules']:
                                prevModuleIntCD = prevModuleVO['intCD']
                                if prevModuleIntCD not in moduleVO['potentialLinks']:
                                    moduleVO['potentialLinks'].append(prevModuleIntCD)
                                if moduleVO['selected'] and prevModuleVO['selected']:
                                    moduleVO['activeLink'] = prevModuleIntCD

    def _getItem(self, intCD):
        raise NotImplementedError

    def __sendUpdate(self, updatedIndexes):
        self.as_updateItemsS([ self._columnsVOs[i] for i in updatedIndexes ])
