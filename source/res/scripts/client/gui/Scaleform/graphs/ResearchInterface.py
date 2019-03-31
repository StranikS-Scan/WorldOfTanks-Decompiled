# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/graphs/ResearchInterface.py
# Compiled at: 2011-12-14 18:35:18
from AccountCommands import RES_SUCCESS
from adisp import process
import BigWorld
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR, LOG_DEBUG
from items import ITEM_TYPE_NAMES, ITEM_TYPE_INDICES, getTypeInfoByName, vehicles
from helpers import i18n
from gui import SystemMessages
from gui.Scaleform.CommandArgsParser import CommandArgsParser
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.graphs import custom_items, _VEHICLE_TYPE_NAME, _VEHICLE_TYPE_IDX, CLIENT_DATA_DIFF_STAT_IDX, CLIENT_DATA_DIFF_INVENTORY_IDX, CLIENT_DATA_DIFF_CACHE_IDX, CACHE_VEHS_LOCK_IDX, INVENTORY_ITEM_VCDESC_IDX, AFTER_UNLOCK_AUTO_PURCHASE_ALLOWED
from gui.Scaleform.graphs.data import VehicleComponentsGraph
from gui.Scaleform.graphs.dumpers import VehicleComponentsGraphXMLDumper
from gui.Scaleform.graphs.MessagesInterface import MessagesInterface
from gui.Scaleform.utils import gui_items, functions
from gui.Scaleform.utils.requesters import StatsRequester
from functools import partial
from PlayerEvents import g_playerEvents

class ResearchInterface(UIInterface, MessagesInterface):
    __isRequestUnlock = False
    __isRequestEquip = False

    def __init__(self):
        super(ResearchInterface, self).__init__()
        self.__vehicleType = None
        self.__vTypeCompactDesc = None
        self.__experiences = (0, 0)
        self.graph = VehicleComponentsGraph()
        self.graph.setDumper(VehicleComponentsGraphXMLDumper())
        self.__unlocks = set()
        return

    def __del__(self):
        LOG_DEBUG('ResearchInterface deleted')

    def setVehicleType(self, vehicleType):
        self.__vehicleType = vehicleType
        self.__vTypeCompactDesc = vehicleType.compactDescr

    @property
    def vehicleType(self):
        return self.__vehicleType

    @property
    def vTypeCompactDesc(self):
        return self.__vTypeCompactDesc

    def updateExperience(self):
        if self.__vehicleType is None:
            return
        else:
            self.__getExperiences()
            return

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.uiHolder.addExternalCallbacks({'VehicleComponents.PopulateCurrentVehicle': self.onPopulateCurrentVehicle,
         'VehicleComponents.PopulateVehicle': self.onPopulateVehicle,
         'VehicleComponents.RequestExperience': self.onRequestExperience,
         'VehicleComponents.RequestInventoryData': self.onRequestInventoryData,
         'VehicleComponents.RequestData': self.onRequestData,
         'VehicleComponents.RequestForUnlock': self.onUnlock,
         'VehicleComponents.ConfirmUnlock': self.onConfirmUnlock,
         'VehicleComponents.RequestForEquip': self.onModuleEquip,
         'VehicleComponents.RequestForBuyAndEquip': self.onModuleBuyAndEquip,
         'VehicleComponents.ConfirmBuyAndEquip': self.onConfirmModuleBuyAndEquip,
         'VehicleComponents.RequestForVehicleBuy': self.onVehicleBuy,
         'LevelingTreeOfVehicles.GoToNation': self.onGoToNationTree,
         'LevelingTreeOfVehicles.GoToNextVehicle': self.onGoToNextVehicle})
        self.uiHolder.onXPConverted += self.updateExperience
        g_playerEvents.onClientUpdated += self.__pe_onClientUpdated

    def dispossessUI(self):
        self.uiHolder.removeExternalCallbacks('VehicleComponents.PopulateCurrentVehicle', 'VehicleComponents.PopulateVehicle', 'VehicleComponents.RequestExperience', 'VehicleComponents.RequestInventoryData', 'VehicleComponents.RequestData', 'VehicleComponents.RequestForUnlock', 'VehicleComponents.ConfirmUnlock', 'VehicleComponents.RequestForEquip', 'VehicleComponents.RequestForBuyAndEquip', 'VehicleComponents.ConfirmBuyAndEquip', 'VehicleComponents.RequestForVehicleBuy', 'LevelingTreeOfVehicles.GoToNation', 'LevelingTreeOfVehicles.GoToNextVehicle')
        self.uiHolder.onXPConverted -= self.updateExperience
        g_playerEvents.onClientUpdated -= self.__pe_onClientUpdated
        UIInterface.dispossessUI(self)

    def __refreshView(self):
        if self.__vehicleType is not None:
            self.call('VehicleComponents.RefreshData')
        return

    def __refreshInventoryData(self):
        if self.__vehicleType is not None:
            self.call('VehicleComponents.RefreshInventoryData')
        return

    def __pe_onClientUpdated(self, diff):
        if not self.__isRequestUnlock:
            if CLIENT_DATA_DIFF_STAT_IDX in diff:
                self.__refreshView()
                return
        if CLIENT_DATA_DIFF_INVENTORY_IDX in diff:
            self.__refreshInventoryData()
        if CLIENT_DATA_DIFF_CACHE_IDX in diff:
            invVehItem = self.graph.getInvItem(self.__vTypeCompactDesc)
            vehsLock = diff[CLIENT_DATA_DIFF_CACHE_IDX].get(CACHE_VEHS_LOCK_IDX, {})
            if invVehItem is not None and invVehItem.inventoryId in vehsLock:
                invVehItem.lock = vehsLock[invVehItem.inventoryId]
                self.__refreshRootNode(invVehItem=invVehItem)
        return

    def __refreshRootNode(self, invVehItem=None):
        if invVehItem is None:
            invVehItem = self.graph.getInvItem(self.__vTypeCompactDesc)
        installArgs = []
        rootVehArgs = [None, False]
        if invVehItem is not None:
            installArgs = invVehItem.descriptor.getDevices()[1]
            installArgs.insert(0, not invVehItem.repairCost and not invVehItem.lock)
            rootVehArgs = [invVehItem.pack(), invVehItem.isXPToTman]
        self.call('VehicleComponents.SetInstalledComponents', installArgs)
        self.call('VehicleComponents.SetRootVehicle', rootVehArgs)
        return

    def onPopulateCurrentVehicle(self, *args):
        if not g_currentVehicle.isPresent():
            return
        parser = CommandArgsParser(self.onPopulateCurrentVehicle.__name__)
        parser.parse(*args)
        self.setVehicleType(g_currentVehicle.vehicle.descriptor.type)
        parser.addArg(i18n.makeString('#menu:vehicleComponents/title', gui_items.getVehicleTypeFullName(self.__vehicleType)))
        self.uiHolder.respond(parser.args())

    def onPopulateVehicle(self, *args):
        parser = CommandArgsParser(self.onPopulateVehicle.__name__, 1, [int])
        compactDescr = parser.parse(*args)
        self.__vTypeCompactDesc = compactDescr
        _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(compactDescr)
        self.__vehicleType = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
        parser.addArg(i18n.makeString('#menu:vehicleComponents/title', gui_items.getVehicleTypeFullName(self.__vehicleType)))
        self.uiHolder.respond(parser.args())

    def onRequestData(self, *args):
        parser = CommandArgsParser(self.onRequestData.__name__)
        parser.parse(*args)
        parser.addArg(self.graph.dump())
        parser.addArg(i18n.makeString('#menu:vehicleComponents/title', gui_items.getVehicleTypeFullName(self.__vehicleType)))
        self.uiHolder.respond(parser.args())

    def onUnlock(self, *args):
        parser = CommandArgsParser(self.onUnlock.__name__, 9, [int,
         int,
         int,
         int,
         str,
         str,
         str,
         int,
         int])
        vCompactDescr, unlockIdx, usedXP, uCompactDescr, uType, uTypeString, uNameString, row, column = parser.parse(*args)
        message = i18n.makeString('#dialogs:vehicleComponents/confirmUnlock/message', uTypeString, uNameString, BigWorld.wg_getIntegralFormat(usedXP))
        self.call('common.showMessageDialog', ['vehicleComponents/confirmUnlock',
         True,
         True,
         message,
         'VehicleComponents.ConfirmUnlock',
         vCompactDescr,
         unlockIdx,
         usedXP,
         uCompactDescr,
         uType,
         uTypeString,
         uNameString,
         row,
         column])

    def onConfirmUnlock(self, *args):
        parser = CommandArgsParser(self.onConfirmUnlock.__name__, 9, [int,
         int,
         int,
         int,
         str,
         str,
         str,
         int,
         int])
        vCompactDescr, unlockIdx, usedXP, uCompactDescr, uType, uTypeString, uNameString, row, column = parser.parse(*args)
        if uCompactDescr in self.__unlocks:
            if uType == _VEHICLE_TYPE_NAME:
                SystemMessages.pushI18nMessage('#system_messages:vehicleComponents/vehicle_is_already_unlocked', type=SystemMessages.SM_TYPE.Error, userString=uNameString)
            else:
                SystemMessages.pushI18nMessage('#system_messages:vehicleComponents/module_is_already_unlocked', type=SystemMessages.SM_TYPE.Error, typeString=uTypeString, userString=uNameString)
            self.call('VehicleComponents.HideWaitingMessage', [])
            return
        if self.__isRequestUnlock:
            SystemMessages.pushI18nMessage('#system_messages:vehicleComponents/unlock_in_processing', type=SystemMessages.SM_TYPE.Warning)
            return
        if usedXP <= sum(self.__experiences):
            self.__isRequestUnlock = True
            self.call('VehicleComponents.ShowWaitingMessage', ['#menu:vehicleComponents/messages/requestUnlock'])
            BigWorld.player().stats.unlock(vCompactDescr, unlockIdx, callback=partial(self.onUnlockResult, usedXP, uType, uCompactDescr, row, column, BigWorld.time()))
        else:
            self.call('VehicleComponents.UnlockFailed', [i18n.makeString('#menu:vehicleComponents/messages/unlockFailed')])

    def onModuleEquip(self, *args):
        parser = CommandArgsParser(self.onModuleEquip.__name__, 2, [str, int])
        itemTypeName, itemCompDescr = parser.parse(*args)
        invVeh = self.graph.getInvItem(self.__vTypeCompactDesc)
        if invVeh is None:
            self._showMessageForVehicle('vehicle_not_found_in_inventory', None, None, userString=invVeh.name)
            return
        else:
            invItem = self.graph.getInvItem(itemCompDescr)
            if invItem is None:
                self._showMessageForModule('module_not_found_in_inventory', itemTypeName, itemCompDescr)
                return
            conflictedEqs = functions.findConflictedEquipments(itemCompDescr, itemTypeName, invVeh)
            if len(conflictedEqs):
                self.__showRemoveIncompatibleEqsDialog(itemTypeName, itemCompDescr, conflictedEqs)
                return
            self.doEquipModule(itemTypeName, itemCompDescr)
            return

    @process
    def __showRemoveIncompatibleEqsDialog(self, itemTypeName, itemCompDescr, conflictedEqs):
        isConfirmed = yield functions.async_showConfirmDialog('removeIncompatibleEqs', customMessage=i18n.makeString('#dialogs:removeIncompatibleEqs/customMessage', "', '".join([ eq['userString'] for eq in conflictedEqs ])))
        if isConfirmed:
            self.doEquipModule(itemTypeName, itemCompDescr)

    def onModuleBuyAndEquip(self, *args):
        parser = CommandArgsParser(self.onModuleBuyAndEquip.__name__, 2, [str, int])
        itemTypeName, itemCompDescr = parser.parse(*args)
        self.requestItemInShop(itemTypeName, itemCompDescr)

    def onConfirmModuleBuyAndEquip(self, *args):
        self.call('VehicleComponents.ShowWaitingMessage', ['#menu:vehicleComponents/messages/requestEquip'])
        parser = CommandArgsParser(self.onConfirmModuleBuyAndEquip.__name__, 5, [str, int, int])
        itemTypeName, itemCompDescr, nationIdx, credits, gold = parser.parse(*args)
        self.doModuleBuy(itemTypeName, itemCompDescr, nationIdx, credits, gold)

    def onVehicleBuy(self, *args):
        parser = CommandArgsParser(self.onVehicleBuy.__name__, 1, [int])
        itemCompDescr = parser.parse(*args)
        self.requestItemInShop(_VEHICLE_TYPE_NAME, itemCompDescr)

    def onGoToNationTree(self, *args):
        parser = CommandArgsParser(self.onGoToNationTree.__name__, 1, [str])
        nationName = parser.parse(*args)
        if self.uiHolder.currentInterface != 'construction_department':
            from gui.Scaleform.ConstructionDepartment import g_selectedNation
            g_selectedNation.setName(nationName)
            self.uiHolder.movie.invoke(('loadConstructionDepartment',))
        else:
            self.uiHolder.call('LevelingTreeOfVehicles.SetSelectedNation', [nationName])

    def onGoToNextVehicle(self, *args):
        parser = CommandArgsParser(self.onGoToNextVehicle.__name__, 1, [int])
        compactDescr = parser.parse(*args)
        self.__vTypeCompactDesc = compactDescr
        _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(compactDescr)
        self.__vehicleType = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
        self.__refreshView()

    def onRequestExperience(self, _):
        self.__getExperiences()
        BigWorld.player().stats.get('unlocks', self.onGetUnlocks)

    def onRequestInventoryData(self, _):
        BigWorld.player().inventory.getItems(_VEHICLE_TYPE_IDX, partial(self.onGetVehiclesFromInventory, False))

    @process
    def __getExperiences(self):
        experiences = yield StatsRequester().getVehicleTypeExperiences()
        uspentXP = experiences.get(self.__vTypeCompactDesc, 0)
        freeExperience = yield StatsRequester().getFreeExperience()
        eliteVehicles = yield StatsRequester().getEliteVehicles()
        isElite = len(self.__vehicleType.unlocksDescrs) == 0 or self.__vTypeCompactDesc in eliteVehicles
        self.__experiences = (uspentXP, freeExperience)
        self.call('VehicleComponents.ExperienceRecieved', [uspentXP,
         freeExperience,
         0,
         isElite])

    def onGetUnlocks(self, resultID, unlocks):
        if resultID < 0:
            LOG_ERROR('Server return error unlocks request: responseCode=', resultID)
            unlocks = set()
        self.__unlocks = unlocks
        self.graph.load(self.__vehicleType, self.__vTypeCompactDesc, unlocks)
        BigWorld.player().inventory.getItems(_VEHICLE_TYPE_IDX, partial(self.onGetVehiclesFromInventory, True))

    def onGetVehiclesFromInventory(self, requestPrice, resultID, data):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory vehicle items request: responseCode=', resultID)
            data = {INVENTORY_ITEM_VCDESC_IDX: {}}
        vCompactDescrs = data[INVENTORY_ITEM_VCDESC_IDX]
        gCompactDescrs = self.graph.compactDescrByTypeId[_VEHICLE_TYPE_IDX]
        for invID, vCompactDescr in vCompactDescrs.iteritems():
            vType = vehicles.getVehicleType(vCompactDescr)
            intCompactDescr = vehicles.makeIntCompactDescrByID(_VEHICLE_TYPE_NAME, vType.id[0], vType.id[1])
            if intCompactDescr in gCompactDescrs:
                self.graph.setInvItem(intCompactDescr, custom_items._makeInventoryVehicle(invID, vCompactDescr, data))
                if intCompactDescr == self.__vTypeCompactDesc:
                    self.__refreshRootNode()

        itemTypeIDs = filter(lambda itemID: itemID != _VEHICLE_TYPE_IDX, self.graph.compactDescrByTypeId.keys())
        self.__requestNextItemsByTypeFromInventory(itemTypeIDs, requestPrice)

    def __requestNextItemsByTypeFromInventory(self, itemTypeIDs, requestPrice):
        if len(itemTypeIDs) > 0:
            next = itemTypeIDs.pop()
            BigWorld.player().inventory.getItems(next, partial(self.onGetItemsFromInventory, next, itemTypeIDs, requestPrice))
        else:
            self.call('VehicleComponents.SetInventoryComponents', self.graph.getInventoryItemsCDs())
            if requestPrice:
                self.__requestNextItemsByTypeFromShop(self.graph.compactDescrByTypeId.keys())
            else:
                self.call('VehicleComponents.DataInited')

    def onGetItemsFromInventory(self, itemTypeID, itemTypeIDs, requestPrice, resultID, data):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error inventory %s items request: responseCode=' % ITEM_TYPE_NAMES[itemTypeID], resultID)
            data = {}
        gCompactDescrs = self.graph.compactDescrByTypeId[itemTypeID]
        filtered = filter(lambda item: item[0] in gCompactDescrs, data.iteritems())
        for itemCompactDesc, count in filtered:
            self.graph.setInvItem(itemCompactDesc, custom_items._makeInventoryItem(itemTypeID, itemCompactDesc, count))

        self.__requestNextItemsByTypeFromInventory(itemTypeIDs, requestPrice)

    def __requestNextItemsByTypeFromShop(self, itemTypeIDs):
        if len(itemTypeIDs) > 0:
            next = itemTypeIDs.pop()
            BigWorld.player().shop.getItems(next, self.__vehicleType.id[0], partial(self.onGetItemsFromShop, next, itemTypeIDs))
        else:
            self.call('VehicleComponents.DataInited')

    def onGetItemsFromShop(self, itemTypeID, itemTypeIDs, resultID, data, _):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error shop %s items request: responseCode=' % ITEM_TYPE_NAMES[itemTypeID], resultID)
            data = {}
        gCompactDescrs = self.graph.compactDescrByTypeId[itemTypeID]
        prices = data[0].iteritems() if len(data) else []
        if itemTypeID == _VEHICLE_TYPE_IDX:
            nationID = self.__vehicleType.id[0]
            prices = map(lambda item: (vehicles.makeIntCompactDescrByID(ITEM_TYPE_NAMES[itemTypeID], nationID, item[0]), item[1]), prices)
        filtered = filter(lambda item: item[0] in gCompactDescrs, prices)
        for itemCompactDesc, price in filtered:
            self.graph.setShopPrice(itemCompactDesc, price)

        self.__requestNextItemsByTypeFromShop(itemTypeIDs)

    def onUnlockResult(self, usedXP, uType, uCompactDescr, row, column, startTime, resultID):
        LOG_DEBUG('onUnlockResult, time spent = ', BigWorld.time() - startTime)
        if RES_SUCCESS == resultID:
            self.__unlocks.add(uCompactDescr)
            xp = self.__experiences[0] - usedXP
            unspentXP = usedXP
            freeXP = 0
            if xp < 0:
                unspentXP = self.__experiences[0]
                freeXP = usedXP - unspentXP
                self.__experiences = (0, self.__experiences[1] + xp)
            else:
                self.__experiences = (xp, self.__experiences[1])
            unspentXP = BigWorld.wg_getIntegralFormat(unspentXP)
            freeXP = BigWorld.wg_getIntegralFormat(freeXP)
            autounlockedItems = []
            if uType == _VEHICLE_TYPE_NAME:
                _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(uCompactDescr)
                vehicle = vehicles.g_cache.vehicle(nationID, vehicleTypeID)
                autounlockedItems = vehicle.autounlockedItems
                self.__unlocks.update(autounlockedItems)
                self._showMessageForVehicle('vehicle_unlock_success', None, None, args={'unspentXP': unspentXP,
                 'freeXP': freeXP}, userString=vehicle.userString, type=SystemMessages.SM_TYPE.PowerLevel)
            else:
                self._showMessageForModule('module_unlock_success', uType, uCompactDescr, args={'unspentXP': unspentXP,
                 'freeXP': freeXP}, type=SystemMessages.SM_TYPE.PowerLevel)
            self.call('VehicleComponents.UnlockSuccess', [row, column] + autounlockedItems)
            self.__isRequestUnlock = False
            if AFTER_UNLOCK_AUTO_PURCHASE_ALLOWED and (uType == _VEHICLE_TYPE_NAME or self.graph.hasInvItem(self.__vTypeCompactDesc)):
                self.requestItemInShop(uType, uCompactDescr, afterUnlock=True)
        else:
            self.call('VehicleComponents.UnlockFailed', [i18n.makeString('#menu:vehicleComponents/messages/serverUnlockFailed')])
            self.__isRequestUnlock = False
        return

    def requestItemInShop(self, itemTypeName, itemCompDescr, afterUnlock=False):
        if self.graph.hasInvItem(itemCompDescr):
            if not afterUnlock:
                if itemTypeName != _VEHICLE_TYPE_NAME:
                    self._showMessageForModule('module_has_in_inventory', itemTypeName, itemCompDescr, type=SystemMessages.SM_TYPE.Warning)
                    self.doEquipModule(itemTypeName, itemCompDescr)
                else:
                    _, nationID, innationID = vehicles.parseIntCompactDescr(itemCompDescr)
                    self._showMessageForVehicle('vehicle_has_in_inventory', nationID, innationID, type=SystemMessages.SM_TYPE.Warning)
        else:
            _, nationID, innationID = vehicles.parseIntCompactDescr(itemCompDescr)
            if itemTypeName == _VEHICLE_TYPE_NAME:
                message = '#menu:vehicleComponents/messages/shop/requestVehicle'
                callback = partial(self.processBuyVehicle, innationID, nationID, afterUnlock)
            else:
                message = '#menu:vehicleComponents/messages/shop/requestModule'
                callback = partial(self.processBuyModule, itemTypeName, itemCompDescr, nationID, afterUnlock)
            self.call('VehicleComponents.ShowWaitingMessage', [message])
            BigWorld.player().shop.getItems(ITEM_TYPE_INDICES[itemTypeName], nationID, callback)

    def doEquipModule(self, itemTypeName, itemCompDescr):
        assert itemTypeName != _VEHICLE_TYPE_NAME
        isEquipTurret = False
        errorMessageArgs = [getTypeInfoByName(itemTypeName)['userString'], vehicles.getDictDescr(itemCompDescr)['userString']]
        invVehItem = self.graph.getInvItem(self.__vTypeCompactDesc)
        if invVehItem is None:
            self._showMessageForVehicle('vehicle_not_found_in_inventory', None, None, userString=invVehItem.name)
            return
        else:
            vDesc = invVehItem.descriptor
            if itemTypeName == ITEM_TYPE_NAMES[3]:
                mayInstall, errorString = vDesc.mayInstallTurret(itemCompDescr, 0)
                isEquipTurret = True
            else:
                mayInstall, errorString = vDesc.mayInstallComponent(itemCompDescr)
            if mayInstall:
                if self.__isRequestEquip:
                    SystemMessages.pushI18nMessage('#system_messages:vehicleComponents/equip_in_processing', type=SystemMessages.SM_TYPE.Warning)
                    return
                callback = partial(self.onEquipModuleResult, itemTypeName, itemCompDescr)
                self.__isRequestEquip = True
                if isEquipTurret:
                    BigWorld.player().inventory.equipTurret(invVehItem.inventoryId, itemCompDescr, 0, callback)
                else:
                    BigWorld.player().inventory.equip(invVehItem.inventoryId, itemCompDescr, callback)
            else:
                error = errorString.replace(' ', '_')
                type = 'module_apply_error_{0:>s}'.format(error)
                if error == 'too_heavy' and itemTypeName == ITEM_TYPE_NAMES[2]:
                    type += '_chassis'
                self.call('VehicleComponents.HideWaitingMessage', [])
                message = i18n.makeString(('#system_messages:fitting/' + type), *errorMessageArgs)
                SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)
            return

    def onEquipModuleResult(self, itemTypeName, itemCompDescr, resultId, ext):
        typeUserString = getTypeInfoByName(itemTypeName)['userString']
        item = vehicles.getDictDescr(itemCompDescr)
        if resultId >= RES_SUCCESS:
            self.call('VehicleComponents.HideWaitingMessage', [])
            message = i18n.makeString('#system_messages:fitting/module_apply_success', typeUserString, item['userString'])
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Information)
        else:
            LOG_ERROR('Server response an error for install item(%s - %s) operation code: %s' % (itemTypeName, item['name'], resultId))
            self.call('VehicleComponents.HideWaitingMessage', [])
            message = i18n.makeString('#system_messages:fitting/module_server_apply_error', typeUserString, item['userString'])
            SystemMessages.pushMessage(message, type=SystemMessages.SM_TYPE.Error)
        self.__isRequestEquip = False

    @process
    def processBuyVehicle(self, innationIdx, nationIdx, afterUnlock, resultID, data, _):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error shop vehicles request:responseCode=' % resultID)
            data = ({}, set([]))
        self.call('VehicleComponents.HideWaitingMessage', [])
        buyPrice = data[0].get(innationIdx) if data and len(data) > 1 else None
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        if buyPrice:
            if (credits, gold) >= buyPrice:
                self.call('common.showVehicleBuyDialog', [gui_items.ShopItem('vehicle', innationIdx, nation=nationIdx, priceOrder=buyPrice).pack()])
            elif not afterUnlock:
                _credits = buyPrice[0] - credits if buyPrice[0] > 0 else 0
                _gold = buyPrice[1] - gold if buyPrice[1] > 0 else 0
                self._showMessageForVehicle('vehicle_not_enough_money', nationIdx, innationIdx, {'price': gui_items.formatPrice([_credits, _gold])})
        elif not afterUnlock:
            self._showMessageForVehicle('vehicle_not_found_in_shop', nationIdx, innationIdx)
        return

    @process
    def processBuyModule(self, itemTypeName, itemCompDescr, nationIdx, afterUnlock, resultID, data, _):
        if resultID < RES_SUCCESS:
            LOG_ERROR('Server return error shop %s items request:responseCode=' % itemTypeName, resultID)
            data = ({}, set([]))
        self.call('VehicleComponents.HideWaitingMessage', [])
        buyPrice = data[0].get(itemCompDescr) if data and len(data) > 1 else None
        credits = yield StatsRequester().getCredits()
        gold = yield StatsRequester().getGold()
        if buyPrice:
            if (credits, gold) >= buyPrice:
                invVehItem = self.graph.getInvItem(self.__vTypeCompactDesc)
                assert invVehItem is not None
                conflictedEqs = functions.findConflictedEquipments(itemCompDescr, itemTypeName, invVehItem)
                conflictedEqsStr = ''
                if len(conflictedEqs):
                    conflictedEqsStr = '\n' + i18n.makeString('#dialogs:vehicleComponents/confirmBuyAndInstall/conflictedEqs', "', '".join([ eq['userString'] for eq in conflictedEqs ]))
                message = i18n.makeString('#dialogs:vehicleComponents/confirmBuyAndInstall/message', type=getTypeInfoByName(itemTypeName)['userString'], name=vehicles.getDictDescr(itemCompDescr)['userString'], price=BigWorld.wg_getIntegralFormat(buyPrice[0]), conflictedEqs=conflictedEqsStr)
                self.call('common.showMessageDialog', ['vehicleComponents/confirmBuyAndInstall',
                 True,
                 True,
                 message,
                 'VehicleComponents.ConfirmBuyAndEquip',
                 itemTypeName,
                 itemCompDescr,
                 nationIdx,
                 buyPrice[0],
                 buyPrice[1]])
            elif not afterUnlock:
                _credits = buyPrice[0] - credits if buyPrice[0] > 0 else 0
                _gold = buyPrice[1] - gold if buyPrice[1] > 0 else 0
                self._showMessageForModule('module_not_enough_money', itemTypeName, itemCompDescr, {'price': gui_items.formatPrice([_credits, _gold])})
        elif not afterUnlock:
            self._showMessageForModule('module_not_found_in_shop', itemTypeName, itemCompDescr)
        return

    def doModuleBuy(self, itemTypeName, itemCompDescr, nationIdx, credits, gold):
        assert itemTypeName != _VEHICLE_TYPE_NAME
        if self.graph.hasInvItem(itemCompDescr):
            self.call('VehicleComponents.HideWaitingMessage', [])
            self._showMessageForModule('module_has_in_inventory', itemTypeName, itemCompDescr, type=SystemMessages.SM_TYPE.Warning)
            return
        callback = partial(self.onModuleBuyResult, itemTypeName, itemCompDescr, credits, gold)
        BigWorld.player().shop.buy(ITEM_TYPE_INDICES[itemTypeName], nationIdx, itemCompDescr, 1, callback)

    def onModuleBuyResult(self, itemTypeName, itemCompDescr, credits, gold, resultId):
        self.call('VehicleComponents.HideWaitingMessage', [])
        if resultId >= RES_SUCCESS:
            self.uiHolder.updateMoneyStats()
            self._showMessageForModule('module_buy_success', itemTypeName, itemCompDescr, args={'price': gui_items.formatPrice([credits, gold]),
             'count': 1}, type=gui_items.getPurchaseSysMessageType([credits, gold]))
            self.doEquipModule(itemTypeName, itemCompDescr)
        else:
            item = vehicles.getDictDescr(itemCompDescr)
            LOG_ERROR('Server response an error for buy item (%s-%s) operation code: %s' % (itemTypeName, item['name'], resultId))
            self._showMessageForModule('module_buy_server_error', itemTypeName, itemCompDescr)
