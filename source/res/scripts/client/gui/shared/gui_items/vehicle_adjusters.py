# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_adjusters.py
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from helpers import dependency
from adisp import process
from debug_utils import LOG_WARNING
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors import module as installer_module
from items import tankmen
from skeletons.gui.shared import IItemsCache

@process
def installModulesSet(vehicle, modules, notFitted):
    UNDEFINED_INDEX = -1

    def __findModuleIndex(mList, moduleTypeID):
        for i in xrange(len(mList)):
            if mList[i].itemTypeID == moduleTypeID:
                return i

        return UNDEFINED_INDEX

    def __updateVehicleModule(vehicle, module):
        typeID = module.itemTypeID
        if typeID == GUI_ITEM_TYPE.CHASSIS:
            vehicle.chassis = module
        elif typeID == GUI_ITEM_TYPE.ENGINE:
            vehicle.engine = module
        elif typeID == GUI_ITEM_TYPE.RADIO:
            vehicle.radio = module
        elif typeID == GUI_ITEM_TYPE.TURRET:
            vehicle.turret = module
        elif typeID == GUI_ITEM_TYPE.GUN:
            vehicle.gun = module

    if modules:
        while modules:
            module = modules.pop()
            isFit, notFitReason = module.mayInstall(vehicle)
            if isFit:
                yield installer_module.getPreviewInstallerProcessor(vehicle, module).request()
                __updateVehicleModule(vehicle, module)
            if notFitReason == 'need turret':
                turretIndex = __findModuleIndex(modules, GUI_ITEM_TYPE.TURRET)
                if turretIndex != UNDEFINED_INDEX:
                    modules.append(module)
                    modules.append(modules.pop(turretIndex))
                    installModulesSet(vehicle, modules, notFitted)
                    break
                else:
                    notFitted.append(notFitReason)
            if notFitReason == 'need gun':
                gunIndex = __findModuleIndex(modules, GUI_ITEM_TYPE.GUN)
                if gunIndex != UNDEFINED_INDEX:
                    modules.append(module)
                    modules.append(modules.pop(gunIndex))
                    installModulesSet(vehicle, modules, notFitted)
                    break
                else:
                    notFitted.append(notFitReason)
            if notFitReason == 'too heavy':
                chassisIndex = __findModuleIndex(modules, GUI_ITEM_TYPE.CHASSIS)
                if chassisIndex != UNDEFINED_INDEX:
                    modules.append(module)
                    modules.append(modules.pop(chassisIndex))
                    installModulesSet(vehicle, modules, notFitted)
                    break
                else:
                    notFitted.append(notFitReason)
            if notFitReason == 'too heavy chassis':
                modules.insert(0, module)
                installModulesSet(vehicle, modules, notFitted)
                break


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def installEquipment(vehicle, intCD, slotIndex, itemsCache=None):
    if intCD and itemsCache is not None:
        equipment = itemsCache.items.getItemByCD(int(intCD))
    else:
        equipment = None
    if equipment:
        success, reason = equipment.mayInstall(vehicle, slotIndex)
        if not success:
            LOG_WARNING('Equipment could not been installed, reason: '.format(reason))
            return
    vehicle.consumables.installed[slotIndex] = equipment
    vehicle.consumables.layout[slotIndex] = equipment
    return


def swapEquipment(vehicle, leftID, rightID):
    vehicle.consumables.swap(leftID, rightID)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def installOptionalDevice(vehicle, newId, slotIndex, itemsCache=None):
    newId = int(newId)
    optDev = itemsCache.items.getItemByCD(newId)
    itemTypeID = optDev.itemTypeID
    mayInstall, reason = optDev.mayInstall(vehicle, slotIndex)
    if mayInstall:
        vehicle.descriptor.installOptionalDevice(optDev.intCD, slotIndex)
        vehicle.optDevices.installed[slotIndex] = optDev
        vehicle.optDevices.layout[slotIndex] = optDev
    else:
        LOG_WARNING('Component "{}" has not been installed. Reason: {}.'.format(itemTypeID, reason))
    return (mayInstall, reason)


def removeOptionalDevice(vehicle, slotIndex):
    installedDevice = vehicle.optDevices.installed[slotIndex]
    if installedDevice is not None:
        mayRemove, reason = vehicle.descriptor.mayRemoveOptionalDevice(slotIndex)
        if mayRemove:
            vehicle.descriptor.removeOptionalDevice(slotIndex)
            vehicle.optDevices.installed[slotIndex] = None
            vehicle.optDevices.layout[slotIndex] = None
        return (mayRemove, reason)
    else:
        LOG_WARNING("Couldn't remove optional device from slot {} because slot is already empty!".format(slotIndex))
        return (False, 'slot is empty')


def swapOptionalDevice(vehicle, leftID, rigthID):
    maySwap, reason = vehicle.descriptor.maySwapOptionalDevice(leftID, rigthID)
    if maySwap:
        vehicle.descriptor.swapOptionalDevice(leftID, rigthID)
        vehicle.optDevices.swap(leftID, rigthID)
    else:
        LOG_WARNING('Slots "{}" has not been swapped. Reason: {}.'.format((leftID, rigthID), reason))
    return (maySwap, reason)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def installBattleBoosterOnVehicle(vehicle, intCD, itemsCache=None):
    if intCD and itemsCache is not None:
        booster = itemsCache.items.getItemByCD(int(intCD))
    else:
        booster = None
    vehicle.battleBoosters.installed[0] = booster
    vehicle.battleBoosters.layout[0] = booster
    return


def changeShell(vehicle, slotIndex):
    if vehicle.descriptor.activeGunShotIndex != slotIndex:
        vehicle.descriptor.activeGunShotIndex = slotIndex
        return True
    return False


def applyTankmanSkillOnVehicle(vehicle, skillsByRolesIdx):
    nationID, vehicleTypeID = vehicle.descriptor.type.id
    crew = vehicle.crew
    for idx, (roleIdx, tman) in enumerate(crew):
        skills = skillsByRolesIdx[roleIdx]
        if skills:
            prevRoleLevel = tankmen.MAX_SKILL_LEVEL
            role = tman.role
            crew[idx] = (roleIdx, cmp_helpers.createTankman(nationID, vehicleTypeID, role, prevRoleLevel, skills))
