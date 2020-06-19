# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TechnicalMaintenance.py
from CurrentVehicle import g_currentVehicle
from adisp import process
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.MENU import MENU
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.tooltips.formatters import packItemActionTooltipData
from gui.Scaleform.daapi.view.meta.TechnicalMaintenanceMeta import TechnicalMaintenanceMeta
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.vehicle import VehicleRepairer, VehicleAutoRepairProcessor, VehicleAutoLoadProcessor, VehicleAutoEquipProcessor
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.vehicle_equipment import RegularEquipmentConsumables
from gui.shared.money import Currency
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA as _RC
from gui.shared import events, event_dispatcher as shared_events
from helpers import dependency
from helpers import i18n
from helpers.i18n import makeString
from account_helpers.settings_core.settings_constants import TUTORIAL
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.shared import IItemsCache

class TechnicalMaintenance(TechnicalMaintenanceMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self, _=None, skipConfirm=False):
        super(TechnicalMaintenance, self).__init__()
        self.__currentVehicleId = None
        self.__isConfirmDialogShown = False
        self.__layout = {}
        self._skipConfirm = skipConfirm
        return

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(TechnicalMaintenance, self)._populate()
        self.itemsCache.onSyncCompleted += self._onShopResync
        self.addListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCurrencyCallback(Currency.CREDITS, self.onCreditsChange)
        g_clientUpdateManager.addCurrencyCallback(Currency.GOLD, self.onGoldChange)
        g_clientUpdateManager.addCallbacks({'cache.mayConsumeWalletResources': self.onGoldChange,
         'cache.vehsLock': self.__onCurrentVehicleChanged})
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        if g_currentVehicle.isPresent():
            self.__currentVehicleId = g_currentVehicle.item.intCD
        self.populateTechnicalMaintenance()
        self.populateTechnicalMaintenanceEquipmentDefaults()
        self.setupContextHints(TUTORIAL.TECHNICAL_MAINTENANCE)

    def _dispose(self):
        self.itemsCache.onSyncCompleted -= self._onShopResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.removeListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        super(TechnicalMaintenance, self)._dispose()

    def onCreditsChange(self, value):
        value = self.itemsCache.items.stats.credits
        self.as_setCreditsS(value)

    def onGoldChange(self, value):
        value = self.itemsCache.items.stats.gold
        self.as_setGoldS(value)

    def _onShopResync(self, reason, diff):
        if not g_currentVehicle.isPresent():
            self.destroy()
            return
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.populateTechnicalMaintenance()
            self.populateTechnicalMaintenanceEquipment(**self.__layout)

    def getEquipment(self, eId1, currency1, eId2, currency2, eId3, currency3):
        eIdsCD = []
        for item in (eId1, eId2, eId3):
            if item is None:
                eIdsCD.append(None)
            eIdsCD.append(int(item))

        self.populateTechnicalMaintenanceEquipment(eIdsCD[0], currency1, eIdsCD[1], currency2, eIdsCD[2], currency3)
        return

    def updateEquipmentCurrency(self, equipmentIndex, currency):
        key = 'currency%d' % (int(equipmentIndex) + 1)
        params = {key: currency}
        self.__saveCurrentLayout(**params)

    @decorators.process('loadStats')
    def setRefillSettings(self, intCD, repair, load, equip):
        vehicle = self.itemsCache.items.getItemByCD(int(intCD))
        if vehicle.isAutoRepair != repair:
            yield VehicleAutoRepairProcessor(vehicle, repair).request()
        if vehicle.isAutoLoad != load:
            yield VehicleAutoLoadProcessor(vehicle, load).request()
        if vehicle.isAutoEquip != equip:
            yield VehicleAutoEquipProcessor(vehicle, equip).request()

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def populateTechnicalMaintenance(self):
        money = self.itemsCache.items.stats.money
        data = {Currency.CREDITS: money.getSignValue(Currency.CREDITS),
         Currency.GOLD: money.getSignValue(Currency.GOLD)}
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            gun = vehicle.descriptor.gun
            cassetteText = ''
            if not isAutoReloadGun(gun):
                cassetteCount = vehicle.descriptor.gun.clip[0]
                if cassetteCount > 1:
                    cassetteText = makeString('#menu:technicalMaintenance/ammoTitleEx') % cassetteCount
            else:
                cassetteCount = 1
            data.update({'vehicleId': str(vehicle.intCD),
             'repairCost': vehicle.repairCost,
             'maxRepairCost': vehicle.descriptor.getMaxRepairCost(),
             'autoRepair': vehicle.isAutoRepair,
             'autoShells': vehicle.isAutoLoad,
             'autoEqip': vehicle.isAutoEquip,
             'maxAmmo': vehicle.gun.maxAmmo,
             'gunIntCD': vehicle.gun.intCD,
             'casseteFieldText': cassetteText,
             'shells': [],
             'infoAfterShellBlock': ''})
            sellGoldShellsForCredits = self.itemsCache.items.shop.isEnabledBuyingGoldShellsForCredits
            shells = data['shells']
            for shell in vehicle.shells:
                if shell.isHidden:
                    continue
                if sellGoldShellsForCredits:
                    prices = shell.buyPrices.getSum().price
                else:
                    prices = shell.buyPrices.itemPrice.price
                currency = shell.buyPrices.itemPrice.price.getCurrency(byWeight=True)
                action = None
                buyPrice = shell.getBuyPrice()
                if buyPrice.isActionPrice() and not self.bootcamp.isInBootcamp():
                    action = packItemActionTooltipData(shell)
                shells.append({'id': str(shell.intCD),
                 'type': shell.type,
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor.icon[0],
                 'count': shell.count,
                 'userCount': shell.defaultCount,
                 'step': cassetteCount,
                 'inventoryCount': shell.inventoryCount,
                 'prices': prices.toMoneyTuple(),
                 'currency': currency,
                 'ammoName': shell.longUserNameAbbr,
                 'tableName': shell.getShortInfo(vehicle, True),
                 'maxAmmo': vehicle.gun.maxAmmo,
                 'userCredits': money.toDict(),
                 'actionPriceData': action,
                 'desc': MENU.SHELLLISTITEMRENDERER_REPLACE})

        self.as_setDataS(data)
        return

    def populateTechnicalMaintenanceEquipmentDefaults(self):
        params = {}
        for i, e in enumerate(g_currentVehicle.item.equipmentLayout.regularConsumables):
            params['eId%s' % (i + 1)] = e.intCD if e else None
            params['currency%s' % (i + 1)] = e.getBuyPrice(preferred=True).getCurrency(byWeight=True) if e else None

        self.populateTechnicalMaintenanceEquipment(**params)
        return

    def populateTechnicalMaintenanceEquipment(self, eId1=None, currency1=None, eId2=None, currency2=None, eId3=None, currency3=None):
        items = self.itemsCache.items
        vehicle = g_currentVehicle.item
        money = self.itemsCache.items.stats.money
        installedItems = vehicle.equipment.regularConsumables
        currencies = [None, None, None]
        selectedItems = [None, None, None]
        if eId1 is not None or eId2 is not None or eId3 is not None:
            selectedItems = []
            for _id in (eId1, eId2, eId3):
                if _id is not None:
                    item = items.getItemByCD(_id)
                else:
                    item = None
                selectedItems.append(item)

            currencies = [currency1, currency2, currency3]
        inventoryVehicles = items.getVehicles(_RC.INVENTORY).values()
        itemsCriteria = ~_RC.HIDDEN | _RC.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.EQUIPMENT])
        data = sorted(self.itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, itemsCriteria).values(), reverse=True)
        vehicle.equipment.setRegularConsumables(RegularEquipmentConsumables(*selectedItems))
        modules = []
        for module in data:
            fits = []
            for i in xrange(3):
                fits.append(self.__getStatus(module.mayInstall(vehicle, i)[1]))

            buyPrice = module.getBuyPrice()
            if items.shop.isEnabledBuyingGoldEqsForCredits:
                prices = module.buyPrices.getSum().price
            else:
                prices = module.buyPrices.itemPrice.price
            inventoryCount = module.inventoryCount
            index = -1
            if module in selectedItems:
                index = selectedItems.index(module)
                priceCurrency = currencies[index] or Currency.CREDITS
                if inventoryCount and module not in installedItems:
                    inventoryCount -= 1
            else:
                priceCurrency = buyPrice.getCurrency(byWeight=True)
            action = None
            if buyPrice.isActionPrice() and not self.bootcamp.isInBootcamp():
                action = packItemActionTooltipData(module)
            highlightType = module.getHighlightType()
            disabledOption = self.__isSlotDisabled(module, selectedItems)
            modules.append({'id': str(module.intCD),
             'name': module.userName,
             'desc': module.fullDescription,
             'target': module.getTarget(vehicle),
             'compactDescr': module.intCD,
             'prices': prices.toMoneyTuple(),
             'currency': priceCurrency,
             'icon': module.icon,
             'index': index,
             'inventoryCount': module.inventoryCount,
             'vehicleCount': len(module.getInstalledVehicles(inventoryVehicles)),
             'count': inventoryCount,
             'fits': fits,
             'userCredits': money.toDict(),
             'actionPriceData': action,
             'moduleLabel': module.getGUIEmblemID(),
             'builtIn': module.isBuiltIn,
             'highlightType': highlightType,
             'disabledOption': disabledOption})

        vehicle.equipment.setRegularConsumables(installedItems)
        installed = []
        for e in installedItems:
            if e is not None:
                installed.append(e.intCD)
            installed.append(None)

        setup = []
        for e in selectedItems:
            if e is not None:
                setup.append(e.intCD)
            setup.append(None)

        self.__saveCurrentLayout(eId1=eId1, currency1=currency1, eId2=eId2, currency2=currency2, eId3=eId3, currency3=currency3)
        self._setEquipment(installed, setup, modules)
        self.as_setEquipmentVisibleS(isVisible=not g_currentVehicle.isEquipmentLocked())
        return

    @decorators.process('updateMyVehicles')
    def repair(self):
        vehicle = g_currentVehicle.item
        if vehicle.isBroken:
            result = yield VehicleRepairer(vehicle).request()
            if result and result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    @process
    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        shellsLayout = []
        eqsLayout = []
        for shell in shells:
            buyGoldShellForCredits = shell.prices[1] > 0 and shell.currency == Currency.CREDITS
            shellsLayout.append(int(shell.id) if not buyGoldShellForCredits else -int(shell.id))
            shellsLayout.append(int(shell.userCount))

        for ei in equipment:
            if ei is not None:
                intCD = int(ei.id)
                buyGoldEqForCredits = ei.prices[1] > 0 and ei.currency == Currency.CREDITS
                eqsLayout.append(intCD if not buyGoldEqForCredits else -intCD)
                eqsLayout.append(1)
            eqsLayout.append(0)
            eqsLayout.append(0)

        if not needRepair and not needAmmo and not needEquipment:
            self.__setVehicleLayouts(g_currentVehicle.item, shellsLayout, eqsLayout)
        else:
            msgPrefix = '{0}'
            if needRepair:
                msgPrefix = msgPrefix.format('_repair{0}')
            if needAmmo or needEquipment:
                msgPrefix = msgPrefix.format('_populate')
            elif isUnload:
                msgPrefix = msgPrefix.format('_unload')
            elif isOrderChanged:
                msgPrefix = msgPrefix.format('_order_change')
            else:
                msgPrefix = msgPrefix.format('')
            msg = i18n.makeString(''.join(['#dialogs:technicalMaintenanceConfirm/msg', msgPrefix]))
            if not self.__isConfirmDialogShown:
                isConfirmed = yield DialogsInterface.showDialog(I18nConfirmDialogMeta('technicalMaintenanceConfirm', messageCtx={'content': msg}))
                if isConfirmed:
                    if needRepair:
                        self.repair()
                    self.__setVehicleLayouts(g_currentVehicle.item, shellsLayout, eqsLayout)
                    self.__isConfirmDialogShown = True
                else:
                    self.__isConfirmDialogShown = False
        return

    @staticmethod
    def __isSlotDisabled(module, slots):
        if module.isBuiltIn:
            installedModules = filter(None, slots)
            if len(installedModules) == 1:
                return True
        return False

    def _setEquipment(self, installed, setup, modules):
        self.as_setEquipmentS(installed, setup, modules)

    def __onCurrentVehicleChanged(self, *args):
        if g_currentVehicle.isLocked() or not g_currentVehicle.isPresent() or g_currentVehicle.isEvent():
            self.destroy()
        else:
            self.populateTechnicalMaintenance()
            if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD != self.__currentVehicleId:
                self.populateTechnicalMaintenanceEquipmentDefaults()
                self.__currentVehicleId = g_currentVehicle.item.intCD

    def __setVehicleLayouts(self, vehicle, shellsLayout=None, eqsLayout=None):
        shellsLayout = shellsLayout or []
        eqsLayout = eqsLayout or []
        ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_LAYOUT, vehicle, shellsLayout, eqsLayout, skipConfirm=self._skipConfirm)
        self.destroy()

    def __saveCurrentLayout(self, **kwargs):
        self.__layout.update(kwargs)

    def __resetEquipment(self, event):
        equipmentCD = event.ctx.get('eqCD', None)
        if equipmentCD is not None:
            self.as_resetEquipmentS(equipmentCD)
        return

    def __getStatus(self, reason):
        return '#menu:moduleFits/' + reason.replace(' ', '_') if reason is not None else ''
