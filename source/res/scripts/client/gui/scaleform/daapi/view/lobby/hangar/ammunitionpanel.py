# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/AmmunitionPanel.py
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_ERROR
from gui import makeHtmlString
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import getFalloutCtrl
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.tooltips import getItemActionTooltipData
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE_INDICES, GUI_ITEM_TYPE_NAMES
from gui.shared.utils import EXTRA_MODULE_INFO, CLIP_ICON_PATH
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared import g_itemsCache
from gui.shared.events import LobbySimpleEvent, LoadViewEvent
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from items import ITEM_TYPE_NAMES
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared import event_dispatcher as shared_events

class AmmunitionPanel(AmmunitionPanelMeta):
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
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.__falloutCtrl = getFalloutCtrl()
        self.__falloutCtrl.onSettingsChanged += self._updateFalloutSettings
        self.update()

    def _dispose(self):
        self.__falloutCtrl.onSettingsChanged -= self._updateFalloutSettings
        self.__falloutCtrl = None
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(AmmunitionPanel, self)._dispose()
        return

    def _updateFalloutSettings(self):
        self._update()

    def update(self):
        self._update()

    def _update(self, modulesData = None, shellsData = None):
        if g_currentVehicle.isPresent():
            self.as_setModulesEnabledS(True)
            self.__updateAmmo(shellsData)
            money = g_itemsCache.items.stats.money
            exchangeRate = g_itemsCache.items.shop.exchangeRate
            vehicle = g_currentVehicle.item
            self.as_setVehicleHasTurretS(vehicle.hasTurrets)
            devices = []
            for slotType in AmmunitionPanel.__FITTING_SLOTS:
                data = g_itemsCache.items.getItems(GUI_ITEM_TYPE_INDICES[slotType], REQ_CRITERIA.VEHICLE.SUITABLE([vehicle], [GUI_ITEM_TYPE_INDICES[slotType]])).values()
                data.sort(reverse=True)
                if slotType in AmmunitionPanel.__ARTEFACTS_SLOTS:
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
                    moduleData = {'id': module.intCD,
                     'type': slotType,
                     'name': module.userName,
                     'desc': module.getShortInfo(),
                     'target': target if thisTypeHBItem is not None else module.getTarget(vehicle),
                     'price': price,
                     'currency': 'credits' if price[1] == 0 else 'gold',
                     'actionPriceData': action,
                     'moduleLabel': module.getGUIEmblemID()}
                    if slotType == ITEM_TYPE_NAMES[4]:
                        if module.isClipGun(vehicle.descriptor):
                            moduleData[EXTRA_MODULE_INFO] = CLIP_ICON_PATH
                    isFit, reason = True, ''
                    if not module.isInInventory:
                        isFit, reason = module.mayPurchase(money)
                        if not isFit and reason == 'credit_error':
                            isFit = module.mayPurchaseWithExchange(money, exchangeRate)
                    if slotType in AmmunitionPanel.__ARTEFACTS_SLOTS:
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
                        moduleData['icon'] = module.level
                        moduleData['removable'] = True
                        moduleData['isSelected'] = moduleData.get('target') == 1
                        moduleData['status'] = self.__getStatus(reason)
                        moduleData['disabled'] = not isFit or reason == 'unlock_error'
                        dataProvider.append(moduleData)

                if slotType in AmmunitionPanel.__ARTEFACTS_SLOTS:
                    for i in xrange(3):
                        self.__addDevice(devices, dataProvider[i], slotType, i)

                else:
                    self.__addDevice(devices, dataProvider, slotType)

            self.as_setDataS(devices)
            statusId, msg, msgLvl = g_currentVehicle.getHangarMessage()
            rentAvailable = False
            if statusId == Vehicle.VEHICLE_STATE.RENTAL_IS_ORVER:
                canBuyOrRent, _ = vehicle.mayRentOrBuy(g_itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            isBackground = False
            if statusId == Vehicle.VEHICLE_STATE.NOT_PRESENT:
                isBackground = True
            isSuitableVeh = not (self.__falloutCtrl.isSelected() and not g_currentVehicle.item.isFalloutAvailable) and g_currentVehicle.item.getCustomState() != Vehicle.VEHICLE_STATE.UNSUITABLE_TO_QUEUE
            if not isSuitableVeh:
                msg = i18n.makeString('#menu:tankCarousel/vehicleStates/%s' % Vehicle.VEHICLE_STATE.NOT_SUITABLE)
                msgLvl = Vehicle.VEHICLE_STATE_LEVEL.WARNING
            msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': i18n.makeString(msg)})
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isBackground': isBackground})
        return

    def __addDevice(self, seq, dp, slotType, slotIndex = 0):
        device = {'slotType': slotType,
         'slotIndex': slotIndex,
         'selectedIndex': self.__getSelectedItemIndex(dp),
         'availableDevices': dp,
         'tooltip': '',
         'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_MODULE}
        self.updateDeviceTooltip(device, slotType)
        seq.append(device)

    def updateDeviceTooltip(self, device, slotType):
        if device['selectedIndex'] == -1:
            if slotType == FITTING_TYPES.OPTIONAL_DEVICE:
                device['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
                device['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_DEVICE_EMPTY
            elif slotType == FITTING_TYPES.EQUIPMENT:
                device['tooltipType'] = TOOLTIPS_CONSTANTS.COMPLEX
                device['tooltip'] = TOOLTIPS.HANGAR_AMMO_PANEL_EQUIPMENT_EMPTY
            else:
                LOG_ERROR('Wrong device state! Module cannot be unselected!')
        else:
            device['tooltipType'] = TOOLTIPS_CONSTANTS.HANGAR_MODULE
            device['tooltip'] = ''

    def __getSelectedItemIndex(self, seq):
        for idx, item in enumerate(seq):
            if item['isSelected']:
                return idx

        return -1

    def _getInstallReason(self, module, vehicle, reason, slotIdx = None):
        _, installReason = module.mayInstall(vehicle, slotIdx)
        if reason == 'credit_error':
            return installReason or reason
        else:
            return installReason

    def __updateAmmo(self, shellsData = None):
        shells = []
        stateWarning = False
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            stateWarning = vehicle.isBroken or not vehicle.isAmmoFull or not g_currentVehicle.isAutoLoadFull() or not g_currentVehicle.isAutoEquipFull()
            if shellsData is None:
                shellsData = map(lambda shell: (shell, shell.count), vehicle.shells)
            for shell, count in shellsData:
                shells.append({'id': str(shell.intCD),
                 'type': shell.type,
                 'label': ITEM_TYPES.shell_kindsabbreviation(shell.type),
                 'icon': '../maps/icons/ammopanel/ammo/%s' % shell.descriptor['icon'][0],
                 'count': count,
                 'historicalBattleID': -1,
                 'tooltip': '',
                 'tooltipType': TOOLTIPS_CONSTANTS.HANGAR_SHELL})

        self.as_setAmmoS(shells, stateWarning)
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
                shared_events.showVehicleBuyDialog(vehicle)

    def showModuleInfo(self, moduleId):
        if moduleId is None:
            return LOG_ERROR('There is error while attempting to show module info window: ', str(moduleId))
        else:
            shared_events.showModuleInfo(moduleId, g_currentVehicle.item.descriptor)
            return

    def setVehicleModule(self, newId, slotIdx, oldId, isRemove):
        invID = g_currentVehicle.invID
        ItemsActionsFactory.doAction(ItemsActionsFactory.SET_VEHICLE_MODULE, invID, newId, slotIdx, oldId, isRemove)

    def __getStatus(self, reason):
        if reason is not None:
            return '#menu:moduleFits/' + reason.replace(' ', '_')
        else:
            return ''

    def __inventoryUpdateCallBack(self, *args):
        self.update()
