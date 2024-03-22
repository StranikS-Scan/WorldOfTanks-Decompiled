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
INSTALL_ITEM = 'installItemAction'
BUY_AND_INSTALL_ITEM = 'buyAndInstallItemAction'
BUY_AND_INSTALL_AND_SELL_ITEM = 'BuyAndInstallWithOptionalSellItemAction'
VEHICLE_AUTO_FILL_LAYOUT = 'vehicleAutoFillLayoutAction'
BUY_BERTHS = 'buyBerths'
BUY_VEHICLE_SLOT = 'buyVehClot'
ACTIVATE_BOOSTER = 'activateBooster'
BUY_BOOSTER = 'buyBooster'
BUY_AND_ACTIVATE_BOOSTER = 'buyAndActivateBooster'
CONVERT_BLUEPRINT_FRAGMENT = 'convertFragment'
USE_CREW_BOOK = 'useCrewBook'
USE_FREE_XP_TO_TANKMAN = 'useFreeXpToTankman'
RETRAIN_TANKMAN = 'retrainTankman'
CHANGE_ROLE_TANKMAN = 'changeRoleTankman'
UNLOAD_TANKMAN = 'unloadTankman'
EQUIP_TANKMAN = 'equipTankman'
CHANGE_TANKMAN_PASSPORT = 'changeTankmanPassport'
DISMISS_TANKMAN = 'dismissTankman'
RESTORE_TANKMAN = 'restoreTankman'
CONVERT_JUNK_TANKMEN = 'convertJunkTankmen'
CHANGE_NATION = 'changeNation'
INSTALL_BATTLE_ABILITIES = 'installBattleAbilities'
FRONTLINE_INSTALL_RESERVES = 'frontlineInstallReserves'
BUY_BATTLE_ABILITIES = 'buyBattleAbilities'
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
 BUY_MODULE: actions.ModuleBuyAction,
 BUY_VEHICLE: actions.VehicleBuyAction,
 INSTALL_ITEM: actions.InstallItemAction,
 BUY_AND_INSTALL_AND_SELL_ITEM: actions.BuyAndInstallWithOptionalSellItemAction,
 VEHICLE_AUTO_FILL_LAYOUT: actions.VehicleAutoFillLayoutAction,
 BUY_BERTHS: actions.BuyBerthsAction,
 BUY_VEHICLE_SLOT: actions.BuyVehicleSlotAction,
 ACTIVATE_BOOSTER: actions.ActivateBoosterAction,
 BUY_BOOSTER: actions.BuyBoosterAction,
 BUY_AND_ACTIVATE_BOOSTER: actions.BuyAndActivateBooster,
 CONVERT_BLUEPRINT_FRAGMENT: actions.ConvertBlueprintFragmentAction,
 USE_CREW_BOOK: actions.UseCrewBookAction,
 USE_FREE_XP_TO_TANKMAN: actions.UseFreeXpToTankman,
 RETRAIN_TANKMAN: actions.TankmanRetrainingAction,
 CHANGE_ROLE_TANKMAN: actions.TankmanChangeRoleAction,
 UNLOAD_TANKMAN: actions.TankmanUnloadAction,
 EQUIP_TANKMAN: actions.TankmanEquipAction,
 CHANGE_TANKMAN_PASSPORT: actions.TankmanChangePassportAction,
 DISMISS_TANKMAN: actions.TankmanDismissAction,
 RESTORE_TANKMAN: actions.TankmanRestoreAction,
 CONVERT_JUNK_TANKMEN: actions.ConvertJunkTankmenAction,
 CHANGE_NATION: actions.ChangeVehicleNationAction,
 INSTALL_BATTLE_ABILITIES: actions.InstallBattleAbilities,
 FRONTLINE_INSTALL_RESERVES: actions.FrontlineInstallReserves,
 BUY_BATTLE_ABILITIES: actions.BuyBattleAbilities,
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
