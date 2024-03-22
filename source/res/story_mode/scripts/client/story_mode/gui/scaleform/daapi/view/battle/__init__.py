# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle import shared
from gui.Scaleform.daapi.view.battle.classic.stats_exchange import ClassicStatisticsDataController
from gui.Scaleform.daapi.view.battle.shared.battle_hint import DefaultBattleHint
from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
from gui.Scaleform.daapi.view.battle.shared.damage_log_panel import DamageLogPanel
from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel
from gui.Scaleform.daapi.view.battle.shared.debug_panel import DebugPanel
from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
from gui.Scaleform.daapi.view.battle.shared.messages import VehicleMessages, VehicleErrorMessages, PlayerMessages
from gui.Scaleform.daapi.view.battle.shared import death_cam_ui
from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
from gui.Scaleform.daapi.view.battle.shared import postmortem_info_panel
from gui.Scaleform.daapi.view.battle.shared import spectator_view
from gui.Scaleform.daapi.view.battle.pve_base.pve_prebattle_timer import PvePrebattleTimer
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, getSwfExtensionUrl, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from story_mode.gui.scaleform.daapi.view.battle.intro_video import IntroVideo
from story_mode.gui.scaleform.daapi.view.battle.minimap import StoryModeMinimapComponent
from story_mode.gui.scaleform.daapi.view.battle.penetration_panel import StoryModePenetrationPanel
from story_mode.gui.scaleform.daapi.view.battle.subtitles import BattleSubtitles
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from story_mode.gui.scaleform.daapi.view.battle.game_messages_panel import StoreModeGameMessagesPanel
from story_mode.gui.scaleform.daapi.view.battle.goal_timer import StoryModeTimer
from story_mode.gui.scaleform.daapi.view.battle.ingame_menu import StoryModeIngameMenu
from story_mode.gui.scaleform.daapi.view.battle.ingame_help import StoryModeIngameHelpWindow
from story_mode.gui.scaleform.daapi.view.battle.page import StoryModeBattlePage
from story_mode.gui.scaleform.daapi.view.battle.settings_window import StoryModeSettingsWindow
from story_mode.gui.scaleform.daapi.view.battle.timers_panel import StoryModelTimersPanel
from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS
__all__ = ('StoryModeBattlePage',)

def getContextMenuHandlers():
    pass


def getViewSettings():
    return (ViewSettings(VIEW_ALIAS.STORY_MODE_BATTLE_PAGE, StoryModeBattlePage, getSwfExtensionUrl('story_mode', 'storyModeBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_HELP, StoryModeIngameHelpWindow, 'ingameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ViewSettings(VIEW_ALIAS.INGAME_MENU, StoryModeIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ViewSettings(VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW, IntroVideo, getSwfExtensionUrl('story_mode', 'IntroVideo.swf'), WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.STORY_MODE_SETTINGS_WINDOW, StoryModeSettingsWindow, 'settingsWindow.swf', WindowLayer.TOP_WINDOW, 'storyModeSettingsWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ComponentSettings(BATTLE_VIEW_ALIASES.PENETRATION_PANEL, StoryModePenetrationPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.NEWBIE_HINT, DefaultBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, PvePrebattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES, BattleSubtitles, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, StoryModelTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(STORY_MODE_BATTLE_VIEW_ALIASES.STORY_MODE_TIMER, StoryModeTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, StoreModeGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, StoryModeMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, DamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEATH_CAM_HUD, death_cam_ui.DeathCamUI, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SPECTATOR_VIEW, spectator_view.SpectatorView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_INFO_PAGE, postmortem_info_panel.PostmortemInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, VehicleMessages, None, WindowLayer.UNDEFINED, None, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, VehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_StoryModeBattlePackageBusinessHandler(),) + shared.getBusinessHandlers()


class _StoryModeBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.STORY_MODE_BATTLE_PAGE, self._loadPage), (VIEW_ALIAS.STORY_MODE_SETTINGS_WINDOW, self.loadViewBySharedEvent), (VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW, self.loadViewBySharedEvent))
        super(_StoryModeBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
