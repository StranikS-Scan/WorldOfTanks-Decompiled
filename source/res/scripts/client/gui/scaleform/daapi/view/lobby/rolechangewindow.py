# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/RoleChangeWindow.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.ingame_shop import showBuyGoldForCrew
from gui.shared.money import Money
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import packActionTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.meta.RoleChangeMeta import RoleChangeMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items import Tankman
from gui.shared.gui_items.serializers import packTankman
from gui.shared.gui_items.processors.tankman import TankmanChangeRole
from gui.shared.money import Currency
from gui.shared.utils import decorators, isVehicleObserver
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.formatters import icons, text_styles
from items import tankmen
from nations import NAMES
from skeletons.gui.shared import IItemsCache

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


def _isRoleAvailableToChange(tankman, role):
    td = tankman.descriptor
    if td.role == role:
        return False
    return False if not tankmen.tankmenGroupHasRole(td.nationID, td.gid, td.isPremium, role) else True


def _getTooltip(tankman, role):
    td = tankman.descriptor
    if not tankmen.tankmenGroupHasRole(td.nationID, td.gid, td.isPremium, role):
        return makeTooltip(TOOLTIPS.ROLECHANGE_ROLECHANGEFORBIDDEN_HEADER, _ms(TOOLTIPS.ROLECHANGE_ROLECHANGEFORBIDDEN_BODY, role=_ms(TOOLTIPS.roleForSkill(role))))
    return makeTooltip(TOOLTIPS.ROLECHANGE_CURRENTROLEWARNING_HEADER, TOOLTIPS.ROLECHANGE_CURRENTROLEWARNING_BODY) if td.role == role else ''


def _isRoleSlotTaken(tmen, vehicle, role):
    roledTankmenInVehicle = []
    rolesCount = 0
    for idx, tankman in vehicle.crew:
        if vehicle.descriptor.type.crewRoles[idx][0] == role:
            rolesCount += 1
            if tankman:
                roledTankmenInVehicle.append(tankman)

    hasFreeSlot = len(roledTankmenInVehicle) < rolesCount
    for roleTankman in tmen:
        if roleTankman.vehicleDescr and roleTankman.vehicleDescr.type.compactDescr == vehicle.intCD:
            return not hasFreeSlot

    return False


def _getTooltipHeader(tankmenCountWithSameRole, isAvailable):
    return _ms(TOOLTIPS.ROLECHANGE_ROLEANDVEHICLETAKEN_HEADER) if tankmenCountWithSameRole > 0 and isAvailable else ''


def _getTooltipBody(sameTankmen, isAvailable, roleSlotIsTaken, role, selectedVehicle):
    bodyStr = ''
    if sameTankmen > 0 and isAvailable:
        if roleSlotIsTaken:
            bodyStr = _ms(TOOLTIPS.ROLECHANGE_ROLEANDVEHICLETAKEN_BODY, count=sameTankmen, role=role, vehicleName=selectedVehicle.shortUserName)
        else:
            bodyStr = _ms(TOOLTIPS.ROLECHANGE_ROLETAKEN_BODY, count=sameTankmen)
    return bodyStr


class RoleChangeWindow(RoleChangeMeta):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(RoleChangeWindow, self).__init__()
        self.__tankman = self.itemsCache.items.getTankman(ctx.get('tankmanID', None))
        self.__nativeVehicleCD = self.__tankman.vehicleNativeDescr.type.compactDescr
        self.__selectedVehicleCD = self.__nativeVehicleCD
        self.__currentVehicleCD = None
        if self.__tankman.vehicleDescr is not None:
            self.__currentVehicleCD = self.__tankman.vehicleDescr.type.compactDescr
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self._onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({'stats.unlock': self._onStatsUpdate,
         'stats.inventory': self._onStatsUpdate})
        self.__checkMoney()
        return

    def onVehicleSelected(self, vehTypeCompDescr):
        self.__selectedVehicleCD = int(vehTypeCompDescr)
        selectedVehicle = self.itemsCache.items.getItemByCD(self.__selectedVehicleCD)
        data = []
        mainRoles = []
        for slotIdx, _ in selectedVehicle.crew:
            mainRole = selectedVehicle.descriptor.type.crewRoles[slotIdx][0]
            if mainRole not in mainRoles:
                mainRoles.append(mainRole)
                criteria = REQ_CRITERIA.TANKMAN.NATIVE_TANKS([self.__selectedVehicleCD]) | REQ_CRITERIA.TANKMAN.ROLES([mainRole]) | REQ_CRITERIA.TANKMAN.ACTIVE
                roleTankmen = self.itemsCache.items.getTankmen(criteria).values()
                sameTankmen = len(roleTankmen)
                roleSlotIsTaken = _isRoleSlotTaken(roleTankmen, selectedVehicle, mainRole)
                roleStr = Tankman.getRoleUserName(mainRole)
                isAvailable = _isRoleAvailableToChange(self.__tankman, mainRole)
                data.append({'id': mainRole,
                 'name': roleStr,
                 'icon': Tankman.getRoleMediumIconPath(mainRole),
                 'available': isAvailable,
                 'tooltip': _getTooltip(self.__tankman, mainRole),
                 'warningHeader': _getTooltipHeader(sameTankmen, isAvailable),
                 'warningBody': _getTooltipBody(sameTankmen, isAvailable, roleSlotIsTaken, roleStr, selectedVehicle)})

        self.as_setRolesS(data)

    @decorators.process('changingRole')
    def changeRole(self, role, vehicleId):
        changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        actualGold = self.itemsCache.items.stats.gold
        if changeRoleCost > actualGold and isIngameShopEnabled():
            showBuyGoldForCrew(changeRoleCost)
            return
        result = yield TankmanChangeRole(self.__tankman, role, int(vehicleId)).request()
        if result.userMsg:
            SystemMessages.pushMessage(result.userMsg, type=result.sysMsgType)
        if result.auxData:
            SystemMessages.pushMessage(result.auxData.userMsg, type=result.auxData.sysMsgType)
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
        changeRoleCost = self.itemsCache.items.shop.changeRoleCost
        defaultChangeRoleCost = self.itemsCache.items.shop.defaults.changeRoleCost
        if changeRoleCost != defaultChangeRoleCost:
            discount = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'changeRoleCost', True, Money(gold=changeRoleCost), Money(gold=defaultChangeRoleCost))
        else:
            discount = None
        formattedPrice = BigWorld.wg_getIntegralFormat(changeRoleCost)
        actualGold = self.itemsCache.items.stats.gold
        enoughGold = actualGold - changeRoleCost >= 0
        if enoughGold:
            priceString = text_styles.gold(formattedPrice)
        else:
            priceString = text_styles.error(formattedPrice)
        priceString += icons.gold()
        changeRoleBtnEnabled = enoughGold or isIngameShopEnabled()
        self.as_setPriceS(priceString, changeRoleBtnEnabled, discount)
        return

    def __setCommonData(self):
        self.as_setCommonDataS({'tankmanModel': _getTankmanVO(self.__tankman),
         'role': self.__tankman.descriptor.role,
         'vehicles': self.__getVehiclesData(self.__tankman.nationID, self.__nativeVehicleCD)})

    def __getVehiclesData(self, nationID, nativeVehicleCD):
        items = []
        criteria = REQ_CRITERIA.NATIONS([nationID]) | REQ_CRITERIA.UNLOCKED
        vehicles = self.itemsCache.items.getVehicles(criteria)
        vehiclesData = vehicles.values()
        if nativeVehicleCD not in vehicles:
            vehiclesData.append(self.itemsCache.items.getItemByCD(nativeVehicleCD))
        for vehicle in sorted(vehiclesData):
            vDescr = vehicle.descriptor
            if isVehicleObserver(vDescr.type.compactDescr):
                continue
            items.append({'id': vehicle.intCD,
             'type': vehicle.type,
             'name': vehicle.shortUserName})

        return {'items': items,
         'nativeVehicleId': nativeVehicleCD,
         'currentVehicleId': self.__currentVehicleCD or -1}
