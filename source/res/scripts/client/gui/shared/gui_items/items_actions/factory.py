# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/factory.py
from debug_utils import LOG_ERROR
from gui.shared.gui_items.items_actions import actions
SELL_ITEM = 'sellItemAction'
SELL_MULTIPLE = 'sellMultipleItems'
BUY_VEHICLE = 'vehBuyAction'
BUY_MODULE = 'moduleBuyAction'
UNLOCK_ITEM = 'unlockAction'
INSTALL_ITEM = 'installItemAction'
BUY_AND_INSTALL_ITEM = 'buyAndInstallItemAction'
SET_VEHICLE_MODULE = 'setVehicleModuleAction'
SET_VEHICLE_LAYOUT = 'setVehicleLayoutAction'
BUY_AND_INSTALL_ITEM_VEHICLE_LAYOUT = 'buyAndInstallItemVehicleLayout'
BUY_BERTHS = 'buyBerths'
BUY_VEHICLE_SLOT = 'buyVehClot'
BUY_BOOSTER = 'buyBooster'
CONVERT_BLUEPRINT_FRAGMENT = 'convertFragment'
USE_CREW_BOOK = 'useCrewBook'
_ACTION_MAP = {SELL_ITEM: actions.SellItemAction,
 SELL_MULTIPLE: actions.SellMultipleItems,
 UNLOCK_ITEM: actions.UnlockItemAction,
 BUY_MODULE: actions.ModuleBuyAction,
 BUY_VEHICLE: actions.VehicleBuyAction,
 INSTALL_ITEM: actions.InstallItemAction,
 BUY_AND_INSTALL_ITEM: actions.BuyAndInstallItemAction,
 SET_VEHICLE_MODULE: actions.SetVehicleModuleAction,
 SET_VEHICLE_LAYOUT: actions.SetVehicleLayoutAction,
 BUY_AND_INSTALL_ITEM_VEHICLE_LAYOUT: actions.BuyAndInstallItemVehicleLayout,
 BUY_BERTHS: actions.BuyBerthsAction,
 BUY_VEHICLE_SLOT: actions.BuyVehicleSlotAction,
 BUY_BOOSTER: actions.BuyBoosterAction,
 CONVERT_BLUEPRINT_FRAGMENT: actions.ConvertBlueprintFragmentAction,
 USE_CREW_BOOK: actions.UseCrewBookAction}

def doAction(actionType, *args, **kwargs):
    if actionType in _ACTION_MAP:
        skipConfirm = kwargs.get('skipConfirm', False)
        action = _ACTION_MAP[actionType](*args)
        action.skipConfirm = skipConfirm
        action.doAction()
    else:
        LOG_ERROR('Action type is not found', actionType)
