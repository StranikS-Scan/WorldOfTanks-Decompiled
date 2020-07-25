# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/backports/context_menu.py
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.impl.backport.backport_context_menu import createContextMenuData
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_fields import TankSetupFields
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
TANK_SETUP_CARD_CM = {TankSetupConstants.BATTLE_BOOSTERS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_BOOSTER_ITEM,
 TankSetupConstants.BATTLE_ABILITIES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_ABILITY_ITEM,
 TankSetupConstants.OPT_DEVICES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_OPTIONAL_DEVICE_ITEM,
 TankSetupConstants.CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_ITEM,
 TankSetupConstants.SHELLS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_SHELL_ITEM}
TANK_SETUP_SLOT_CM = {TankSetupConstants.BATTLE_BOOSTERS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_BOOSTER_SLOT,
 TankSetupConstants.BATTLE_ABILITIES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_ABILITY_SLOT,
 TankSetupConstants.OPT_DEVICES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_OPTIONAL_DEVICE_SLOT,
 TankSetupConstants.CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_SLOT,
 TankSetupConstants.SHELLS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_SHELL_ITEM}
HANGAR_TANK_SETUP_SLOT_CM = {TankSetupConstants.BATTLE_BOOSTERS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_BATTLE_BOOSTER_SLOT,
 TankSetupConstants.BATTLE_ABILITIES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_BATTLE_ABILITY_SLOT,
 TankSetupConstants.OPT_DEVICES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_OPTIONAL_DEVICE_SLOT,
 TankSetupConstants.CONSUMABLES: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_CONSUMABLE_SLOT,
 TankSetupConstants.SHELLS: CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_SHELL_SLOT}

def getContextMenuData(event, uniqueID, selectedSetup):
    cmType = event.getArgument('fieldType')
    slotType = event.getArgument('slotType')
    if cmType == TankSetupFields.TANK_SETUP_CARD:
        contextMenuArgs = {paramName:event.getArgument(paramName) for paramName in ('intCD', 'slotType', 'isMounted', 'installedSlotId', 'isDisabled')}
        contextMenuArgs['emitterUID'] = uniqueID
        if contextMenuArgs['installedSlotId'] == NONE_ID:
            return createContextMenuData(TANK_SETUP_CARD_CM.get(event.getArgument('slotType')), contextMenuArgs)
        return createContextMenuData(TANK_SETUP_SLOT_CM.get(event.getArgument('slotType')), contextMenuArgs)
    else:
        if cmType == TankSetupFields.AMMO_PANEL_SLOT and slotType == selectedSetup:
            contextMenuArgs = {paramName:event.getArgument(paramName) for paramName in ('intCD', 'slotType', 'isMounted', 'installedSlotId')}
            contextMenuArgs['emitterUID'] = uniqueID
            if contextMenuArgs['intCD'] > 0:
                return createContextMenuData(TANK_SETUP_SLOT_CM.get(event.getArgument('slotType')), contextMenuArgs)
        elif cmType == TankSetupFields.AMMO_PANEL_SLOT and slotType != selectedSetup:
            return getHangarContextMenuData(event, uniqueID)
        return None


def getHangarContextMenuData(event, uniqueID):
    cmType = event.getArgument('fieldType')
    if cmType == TankSetupFields.AMMO_PANEL_SLOT:
        contextMenuArgs = {paramName:event.getArgument(paramName) for paramName in ('intCD', 'slotType', 'isMounted', 'installedSlotId')}
        contextMenuArgs['emitterUID'] = uniqueID
        if contextMenuArgs['intCD'] > 0:
            return createContextMenuData(HANGAR_TANK_SETUP_SLOT_CM.get(event.getArgument('slotType')), contextMenuArgs)
    return None
