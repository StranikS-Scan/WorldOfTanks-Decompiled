# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_page import RankedMainSeasonOnPage, RankedMainSeasonOffPage
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_intro import RankedBattlesIntro
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_rewards_view import RankedRewardsSeasonOnView, RankedRewardsSeasonOffView, RankedBattlesRewardsRanksView, RankedBattlesRewardsLeaguesView, RankedBattlesRewardsYearView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_divisions import RankedBattlesDivisionsView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_leagues import RankedBattlesLeaguesView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_season_gap import RankedBattlesSeasonGapView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_unreachable_view import RankedBattlesUnreachableView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_results import RankedBattlesResults
    from gui.Scaleform.daapi.view.lobby.rankedBattles.postbattle_ranked_awards_view import PostbattleRankedAwardsView
    from gui.Scaleform.daapi.view.lobby.hangar.ranked_battles_widget import RankedBattleResultsWidget
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_season_complete_view import RankedBattlesSeasonCompleteView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_prime_time_view import RankedBattlesPrimeTimeView
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_browser_pages import RankedRatingPage, RankedBattlesInfoPage, RankedSeasonGapPage, RankedYearRatingPage, RankedYearLBLandingView, RankedShopPage, RankedShopLandingView, RankedWebOverlay
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_progress import RankedBattlesProgress
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_battles_qualification import RankedBattlesQualification
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_entry_point import RankedBattlesEntryPoint
    from gui.Scaleform.daapi.view.lobby.rankedBattles.ranked_qualification_rewards import RankedQualificationRewards
    return (ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, RankedMainSeasonOnPage, 'rankedBattlesPage.swf', WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_SEASON_OFF_ALIAS, RankedMainSeasonOffPage, 'rankedBattlesPage.swf', WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_SEASON_OFF_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, RankedBattlesIntro, 'rankedBattlesIntro.swf', WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_UI, RankedRewardsSeasonOnView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_SEASON_OFF_ALIAS, RankedRewardsSeasonOffView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_RANKS_UI, RankedBattlesRewardsRanksView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_LEAGUES_UI, RankedBattlesRewardsLeaguesView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_WEB_SEASON_GAP_ALIAS, RankedSeasonGapPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SHOP_ALIAS, RankedShopPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_RAITING_ALIAS, RankedRatingPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_YEAR_RAITING_ALIAS, RankedYearRatingPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_INFO_ALIAS, RankedBattlesInfoPage, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_REWARDS_YEAR_UI, RankedBattlesRewardsYearView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_VIEW_UI, RankedBattlesDivisionsView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_PROGRESS_UI, RankedBattlesProgress, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_DIVISIONS_QUALIFICATION_UI, RankedBattlesQualification, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_LEAGUES_VIEW_UI, RankedBattlesLeaguesView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_GAP_VIEW_UI, RankedBattlesSeasonGapView, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, RankedBattlesUnreachableView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_UI, WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, RankedBattlesResults, RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS_UI, WindowLayer.FULLSCREEN_WINDOW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, PostbattleRankedAwardsView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD_UI, WindowLayer.FULLSCREEN_WINDOW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, RankedBattlesSeasonCompleteView, RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE_UI, WindowLayer.FULLSCREEN_WINDOW, RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, True),
     ComponentSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_RESULTS_WIDGET, RankedBattleResultsWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.ENTRY_POINT, RankedBattlesEntryPoint, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(RANKEDBATTLES_ALIASES.QUALIFICATION_REWARDS_VIEW_ALIAS, RankedQualificationRewards, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, RankedBattlesPrimeTimeView, HANGAR_ALIASES.RANKED_PRIME_TIME, WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_SHOP_LANDING, RankedShopLandingView, 'browserScreen.swf', WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLE_SHOP_LANDING, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_BATTLE_YEAR_RATING_LANDING, RankedYearLBLandingView, 'browserScreen.swf', WindowLayer.SUB_VIEW, RANKEDBATTLES_ALIASES.RANKED_BATTLE_YEAR_RATING_LANDING, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(RANKEDBATTLES_ALIASES.RANKED_WEB_OVERLAY, RankedWebOverlay, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, RANKEDBATTLES_ALIASES.RANKED_WEB_OVERLAY, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (RankedBattlesPackageBusinessHandler(),)


class RankedBattlesPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_PAGE_SEASON_OFF_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_INTRO_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_UNREACHABLE_VIEW_ALIAS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_BATTLE_RESULTS, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_AWARD, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLES_SEASON_COMPLETE, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLE_PRIME_TIME, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLE_SHOP_LANDING, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_BATTLE_YEAR_RATING_LANDING, self.loadViewByCtxEvent),
         (RANKEDBATTLES_ALIASES.RANKED_WEB_OVERLAY, self.loadViewByCtxEvent))
        super(RankedBattlesPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
