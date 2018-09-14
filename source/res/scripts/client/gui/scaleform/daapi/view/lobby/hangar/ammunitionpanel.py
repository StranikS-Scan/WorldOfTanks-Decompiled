# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import getItemActionTooltipData
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.Scaleform.framework import AppRef
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREQUEUE_SETTING_NAME
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH
from gui.shared.utils.functions import getViewName
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import events, g_itemsCache
from gui.server_events import g_eventsCache
from gui.shared.events import LobbySimpleEvent, LoadViewEvent
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from items import ITEM_TYPE_NAMES
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory

class AmmunitionPanel(AmmunitionPanelMeta, GlobalListener, AppRef):
    __FITTING_SLOTS = (GUI_ITEM_TYPE_NAMES[2],
     GUI_ITEM_TYPE_NAMES[3],
     GUI_ITEM_TYPE_NAMES[4],
     GUI_ITEM_TYPE_NAMES[5],
     GUI_ITEM_TYPE_NAMES[7],
     GUI_ITEM_TYPE_NAMES[9],
     GUI_ITEM_TYPE_NAMES[11])
    __ARTEFACTS_SLOTS = (GUI_ITEM_TYPE_NAMES[9], GUI_ITEM_TYPE_NAMES[11])

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        self.startGlobalListening()
        self.update()

    def _dispose(self):
        self.stopGlobalListening()
        super(AmmunitionPanel, self)._dispose()

    def update(self):
        self._update(*self._getHistoricalBattleData())

    def _update(self, modulesData = None, shellsData = None, historicalBattleID = -1):
        if g_currentVehicle.isPresent():
            self.as_setHistoricalBattleS(historicalBattleID)
            self.as_setModulesEnabledS(historicalBattleID == -1)
            self.__updateAmmo(shellsData, historicalBattleID)
            money = g_itemsCache.items.stats.money
            exchangeRate = g_itemsCache.items.shop.exchangeRate
            vehicle = g_currentVehicle.item
            self.as_setVehicleHasTurretS(vehicle.hasTurrets)
            for type in AmmunitionPanel.__FITTING_SLOTS:
                data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[type], REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE_INDICES[type]])).values()
                data.sort(reverse=True)
                if type in AmmunitionPanel.__ARTEFACTS_SLOTS:
                    dataProvider = [[], [], []]
                else:
                    dataProvider = []
                for module in data:
                    price = module.buyPrice
                    defaultPrice = module.defaultPrice
                    thisTypeHBItem = None
                    target = module.TARGETS.OTHER
                    if modulesData is not None:
                        thisTypeHBItem = modulesData.get(module.itemTypeID)
                        if thisTypeHBItem and thisTypeHBItem.intCD == module.intCD:
                            target = module.TARGETS.CURRENT
                    action = None
                    if price != defaultPrice:
                        action = getItemActionTooltipData(module)
                    moduleData = {'id': str(module.intCD),
                     'type': type,
                     'name': module.userName,
                     'desc': module.getShortInfo(),
                     'target': target if thisTypeHBItem is not None else module.getTarget(vehicle),
                     'price': price,
                     'money': money,
                     'currency': 'credits' if price[1] == 0 else 'gold',
                     'icon': module.icon if type in AmmunitionPanel.__ARTEFACTS_SLOTS else module.level,
                     'actionPriceData': action,
                     'exchangeRate': exchangeRate,
                     'moduleLabel': module.getGUIEmblemID()}
                    if type == ITEM_TYPE_NAMES[4]:
                        if module.isClipGun(vehicle.descriptor):
                            moduleData[EXTRA_MODULE_INFO] = CLIP_ICON_PATH
                    isFit, reason = True, ''
                    if not module.isInInventory:
                        isFit, reason = module.mayPurchase(money)
                        if not isFit and reason == 'credit_error':
                            isFit = module.mayPurchaseWithExchange(money, exchangeRate)
                    if type in AmmunitionPanel.__ARTEFACTS_SLOTS:
                        moduleData['removable'] = module.isRemovable
                        for i in xrange(3):
                            md = moduleData.copy()
                            if isFit:
                                reason = self._getInstallReason(module, vehicle, reason, i)
                            isCurrent = module.isInstalled(vehicle, i)
                            if md.get('target') == 1:
                                md['status'] = MENU.MODULEFITS_WRONG_SLOT if not isCurrent else self.__getStatus(reason)
                                md['isSelected'] = isCurrent
                                md['disabled'] = not isFit or not isCurrent or reason == 'unlock_error'
                            else:
                                md['status'] = self.__getStatus(reason)
                                md['isSelected'] = False
                                md['disabled'] = not isFit or reason == 'unlock_error'
                            md['slotIndex'] = i
                            dataProvider[i].append(md)

                    else:
                        if isFit:
                            reason = self._getInstallReason(module, vehicle, reason)
                        moduleData['removable'] = True
                        moduleData['isSelected'] = moduleData.get('target') == 1
                        moduleData['status'] = self.__getStatus(reason)
                        moduleData['disabled'] = not isFit or reason == 'unlock_error'
                        dataProvider.append(moduleData)

                self.as_setDataS(dataProvider, type)

            statusId, msg, msgLvl = g_currentVehicle.getHangarMessage()
            rentAvailable = False
            if statusId == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
                canBuyOrRent, _ = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            self.as_updateVehicleStatusS(msg, msgLvl, rentAvailable)
        return

    def _getInstallReason(self, module, vehicle, reason, slotIdx = None):
        _, installReason = module.mayInstall(vehicle, slotIdx)
        if reason == 'credit_error':
            return installReason or reason
        else:
            return installReason

    def __updateAmmo(self, shellsData = None, historicalBattleID = -1):
        ammo = {'gunName': '',
         'maxAmmo': 0,
         'defaultAmmoCount': 0,
         'vehicleLocked': True,
         'shells': [],
         'stateWarning': 0}
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            default_ammo_count = 0
            default_ammo = dict(((s.intCD, s.defaultCount) for s in vehicle.shells))
            isAmmoFull = vehicle.isAmmoFull or historicalBattleID != -1
            stateWarning = vehicle.isBroken or not isAmmoFull or not g_currentVehicle.isAutoLoadFull() or not g_currentVehicle.isAutoEquipFull()
            for compactDescr, count in default_ammo.iteritems():
                default_ammo_count += count

            ammo.update({'gunName': vehicle.gun.longUserName,
             'maxAmmo': vehicle.ammoMaxSize,
             'defaultAmmoCount': default_ammo_count,
             'vehicleLocked': g_currentVehicle.isLocked(),
             'stateWarning': int(stateWarning)})
            if shellsData is None:
                shellsData = map(lambda shell: (shell, shell.count), vehicle.shells)
            shells = ammo.get('shells')
            for shell, count in shellsData:
                shells.append({'id': str(shell.intCD),
                 'type': shell.type,
                 'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
                 'count': count,
                 'historicalBattleID': historicalBattleID})

        self.as_setAmmoS(ammo)
        return

    def showTechnicalMaintenance(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.TECHNICAL_MAINTENANCE), EVENT_BUS_SCOPE.LOBBY)

    def showCustomization(self):
        self.fireEvent(LoadViewEvent(VIEW_ALIAS.LOBBY_CUSTOMIZATION), EVENT_BUS_SCOPE.LOBBY)

    def highlightParams(self, type):
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.HIGHLIGHT_TANK_PARAMS, {'type': type}), EVENT_BUS_SCOPE.LOBBY)

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.VEHICLE_BUY_WINDOW, ctx={'nationID': vehicle.nationID,
                 'itemID': vehicle.innationID}))

    def showModuleInfo(self, moduleId):
        if moduleId is None:
            return LOG_ERROR('There is error while attempting to show module info window: ', str(moduleId))
        else:
            vehicle = g_currentVehicle.item
            vDescr = vehicle.descriptor
            _, _, battleID = self._getHistoricalBattleData()
            battle = g_eventsCache.getHistoricalBattles().get(battleID)
            if battle is not None and battle.canParticipateWith(vehicle.intCD):
                vDescr = battle.getVehicleModifiedDescr(vehicle)
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.MODULE_INFO_WINDOW, getViewName(VIEW_ALIAS.MODULE_INFO_WINDOW, moduleId), {'moduleCompactDescr': str(moduleId),
             'vehicleDescr': vDescr}))
            return

    def setVehicleModule(self, newId, slotIdx, oldId, isRemove):
        invID = g_currentVehicle.invID
        ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_MODULE, invID, newId, slotIdx, oldId, isRemove)

    def clearHistorical(self):
        self._update()
        self.as_setHistoricalBattleS(-1)
        self.as_setModulesEnabledS(True)

    def _getHistoricalBattleData(self):
        modulesData, shellsData = (None, None)
        historicalBattleID = -1
        if self.preQueueFunctional.getQueueType() == QUEUE_TYPE.HISTORICAL:
            battleId = self.preQueueFunctional.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID)
            battle = g_eventsCache.getHistoricalBattles().get(battleId)
            if battle is not None and g_currentVehicle.isPresent():
                vehicleData = battle.getVehicleData(g_currentVehicle.item.intCD)
                if vehicleData is not None:
                    historicalBattleID = battleId
                    modulesData = battle.getModules(g_currentVehicle.item)
                    shellsData = battle.getShellsLayout(g_currentVehicle.item.intCD)
        return (modulesData, shellsData, historicalBattleID)

    def __getStatus(self, reason):
        if reason is not None:
            return '#menu:moduleFits/' + reason.replace(' ', '_')
        else:
            return ''
