# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/scaleform/daapi/view/battle/__init__.py
import BigWorld
from constants import ARENA_GUI_TYPE
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle import shared
from gui.Scaleform.framework import ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from story_mode.gui.story_mode_gui_constants import VIEW_ALIAS

class ConditionalStoryModeViewSettings(ComponentSettings):

    @staticmethod
    def __new__(cls, alias, onBoardingClazz, storyModeClazz, scope):
        arenaGuiType = getattr(BigWorld.player(), 'arenaGuiType', ARENA_GUI_TYPE.UNKNOWN)
        clazz = onBoardingClazz if arenaGuiType == ARENA_GUI_TYPE.STORY_MODE_ONBOARDING else storyModeClazz
        return ComponentSettings.__new__(cls, alias, clazz, scope)


def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared.battle_hint import DefaultBattleHint
    from gui.Scaleform.framework import ViewSettings, ScopeTemplates, getSwfExtensionUrl, GroupedViewSettings
    from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
    from story_mode.gui.scaleform.daapi.view.battle.damage_log_panel import StoryModeDamageLogPanel
    from story_mode.gui.scaleform.daapi.view.battle.fullmap import StoryModeFullMapComponent
    from story_mode.gui.scaleform.daapi.view.battle.game_messages_panel import StoreModeGameMessagesPanel
    from story_mode.gui.scaleform.daapi.view.battle.goal_timer import StoryModeTimer
    from story_mode.gui.scaleform.daapi.view.battle.ingame_help import StoryModeIngameHelpWindow
    from story_mode.gui.scaleform.daapi.view.battle.ingame_menu import StoryModeIngameMenu
    from story_mode.gui.scaleform.daapi.view.battle.intro_video import IntroVideo
    from story_mode.gui.scaleform.daapi.view.battle.minimap import StoryModeMinimapComponent
    from story_mode.gui.scaleform.daapi.view.battle.page import OnboardingBattlePage
    from story_mode.gui.scaleform.daapi.view.battle.penetration_panel import StoryModePenetrationPanel
    from story_mode.gui.scaleform.daapi.view.battle.postmortem_panel import StoryModePostmortemPanel
    from story_mode.gui.scaleform.daapi.view.battle.ribbons_panel import StoryModeRibbonsPanel
    from story_mode.gui.scaleform.daapi.view.battle.settings_window import OnboardingSettingsWindow
    from story_mode.gui.scaleform.daapi.view.battle.story_mode_page import StoryModeBattlePage
    from story_mode.gui.scaleform.daapi.view.battle.subtitles import BattleSubtitles
    from story_mode.gui.scaleform.daapi.view.battle.timers_panel import StoryModelTimersPanel
    from story_mode.gui.scaleform.genConsts.STORY_MODE_BATTLE_VIEW_ALIASES import STORY_MODE_BATTLE_VIEW_ALIASES
    from gui.Scaleform.daapi.view.battle.pve_base.pve_prebattle_timer import PvePrebattleTimer
    from messenger.gui.Scaleform.view.battle import messenger_view
    from gui.Scaleform.daapi.view.battle.shared.messages import VehicleMessages, VehicleErrorMessages
    from gui.Scaleform.daapi.view.battle.shared.situation_indicators import SituationIndicators
    from gui.Scaleform.daapi.view.battle.shared.indicators import RocketAcceleratorIndicator
    from gui.Scaleform.daapi.view.battle.shared.indicators import SiegeModeIndicator
    from gui.Scaleform.daapi.view.battle.shared.vehicles import DualGunComponent
    from gui.Scaleform.daapi.view.battle.shared.indicators import SixthSenseIndicator
    from gui.Scaleform.daapi.view.battle.shared.damage_info_panel import DamageInfoPanel
    from gui.Scaleform.daapi.view.battle.classic.map_info_tip import MapInfoTip
    from gui.Scaleform.daapi.view.battle.shared.battle_timers import BattleTimer
    from gui.Scaleform.daapi.view.battle.shared.damage_panel import DamagePanel
    from gui.Scaleform.daapi.view.battle.classic.team_bases_panel import TeamBasesPanel
    from gui.Scaleform.daapi.view.battle.pve_base.status_notifications.panel import PveStatusNotificationTimerPanel
    from gui.Scaleform.daapi.view.battle.shared.debug_panel import DebugPanel
    from gui.Scaleform.daapi.view.battle.shared.callout_panel import CalloutPanel
    from gui.Scaleform.daapi.view.battle.shared.consumables_panel import ConsumablesPanel
    from gui.Scaleform.daapi.view.battle.pve_base.hint_panel import PveBattleHintPanel
    from gui.Scaleform.daapi.view.battle.pve_base.pve_player_lives import PvePlayerLives
    from gui.Scaleform.daapi.view.battle.pve_base.secondary_objectives.secondary_objectives import PveSecondaryObjectives
    from gui.Scaleform.daapi.view.battle.pve_base.primary_objective.primary_objective import PvePrimaryObjective
    from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.progress_counter import PveProgressCounter
    from gui.Scaleform.daapi.view.battle.shared.messages import PlayerMessages
    from gui.impl.battle.battle_page.ammunition_panel.prebattle_ammunition_panel_inject import PrebattleAmmunitionPanelInject
    from gui.Scaleform.daapi.view.battle.pve_base.stats_exchange import PveStatisticsDataController
    from gui.Scaleform.daapi.view.battle.shared.postmortem_info_panel import PostmortemInfoPanel
    from gui.Scaleform.daapi.view.battle.shared.postmortem_panel import PostmortemPanel
    return (ViewSettings(VIEW_ALIAS.STORY_MODE_BATTLE_PAGE, StoryModeBattlePage, getSwfExtensionUrl('story_mode', 'storyModeBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.ONBOARDING_BATTLE_PAGE, OnboardingBattlePage, getSwfExtensionUrl('story_mode', 'onboardingBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.INGAME_HELP, StoryModeIngameHelpWindow, 'ingameHelpWindow.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, canClose=False, canDrag=False, isModal=True),
     ViewSettings(VIEW_ALIAS.INGAME_MENU, StoryModeIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),
     ViewSettings(VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW, IntroVideo, getSwfExtensionUrl('story_mode', 'IntroVideo.swf'), WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.ONBOARDING_SETTINGS_WINDOW, OnboardingSettingsWindow, 'settingsWindow.swf', WindowLayer.TOP_WINDOW, 'storyModeSettingsWindow', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ComponentSettings(BATTLE_VIEW_ALIASES.PENETRATION_PANEL, StoryModePenetrationPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(STORY_MODE_BATTLE_VIEW_ALIASES.SUBTITLES, BattleSubtitles, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, StoryModelTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(STORY_MODE_BATTLE_VIEW_ALIASES.STORY_MODE_TIMER, StoryModeTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, StoreModeGameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, StoryModeMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, StoryModeRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, StoryModeDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_HINT, DefaultBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULLSCREEN_MAP, StoryModeFullMapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, PveStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, PvePrebattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, PveBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PLAYER_LIVES, PvePlayerLives, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_SECONDARY_OBJECTIVES, PveSecondaryObjectives, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PRIMARY_OBJECTIVE, PvePrimaryObjective, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PROGRESS_COUNTER, PveProgressCounter, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, PveStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, BattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.NEWBIE_HINT, DefaultBattleHint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MAP_INFO_TIP, MapInfoTip, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, ConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_AMMUNITION_PANEL, PrebattleAmmunitionPanelInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_INFO_PANEL, DamageInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIXTH_SENSE, SixthSenseIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DUAL_GUN_PANEL, DualGunComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SIEGE_MODE_INDICATOR, SiegeModeIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, RocketAcceleratorIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DEBUG_PANEL, DebugPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CALLOUT_PANEL, CalloutPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, SituationIndicators, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_MESSAGES, VehicleMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.VEHICLE_ERROR_MESSAGES, VehicleErrorMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_MESSENGER, messenger_view.BattleMessengerView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_INFO_PAGE, PostmortemInfoPanel, ScopeTemplates.DEFAULT_SCOPE),
     ConditionalStoryModeViewSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, PostmortemPanel, StoryModePostmortemPanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_StoryModeBattlePackageBusinessHandler(),) + shared.getBusinessHandlers()


class _StoryModeBattlePackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.STORY_MODE_BATTLE_PAGE, self._loadPage),
         (VIEW_ALIAS.ONBOARDING_BATTLE_PAGE, self._loadPage),
         (VIEW_ALIAS.ONBOARDING_SETTINGS_WINDOW, self.loadViewBySharedEvent),
         (VIEW_ALIAS.STORY_MODE_INTRO_VIDEO_WINDOW, self.loadViewByCtxEvent))
        super(_StoryModeBattlePackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def _loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
