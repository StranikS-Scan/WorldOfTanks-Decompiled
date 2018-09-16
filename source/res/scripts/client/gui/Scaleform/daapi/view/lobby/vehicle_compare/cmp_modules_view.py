# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_modules_view.py
from adisp import process
from debug_utils import LOG_WARNING, LOG_DEBUG, LOG_ERROR
from gui.Scaleform.daapi.view.lobby.techtree import dumpers, nodes
from gui.Scaleform.daapi.view.lobby.techtree.data import ResearchItemsData
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.Scaleform.daapi.view.lobby.vehicle_compare.cmp_configurator_base import VehicleCompareConfiguratorBaseView
from gui.Scaleform.daapi.view.meta.VehicleModulesViewMeta import VehicleModulesViewMeta
from gui.Scaleform.genConsts.NODE_STATE_FLAGS import NODE_STATE_FLAGS
from gui.Scaleform.locale.VEH_COMPARE import VEH_COMPARE
from gui.game_control.veh_comparison_basket import getSuitableChassis, getInstalledModulesCDs
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from helpers.i18n import makeString as _ms
from items import getTypeOfCompactDescr
from nations import AVAILABLE_NAMES
from gui.Scaleform.genConsts.VEHICLE_COMPARE_CONSTANTS import VEHICLE_COMPARE_CONSTANTS
from skeletons.gui.shared import IItemsCache

class _MODULES_TYPES(object):
    BASIC = 'basic'
    CURRENT = 'current'
    CUSTOM = 'custom'


_MODULES_INSTALL_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)

def _getModule(moduleId):
    module = _getItem(moduleId)
    assert module.itemTypeID in GUI_ITEM_TYPE.VEHICLE_MODULES
    return module


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def _getItem(itemID, itemsCache=None):
    return itemsCache.items.getItemByCD(itemID)


@process
def _installModule(vehicle, module):
    yield getPreviewInstallerProcessor(vehicle, module).request()


def _getSuitableChassisIDs(vehicle):
    return map(lambda ch: ch.intCD, getSuitableChassis(vehicle))


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
            suitableTurret = _getModule(turretIntCS)
            isFit, reason = suitableTurret.mayInstall(vehicle)
            if not isFit:
                if reason == 'too heavy':
                    chassisCDs = map(lambda ch: ch.intCD, getSuitableChassis(vehicle))
            currentTurret = vehicle.turret
            _installModule(vehicle, suitableTurret)
            gun = _getModule(gunIntCD)
            isFit, reason = gun.mayInstall(vehicle)
            if not isFit:
                if reason == 'too heavy':
                    chassisCDs = _getSuitableChassisIDs(vehicle)
            _installModule(vehicle, currentTurret)

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
        displayInfo = {'path': path,
         'renderer': renderer,
         'level': level}
        return nodes.RealNode(nodeCD, guiItem, 0, state, displayInfo, unlockProps=unlockProps)

    def _loadTopLevel(self, rootItem, unlockStats):
        pass


class VehicleModulesView(VehicleModulesViewMeta, VehicleCompareConfiguratorBaseView):

    def __init__(self):
        super(VehicleModulesView, self).__init__()
        self.__nodes = None
        self.__vehicle = None
        self.__nodeDataGenerator = None
        self.__currentModulesType = None
        self.__isInited = False
        self.__configuredVehModulesIDs = set()
        self.__initialModulesIDs = set()
        return

    def _init(self):
        super(VehicleModulesView, self)._init()
        configuratedVehicle = self._container.getCurrentVehicle()
        basketVehCmpData = self._container.getBasketVehCmpData()
        self.__configuredVehModulesIDs = set(getInstalledModulesCDs(self._container.getInitialVehicleData()[0]))
        self.__initialize(configuratedVehicle.descriptor.makeCompactDescr(), self.__detectModulesType(configuratedVehicle))
        stockVehicle = Vehicle(basketVehCmpData.getStockVehStrCD())
        self.__modulesInstaller = _ModulesInstaller(getInstalledModulesCDs(stockVehicle))
        self.as_setInitDataS({'title': _ms(VEH_COMPARE.MODULESVIEW_TITLE, vehName=stockVehicle.userName),
         'resetBtnLabel': VEH_COMPARE.MODULESVIEW_RESETBTNLABEL,
         'cancelBtnLabel': VEH_COMPARE.MODULESVIEW_CLOSEBTNLABEL,
         'applyBtnLabel': VEH_COMPARE.MODULESVIEW_COMPAREBTNLABEL,
         'resetBtnTooltip': VEH_COMPARE.MODULESVIEW_RESETBTNLABEL_TOOLTIP,
         'cancelBtnTooltip': VEH_COMPARE.MODULESVIEW_CLOSEBTNLABEL_TOOLTIP,
         'applyBtnTooltip': VEH_COMPARE.MODULESVIEW_COMPAREBTNLABEL_TOOLTIP})
        self.__isInited = True

    def _dispose(self):
        self.__configuredVehModulesIDs = None
        self.__vehicle = None
        self.__modulesInstaller.dispose()
        self.__modulesInstaller = None
        if self.__nodeDataGenerator:
            self.__nodeDataGenerator.clear(True)
            self.__nodeDataGenerator = None
        super(VehicleModulesView, self)._dispose()
        return

    def onShow(self):
        if self.__isInited:
            self._init()

    def onCloseView(self):
        self._container.as_showViewS(VEHICLE_COMPARE_CONSTANTS.VEHICLE_CONFIGURATOR_VIEW)

    def resetConfig(self):

        def __logModuleWarning():
            LOG_WARNING('Unable to apply the following modules type: {}'.format(self.__currentModulesType))

        def __logModuleError():
            LOG_ERROR('Attempt to apply unsupported modules type: {}'.format(self.__currentModulesType))

        basketVehicle = self._container.getBasketVehCmpData()
        if basketVehicle.isInInventory():
            if self.__currentModulesType == _MODULES_TYPES.CUSTOM or self.__currentModulesType == _MODULES_TYPES.BASIC:
                self.__initialize(basketVehicle.getInvVehStrCD(), _MODULES_TYPES.CURRENT)
            elif self.__currentModulesType == _MODULES_TYPES.CURRENT:
                __logModuleWarning()
            else:
                __logModuleError()
        elif self.__currentModulesType == _MODULES_TYPES.CUSTOM:
            self.__initialize(basketVehicle.getStockVehStrCD(), _MODULES_TYPES.BASIC)
        elif self.__currentModulesType == _MODULES_TYPES.BASIC:
            __logModuleWarning()
        else:
            __logModuleError()

    def applyConfig(self):
        self._container.setModules(cmp_helpers.getVehicleModules(self.__vehicle))
        self.onCloseView()

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

    def onModuleClick(self, moduleId):
        moduleId = int(moduleId)
        newComponentItem = _getModule(moduleId)
        isMainFit, mainReason = newComponentItem.mayInstall(self.__vehicle)
        if isMainFit:
            _installModule(self.__vehicle, newComponentItem)
        conflictedModules = self.__modulesInstaller.getConflictedModules()
        if self.__modulesInstaller.hasConflicted():
            for modulesByType in conflictedModules:
                for moduleCD in modulesByType:
                    conflictedModule = _getModule(moduleCD)
                    _installModule(self.__vehicle, conflictedModule)

        if not isMainFit:
            _installModule(self.__vehicle, newComponentItem)
        self.__updateChangedSlots()
        self.__updateModulesType(self.__detectModulesType(self.__vehicle))

    def __initialize(self, strCD, modulesType):
        self.__vehicle = Vehicle(strCD)
        if self.__nodeDataGenerator is not None:
            self.__nodeDataGenerator.setVehicle(vehicle=self.__vehicle)
        else:
            self.__nodeDataGenerator = _PreviewItemsData(dumpers.ResearchBaseDumper(), self.__vehicle)
        self.__updateModulesData()
        self.__initialModulesIDs = set(getInstalledModulesCDs(self.__vehicle))
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
        basketVehicle = self._container.getBasketVehCmpData()
        if basketVehicle.isInInventory():
            btnEnabled = modulesType != _MODULES_TYPES.CURRENT
        else:
            btnEnabled = modulesType != _MODULES_TYPES.BASIC
        self.as_setResetEnabledS(btnEnabled)
        self.as_setApplyEnabledS(self.__initialModulesIDs != set(getInstalledModulesCDs(self.__vehicle)))

    def __detectModulesType(self, targetVeh):
        if self.__configuredVehModulesIDs == set(getInstalledModulesCDs(targetVeh)):
            if self._container.getBasketVehCmpData().isInInventory():
                return _MODULES_TYPES.CURRENT
            return _MODULES_TYPES.BASIC
        return _MODULES_TYPES.CUSTOM
