# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from grinch.gui.Scaleform.daapi.view.battle.page import GrinchBattlePage
from grinch.gui.grinch_gui_constants import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, GroupedViewSettings, getSwfExtensionUrl
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
__all__ = ('GrinchBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import battle_notifier
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from grinch.gui.Scaleform.daapi.view.battle import battle_loading
    from grinch.gui.Scaleform.daapi.view.battle import grinch_hud
    from grinch.gui.Scaleform.daapi.view.battle import minimap
    from grinch.gui.Scaleform.daapi.view.battle import timers_panel
    from grinch.gui.Scaleform.daapi.view.battle.ingame_menu import GrinchIngameMenu
    from grinch.gui.Scaleform.daapi.view.battle import ribbons_panel
    from grinch.gui.Scaleform.daapi.view.battle.settings_window import GrinchSettingsWindow
    from grinch.gui.Scaleform.daapi.view.battle.hint_panel import component
    return (ViewSettings(VIEW_ALIAS.GRINCH_BATTLE_PAGE, GrinchBattlePage, getSwfExtensionUrl('grinch', 'grinchBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.GrinchBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER, battle_notifier.BattleNotifier, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.GrinchRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.GrinchMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.GrinchTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GRINCH_HUD, grinch_hud.GrinchHud, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.GrinchBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_MENU, GrinchIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(VIEW_ALIAS.GRINCH_SETTINGS_WINDOW, GrinchSettingsWindow, 'settingsWindow.swf', WindowLayer.TOP_WINDOW, 'grinchSettingsWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False))


def getBusinessHandlers():
    return (_GrinchBattlePackageBusinessHandler(),)


class _GrinchBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.GRINCH_LOADING, self.loadViewByCtxEvent), (VIEW_ALIAS.GRINCH_BATTLE_PAGE, self._loadPage), (VIEW_ALIAS.GRINCH_SETTINGS_WINDOW, self.loadViewBySharedEvent))
        super(_GrinchBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
