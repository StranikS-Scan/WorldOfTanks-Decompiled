# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/__init__.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework import ViewSettings, ViewTypes
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import RankedBattlesPage
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_intro import RankedBattlesIntro
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_rewards_view import RankedBattlesRewardsView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_rewards_view import RankedBattlesRewardsRanksView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_rewards_view import RankedBattlesRewardsLeaguesView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_rewards_view import RankedBattlesRewardsYearView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_divisions import RankedBattlesDivisionsView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_leagues import RankedBattlesLeaguesView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_unreachable_view import RankedBattlesUnreachableView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_results import RankedBattlesResults
    from gui.Scaleform.daapi.view.lobby.rankedBattles.postbattle_ranked_awards_view import PostbattleRankedAwardsView
    from gui.Scaleform.daapi.view.lobby.hangar.ranked_battles_widget import RankedBattleResultsWidget
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_season_complete_view import RankedBattlesSeasonCompleteView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_prime_time_view import RankedBattlesPrimeTimeView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_browser_pages import LeaderBoardBrowserPage
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_browser_pages import RankedBattlesInfoPage
    return (ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, RankedBattlesPage, 'rankedBattlesPage.swf', ViewTypes.LOBBY_SUB, RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, RankedBattlesIntro, 'rankedBattlesIntro.swf', ViewTypes.LOBBY_SUB, RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI, RankedBattlesRewardsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI, RankedBattlesRewardsRanksView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI, RankedBattlesRewardsLeaguesView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS, LeaderBoardBrowserPage, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS, RankedBattlesInfoPage, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI, RankedBattlesRewardsYearView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI, RankedBattlesDivisionsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI, RankedBattlesLeaguesView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, RankedBattlesUnreachableView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_UI, ViewTypes.LOBBY_SUB, RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, RankedBattlesResults, RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS_UI, ViewTypes.OVERLAY, RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, PostbattleRankedAwardsView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD_UI, ViewTypes.OVERLAY, RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, RankedBattlesSeasonCompleteView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE_UI, ViewTypes.OVERLAY, RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_RESULTS_WIDGET, RankedBattleResultsWidget, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, RankedBattlesPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, ViewTypes.LOBBY_SUB, RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True))


def getBusinessHandlers():
    return (RankedBattlesPackageBusinessHandler(),)


class RankedBattlesPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, self.loadViewByCtxEvent))
        super(RankedBattlesPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
