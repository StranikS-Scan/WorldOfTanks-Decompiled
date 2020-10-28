# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/__init__.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.page import SharedPage
from gui.Scaleform.daapi.view.bootcamp.BCPreBattleTimer import BCPreBattleTimer
from gui.Scaleform.daapi.view.bootcamp.BCVehicleMessages import BCVehicleMessages
from gui.Scaleform.daapi.view.bootcamp.component_override import BootcampComponentOverride
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, ConditionalViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE, events
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent
__all__ = ('SharedPage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import damage_info_panel
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared import debug_panel
    from gui.Scaleform.daapi.view.battle.shared import indicators
    from gui.Scaleform.daapi.view.battle.shared import ingame_help
    from gui.Scaleform.daapi.view.battle.shared import ingame_menu
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared.radial_menu import RadialMenu
    from gui.Scaleform.daapi.view.dialogs import deserter_dialog
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from gui.Scaleform.daapi.view.battle.shared import damage_log_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading_minimap
    from gui.Scaleform.daapi.view.battle.shared.vehicles import dualgun_component
    from gui.Scaleform.daapi.view.battle.shared import callout_panel
    from gui.Scaleform.daapi.view.battle.event import radial_menu, component_override
    return (ViewSettings(VIEW_ALIAS.INGAME_MENU, ingame_menu.IngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ViewSettings(VIEW_ALIAS.INGAME_DESERTER, deserter_dialog.IngameDeserterDialog, 'deserterDialog.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DYNAMIC_SCOPE, isModal=True, canDrag=False),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, damage_log_panel.DamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_HELP, ingame_help.IngameHelpWindow, 'ingameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ViewSettings(VIEW_ALIAS.INGAME_DETAILS_HELP, ingame_help.IngameDetailsHelpWindow, 'ingameDetailsHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, debug_panel.DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BootcampComponentOverride(battle_timers.PreBattleTimer, BCPreBattleTimer), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, BootcampComponentOverride(messages.VehicleMessages, BCVehicleMessages), None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, messages.VehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalViewSettings(BATTLE_VIEW_ALIASES.RADIAL_MENU, component_override.EventComponentOverride(RadialMenu, radial_menu.EventRadialMenu), None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL, damage_info_panel.DamageInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, indicators.SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_ON_BATTLE_LOADING, battle_loading_minimap.BattleLoadingMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, indicators.SiegeModeIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL, dualgun_component.DualGunComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CALLOUT_PANEL, callout_panel.CalloutPanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePackageBusinessHandler(), BattleDialogHandler())


class BattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.ACOUSTIC_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.INGAME_MENU, self.__handleIngameMenuEvent),
         (VIEW_ALIAS.INGAME_HELP, self.__handleHelpEvent),
         (VIEW_ALIAS.INGAME_DETAILS_HELP, self.__handleDetailsHelpEvent))
        super(BattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def __handleIngameMenuEvent(self, event):
        window = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.INGAME_MENU)
        if window is not None:
            window.destroy()
        else:
            self.loadViewByCtxEvent(event)
        return

    def __handleHelpEvent(self, _):
        window = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.INGAME_HELP)
        if window is not None:
            window.destroy()
        elif self._app is None or not self._app.isModalViewShown():
            self.loadViewWithDefName(VIEW_ALIAS.INGAME_HELP)
        return

    def __handleDetailsHelpEvent(self, event):
        window = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.INGAME_DETAILS_HELP)
        if window is not None:
            window.destroy()
        elif self._app is None or not (self._app.isModalViewShown() or self.__isFullStatsShown(event.ctx)):
            self.loadViewWithDefName(VIEW_ALIAS.INGAME_DETAILS_HELP, None, event.ctx)
        return

    def __isFullStatsShown(self, ctx):
        if not ctx.get('battleRoyale', False):
            return False
        battlePage = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.BATTLE_ROYALE_PAGE)
        return battlePage.isFullStatsShown()


class BattleDialogHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((events.ShowDialogEvent.SHOW_DESERTER_DLG, self.__showDeserterDialog),)
        super(BattleDialogHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.GLOBAL)

    def __showDeserterDialog(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.INGAME_DESERTER, event.meta, event.handler)
