# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_modules_window.py
from adisp import process
from constants import IS_DEVELOPMENT
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree import dumpers
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.techtree.settings import USE_XML_DUMPING
from gui.Scaleform.daapi.view.meta.VehicleModulesWindowMeta import VehicleModulesWindowMeta
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import MODULES_TYPES, getSuitableChassis, getInstalledModulesCDs
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import getTypeOfCompactDescr
from nations import AVAILABLE_NAMES
from skeletons.gui.game_control import IVehicleComparisonBasket
_MODULES_INSTALL_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)

def _getModule(moduleId):
    module = _getItem(moduleId)
    assert module.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
    return module


def _getItem(itemID):
    return g_itemsCache.items.getItemByCD(itemID)


class _ModulesInstaller(object):

    def __init__(self, stockModules):
        super(_ModulesInstaller, self).__init__()
        self.__initConflictedList()
        self.__stockModules = stockModules
        self.__hasConflicted = False

    def dispose(self):
        self.__conflictedModulesCD = None
        self.__stockModules = None
        return

    def hasConflicted(self):
        return self.__hasConflicted

    def getConflictedModules(self):
        return self.__conflictedModulesCD

    def updateConflicted(self, moduleId, vehicle):
        moduleId = int(moduleId)
        self.__initConflictedList()
        if moduleId:
            module = _getModule(moduleId)
            isFit, reason = module.mayInstall(vehicle)
            if not isFit:
                if reason == 'need turret':
                    turretsCDs, chassisCDs = self.__getSuitableModulesForGun(moduleId, vehicle)
                    self.__addConflicted(GUI_ITEM_TYPE.TURRET, turretsCDs)
                    self.__addConflicted(GUI_ITEM_TYPE.CHASSIS, chassisCDs)
                elif reason == 'too heavy':
                    chassis = []
                    for _, _, nodeCD, _ in vehicle.getUnlocksDescrs():
                        itemTypeID = getTypeOfCompactDescr(nodeCD)
                        if itemTypeID == GUI_ITEM_TYPE.CHASSIS:
                            chassisCand = _getModule(nodeCD)
                            if chassisCand.mayInstall(vehicle) and not chassisCand.isInstalled(vehicle):
                                chassis.append(nodeCD)

                    if chassis:
                        self.__addConflicted(GUI_ITEM_TYPE.CHASSIS, chassis)
                elif reason == 'too heavy chassis':
                    for i, stockCD in enumerate(self.__stockModules):
                        if stockCD is not None and not _getModule(stockCD).isInstalled(vehicle):
                            self.__addConflicted(GUI_ITEM_TYPE.VEHICLE_MODULES[i], (stockCD,))

                elif reason == 'need gun':
                    stockGunCD = self.__stockModules[GUI_ITEM_TYPE.VEHICLE_MODULES.index(GUI_ITEM_TYPE.GUN)]
                    if stockGunCD is not None and not _getModule(stockGunCD).isInstalled(vehicle):
                        self.__addConflicted(GUI_ITEM_TYPE.GUN, (stockGunCD,))
                else:
                    LOG_DEBUG('Install component. Unsupported error type: "{}"'.format(reason))
        return self.__conflictedModulesCD

    def clearConflictedModules(self):
        self.__initConflictedList()

    def __addConflicted(self, moduleTypeID, moduleCDs):
        """
        Adds items in the right order into conflicted modules list:
        :param moduleTypeID: item from the GUI_ITEM_TYPE
        :param moduleCDs: list of adding items
        """
        self.__hasConflicted = True
        self.__conflictedModulesCD[_MODULES_INSTALL_ORDER.index(moduleTypeID)].extend(moduleCDs)

    def __getSuitableModulesForGun(self, gunIntCD, vehicle):
        """
        Get suitable turrets and chassis for particular gun.
        Turrets also may be unsuitable because of high weight,
        in that case need to find suitable chassis
        :param gunIntCD: int compact descriptor of gun module
        :param gui.shared.gui_items.Vehicle:
        :return: tuple: (turrets int compact descriptors, chassis int compact descriptors)
        """
        chassisCDs = []
        turretsCDs = g_paramsCache.getPrecachedParameters(gunIntCD).getTurretsForVehicle(vehicle.intCD)
        for turretIntCS in turretsCDs:
            turret = _getModule(turretIntCS)
            isFit, reason = turret.mayInstall(vehicle)
            if not isFit:
                if reason == 'too heavy':
                    chassisCDs = map(lambda ch: ch.intCD, getSuitableChassis(vehicle))

        return (turretsCDs, chassisCDs)

    def __initConflictedList(self):
        self.__hasConflicted = False
        self.__conflictedModulesCD = [ [] for m in GUI_ITEM_TYPE.VEHICLE_MODULES ]


class _PreviewItemsData(ResearchItemsData):

    def __init__(self, dumper, vehicle):
        super(_PreviewItemsData, self).__init__(dumper)
        self.__previewVehicle = None
        self.setVehicle(vehicle)
        return

    def setVehicle(self, vehicle):
        self.__previewVehicle = vehicle
        self.setRootCD(self.__previewVehicle.intCD)

    def clear(self, full=False):
        if full:
            self.clearRootCD()
            self.__previewVehicle = None
        super(_PreviewItemsData, self).clear(full=full)
        return

    def getRootItem(self):
        return self.__previewVehicle

    def _getRootUnlocksDescrs(self, rootItem):
        unlockedDescrs = super(_PreviewItemsData, self)._getRootUnlocksDescrs(rootItem)
        for unlockIdx, xpCost, nodeCD, required in unlockedDescrs:
            itemTypeID = getTypeOfCompactDescr(nodeCD)
            if itemTypeID != GUI_ITEM_TYPE.VEHICLE:
                yield (unlockIdx,
                 xpCost,
                 nodeCD,
                 required)

    def _getNodeData(self, nodeCD, previewItem, guiItem, unlockStats, unlockProps, path, level=-1, topLevel=False):
        itemTypeID = guiItem.itemTypeID
        if itemTypeID == GUI_ITEM_TYPE.VEHICLE:
            renderer = 'root' if self._rootCD == nodeCD else 'vehicle'
        else:
            renderer = 'item'
        state = NODE_STATE_FLAGS.LOCKED
        if itemTypeID != GUI_ITEM_TYPE.VEHICLE:
            if guiItem.isInstalled(previewItem):
                state |= NODE_STATE_FLAGS.SELECTED
        else:
            inventoryVehicle = self.getItem(nodeCD)
            if inventoryVehicle.isUnlocked:
                state = NODE_STATE_FLAGS.UNLOCKED
                if inventoryVehicle.isInInventory:
                    state |= NODE_STATE_FLAGS.IN_INVENTORY
        return {'id': nodeCD,
         'state': state,
         'unlockProps': unlockProps,
         'displayInfo': {'path': path,
                         'renderer': renderer,
                         'level': level}}

    def _loadTopLevel(self, rootItem, unlockStats):
        pass


class VehicleModulesWindow(VehicleModulesWindowMeta):
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, ctx=None):
        super(VehicleModulesWindow, self).__init__()
        self.__vehIntCD = ctx['vehCD']
        self.__vehIndex = ctx['index']
        self.__nodes = None
        self.__vehicle = None
        self.__nodeDataGenerator = None
        self.__currentModulesType = None
        return

    def _populate(self):
        super(VehicleModulesWindow, self)._populate()
        basketVehicle = self.comparisonBasket.getVehicleAt(self.__vehIndex)
        self.__initialize(basketVehicle.getVehicleStrCD(), basketVehicle.getModulesType())
        self.as_setAttentionVisibleS(basketVehicle.isInInventory() and not basketVehicle.isActualModules())
        stockVehicle = Vehicle(basketVehicle.getStockVehStrCD())
        self.__modulesInstaller = _ModulesInstaller(getInstalledModulesCDs(stockVehicle))
        self.comparisonBasket.onSwitchChange += self.onWindowClose
        self.as_setInitDataS({'windowTitle': _ms(VEH_COMPARE.MODULESVIEW_WINDOWTITLE, vehName=stockVehicle.userName),
         'description': text_styles.main(_ms(VEH_COMPARE.MODULESVIEW_DESCRIPTION)),
         'resetBtnLabel': VEH_COMPARE.MODULESVIEW_RESETBTNLABEL,
         'closeBtnLabel': VEH_COMPARE.MODULESVIEW_CLOSEBTNLABEL,
         'compareBtnLabel': VEH_COMPARE.MODULESVIEW_COMPAREBTNLABEL,
         'resetBtnTooltip': VEH_COMPARE.MODULESVIEW_RESETBTNLABEL_TOOLTIP,
         'closeBtnTooltip': VEH_COMPARE.MODULESVIEW_CLOSEBTNLABEL_TOOLTIP,
         'compareBtnTooltip': VEH_COMPARE.MODULESVIEW_COMPAREBTNLABEL_TOOLTIP})

    def _dispose(self):
        self.comparisonBasket.onSwitchChange -= self.onWindowClose
        self.__vehicle = None
        self.__modulesInstaller.dispose()
        self.__modulesInstaller = None
        if self.__nodeDataGenerator:
            self.__nodeDataGenerator.clear(True)
            self.__nodeDataGenerator = None
        super(VehicleModulesWindow, self)._dispose()
        return

    def onWindowClose(self):
        self.destroy()

    def onResetBtnBtnClick(self):

        def __logModuleWarning():
            LOG_WARNING('Unable to apply the following modules type: {}'.format(self.__currentModulesType))

        def __logModuleError():
            LOG_ERROR('Attempt to apply unsupported modules type: {}'.format(self.__currentModulesType))

        basketVehicle = self.comparisonBasket.getVehicleAt(self.__vehIndex)
        if basketVehicle.isInInventory():
            if self.__currentModulesType == MODULES_TYPES.CUSTOM or self.__currentModulesType == MODULES_TYPES.BASIC:
                self.__initialize(basketVehicle.getInvVehStrCD(), MODULES_TYPES.CURRENT)
            elif self.__currentModulesType == MODULES_TYPES.CURRENT:
                __logModuleWarning()
            else:
                __logModuleError()
        elif self.__currentModulesType == MODULES_TYPES.CUSTOM:
            self.__initialize(basketVehicle.getStockVehStrCD(), MODULES_TYPES.BASIC)
        elif self.__currentModulesType == MODULES_TYPES.BASIC:
            __logModuleWarning()
        else:
            __logModuleError()

    def onCompareBtnClick(self):
        self.comparisonBasket.applyModulesFromVehicle(self.__vehIndex, self.__vehicle)
        self.destroy()

    def onModuleHover(self, moduleId):
        moduleId = int(moduleId)
        if moduleId:
            allConflicted = self.__modulesInstaller.updateConflicted(moduleId, self.__vehicle)
            changedNodesStates = []
            for modulesByType in allConflicted:
                for conflictedIntCD in modulesByType:
                    for mData in self.__nodes:
                        if mData['id'] == conflictedIntCD:
                            mData['state'] |= NODE_STATE_FLAGS.DASHED
                            changedNodesStates.append((conflictedIntCD, mData['state']))

            if changedNodesStates:
                self.as_setNodesStatesS(changedNodesStates)
        else:
            allConflicted = self.__modulesInstaller.getConflictedModules()
            if allConflicted:
                changedNodesStates = []
                for modulesByType in allConflicted:
                    for conflictedIntCD in modulesByType:
                        for mData in self.__nodes:
                            if mData['id'] == conflictedIntCD:
                                mData['state'] &= ~NODE_STATE_FLAGS.DASHED
                                changedNodesStates.append((conflictedIntCD, mData['state']))

                self.__modulesInstaller.clearConflictedModules()
                self.as_setNodesStatesS(changedNodesStates)

    @process
    def onModuleClick(self, moduleId):
        moduleId = int(moduleId)
        newComponentItem = _getModule(moduleId)
        isMainFit, mainReason = newComponentItem.mayInstall(self.__vehicle)
        if isMainFit:
            yield getPreviewInstallerProcessor(self.__vehicle, newComponentItem).request()
        conflictedModules = self.__modulesInstaller.getConflictedModules()
        if self.__modulesInstaller.hasConflicted():
            for modulesByType in conflictedModules:
                for moduleCD in modulesByType:
                    conflictedModule = _getModule(moduleCD)
                    yield getPreviewInstallerProcessor(self.__vehicle, conflictedModule).request()

        if not isMainFit:
            yield getPreviewInstallerProcessor(self.__vehicle, newComponentItem).request()
        self.__updateChangedSlots()
        self.__updateModulesType(self.comparisonBasket.getVehicleAt(self.__vehIndex).getModulesType(strCD=self.__vehicle.descriptor.makeCompactDescr()))

    def __initialize(self, strCD, modulesType):
        self.__vehicle = Vehicle(strCD)
        if self.__nodeDataGenerator is not None:
            self.__nodeDataGenerator.setVehicle(vehicle=self.__vehicle)
        else:
            if USE_XML_DUMPING and IS_DEVELOPMENT:
                dumper = dumpers.ResearchItemsXMLDumper()
            else:
                dumper = dumpers.ResearchBaseDumper()
            self.__nodeDataGenerator = _PreviewItemsData(dumper, self.__vehicle)
        self.__updateModulesData()
        self.as_setItemS(AVAILABLE_NAMES[self.__vehicle.nationID], self.__nodes)
        self.__updateModulesType(modulesType)
        return

    def __updateChangedSlots(self):

        def __extractData(targetList):
            return dict(map(lambda moduleData: (moduleData['id'], moduleData['state']), targetList))

        oldModulesData = __extractData(self.__nodes)
        self.__updateModulesData()
        newModulesData = __extractData(self.__nodes)
        changedSlots = []
        for k, v in newModulesData.iteritems():
            if v != oldModulesData[k]:
                changedSlots.append((k, v))

        self.as_setNodesStatesS(changedSlots)

    def __updateModulesData(self):
        self.__nodeDataGenerator.load()
        dump = self.__nodeDataGenerator.dump()
        self.__nodes = dump['nodes']

    def __updateModulesType(self, modulesType):
        self.__currentModulesType = modulesType
        basketVehicle = self.comparisonBasket.getVehicleAt(self.__vehIndex)
        if basketVehicle.isInInventory():
            btnEnabled = modulesType != MODULES_TYPES.CURRENT
        else:
            btnEnabled = modulesType != MODULES_TYPES.BASIC
        self.as_setStateS(stateText=text_styles.neutral(_ms('#veh_compare:modulesView/moduleSet/{}'.format(modulesType))), stateEnabled=btnEnabled)
