# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/shared/__init__.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.page import SharedPage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from last_stand.gui.impl.battle.full_stats import FullEventStatsView
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from last_stand.gui.impl.battle.help_view import HelpWindow, HelpView
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent
__all__ = ('SharedPage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import damage_info_panel
    from gui.Scaleform.daapi.view.battle.shared import debug_panel
    from gui.Scaleform.daapi.view.battle.shared import indicators
    from gui.Scaleform.daapi.view.battle.shared import ingame_help
    from gui.Scaleform.daapi.view.battle.shared import battle_loading_minimap
    from gui.Scaleform.daapi.view.battle.shared.legacy_mechanics import dualgun_component
    from gui.Scaleform.daapi.view.battle.shared import callout_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_notifier
    from gui.Scaleform.daapi.view.battle.shared import death_cam_ui
    from last_stand.gui.scaleform.daapi.view.battle.shared.ls_ingame_menu import LSIngameMenu
    from last_stand.gui.scaleform.daapi.view.battle.shared.ls_radial_menu import LSRadialMenu
    return (ViewSettings(VIEW_ALIAS.INGAME_MENU, LSIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ViewSettings(VIEW_ALIAS.INGAME_DETAILS_HELP, ingame_help.IngameDetailsHelpWindow, 'ingameDetailsHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, debug_panel.DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RADIAL_MENU, LSRadialMenu, None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL, damage_info_panel.DamageInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, indicators.SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TARGET_DESIGNATOR_UNSPOTTED_MARKER, indicators.TargetDesignatorUnspottedIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.MINIMAP_ON_BATTLE_LOADING, battle_loading_minimap.BattleLoadingMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, indicators.SiegeModeIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL, dualgun_component.DualGunComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CALLOUT_PANEL, callout_panel.CalloutPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER, battle_notifier.BattleNotifier, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEATH_CAM_HUD, death_cam_ui.DeathCamUI, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePackageBusinessHandler(),)


class BattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ('__guiLoader',)

    def __init__(self):
        listeners = ((VIEW_ALIAS.ACOUSTIC_POPOVER, self.loadViewByCtxEvent),
         (VIEW_ALIAS.INGAME_MENU, self.__handleIngameMenuEvent),
         (VIEW_ALIAS.INGAME_HELP, self.__handleHelpEvent),
         (VIEW_ALIAS.INGAME_DETAILS_HELP, self.__handleHelpEvent))
        self.__guiLoader = dependency.instance(IGuiLoader)
        super(BattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def __handleIngameMenuEvent(self, event):
        window = self.findViewByAlias(WindowLayer.TOP_WINDOW, VIEW_ALIAS.INGAME_MENU)
        view = self.__guiLoader.windowsManager.getViewByLayoutID(HelpView.getLayoutId())
        if view is not None and not view.getParentWindow().isHidden():
            return
        elif self.__isFullStatsShown():
            return
        else:
            if window is not None:
                window.destroy()
            else:
                self.loadViewByCtxEvent(event)
            return

    def __handleHelpEvent(self, _):
        if self._app.containerManager.isModalViewsIsExists():
            return
        elif self.__isFullStatsShown():
            return
        else:
            window = self.findViewByAlias(WindowLayer.TOP_WINDOW, VIEW_ALIAS.INGAME_MENU)
            if window is not None:
                return
            view = self.__guiLoader.windowsManager.getViewByLayoutID(HelpView.getLayoutId())
            if view is not None:
                view.getParentWindow().destroy()
            else:
                HelpWindow().load()
            return

    def __isFullStatsShown(self):
        fullStats = self.__guiLoader.windowsManager.getViewByLayoutID(FullEventStatsView.getLayoutID())
        return fullStats is not None
