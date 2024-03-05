# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/vehicle_utils.py
import NetworkFilters
import BigWorld
from adisp import adisp_process
from debug_utils import LOG_DEBUG
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.module import getPreviewInstallerProcessor
from gui.shared.items_parameters.params_cache import g_paramsCache
from helpers import dependency
from items import getTypeOfCompactDescr
from skeletons.gui.shared import IItemsCache
_MODULES_INSTALL_ORDER = (GUI_ITEM_TYPE.CHASSIS,
 GUI_ITEM_TYPE.TURRET,
 GUI_ITEM_TYPE.GUN,
 GUI_ITEM_TYPE.ENGINE,
 GUI_ITEM_TYPE.RADIO)

def createWheelFilters(typeDescriptor):
    wheelsScrollFilter = None
    wheelsSteeringFilter = None
    if typeDescriptor.chassis.generalWheelsAnimatorConfig is not None:
        scrollableWheelsCount = typeDescriptor.chassis.generalWheelsAnimatorConfig.getNonTrackWheelsCount()
        wheelsScrollFilter = []
        for _ in range(scrollableWheelsCount):
            wheelsScrollFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
            wheelsScrollFilter[-1].input(BigWorld.time(), 0.0)

        steerableWheelsCount = typeDescriptor.chassis.generalWheelsAnimatorConfig.getSteerableWheelsCount()
        wheelsSteeringFilter = []
        for _ in range(steerableWheelsCount):
            wheelsSteeringFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
            wheelsSteeringFilter[-1].input(BigWorld.time(), 0.0)

    return (wheelsScrollFilter, wheelsSteeringFilter)


class ModuleDependencies(object):
    __slots__ = ('__stockModules', '__hasConflicted', '__conflictedModulesCD', '__hasConflicted')

    def __init__(self, stockModules):
        super(ModuleDependencies, self).__init__()
        self.__stockModules = stockModules
        self.__hasConflicted = False
        self.__hasConflicted = False
        self.__conflictedModulesCD = None
        self.__initConflictedList()
        return

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
            module = self._getModule(moduleId)
            isFit, reason = module.mayInstall(vehicle)
            if not isFit:
                if reason == 'need turret':
                    turretsCDs, chassisCDs = self.__getSuitableModulesForGun(moduleId, vehicle)
                    self.__addConflicted(GUI_ITEM_TYPE.TURRET, turretsCDs)
                    self.__addConflicted(GUI_ITEM_TYPE.CHASSIS, chassisCDs)
                elif reason == 'need gun':
                    stockGunCD = self.__stockModules[GUI_ITEM_TYPE.VEHICLE_MODULES.index(GUI_ITEM_TYPE.GUN)]
                    if stockGunCD is not None and not self._getModule(stockGunCD).isInstalled(vehicle):
                        self.__addConflicted(GUI_ITEM_TYPE.GUN, (stockGunCD,))
                else:
                    LOG_DEBUG('[Module dependencies]. Unsupported error type: "{}"'.format(reason))
        return self.__conflictedModulesCD

    def clearConflictedModules(self):
        self.__initConflictedList()

    def __addConflicted(self, moduleTypeID, moduleCDs):
        self.__hasConflicted = True
        self.__conflictedModulesCD[_MODULES_INSTALL_ORDER.index(moduleTypeID)].extend(moduleCDs)

    def __getSuitableModulesForGun(self, gunIntCD, vehicle):
        chassisCDs = []
        turretsCDs = g_paramsCache.getPrecachedParameters(gunIntCD).getTurretsForVehicle(vehicle.intCD)
        for turretIntCD in turretsCDs:
            suitableTurret = self._getModule(turretIntCD)
            isFit, _ = suitableTurret.mayInstall(vehicle)
            if isFit:
                currentTurret = vehicle.turret
                self._installModule(vehicle, suitableTurret)
                self._installModule(vehicle, currentTurret)

        return (turretsCDs, chassisCDs)

    def __initConflictedList(self):
        self.__hasConflicted = False
        self.__conflictedModulesCD = [ [] for _ in GUI_ITEM_TYPE.VEHICLE_MODULES ]

    @adisp_process
    def _installModule(self, vehicle, module):
        yield getPreviewInstallerProcessor(vehicle, module).request()

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def _getModule(self, moduleId, itemsCache=None):
        module = itemsCache.items.getItemByCD(moduleId)
        return module

    @dependency.replace_none_kwargs(itemsCache=IItemsCache)
    def getSuitableChassis(self, vehicle, itemsCache=None):
        chassis = []
        for _, _, nodeCD, _ in vehicle.getUnlocksDescrs():
            itemTypeID = getTypeOfCompactDescr(nodeCD)
            if itemTypeID == GUI_ITEM_TYPE.CHASSIS:
                chassisCand = itemsCache.items.getItemByCD(nodeCD)
                if chassisCand.mayInstall(vehicle) and not chassisCand.isInstalled(vehicle):
                    chassis.append(chassisCand)

        return chassis
