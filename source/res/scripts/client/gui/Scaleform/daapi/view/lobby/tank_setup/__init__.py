# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/tank_setup/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.battle_ability import BattleAbilityItemContextMenu, BattleAbilitySlotContextMenu, HangarBattleAbilitySlotContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.battle_booster import BattleBoosterItemContextMenu, HangarBattleBoosterSlotContextMenu, BattleBoosterSlotContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import ConsumableItemContextMenu, ConsumableSlotContextMenu, HangarConsumableSlotContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.opt_device import OptDeviceItemContextMenu, OptDeviceSlotContextMenu, HangarOptDeviceSlotContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.shell import ShellItemContextMenu, HangarShellItemContextMenu
from gui.Scaleform.daapi.view.lobby.tank_setup.context_menu.veh_module import VehModuleItemContextMenu
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework import ViewSettings, ComponentSettings

def getContextMenuHandlers():
    return ((CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_OPTIONAL_DEVICE_ITEM, OptDeviceItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_BOOSTER_ITEM, BattleBoosterItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_ABILITY_ITEM, BattleAbilityItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_ITEM, ConsumableItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_SHELL_ITEM, ShellItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_MODULE_ITEM, VehModuleItemContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_OPTIONAL_DEVICE_SLOT, OptDeviceSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_ABILITY_SLOT, BattleAbilitySlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_CONSUMABLE_SLOT, ConsumableSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_BATTLE_BOOSTER_SLOT, BattleBoosterSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_OPTIONAL_DEVICE_SLOT, HangarOptDeviceSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_BATTLE_BOOSTER_SLOT, HangarBattleBoosterSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_CONSUMABLE_SLOT, HangarConsumableSlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_BATTLE_ABILITY_SLOT, HangarBattleAbilitySlotContextMenu),
     (CONTEXT_MENU_HANDLER_TYPE.TANK_SETUP_HANGAR_SHELL_SLOT, HangarShellItemContextMenu))


def getViewSettings():
    from gui.Scaleform.framework import ScopeTemplates
    from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_view import AmmunitionSetupView
    from gui.Scaleform.daapi.view.lobby.detachment.detachment_view_veh_params import DetachmentViewVehicleParams
    from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_view_adaptor import AmmunitionSetupViewAdaptor
    return (ViewSettings(VIEW_ALIAS.AMMUNITION_SETUP_VIEW, AmmunitionSetupView, 'ammunitionSetupView.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.AMMUNITION_SETUP_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True, isModal=True), ComponentSettings(HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_INJECT, AmmunitionSetupViewAdaptor, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(HANGAR_ALIASES.AMMUNITION_SETUP_VIEW_VEHICLE_PARAMS, DetachmentViewVehicleParams, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_TankSetupBusinessHandler(),)


class _TankSetupBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.AMMUNITION_SETUP_VIEW, self.loadViewByCtxEvent),)
        super(_TankSetupBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
