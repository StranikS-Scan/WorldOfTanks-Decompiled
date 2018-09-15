# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/battle/__init__.py
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.framework.managers.loaders import ViewLoadParams
from gui.Scaleform.daapi.view.bootcamp.BCBattlePage import BootcampMinimapComponent
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.shared.events import BootcampEvent
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.classic import team_bases_panel
    from gui.Scaleform.daapi.view.battle.classic import frag_correlation_bar
    from gui.Scaleform.daapi.view.battle.classic import full_stats
    from gui.Scaleform.daapi.view.battle.classic import players_panel
    from gui.Scaleform.daapi.view.battle.classic import stats_exchange
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_loading
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from gui.Scaleform.daapi.view.bootcamp.battle import bootcamp_battle_timer
    from gui.Scaleform.daapi.view.bootcamp.BCIntroFadeOut import BCIntroFadeOut
    from gui.Scaleform.daapi.view.bootcamp.BCBattleTopHint import BCBattleTopHint
    from gui.Scaleform.daapi.view.bootcamp.BCOverlayFinalWindow import BCOverlayFinalWindow
    from gui.Scaleform.daapi.view.bootcamp.BCBattlePage import BCBattlePage
    from gui.Scaleform.daapi.view.bootcamp.BCHighlights import BCHighlights
    from gui.Scaleform.daapi.view.bootcamp.BCConsumablesPanel import BCConsumablesPanel
    from gui.Scaleform.daapi.view.bootcamp.BCIntroVideoPage import BCIntroVideoPage
    from gui.Scaleform.daapi.view.bootcamp.BCRibbonsPanel import BCRibbonsPanel
    from gui.Scaleform.daapi.view.bootcamp.BCSecondaryHint import BCSecondaryHint
    from gui.Scaleform.daapi.view.bootcamp.BCPrebattleHints import BCPrebattleHints
    from gui.Scaleform.daapi.view.battle.shared import game_messages_panel
    return (ViewSettings(VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, BCIntroVideoPage, 'BCIntroVideo.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, BCBattlePage, 'BCbattlePage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, BCIntroFadeOut, 'BCIntroFadeOut.swf', ViewTypes.WINDOW, None, ScopeTemplates.TOP_WINDOW_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BOOTCAMP_BATTLE_TOP_HINT, BCBattleTopHint, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_FINISHED_WINDOW, BCOverlayFinalWindow, 'BCOverlayFinalWindow.swf', ViewTypes.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, BCHighlights, 'BCHighlights.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, BCConsumablesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, BCRibbonsPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BOOTCAMP_SECONDARY_HINT, BCSecondaryHint, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS, BCPrebattleHints, 'BCPrebattleHints.swf', ViewTypes.WINDOW, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FRAG_CORRELATION_BAR, frag_correlation_bar.FragCorrelationBar, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, bootcamp_battle_timer.BootcampBattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.TEAM_BASES_PANEL, team_bases_panel.TeamBasesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.FULL_STATS, full_stats.FullStatsComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PlayersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, stats_exchange.ClassicStatisticsDataController, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.BattleLoading, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, BootcampMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.GAME_MESSAGES_PANEL, game_messages_panel.GameMessagesPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BootcampPackageBusinessHandler(),)


class BootcampPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        self.__hideHints = False
        listeners = ((VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, self.__loadPage),
         (VIEW_ALIAS.BOOTCAMP_INTRO_VIDEO, self.onShowIntro),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_INTRO_FADEOUT, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE, self.loadViewByCtxEvent),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_TOP_HINT, self.onShowHint),
         (VIEW_ALIAS.BOOTCAMP_BATTLE_FINISHED_WINDOW, self.onShowBattleFinished),
         (VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS, self.loadViewByCtxEvent),
         (BootcampEvent.ADD_HIGHLIGHT, self.onHighlightHint),
         (BootcampEvent.REMOVE_HIGHLIGHT, self.onRemoveHighlight),
         (BootcampEvent.REMOVE_ALL_HIGHLIGHTS, self.onRemoveAllHighlights),
         (BootcampEvent.SHOW_NEW_ELEMENTS, self.showNewElements),
         (BootcampEvent.HINT_COMPLETE, self.onComplete),
         (BootcampEvent.HINT_HIDE, self.onHide),
         (BootcampEvent.HINT_CLOSE, self.onCloseHint),
         (BootcampEvent.CLOSE_PREBATTLE, self.onClosePrebattle))
        super(BootcampPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)

    def onShowIntro(self, event):
        LOG_DEBUG_DEV_BOOTCAMP('onShowIntro', event.name, event.ctx)
        self._app.loadView(ViewLoadParams(event.eventType, event.name), event.ctx)

    def onShowHint(self, event):
        if not self.__hideHints:
            battleView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
            if battleView is not None:
                battleView.topHint.showHint(event.ctx)
        return

    def onComplete(self, event):
        battleView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.complete()
        return

    def onHide(self, event):
        battleView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None:
            battleView.topHint.hideHint()
        return

    def onCloseHint(self, event):
        battleView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView is not None and battleView.topHint is not None:
            battleView.topHint.closeHint()
        return

    def onClosePrebattle(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_PREBATTLE_HITNS)
        if hintWindow:
            hintWindow.destroy()

    def showNewElements(self, event):
        ctx = event.ctx
        battleView = self.findViewByAlias(ViewTypes.DEFAULT, VIEW_ALIAS.BOOTCAMP_BATTLE_PAGE)
        if battleView:
            battleView.showNewElements(ctx)

    def onRemoveHighlight(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS)
        if hintWindow:
            hintWindow.hideHint(event.ctx)

    def onRemoveAllHighlights(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS)
        if hintWindow:
            hintWindow.hideAllHints()

    def onHighlightHint(self, event):
        hintWindow = self.findViewByAlias(ViewTypes.WINDOW, VIEW_ALIAS.BOOTCAMP_BATTLE_HIGHLIGHTS)
        LOG_DEBUG_DEV_BOOTCAMP('onHighlightHint', hintWindow, event.ctx)
        if hintWindow is not None:
            hintWindow.showHint(event.ctx)
        return

    def onShowBattleFinished(self, event):
        self.onCloseHint(event)
        self.__hideHints = True
        self._app.loadView(ViewLoadParams(event.eventType, event.name), event.ctx)

    def __loadPage(self, event):
        page = self.findViewByAlias(ViewTypes.DEFAULT, event.name)
        if page is not None:
            page.reload()
        else:
            self.loadViewBySharedEvent(event)
        return
