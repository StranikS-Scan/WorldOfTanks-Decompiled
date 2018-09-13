# Embedded file name: scripts/client/gui/shared/utils/functions.py
import random
import re
import ArenaType
from adisp import async, process
from constants import CLAN_MEMBER_FLAGS
from helpers import i18n
from helpers.i18n import makeString
from gui.shared.utils.gui_items import ShopItem, VehicleItem
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES, tankmen, vehicles
from debug_utils import LOG_DEBUG

def getTankmanRoleLevel(startRoleLevel, freeXpValue = 0, vehTypeName = 'ussr:T-34'):
    vehType = vehicles.VehicleDescr(typeName=vehTypeName).type
    tmanDescr = tankmen.TankmanDescr(tankmen.generateCompactDescr(tankmen.generatePassport(vehType.id[0], False), vehType.id[1], vehType.crewRoles[0][0], startRoleLevel))
    tmanDescr.addXP(freeXpValue)
    return tmanDescr.roleLevel


def rnd_choice(*args):
    args = list(args)
    for i in xrange(len(args)):
        c = random.choice(args)
        yield c
        args.remove(c)


def clamp(value, minRange, maxRange):
    if value < minRange:
        return minRange
    if value > maxRange:
        return maxRange
    return value


def roundToMinOrZero(value, minValue):
    if value == 0:
        return value
    else:
        return max(minValue, value)


def getShortDescr(descr):
    """
    Retrieves first occurrence of short description from string.
    Short description can de added to string using <shortDesc></shortDesc> tags
    """
    res_str = ''
    res = re.findall('<shortDesc>(.*?)</shortDesc>', descr)
    if len(res) > 0:
        res_str = res[0]
    else:
        res_str = descr
    return res_str


def stripShortDescrTags(descr):
    """
    Strips short description tags from passed string
    """
    return re.sub('<shortDesc>|</shortDesc>', '', descr)


def stripShortDescr(descr):
    """
    Removes short description from passed string
    """
    return re.sub('<shortDesc>(.*?)</shortDesc>', '', descr)


def makeTooltip(header = None, body = None, note = None):
    """
    Make complex tooltip from carrying params.
    This special formatted string will be parsed from Flash
    net.wargaming.managers.ToolTip.showComplex(str, props)
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
@process
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
    from CurrentVehicle import g_currentVehicle
    if g_currentVehicle.isReadyToFight():
        vehicle = g_currentVehicle.item
        if not g_currentVehicle.isAutoLoadFull() or not g_currentVehicle.isAutoEquipFull():
            from gui import SystemMessages
            from gui.shared.gui_items.processors.vehicle import VehicleLayoutProcessor
            shellsLayout = []
            eqsLayout = []
            for shell in vehicle.shells:
                shellsLayout.extend(shell.defaultLayoutValue)

            for eq in vehicle.eqsLayout:
                if eq is not None:
                    eqsLayout.extend(eq.defaultLayoutValue)
                else:
                    eqsLayout.extend((0, 0))

            LOG_DEBUG('setVehicleLayouts', shellsLayout, eqsLayout)
            result = yield VehicleLayoutProcessor(vehicle, shellsLayout, eqsLayout).request()
            if result and result.auxData:
                for m in result.auxData:
                    SystemMessages.g_instance.pushI18nMessage(m.userMsg, type=m.sysMsgType)

            if result and len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        showAmmoWarning = not g_currentVehicle.item.isAmmoFull
    if showAmmoWarning:
        from gui import DialogsInterface
        success = yield DialogsInterface.showI18nConfirmDialog('lowAmmo')
        callback(success)
    else:
        yield lambda callback: callback(None)
        callback(True)
    return


def isModuleFitVehicle(module, vehicle, price, money, unlocks, positionIndex = 0, isRemove = False):
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
    reason = ''
    installPosible = True
    prefix = 'deviceFits/' if module.itemTypeName == ITEM_TYPE_NAMES[9] else 'moduleFits/'
    if isinstance(module, ShopItem) or isRemove:
        if module.itemTypeName not in (ITEM_TYPE_NAMES[9], ITEM_TYPE_NAMES[11]) and module.compactDescr not in unlocks:
            return (False, '#menu:moduleFits/unlock_error', '#tooltips:moduleFits/unlock_error')
        couldBeBought, menu, tooltip = getModuleGoldStatus(price, money)
        if not couldBeBought:
            return (couldBeBought, menu, tooltip)
    if vehicle is None:
        if isinstance(module, VehicleItem):
            tooltip = '#tooltips:deviceFits/already_installed' if module.itemTypeName == ITEM_TYPE_NAMES[9] else '#tooltips:moduleFits/already_installed'
            return (True, '', tooltip)
        return (True, '', '')
    else:
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
                return (installPosible, '#menu:moduleFits/need_turret', '#tooltips:moduleFits/need_turret')
            if module.itemTypeName == ITEM_TYPE_NAMES[2] and reason == 'too_heavy':
                return (installPosible, '#menu:moduleFits/too_heavy_chassi', '#tooltips:moduleFits/too_heavy_chassi')
            return (installPosible, '#menu:moduleFits/' + reason, '#tooltips:' + prefix + reason)
        return (True, '', '')


def getModuleGoldStatus(price, money):
    """
    @param price: module price
    @param money: player's money
    @return: tuple(CouldBeBought, menuStatus, tooltipStatus)
    """
    currency = 'gold'
    availableForCredits = 1
    availableForGold = 2
    couldBeBought = 0
    if price[0] and price[0] > money[0]:
        currency = 'credit'
    else:
        couldBeBought |= availableForCredits
    if price[1] and price[1] < money[1]:
        couldBeBought |= availableForGold
    if not couldBeBought:
        return (False, '#menu:moduleFits/%s_error' % currency, '#tooltips:moduleFits/%s_error' % currency)
    return (True, '', '')


def findConflictedEquipments(itemCompactDescr, itemTypeID, vehicle):
    conflictEqs = []
    if itemTypeID != ITEM_TYPE_INDICES['vehicleEngine']:
        return conflictEqs
    oldModule, = vehicle.descriptor.installComponent(itemCompactDescr)
    for equipmentDescr in vehicle.equipments:
        if equipmentDescr:
            equipment = vehicles.getDictDescr(equipmentDescr)
            installPossible, reason = equipment.checkCompatibilityWithVehicle(vehicle.descriptor)
            if not installPossible:
                conflictEqs.append(equipment)

    vehicle.descriptor.installComponent(oldModule)
    return conflictEqs


def findConflictedEquipmentForModule(module, vehicle):
    return findConflictedEquipments(module.compactDescr, ITEM_TYPE_INDICES[module.itemTypeName], vehicle)


def getArenaSubTypeID(arenaTypeID):
    return arenaTypeID >> 16


def getArenaSubTypeName(arenaTypeID):
    return ArenaType.g_cache[arenaTypeID].gameplayName


def getArenaShortName(arenaTypeID):
    return ArenaType.g_cache[arenaTypeID].name


def getArenaFullName(arenaTypeID):
    arenaType = ArenaType.g_cache[arenaTypeID]
    arenaName = arenaType.name
    if arenaType.gameplayName != 'ctf':
        arenaName = '%s - %s' % (arenaName, makeString('#arenas:type/%s/name' % arenaType.gameplayName))
    return arenaName


def getBattleSubTypeWinText(arenaTypeID, teamID):
    key = 'type/%s/description' % ArenaType.g_cache[arenaTypeID].gameplayName
    winText = i18n.makeString('#arenas:%s' % key)
    if winText == key:
        return i18n.makeString('#arenas:%s%d' % (key, teamID))
    return winText


def getBattleSubTypeBaseNumder(arenaTypeID, team, baseID):
    teamBasePositions = ArenaType.g_cache[arenaTypeID].teamBasePositions
    if len(teamBasePositions) >= team:
        points = teamBasePositions[team - 1]
        if len(points) > 1:
            return ' %d' % (sorted(points.keys()).index(baseID) + 1)
    points = ArenaType.g_cache[arenaTypeID].controlPoints
    if points:
        if len(points) > 1:
            return ' %d' % baseID
    return ''


def isBaseExists(arenaTypeID, team):
    teamBasePositions = ArenaType.g_cache[arenaTypeID].teamBasePositions
    if len(teamBasePositions) >= team:
        points = teamBasePositions[team - 1]
        if len(points) > 0:
            return True
    return False


def isControlPointExists(arenaTypeID):
    controlPoint = ArenaType.g_cache[arenaTypeID].controlPoints
    if controlPoint:
        return True
    return False


def getAbsoluteUrl(url):
    return url.replace('../', 'img://gui/')


def showInformationDialog(infDialog, callback, customMessage = '', ns = 'common'):
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
        g_windowsManager.battleWindow.removeExternalCallbacks('informationDialog.onClose')
        callback()

    g_windowsManager.battleWindow.addExternalCallbacks({'informationDialog.onClose': onInformationDialogClosed})
    g_windowsManager.battleWindow.call('{0:>s}.showInformationDialog'.format(ns), [infDialog, customMessage, 'informationDialog.onClose'])


def showConfirmDialog(confirmDialog, callback, customMessage = '', ns = 'common'):
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
        g_windowsManager.battleWindow.removeExternalCallbacks('confirmDialog.onConfirm', 'confirmDialog.onClose')
        callback(confirm)

    g_windowsManager.battleWindow.addExternalCallbacks({'confirmDialog.onConfirm': lambda callBackId: onConfirmResponse(True),
     'confirmDialog.onClose': lambda callBackId: onConfirmResponse(False)})
    g_windowsManager.battleWindow.call('{0:>s}.showConfirmDialog'.format(ns), [confirmDialog,
     customMessage,
     'confirmDialog.onConfirm',
     'confirmDialog.onClose'])


CLAN_MEMBERS = {CLAN_MEMBER_FLAGS.LEADER: 'leader',
 CLAN_MEMBER_FLAGS.VICE_LEADER: 'vice_leader',
 CLAN_MEMBER_FLAGS.RECRUITER: 'recruiter',
 CLAN_MEMBER_FLAGS.TREASURER: 'treasurer',
 CLAN_MEMBER_FLAGS.DIPLOMAT: 'diplomat',
 CLAN_MEMBER_FLAGS.COMMANDER: 'commander',
 CLAN_MEMBER_FLAGS.PRIVATE: 'private',
 CLAN_MEMBER_FLAGS.RECRUIT: 'recruit',
 CLAN_MEMBER_FLAGS.STAFF: 'staff',
 CLAN_MEMBER_FLAGS.JUNIOR: 'junior',
 CLAN_MEMBER_FLAGS.RESERVIST: 'reservist'}

def getClanRoleString(position = CLAN_MEMBER_FLAGS.LEADER):
    if position in CLAN_MEMBERS:
        return i18n.makeString('#menu:profile/header/clan/position/%s' % CLAN_MEMBERS[position])
    return ''
