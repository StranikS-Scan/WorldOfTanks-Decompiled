# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/ammunition_panel.py
from adisp import adisp_process
from constants import ROLE_TYPE
from CurrentVehicle import g_currentVehicle
from constants import RENEWABLE_SUBSCRIPTION_CONFIG
from gui import makeHtmlString
from gui.impl import backport
from gui.impl.gen import R
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.customization.shared import getItemTypesAvailableForVehicle
from gui.Scaleform.daapi.view.meta.AmmunitionPanelMeta import AmmunitionPanelMeta
from gui.impl.lobby.tank_setup.dialogs.need_repair import NeedRepair
from gui.limited_ui.lui_rules_storage import LUI_RULES
from gui.prb_control.entities.listener import IGlobalListener
from gui.shared import event_dispatcher as shared_events
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from gui.shared.gui_items.items_actions.actions import VehicleRepairAction
from gui.shared.gui_items.vehicle_helpers import getRoleMessage
from helpers import dependency, int2roman
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.tank_setup.dialogs.main_content.main_contents import NeedRepairMainContent

class AmmunitionPanel(AmmunitionPanelMeta, IGlobalListener):
    __slots__ = ('__hangarMessage',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __service = dependency.descriptor(ICustomizationService)
    __limitedUIController = dependency.descriptor(ILimitedUIController)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(AmmunitionPanel, self).__init__()
        self.__hangarMessage = None
        return

    def update(self):
        self._update()

    @adisp_process
    def showRepairDialog(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            yield VehicleRepairAction(vehicle, NeedRepair, NeedRepairMainContent).doAction()

    def showCustomization(self):
        self.__service.showCustomization()

    def toRentContinue(self):
        if g_currentVehicle.isPresent():
            vehicle = g_currentVehicle.item
            canBuyOrRent, _ = vehicle.mayObtainForMoney(self.__itemsCache.items.stats.money)
            if vehicle.isRentable and vehicle.rentalIsOver and canBuyOrRent:
                shared_events.showVehicleBuyDialog(vehicle)

    def showChangeNation(self):
        if g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup:
            ItemsActionsFactory.doAction(ItemsActionsFactory.CHANGE_NATION, g_currentVehicle.item.intCD)

    def showModuleInfo(self, itemCD):
        if itemCD is not None and int(itemCD) > 0:
            shared_events.showModuleInfo(itemCD, g_currentVehicle.item.descriptor)
        return

    def _populate(self):
        super(AmmunitionPanel, self)._populate()
        self.startGlobalListening()
        g_clientUpdateManager.addMoneyCallback(self.__moneyUpdateCallback)
        g_clientUpdateManager.addCallbacks({'inventory': self.__inventoryUpdateCallBack})
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged

    def _dispose(self):
        self.stopGlobalListening()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__hangarMessage = None
        super(AmmunitionPanel, self)._dispose()
        return

    def _update(self, onlyMoneyUpdate=False):
        if g_currentVehicle.isPresent():
            hangarMessage = g_currentVehicle.getHangarMessage()
            if onlyMoneyUpdate and self.__hangarMessage == hangarMessage:
                return
            vehicle = g_currentVehicle.item
            viewState = g_currentVehicle.getViewState()
            self.__hangarMessage = hangarMessage
            statusId, msg, msgLvl = hangarMessage
            rentAvailable = False
            if statusId in (Vehicle.VEHICLE_STATE.RENTAL_IS_OVER, Vehicle.VEHICLE_STATE.RENTABLE_AGAIN):
                canBuyOrRent, _ = vehicle.mayObtainForMoney(self.__itemsCache.items.stats.money)
                rentAvailable = vehicle.isRentable and canBuyOrRent
            if msgLvl == Vehicle.VEHICLE_STATE_LEVEL.RENTABLE:
                msgLvl = Vehicle.VEHICLE_STATE_LEVEL.INFO
            statusOverrideRes = R.strings.ranked_battles.currentVehicleStatus.dyn(statusId)
            if statusOverrideRes:
                msg = backport.text(statusOverrideRes())
            msgString = ''
            if statusId != Vehicle.VEHICLE_STATE.UNDAMAGED:
                msgString = makeHtmlString('html_templates:vehicleStatus', msgLvl, {'message': msg})
            self.__applyCustomizationNewCounter(vehicle)
            self.__updateDevices(vehicle)
            isElite = vehicle.isElite and viewState.isEliteShown()
            self.as_updateVehicleStatusS({'message': msgString,
             'rentAvailable': rentAvailable,
             'isElite': isElite,
             'tankType': '{}_elite'.format(vehicle.type) if isElite else vehicle.type,
             'vehicleLevel': '{}'.format(int2roman(vehicle.level)) if viewState.isLevelShown() else '',
             'vehicleName': '{}'.format(vehicle.shortUserName),
             'roleId': vehicle.role if viewState.isRoleShown() else ROLE_TYPE.NOT_DEFINED,
             'roleMessage': getRoleMessage(g_currentVehicle.item.role) if viewState.isRoleShown() else '',
             'vehicleCD': vehicle.intCD})

    def __inventoryUpdateCallBack(self, *args):
        self.update()

    def __onServerSettingChanged(self, diff):
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.update()

    def __applyCustomizationNewCounter(self, vehicle):
        if vehicle.isCustomizationEnabled() and self.__limitedUIController.isRuleCompleted(LUI_RULES.CustomizationBtnBubble):
            availableItemTypes = getItemTypesAvailableForVehicle()
            itemsFilter = lambda item: self.__filterAvailableCustomizations(item, vehicle)
            counter = vehicle.getC11nItemsNoveltyCounter(self.__itemsCache.items, itemTypes=availableItemTypes, itemFilter=itemsFilter)
        else:
            counter = 0
        self.as_setCustomizationBtnCounterS(counter)

    @staticmethod
    def __filterAvailableCustomizations(item, vehicle):
        if item.isStyleOnly:
            season = vehicle.getAnyOutfitSeason()
            style = vehicle.outfits[season].style
            return style and style.isItemInstallable(item.descriptor)
        return item.inventoryCount or item.installedCount(vehicle.intCD)

    def __moneyUpdateCallback(self, *_):
        self._update(onlyMoneyUpdate=True)

    def __updateDevices(self, vehicle):
        stateWarning = False
        if g_currentVehicle.isPresent():
            stateWarning = vehicle.isBroken
        self.as_setWarningStateS(stateWarning)
