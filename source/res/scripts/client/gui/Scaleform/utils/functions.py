# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/utils/functions.py
# Compiled at: 2011-12-14 18:35:18
import ArenaType, BigWorld
from adisp import async, process
from CurrentVehicle import g_currentVehicle
from helpers.i18n import makeString
from gui_items import ShopItem
from items.vehicles import getDictDescr
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES

def makeTooltip(header=None, body=None, note=None):
    """
    Make complex tooltip from carrying params.
    This special formatted string will be parsed from Flash
    net.wargaming.managers.ToolTipManager.showComplex(str, props)
    """
    res_str = ''
    if header is not None:
        res_str += '{HEADER}%s{/HEADER}' % makeString(header)
    if body is not None:
        res_str += '{BODY}%s{/BODY}' % makeString(body)
    if note is not None:
        res_str += '{NOTE}%s{/NOTE}' % makeString(note)
    return res_str


@async
def checkAmmoLevel(callback):
    """
    Check ammo for current vehicle, if it is lower then 20% shows message dialog
    Example:
            isAmmoOk = yield checkAmmoLevel()
            if isAmmoOk:
                    do something...
    
    @return: True if ammo level is ok or user confirm, False otherwise
    """
    showAmmoWarning = False
    if g_currentVehicle.isReadyToFight():
        vehicle = g_currentVehicle.vehicle
        maxAmmo = vehicle.descriptor.gun['maxAmmo']
        currentAmmo = 0
        for shell in vehicle.shells:
            currentAmmo += shell.count

        showAmmoWarning = currentAmmo * 100.0 / maxAmmo < 20

    @process
    def showConfirmation(callBack):
        isConfirmed = yield async_showConfirmDialog('lowAmmo')
        callBack(isConfirmed)

    if showAmmoWarning:
        showConfirmation(callback)
    else:
        callback(True)


def showInformationDialog(infDialog, callback, customMessage='', ns='common'):
    """
    Show information dialog (1 button - Close) and wait when player closes
            this dialog.
    
    @param infDialog: dialog name. Title, button labels, message builds as
            #dialogs:' + dialog + '/title'.
    @param callback: method is invoked when closing the dialog, without arguments.
    @param customMessage: external message if #dialogs:' + dialog + '/message'
            does not fit.
    @param ns: 'common' or 'battle'.
    """
    from gui.WindowsManager import g_windowsManager

    def onInformationDialogClosed(_):
        g_windowsManager.window.removeExternalCallbacks('informationDialog.onClose')
        callback()

    g_windowsManager.window.addExternalCallbacks({'informationDialog.onClose': onInformationDialogClosed})
    g_windowsManager.window.call('{0:>s}.showInformationDialog'.format(ns), [infDialog, customMessage, 'informationDialog.onClose'])


def showConfirmDialog(confirmDialog, callback, customMessage='', ns='common'):
    """
    Show confirmation dialog (2 buttons - Submit, Close) and wait when player
            closes this dialog.
    
    @param confirmDialog: dialog name. Title, button labels, message builds as
            #dialogs:' + dialog + '/title'.
    @param callback: method is invoked when closing the dialog with argument -
            True if player confirmed actions, otherwise - False.
    @param customMessage: external message if #dialogs:' + dialog + '/message'
            does not fit.
    @param ns: 'common' or 'battle'.
    """
    from gui.WindowsManager import g_windowsManager

    def onConfirmResponse(confirm):
        g_windowsManager.window.removeExternalCallbacks('confirmDialog.onConfirm', 'confirmDialog.onClose')
        callback(confirm)

    g_windowsManager.window.addExternalCallbacks({'confirmDialog.onConfirm': lambda callBackId: onConfirmResponse(True),
     'confirmDialog.onClose': lambda callBackId: onConfirmResponse(False)})
    g_windowsManager.window.call('{0:>s}.showConfirmDialog'.format(ns), [confirmDialog,
     customMessage,
     'confirmDialog.onConfirm',
     'confirmDialog.onClose'])


@async
def async_showConfirmDialog(confirmDialog, callback, customMessage='', ns='common'):
    """
    Asynchronous method. Show confirmation dialog and wait for user respond.
    Example:
            isConfirmed = yield showConfirmDialog('lowAmmo', customMessage = 'Are you shure?')
            if isConfirmed:
                    do something...
    
    @param confirmDialog: string - localization key
    @return: True if confirmed? False otherwise
    """
    showConfirmDialog(confirmDialog, callback, customMessage=customMessage, ns=ns)


def isModuleFitVehicle(module, vehicle, price, money, unlocks, positionIndex=0, isRemove=False):
    """
    Check module fits vehicle, return localized error string in falure
    @param module: FittingItem - module
    @param vehicle: FittiingItem - vehicle
    @param price: tuple (credits, gold)
    @param money: tuple (credits, gold)
    @param unlocks: list of compactDescr
    @param positionIndex: index of module, used in artefacts
    @param isRemove: boolean - specify if module will install or remove
    @return: tuple (succesBooleanFlag, localizedStringReason, localizedStringTooltipReason)
    """
    installPosible = True
    if isinstance(module, ShopItem) or isRemove:
        if module.itemTypeName not in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]) and module.compactDescr not in unlocks:
            return (False, '#menu:moduleFits/unlock_error', '#tooltips:moduleFits/unlock_error/body')
        if price[0] > money[0] or price[1] > money[1]:
            return (False, '#menu:moduleFits/credit_error', '#tooltips:moduleFits/credit_error/body')
    if module.itemTypeName == ITEM_TYPE_NAMES[3]:
        installPosible, reason = vehicle.descriptor.mayInstallTurret(module.compactDescr, 0)
    elif module.itemTypeName in ITEM_TYPE_NAMES[9]:
        installPosible, reason = vehicle.descriptor.mayInstallOptionalDevice(module.compactDescr, positionIndex)
        if not installPosible and reason == 'already installed' and positionIndex == module.index:
            installPosible, reason = vehicle.descriptor.mayRemoveOptionalDevice(positionIndex)
            if not installPosible:
                reason = 'remove ' + reason
    elif module.itemTypeName in ITEM_TYPE_NAMES[11]:
        for m in unlocks:
            if m.index != positionIndex and m is not module:
                installPosible = m.descriptor.checkCompatibilityWithActiveEquipment(module.descriptor)
                if installPosible:
                    installPosible = module.descriptor.checkCompatibilityWithEquipment(m.descriptor)
                if not installPosible:
                    reason = 'not with installed equipment'
                    break

    else:
        installPosible, reason = vehicle.descriptor.mayInstallComponent(module.compactDescr)
    if not installPosible:
        reason = reason.replace(' ', '_')
        if module.itemTypeName == ITEM_TYPE_NAMES[4] and reason == 'not_for_current_vehicle':
            return (installPosible, '#menu:moduleFits/need_tuuret', '#tooltips:moduleFits/need_tuuret/body')
        if module.itemTypeName == ITEM_TYPE_NAMES[2] and reason == 'too_heavy':
            return (installPosible, '#menu:moduleFits/too_heavy_chassi', '#tooltips:moduleFits/too_heavy_chassi/body')
        return (installPosible, '#menu:moduleFits/' + reason, '#tooltips:moduleFits/' + reason + '/body')
    return (True, '', '')


def findConflictedEquipments(itemCompactDescr, itemTypeName, vehicle):
    conflictEqs = []
    if itemTypeName != ITEM_TYPE_INDICES['vehicleEngine']:
        return conflictEqs
    oldModule = vehicle.descriptor.installComponent(itemCompactDescr)
    for equipmentDescr in vehicle.equipments:
        if equipmentDescr:
            equipment = getDictDescr(equipmentDescr)
            installPossible, reason = equipment.checkCompatibilityWithVehicle(vehicle.descriptor)
            if not installPossible:
                conflictEqs.append(equipment)

    vehicle.descriptor.installComponent(oldModule)
    return conflictEqs


def findConflictedEquipmentForModule(module, vehicle):
    return findConflictedEquipments(module.compactDescr, module.itemTypeName, vehicle)


def getArenaSubTypeID(arenaTypeID):
    return arenaTypeID >> 16


def getArenaSubTypeName(arenaTypeID):
    return ArenaType._GAMEPLAY_TYPE_TO_NAME[getArenaSubTypeID(arenaTypeID)]


def getBattleSubTypeWinText(arenaTypeID):
    return '#arenas:type/%s/description' % getArenaSubTypeName(arenaTypeID)


def getBattleSubTypeBaseNumder(arenaTypeID, team, baseID):
    arenaSubTypeId = getArenaSubTypeID(arenaTypeID)
    teamBasePositions = ArenaType.g_cache.get(arenaTypeID).gameplayTypes.get(arenaSubTypeId, {}).get('teamBasePositions', tuple())
    if len(teamBasePositions) >= team:
        points = teamBasePositions[team - 1]
        if len(points) > 1:
            return ' %d' % (sorted(points.keys()).index(baseID) + 1)


def isPontrolPointExists(arenaTypeID):
    arenaSubTypeId = getArenaSubTypeID(arenaTypeID)
    controlPoint = ArenaType.g_cache.get(arenaTypeID).gameplayTypes.get(arenaSubTypeId, {}).get('controlPoint', tuple())
    if controlPoint:
        return True
    return False
