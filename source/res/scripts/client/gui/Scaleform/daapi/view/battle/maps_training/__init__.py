# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/maps_training/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.daapi.view.battle.maps_training.ingame_help import MapsTrainingIngameHelpWindow
from gui.Scaleform.daapi.view.battle.maps_training.prebattle_timer import MapsTrainingPreBattleTimer
from gui.Scaleform.daapi.view.battle.maps_training.battle_goals import MapsTrainingBattleGoals
from gui.Scaleform.daapi.view.battle.maps_training.loading_page import MapsTrainingLoadingPage
from gui.Scaleform.daapi.view.battle.maps_training.page import MapsTrainingPage
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle import shared
from gui.Scaleform.daapi.view.battle.shared import ingame_menu
from gui.Scaleform.daapi.view.battle.shared import damage_log_panel
from gui.Scaleform.daapi.view.battle.shared import damage_panel
from gui.Scaleform.daapi.view.battle.shared import debug_panel
from gui.Scaleform.daapi.view.battle.shared import messages
from gui.Scaleform.daapi.view.battle.shared import radial_menu
from gui.Scaleform.daapi.view.battle.shared import damage_info_panel
from gui.Scaleform.daapi.view.battle.shared import indicators
from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
from gui.Scaleform.daapi.view.battle.shared import callout_panel
from gui.Scaleform.daapi.view.battle.shared import battle_notifier
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES

def getContextMenuHandlers():
    return tuple()


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.event import battle_hint
    from gui.Scaleform.daapi.view.battle.shared.hint_panel.component import BattleHintPanel
    from gui.Scaleform.daapi.view.battle.maps_training.minimap import MapsTrainingMinimapComponent
    from gui.Scaleform.daapi.view.battle.maps_training.game_messages_panel import MapsTrainingGameMessagesPanel
    from gui.Scaleform.daapi.view.battle.maps_training.ribbon_panel import MapsTrainingRibbonPanel
    from gui.Scaleform.daapi.view.battle.maps_training.consumables_panel import MapsTrainingConsumablesPanel
    return (ViewSettings(VIEW_ALIAS.MAPS_TRAINING_PAGE, MapsTrainingPage, 'mapsTrainingBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_HELP, MapsTrainingIngameHelpWindow, 'mapsTrainingIngameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ViewSettings(VIEW_ALIAS.INGAME_MENU, ingame_menu.IngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, damage_log_panel.DamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, debug_panel.DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, MapsTrainingPreBattleTimer, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, messages.VehicleMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, messages.VehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RADIAL_MENU, radial_menu.RadialMenu, None, WindowLayer.UNDEFINED, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL, damage_info_panel.DamageInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, indicators.SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, indicators.SiegeModeIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, indicators.RocketAcceleratorIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CALLOUT_PANEL, callout_panel.CalloutPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_NOTIFIER, battle_notifier.BattleNotifier, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, MapsTrainingLoadingPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, MapsTrainingMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, MapsTrainingConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, MapsTrainingRibbonPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, MapsTrainingGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, battle_hint.BattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MAPS_TRAINING_GOALS, MapsTrainingBattleGoals, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_MapsTrainingPackageBusinessHandler(),) + shared.getBusinessHandlers()


class _MapsTrainingPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.MAPS_TRAINING_PAGE, self._loadPage),)
        super(_MapsTrainingPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
