# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/RoleChangeWindow.py
import BigWorld
from helpers.i18n import makeString
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RoleChangeMeta import RoleChangeMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.serializers import packTankman
from gui.shared.gui_items.processors.tankman import TankmanChangeRole
from gui.shared.ItemsCache import g_itemsCache
from gui.shared.utils import decorators, isVehicleObserver
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.formatters import icons, text_styles
from nations import NAMES

def _getTankmanVO(tankman):
    packedTankman = packTankman(tankman, isCountPermanentSkills=False)
    fullName = '%s %s' % (packedTankman['firstUserName'], packedTankman['lastUserName'])
    return {'name': fullName,
     'nation': NAMES[tankman.nationID],
     'rank': packedTankman['rankUserName'],
     'vehicle': packedTankman['nativeVehicle']['userName'],
     'faceIcon': packedTankman['icon']['big'],
     'rankIcon': packedTankman['iconRank']['big'],
     'roleIcon': packedTankman['iconRole']['medium']}


def _isRoleSlotTaken(tankmen, vehicle, role):
    roledTankmenInVehicle = []
    rolesCount = 0
    for idx, tankman in vehicle.crew:
        if vehicle.descriptor.type.crewRoles[idx][0] == role:
            rolesCount += 1
            if tankman:
                roledTankmenInVehicle.append(tankman)

    hasFreeSlot = len(roledTankmenInVehicle) < rolesCount
    for roleTankman in tankmen:
        if roleTankman.vehicleDescr and roleTankman.vehicleDescr.type.compactDescr == vehicle.intCD:
            return not hasFreeSlot

    return False


def _getTooltipHeader(tankmenCountWithSameRole, isAvailable):
    if tankmenCountWithSameRole > 0 and isAvailable:
        return makeString(TOOLTIPS.ROLECHANGE_ROLEANDVEHICLETAKEN_HEADER)
    return ''


def _getTooltipBody(sameTankmen, isAvailable, roleSlotIsTaken, role, selectedVehicle):
    bodyStr = ''
    if sameTankmen > 0 and isAvailable:
        if roleSlotIsTaken:
            bodyStr = makeString(TOOLTIPS.ROLECHANGE_ROLEANDVEHICLETAKEN_BODY, count=sameTankmen, role=role, vehicleName=selectedVehicle.shortUserName)
        else:
            bodyStr = makeString(TOOLTIPS.ROLECHANGE_ROLETAKEN_BODY, count=sameTankmen)
    return bodyStr


class RoleChangeWindow(RoleChangeMeta):

    def __init__(self, ctx = None):
        super(RoleChangeWindow, self).__init__()
        self.__items = g_itemsCache.items
        self.__tankman = self.__items.getTankman(ctx.get('tankmanID', None))
        self.__nativeVehicleCD = self.__tankman.vehicleNativeDescr.type.compactDescr
        self.__selectedVehicleCD = self.__nativeVehicleCD
        self.__currentVehicleCD = None
        if self.__tankman.vehicleDescr is not None:
            self.__currentVehicleCD = self.__tankman.vehicleDescr.type.compactDescr
        g_clientUpdateManager.addCallbacks({'stats.gold': self._onMoneyUpdate,
         'stats.unlock': self._onStatsUpdate,
         'stats.inventory': self._onStatsUpdate})
        return

    def onVehicleSelected(self, vehTypeCompDescr):
        self.__selectedVehicleCD = int(vehTypeCompDescr)
        selectedVehicle = self.__items.getItemByCD(self.__selectedVehicleCD)
        data = []
        mainRoles = []
        for slotIdx, tman in selectedVehicle.crew:
            mainRole = selectedVehicle.descriptor.type.crewRoles[slotIdx][0]
            if mainRole not in mainRoles:
                mainRoles.append(mainRole)
                criteria = REQ_CRITERIA.TANKMAN.NATIVE_TANKS([self.__selectedVehicleCD]) | REQ_CRITERIA.TANKMAN.ROLES([mainRole])
                roleTankmen = self.__items.getTankmen(criteria).values()
                sameTankmen = len(roleTankmen)
                roleSlotIsTaken = _isRoleSlotTaken(roleTankmen, selectedVehicle, mainRole)
                roleStr = Tankman.getRoleUserName(mainRole)
                isAvailable = self.__tankman.descriptor.role != mainRole
                data.append({'id': mainRole,
                 'name': roleStr,
                 'icon': Tankman.getRoleMediumIconPath(mainRole),
                 'available': isAvailable,
                 'warningHeader': _getTooltipHeader(sameTankmen, isAvailable),
                 'warningBody': _getTooltipBody(sameTankmen, isAvailable, roleSlotIsTaken, roleStr, selectedVehicle)})

        self.as_setRolesS(data)

    @decorators.process('changingRole')
    def changeRole(self, role, vehicleId):
        result = yield TankmanChangeRole(self.__tankman, role, int(vehicleId)).request()
        if len(result.userMsg):
            SystemMessages.g_instance.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.auxData:
            SystemMessages.g_instance.pushMessage(result.auxData.userMsg, type=result.auxData.sysMsgType)
        if result.success:
            self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(RoleChangeWindow, self)._populate()
        self.__setCommonData()
        self.onVehicleSelected(self.__nativeVehicleCD)
        self.__checkMoney()

    def _dispose(self):
        self.__items = None
        self.__tankman = None
        self.__selectedVehicleCD = None
        self.__currentVehicleCD = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(RoleChangeWindow, self)._dispose()
        return

    def _onMoneyUpdate(self, *args):
        self.__checkMoney()

    def _onStatsUpdate(self, *args):
        self.__setCommonData()

    def __checkMoney(self):
        changeRoleCost = self.__items.shop.changeRoleCost
        formattedPrice = BigWorld.wg_getIntegralFormat(changeRoleCost)
        actualGold = self.__items.stats.gold
        enoughGold = actualGold - changeRoleCost >= 0
        if enoughGold:
            priceString = text_styles.gold(formattedPrice)
        else:
            priceString = text_styles.error(formattedPrice)
        priceString += icons.gold()
        self.as_setPriceS(priceString, enoughGold)

    def __setCommonData(self):
        self.as_setCommonDataS({'tankmanModel': _getTankmanVO(self.__tankman),
         'role': self.__tankman.descriptor.role,
         'vehicles': self.__getVehiclesData(self.__tankman.nationID, self.__nativeVehicleCD)})

    def __getVehiclesData(self, nationID, nativeVehicleCD):
        items = []
        criteria = REQ_CRITERIA.NATIONS([nationID]) | REQ_CRITERIA.UNLOCKED
        vehicles = self.__items.getVehicles(criteria)
        vehiclesData = vehicles.values()
        if nativeVehicleCD not in vehicles:
            vehiclesData.append(self.__items.getItemByCD(nativeVehicleCD))
        for vehicle in sorted(vehiclesData):
            vDescr = vehicle.descriptor
            if isVehicleObserver(vDescr.type.compactDescr):
                continue
            items.append({'id': vehicle.intCD,
             'type': vehicle.type,
             'name': vehicle.shortUserName})

        return {'items': items,
         'nativeVehicleId': nativeVehicleCD,
         'currentVehicleId': self.__currentVehicleCD if self.__currentVehicleCD != None else -1}
