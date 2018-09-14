# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/TechnicalMaintenance.py
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR, LOG_DEBUG
from gui import SystemMessages, DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.tooltips import getItemActionTooltipData
from gui.Scaleform.daapi.view.meta.TechnicalMaintenanceMeta import TechnicalMaintenanceMeta
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.vehicle import VehicleLayoutProcessor, VehicleRepairer, VehicleAutoRepairProcessor, VehicleAutoLoadProcessor, VehicleAutoEquipProcessor
from gui.shared.utils import decorators
from gui.shared.utils.requesters import REQ_CRITERIA as _RC
from gui.shared import events, g_itemsCache, event_dispatcher as shared_events
from helpers import i18n
from helpers.i18n import makeString
from account_helpers.settings_core.settings_constants import TUTORIAL

class TechnicalMaintenance(TechnicalMaintenanceMeta):

    def __init__(self, _ = None):
        super(TechnicalMaintenance, self).__init__()
        self.__currentVehicleId = None
        self.__isConfirmDialogShown = False
        self.__layout = {}
        return

    def onCancelClick(self):
        self.destroy()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(TechnicalMaintenance, self)._populate()
        g_itemsCache.onSyncCompleted += self._onShopResync
        self.addListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onCreditsChange,
         'stats.gold': self.onGoldChange,
         'cache.mayConsumeWalletResources': self.onGoldChange,
         'cache.vehsLock': self.__onCurrentVehicleChanged})
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        if g_currentVehicle.isPresent():
            self.__currentVehicleId = g_currentVehicle.item.intCD
        self.populateTechnicalMaintenance()
        self.populateTechnicalMaintenanceEquipmentDefaults()
        self.setupContextHints(TUTORIAL.TECHNICAL_MAINTENANCE)

    def _dispose(self):
        g_itemsCache.onSyncCompleted -= self._onShopResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.removeListener(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, self.__resetEquipment, scope=EVENT_BUS_SCOPE.LOBBY)
        super(TechnicalMaintenance, self)._dispose()

    def onCreditsChange(self, value):
        value = g_itemsCache.items.stats.credits
        self.as_setCreditsS(value)

    def onGoldChange(self, value):
        value = g_itemsCache.items.stats.gold
        self.as_setGoldS(value)

    def _onShopResync(self, reason, diff):
        if not g_currentVehicle.isPresent():
            self.destroy()
            return
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC or self.__currentVehicleId in diff.get(GUI_ITEM_TYPE.VEHICLE, {}):
            self.populateTechnicalMaintenance()
            self.populateTechnicalMaintenanceEquipment(**self.__layout)

    def getEquipment(self, eId1, currency1, eId2, currency2, eId3, currency3, slotIndex):
        eIdsCD = []
        for item in (eId1, eId2, eId3):
            if item is None:
                eIdsCD.append(None)
            else:
                eIdsCD.append(int(item))

        self.populateTechnicalMaintenanceEquipment(eIdsCD[0], currency1, eIdsCD[1], currency2, eIdsCD[2], currency3, slotIndex)
        return

    def updateEquipmentCurrency(self, equipmentIndex, currency):
        key = 'currency%d' % (int(equipmentIndex) + 1)
        params = {key: currency}
        self.__seveCurrentLayout(**params)

    @decorators.process('loadStats')
    def setRefillSettings(self, intCD, repair, load, equip):
        vehicle = g_itemsCache.items.getItemByCD(int(intCD))
        if vehicle.isAutoRepair != repair:
            yield VehicleAutoRepairProcessor(vehicle, repair).request()
        if vehicle.isAutoLoad != load:
            yield VehicleAutoLoadProcessor(vehicle, load).request()
        if vehicle.isAutoEquip != equip:
            yield VehicleAutoEquipProcessor(vehicle, equip).request()

    def showModuleInfo(self, moduleId):
        if moduleId is None:
            return LOG_ERROR('There is error while attempting to show module info window: ', str(moduleId))
        else:
            shared_events.showModuleInfo(moduleId, g_currentVehicle.item.descriptor)
            return

    def populateTechnicalMaintenance(self):
        credits, gold = g_itemsCache.items.stats.money
        goldShellsForCredits = g_itemsCache.items.shop.isEnabledBuyingGoldShellsForCredits
        data = {'gold': gold,
         'credits': credits}
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            casseteCount = vehicle.descriptor.gun['clip'][0]
            casseteText = makeString('#menu:technicalMaintenance/ammoTitleEx') % casseteCount
            data.update({'vehicleId': str(vehicle.intCD),
             'repairCost': vehicle.repairCost,
             'maxRepairCost': vehicle.descriptor.getMaxRepairCost(),
             'autoRepair': vehicle.isAutoRepair,
             'autoShells': vehicle.isAutoLoad,
             'autoEqip': vehicle.isAutoEquip,
             'maxAmmo': vehicle.gun.maxAmmo,
             'gunIntCD': vehicle.gun.intCD,
             'casseteFieldText': '' if casseteCount == 1 else casseteText,
             'shells': [],
             'infoAfterShellBlock': ''})
            shells = data['shells']
            for shell in vehicle.shells:
                price = shell.altPrice
                defaultPrice = shell.defaultAltPrice
                action = None
                if price != defaultPrice:
                    action = getItemActionTooltipData(shell)
                shells.append({'id': str(shell.intCD),
                 'type': shell.type,
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
                 'count': shell.count,
                 'userCount': shell.defaultCount,
                 'step': casseteCount,
                 'inventoryCount': shell.inventoryCount,
                 'goldShellsForCredits': goldShellsForCredits,
                 'prices': shell.altPrice,
                 'currency': shell.getBuyPriceCurrency(),
                 'ammoName': shell.longUserNameAbbr,
                 'tableName': shell.getShortInfo(vehicle, True),
                 'maxAmmo': vehicle.gun.maxAmmo,
                 'userCredits': {'credits': credits,
                                 'gold': gold},
                 'actionPriceData': action})

        self.as_setDataS(data)
        return

    def populateTechnicalMaintenanceEquipmentDefaults(self):
        """
        Loads layout and sets equipment according to it as a default
        """
        params = {}
        for i, e in enumerate(g_currentVehicle.item.eqsLayout):
            params['eId%s' % (i + 1)] = e.intCD if e else None
            params['currency%s' % (i + 1)] = e.getBuyPriceCurrency() if e else None

        self.populateTechnicalMaintenanceEquipment(**params)
        return

    def populateTechnicalMaintenanceEquipment(self, eId1 = None, currency1 = None, eId2 = None, currency2 = None, eId3 = None, currency3 = None, slotIndex = None):
        items = g_itemsCache.items
        goldEqsForCredits = items.shop.isEnabledBuyingGoldEqsForCredits
        vehicle = g_currentVehicle.item
        credits, gold = g_itemsCache.items.stats.money
        installedItems = list(vehicle.eqs)
        currencies = [None, None, None]
        selectedItems = [None, None, None]
        if eId1 is not None or eId2 is not None or eId3 is not None or slotIndex is not None:
            selectedItems = map(lambda id: (items.getItemByCD(id) if id is not None else None), (eId1, eId2, eId3))
            currencies = [currency1, currency2, currency3]
        inventoryVehicles = items.getVehicles(_RC.INVENTORY).values()
        itemsCriteria = ~_RC.HIDDEN | _RC.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE.EQUIPMENT])
        data = sorted(g_itemsCache.items.getItems(GUI_ITEM_TYPE.EQUIPMENT, itemsCriteria).values(), reverse=True)
        vehicle.eqs = list(selectedItems)
        modules = []
        for module in data:
            fits = []
            for i in xrange(3):
                fits.append(self.__getStatus(module.mayInstall(vehicle, i)[1]))

            price = module.altPrice
            defaultPrice = module.defaultAltPrice
            index = None
            if module in selectedItems:
                index = selectedItems.index(module)
                priceCurrency = currencies[index] or 'credits'
            else:
                priceCurrency = module.getBuyPriceCurrency()
            action = None
            if price != defaultPrice:
                action = getItemActionTooltipData(module)
            modules.append({'id': str(module.intCD),
             'name': module.userName,
             'desc': module.fullDescription,
             'target': module.getTarget(vehicle),
             'compactDescr': module.intCD,
             'prices': price,
             'currency': priceCurrency,
             'icon': module.icon,
             'index': index,
             'inventoryCount': module.inventoryCount,
             'vehicleCount': len(module.getInstalledVehicles(inventoryVehicles)),
             'count': module.inventoryCount,
             'fits': fits,
             'goldEqsForCredits': goldEqsForCredits,
             'userCredits': {'credits': credits,
                             'gold': gold},
             'actionPriceData': action,
             'moduleLabel': module.getGUIEmblemID()})

        vehicle.eqs = list(installedItems)
        installed = map(lambda e: (e.intCD if e is not None else None), installedItems)
        setup = map(lambda e: (e.intCD if e is not None else None), selectedItems)
        self.__seveCurrentLayout(eId1=eId1, currency1=currency1, eId2=eId2, currency2=currency2, eId3=eId3, currency3=currency3)
        self.as_setEquipmentS(installed, setup, modules)
        return

    @decorators.process('updateMyVehicles')
    def repair(self):
        vehicle = g_currentVehicle.item
        if vehicle.isBroken:
            result = yield VehicleRepairer(vehicle).request()
            if result and len(result.userMsg):
                SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)

    def fillVehicle(self, needRepair, needAmmo, needEquipment, isPopulate, isUnload, isOrderChanged, shells, equipment):
        shellsLayout = []
        eqsLayout = []
        for shell in shells:
            buyGoldShellForCredits = shell.goldShellsForCredits and shell.prices[1] > 0 and shell.currency == 'credits'
            shellsLayout.append(int(shell.id) if not buyGoldShellForCredits else -int(shell.id))
            shellsLayout.append(int(shell.userCount))

        for ei in equipment:
            if ei is not None:
                intCD = int(ei.id)
                buyGoldEqForCredits = ei.goldEqsForCredits and ei.prices[1] > 0 and ei.currency == 'credits'
                eqsLayout.append(intCD if not buyGoldEqForCredits else -intCD)
                eqsLayout.append(1)
            else:
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

                def fillConfirmationCallback(isConfirmed):
                    if isConfirmed:
                        if needRepair:
                            self.repair()
                        self.__setVehicleLayouts(g_currentVehicle.item, shellsLayout, eqsLayout)
                    self.__isConfirmDialogShown = False

                DialogsInterface.showDialog(I18nConfirmDialogMeta('technicalMaintenanceConfirm', messageCtx={'content': msg}), fillConfirmationCallback)
                self.__isConfirmDialogShown = True
        return

    def __onCurrentVehicleChanged(self, *args):
        if g_currentVehicle.isLocked() or not g_currentVehicle.isPresent():
            self.destroy()
        else:
            self.populateTechnicalMaintenance()
            if g_currentVehicle.isPresent() and g_currentVehicle.item.intCD != self.__currentVehicleId:
                self.populateTechnicalMaintenanceEquipmentDefaults()
                self.__currentVehicleId = g_currentVehicle.item.intCD

    @decorators.process('techMaintenance')
    def __setVehicleLayouts(self, vehicle, shellsLayout = list(), eqsLayout = list()):
        LOG_DEBUG('setVehicleLayouts', shellsLayout, eqsLayout)
        result = yield VehicleLayoutProcessor(vehicle, shellsLayout, eqsLayout).request()
        if result and result.auxData:
            for m in result.auxData:
                SystemMessages.g_instance.pushI18nMessage(m.userMsg, type=m.sysMsgType)

        if result and len(result.userMsg):
            SystemMessages.g_instance.pushI18nMessage(result.userMsg, type=result.sysMsgType)
        self.destroy()

    def __seveCurrentLayout(self, **kwargs):
        self.__layout.update(kwargs)

    def __resetEquipment(self, event):
        equipmentCD = event.ctx.get('eqCD', None)
        if equipmentCD is not None:
            self.as_resetEquipmentS(equipmentCD)
        return

    def __getStatus(self, reason):
        if reason is not None:
            return '#menu:moduleFits/' + reason.replace(' ', '_')
        else:
            return ''
