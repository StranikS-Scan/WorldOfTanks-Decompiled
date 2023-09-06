# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/battle/__init__.py
import typing
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.daapi.view.bootcamp.BCBattlePage import BootcampMinimapComponent
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
if typing.TYPE_CHECKING:
    from gui.shared.events import LoadViewEvent

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from gui.Scaleform.daapi.view.battle.classic import players_panel
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.shared import timers_panel
    from gui.Scaleform.daapi.view.battle.shared import damage_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.bootcamp.battle import bootcamp_battle_timer
    from gui.Scaleform.daapi.view.bootcamp.battle.frag_correlation_bar import BootcampFragCorrelationBar
    from gui.Scaleform.daapi.view.bootcamp.BCIntroFadeOut import BCIntroFadeOut
    from gui.Scaleform.daapi.view.bootcamp.BCBattlePage import BCBattlePage
    from gui.Scaleform.daapi.view.bootcamp.BCHighlights import BCHighlights
    from gui.Scaleform.daapi.view.bootcamp.BCConsumablesPanel import BCConsumablesPanel
    from gui.Scaleform.daapi.view.bootcamp.BCIntroVideoPage import BCIntroVideoPage
    from gui.Scaleform.daapi.view.bootcamp.BCRibbonsPanel import BCRibbonsPanel
    from gui.Scaleform.daapi.view.bootcamp.BCSecondaryHint import BCSecondaryHint
    from gui.Scaleform.daapi.view.bootcamp.BCPrebattleHints import BCPrebattleHints
    from gui.Scaleform.daapi.view.bootcamp.BCPreBattleTimer import BCPreBattleTimer
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    from gui.Scaleform.daapi.view.battle.shared.hint_panel import component
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared import perks_panel
    return (ViewSettings(VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, BCIntroVideoPage, 'BCIntroVideo.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, BCBattlePage, 'BCbattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, BCIntroFadeOut, 'BCIntroFadeOut.swf', WindowLayer.WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, BCHighlights, 'BCHighlights.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BCConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BCRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BOOTCAMP_SECONDARY_HINT, BCSecondaryHint, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS, BCPrebattleHints, 'BCPrebattleHints.swf', WindowLayer.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, BootcampFragCorrelationBar, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, bootcamp_battle_timer.BootcampBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.TimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, BootcampMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.DamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, component.BattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, BCPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PERKS_PANEL, perks_panel.PerksPanel, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BootcampPackageBusinessHandler(),)


class BootcampPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        self.__hideHints = False
        listeners = ((VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, self.__loadPage),
         (VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, self.__onShowIntro),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_TOP_HINT, self.__onShowHint),
         (VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_ADD_HIGHLIGHT, self.__onHighlightHint),
         (VIEW_ALIAS.BOOTCAMP_REMOVE_HIGHLIGHT, self.__onRemoveHighlight),
         (VIEW_ALIAS.BOOTCAMP_HINT_COMPLETE, self.__onComplete),
         (VIEW_ALIAS.BOOTCAMP_HINT_HIDE, self.__onHide),
         (VIEW_ALIAS.BOOTCAMP_HINT_CLOSE, self.__onCloseHint),
         (VIEW_ALIAS.BOOTCAMP_CLOSE_PREBATTLE, self.__onClosePrebattle))
        super(BootcampPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def __onShowIntro(self, event):
        LOG_DEBUG_DEV_BOOTCAMP('onShowIntro', event.name, event.ctx)
        self._app.loadView(event.loadParams, event.ctx)

    def __onShowHint(self, event):
        if not self.__hideHints:
            battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
            if battleView is not None:
                battleView.topHint.showHint(event.ctx)
        return

    def __onComplete(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.complete()
        return

    def __onHide(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.hideHint()
        return

    def __onCloseHint(self, _):
        battleView = self.findViewByAlias(WindowLayer.VIEW, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None and battleView.topHint is not None:
            battleView.topHint.closeHint()
        return

    def __onClosePrebattle(self, _):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS)
        if hintWindow:
            hintWindow.destroy()

    def __onRemoveHighlight(self, event):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS)
        if hintWindow:
            hintWindow.hideHint(event.ctx)

    def __onHighlightHint(self, event):
        hintWindow = self.findViewByAlias(WindowLayer.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS)
        LOG_DEBUG_DEV_BOOTCAMP('onHighlightHint', hintWindow, event.ctx)
        if hintWindow is not None:
            hintWindow.showHint(event.ctx)
        return

    def __loadPage(self, event):
        page = self.findViewByAlias(WindowLayer.VIEW, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
