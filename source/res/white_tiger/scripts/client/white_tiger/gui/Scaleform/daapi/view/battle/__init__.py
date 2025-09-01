# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from white_tiger.gui import white_tiger_gui_constants
from white_tiger.gui.Scaleform.daapi.view.battle.page import WhiteTigerBattlePage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, getSwfExtensionUrl, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from white_tiger.gui.white_tiger_gui_constants import VIEW_ALIAS
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from white_tiger.gui.Scaleform.genConsts.WHITE_TIGER_BATTLE_VIEW_ALIASES import WHITE_TIGER_BATTLE_VIEW_ALIASES
__all__ = ('WhiteTigerBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import ribbons_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import minimap
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared.base_stats import StatsBase
    from white_tiger.gui.Scaleform.daapi.view.battle import consumables_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import players_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import white_tiger_hud
    from white_tiger.gui.Scaleform.daapi.view.battle import boss_teleport
    from white_tiger.gui.Scaleform.daapi.view.battle import hunter_respawn
    from white_tiger.gui.Scaleform.daapi.view.battle import overtime_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import battle_hint
    from white_tiger.gui.Scaleform.daapi.view.battle import team_bases_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import battle_timer
    from white_tiger.gui.Scaleform.daapi.view.battle import stats_exchange
    from white_tiger.gui.Scaleform.daapi.view.battle.status_notifications import panel as sn_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import white_tiger_ingame_menu
    from white_tiger.gui.Scaleform.daapi.view.battle import game_messages_panel
    from white_tiger.gui.Scaleform.daapi.view.battle import postmortem_panel
    from white_tiger.gui.Scaleform.daapi.view.common.settings.settings_window import WhiteTigerSettingsWindow
    return (ViewSettings(white_tiger_gui_constants.VIEW_ALIAS.WHITE_TIGER_BATTLE_PAGE, WhiteTigerBattlePage, getSwfExtensionUrl('white_tiger', 'whiteTigerBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.WhiteTigerStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, StatsBase, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.WhiteTigerTeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timer.WhiteTigerBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, sn_panel.WhiteTigerStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.WhiteTigerMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.WTBattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.WhiteTigerGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.WhiteTigerConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUD, white_tiger_hud.WhiteTigerHud, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_PLAYERS_PANEL, players_panel.WhiteTigerPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_HUNTER_RESPAWN, hunter_respawn.WhiteTigerHunterRespawnView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BOSS_TELEPORT, boss_teleport.WhiteTigerBossTeleportView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_OVERTIME, overtime_panel.WhiteTigerOvertimePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(WHITE_TIGER_BATTLE_VIEW_ALIASES.WHITE_TIGER_BATTLE_HINT, battle_hint.WhiteTigerBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.WhiteTigerPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_MENU, white_tiger_ingame_menu.WhiteTigerIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     GroupedViewSettings(white_tiger_gui_constants.VIEW_ALIAS.WHITE_TIGER_SETTINGS_WINDOW, WhiteTigerSettingsWindow, getSwfExtensionUrl('white_tiger', 'whiteTigerSettingsWindow.swf'), WindowLayer.TOP_WINDOW, white_tiger_gui_constants.VIEW_ALIAS.WHITE_TIGER_SETTINGS_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False))


def getBusinessHandlers():
    return (_WhiteTigerBattlePackageBusinessHandler(),)


class _WhiteTigerBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.WHITE_TIGER_BATTLE_PAGE, self._loadPage), (white_tiger_gui_constants.VIEW_ALIAS.WHITE_TIGER_SETTINGS_WINDOW, self.loadViewBySharedEvent))
        super(_WhiteTigerBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
