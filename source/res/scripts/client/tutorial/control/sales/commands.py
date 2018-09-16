# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/sales/commands.py
from account_helpers.AccountSettings import AccountSettings, DEFAULT_VEHICLE_TYPES_FILTER, DEFAULT_LEVELS_FILTERS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from gui.shared.gui_items.items_actions import factory as ActionsFactory

def buySlots():
    ActionsFactory.doAction(ActionsFactory.BUY_VEHICLE_SLOT)


def buyBerths():
    ActionsFactory.doAction(ActionsFactory.BUY_BERTHS)


def createClan():
    g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.CLAN_CREATE))


def showMarathonPage():
    showMissionsMarathon()


def configureShopForEquipment():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.EQUIPMENT, True))
    eqFilter = AccountSettings.getFilter('shop_equipment')
    eqFilter['fitsType'] = STORE_CONSTANTS.OTHER_VEHICLES_ARTEFACT_FIT
    AccountSettings.setFilter('shop_equipment', eqFilter)


def configureShopForOptionalDevice():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.OPTIONAL_DEVICE, True))
    optDevFilter = AccountSettings.getFilter('shop_optionalDevice')
    optDevFilter['fitsType'] = STORE_CONSTANTS.OTHER_VEHICLES_ARTEFACT_FIT
    AccountSettings.setFilter('shop_optionalDevice', optDevFilter)


def configureShopForShells():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.SHELL, True))
    shellsFilter = AccountSettings.getFilter('shop_shell')
    shellsFilter['fitsType'] = STORE_CONSTANTS.OTHER_VEHICLES_SHELL_FIT
    shellsFilter['itemTypes'] = [STORE_CONSTANTS.ARMOR_PIERCING_SHELL,
     STORE_CONSTANTS.ARMOR_PIERCING_CR_SHELL,
     STORE_CONSTANTS.HOLLOW_CHARGE_SHELL,
     STORE_CONSTANTS.HIGH_EXPLOSIVE_SHELL]
    AccountSettings.setFilter('shop_shell', shellsFilter)


def configureShopForVehicleBuy():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.VEHICLE, True))
    vehFilter = AccountSettings.getFilter('shop_vehicle')
    vehFilter['obtainingType'] = STORE_CONSTANTS.VEHICLE
    vehFilter['selectedTypes'] = DEFAULT_VEHICLE_TYPES_FILTER
    vehFilter['selectedLevels'] = DEFAULT_LEVELS_FILTERS
    vehFilter['extra'] = [STORE_CONSTANTS.LOCKED_EXTRA_NAME, STORE_CONSTANTS.IN_HANGAR_EXTRA_NAME]
    AccountSettings.setFilter('shop_vehicle', vehFilter)


def configureShopForVehicleRent():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.VEHICLE, True))
    vehFilter = AccountSettings.getFilter('shop_vehicle')
    vehFilter['obtainingType'] = STORE_CONSTANTS.VEHICLE
    vehFilter['selectedTypes'] = DEFAULT_VEHICLE_TYPES_FILTER
    vehFilter['selectedLevels'] = DEFAULT_LEVELS_FILTERS
    vehFilter['extra'] = [STORE_CONSTANTS.RENTALS_EXTRA_NAME]
    AccountSettings.setFilter('shop_vehicle', vehFilter)


def configureShopForVehicleTradeIn():
    AccountSettings.setFilter('shop_current', (-1, STORE_CONSTANTS.VEHICLE, True))
    vehFilter = AccountSettings.getFilter('shop_vehicle')
    vehFilter['obtainingType'] = STORE_CONSTANTS.TRADE_IN_VEHICLE
    vehFilter['selectedTypes'] = DEFAULT_VEHICLE_TYPES_FILTER
    vehFilter['selectedLevels'] = DEFAULT_LEVELS_FILTERS
    AccountSettings.setFilter('shop_vehicle', vehFilter)
