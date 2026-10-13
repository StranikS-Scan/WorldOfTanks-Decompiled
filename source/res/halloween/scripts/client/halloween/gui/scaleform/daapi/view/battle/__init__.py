# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/__init__.py
from __future__ import absolute_import
from halloween.gui.halloween_gui_constants import VIEW_ALIAS
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.framework import getSwfExtensionUrl, ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.genConsts.BATTLE_CONTEXT_MENU_HANDLER_TYPE import BATTLE_CONTEXT_MENU_HANDLER_TYPE
from halloween.gui.scaleform.daapi.view.battle.anomaly_recipes_view import HWAnomalyRecipesView
from halloween.gui.scaleform.genConsts.HALLOWEEN_BATTLE_VIEW_ALIASES import HALLOWEEN_BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.battle.classic import player_menu_handler
    return ((BATTLE_CONTEXT_MENU_HANDLER_TYPE.PLAYERS_PANEL, player_menu_handler.PlayerMenuHandler),)


def getViewSettings():
    from halloween.gui.scaleform.daapi.view.battle.page import HalloweenBattlePage
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import quest_progress_top_view
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.shared import indicators
    from gui.impl.battle.battle_page.ammunition_panel import prebattle_ammunition_panel_inject
    from halloween.gui.scaleform.daapi.view.battle.phase_indicator import HWPhaseIndicator
    from halloween.gui.scaleform.daapi.view.battle.status_notifications.panel import HWStatusNotificationTimerPanel
    from halloween.gui.scaleform.daapi.view.battle import damage_log_panel
    from halloween.gui.scaleform.daapi.view.battle import ribbons_panel
    from halloween.gui.scaleform.daapi.view.battle.souls_counter_panel import HWSoulsCounter
    from halloween.gui.scaleform.daapi.view.battle import event_timer
    from halloween.gui.scaleform.daapi.view.battle import postmortem_panel
    from halloween.gui.scaleform.daapi.view.battle.minimap.minimap import HalloweenMinimapComponent
    from halloween.gui.scaleform.daapi.view.battle import consumables_panel
    from halloween.gui.scaleform.daapi.view.battle.buffs_panel import BuffsPanel
    from halloween.gui.scaleform.daapi.view.battle import messages as hw_messages
    from halloween.gui.scaleform.daapi.view.battle.buffs_notification_panel import BuffsNotificationSystem
    from halloween.gui.scaleform.daapi.view.battle import indicators as hw_indicators
    from halloween.gui.scaleform.daapi.view.battle import battle_hint
    from halloween.gui.scaleform.daapi.view.battle.boss_hp_bar import HWBossHPBar
    from halloween.gui.scaleform.daapi.view.battle.boss_indicator import HWBossIndicator
    from halloween.gui.scaleform.daapi.view.battle import damage_panel
    from halloween.gui.scaleform.daapi.view.battle.players_panel import HWPlayersPanel
    from halloween.gui.scaleform.daapi.view.battle import game_messages_panel
    from halloween.gui.scaleform.daapi.view.battle import battle_timers
    from halloween.gui.scaleform.daapi.view.battle import stats_exchange
    from halloween.gui.scaleform.daapi.view.battle import subtitles
    from halloween.gui.scaleform.daapi.view.battle.hint_panel.component import HWBattleHintPanel
    from halloween.gui.scaleform.daapi.view.battle.battle_upgrade_panel import HWBattleUpgradePanel
    from halloween.gui.scaleform.daapi.view.battle.modifier_widget import HWModifierWidget
    from halloween.gui.scaleform.daapi.view.battle.modifier_hint import HWPhaseModifierHint
    return (ViewSettings(VIEW_ALIAS.HALLOWEEN_BATTLE_PAGE, HalloweenBattlePage, getSwfExtensionUrl('halloween', 'HalloweenBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, hw_messages.HalloweenVehicleMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, damage_log_panel.HWDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.HWStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.HW_PLAYERS_PANEL, HWPlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, HalloweenMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.HalloweenDamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.HWConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.HWBattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.HWGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.QUEST_PROGRESS_TOP_VIEW, quest_progress_top_view.QuestProgressTopView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, HWBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, hw_messages.HalloweenVehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, hw_messages.HalloweenPlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, prebattle_ammunition_panel_inject.PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.PreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.PHASE_INDICATOR, HWPhaseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, HWStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.POINT_COUNTER, HWSoulsCounter, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_TIMER, event_timer.EventTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.HWPostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.EVENT_BUFFS_PANEL, BuffsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.BUFF_NOTIFICATION_SYSTEM, BuffsNotificationSystem, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, hw_indicators.HalloweenSixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TARGET_DESIGNATOR_UNSPOTTED_MARKER, indicators.TargetDesignatorUnspottedIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.BOSS_INDICATOR_PROGRESS, HWBossIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.PINNABLE_BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.PROGRESS_BAR_BATTLE_HINT, battle_hint.ProgressBarBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.BOSS_HPBAR, HWBossHPBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.SUBTITLES, subtitles.BattleSubtitles, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.UPGRADE_PANEL, HWBattleUpgradePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.ANOMALY_RECIPES_VIEW, HWAnomalyRecipesView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.PHASE_MODIFIER_WIDGET, HWModifierWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(HALLOWEEN_BATTLE_VIEW_ALIASES.PHASE_MODIFIER_HINT, HWPhaseModifierHint, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_HalloweenBattlePackageBusinessHandler(),)


class _HalloweenBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.HALLOWEEN_BATTLE_PAGE, self._loadPage),)
        super(_HalloweenBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
