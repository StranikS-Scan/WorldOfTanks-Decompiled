# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/items_actions/factory.py
import logging
from adisp import adisp_process, adisp_async
from gui.shared.gui_items.items_actions import actions
_logger = logging.getLogger(__name__)
SELL_ITEM = 'sellItemAction'
SELL_MULTIPLE = 'sellMultipleItems'
BUY_VEHICLE = 'vehBuyAction'
BUY_MODULE = 'moduleBuyAction'
UNLOCK_ITEM = 'unlockAction'
BC_UNLOCK_ITEM = 'bcUnlockAction'
INSTALL_ITEM = 'installItemAction'
BUY_AND_INSTALL_ITEM = 'buyAndInstallItemAction'
BUY_AND_INSTALL_AND_SELL_ITEM = 'BuyAndInstallWithOptionalSellItemAction'
BC_BUY_AND_INSTALL_ITEM = 'bcBuyAndInstallItemAction'
VEHICLE_AUTO_FILL_LAYOUT = 'vehicleAutoFillLayoutAction'
BUY_BERTHS = 'buyBerths'
BUY_VEHICLE_SLOT = 'buyVehClot'
ACTIVATE_BOOSTER = 'activateBooster'
BUY_BOOSTER = 'buyBooster'
BUY_AND_ACTIVATE_BOOSTER = 'buyAndActivateBooster'
CONVERT_BLUEPRINT_FRAGMENT = 'convertFragment'
USE_CREW_BOOK = 'useCrewBook'
CHANGE_NATION = 'changeNation'
INSTALL_BATTLE_ABILITIES = 'installBattleAbilities'
BUY_AND_INSTALL_OPT_DEVICES = 'buyAndInstallOptDevices'
BUY_AND_INSTALL_CONSUMABLES = 'buyAndInstallConsumables'
BUY_AND_INSTALL_SHELLS = 'buyAndInstallShells'
BUY_AND_INSTALL_BATTLE_BOOSTERS = 'buyAndInstallBattleBoosters'
UPGRADE_OPT_DEVICE = 'upgradeOptDevice'
DECONSTRUCT_OPT_DEVICE = 'deconstructOptDevice'
DECONSTRUCT_MULT_OPT_DEVICE = 'deconstructMultOptDevice'
REMOVE_OPT_DEVICE = 'removeOptDevice'
CHANGE_SETUP_EQUIPMENTS_INDEX = 'changeSetupEquipmentsIndex'
SET_EQUIPMENT_SLOT_TYPE = 'setEquipmentSlotType'
DISCARD_POST_PROGRESSION_PAIRS = 'discardPostProgressionPairs'
PURCHASE_POST_PROGRESSION_PAIR = 'purchasePostProgressionPair'
PURCHASE_POST_PROGRESSION_STEPS = 'purchasePostProgressionSteps'
SWITCH_PREBATTLE_AMMO_PANEL_AVAILABILITY = 'switchPrebattleAmmoPanelAvailability'
_ACTION_MAP = {SELL_ITEM: actions.SellItemAction,
 SELL_MULTIPLE: actions.SellMultipleItems,
 UNLOCK_ITEM: actions.UnlockItemAction,
 BC_UNLOCK_ITEM: actions.BCUnlockItemAction,
 BUY_MODULE: actions.ModuleBuyAction,
 BUY_VEHICLE: actions.VehicleBuyAction,
 INSTALL_ITEM: actions.InstallItemAction,
 BUY_AND_INSTALL_AND_SELL_ITEM: actions.BuyAndInstallWithOptionalSellItemAction,
 BC_BUY_AND_INSTALL_ITEM: actions.BCBuyAndInstallItemAction,
 VEHICLE_AUTO_FILL_LAYOUT: actions.VehicleAutoFillLayoutAction,
 BUY_BERTHS: actions.BuyBerthsAction,
 BUY_VEHICLE_SLOT: actions.BuyVehicleSlotAction,
 ACTIVATE_BOOSTER: actions.ActivateBoosterAction,
 BUY_BOOSTER: actions.BuyBoosterAction,
 BUY_AND_ACTIVATE_BOOSTER: actions.BuyAndActivateBooster,
 CONVERT_BLUEPRINT_FRAGMENT: actions.ConvertBlueprintFragmentAction,
 USE_CREW_BOOK: actions.UseCrewBookAction,
 CHANGE_NATION: actions.ChangeVehicleNationAction,
 INSTALL_BATTLE_ABILITIES: actions.InstallBattleAbilities,
 BUY_AND_INSTALL_OPT_DEVICES: actions.BuyAndInstallOptDevices,
 BUY_AND_INSTALL_CONSUMABLES: actions.BuyAndInstallConsumables,
 BUY_AND_INSTALL_SHELLS: actions.BuyAndInstallShells,
 BUY_AND_INSTALL_BATTLE_BOOSTERS: actions.BuyAndInstallBattleBoosters,
 UPGRADE_OPT_DEVICE: actions.UpgradeOptDeviceAction,
 DECONSTRUCT_OPT_DEVICE: actions.DeconstructOptDevice,
 DECONSTRUCT_MULT_OPT_DEVICE: actions.DeconstructMultOptDevice,
 REMOVE_OPT_DEVICE: actions.RemoveOptionalDevice,
 CHANGE_SETUP_EQUIPMENTS_INDEX: actions.ChangeSetupEquipmentsIndex,
 DISCARD_POST_PROGRESSION_PAIRS: actions.DiscardPostProgressionPairs,
 PURCHASE_POST_PROGRESSION_PAIR: actions.PurchasePostProgressionPair,
 PURCHASE_POST_PROGRESSION_STEPS: actions.PurchasePostProgressionSteps,
 SET_EQUIPMENT_SLOT_TYPE: actions.SetEquipmentSlotType,
 SWITCH_PREBATTLE_AMMO_PANEL_AVAILABILITY: actions.SwitchPrebattleAmmoPanelAvailabilityAction}

@adisp_process
def doAction(actionType, *args, **kwargs):
    action = getAction(actionType, *args, **kwargs)
    if action is not None:
        if action.isAsync():
            yield action.doAction()
        else:
            action.doAction()
    return


@adisp_async
@adisp_process
def asyncDoAction(action, callback):
    result = False
    if action is not None:
        if action.isAsync():
            result = yield action.doAction()
        else:
            action.doAction()
            result = True
    callback(result)
    return


def getAction(actionType, *args, **kwargs):
    if actionType in _ACTION_MAP:
        skipConfirm = kwargs.pop('skipConfirm', False)
        action = _ACTION_MAP[actionType](*args, **kwargs)
        action.skipConfirm = skipConfirm
        return action
    else:
        _logger.error('Action type is not found %s', actionType)
        return None
