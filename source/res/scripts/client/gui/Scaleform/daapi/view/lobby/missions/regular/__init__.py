# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.regular.daily_quests_injector_view import DailyQuestsInjectorView
from gui.Scaleform.daapi.view.lobby.missions.regular.missions_tab_bar import MissionsTabBarComponent
from gui.Scaleform.framework import ComponentSettings, GroupedViewSettings, ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.app_loader import settings as app_settings
from gui.impl.lobby.battle_pass.battle_pass_view import BattlePassViewsHolderComponent
from gui.impl.lobby.mapbox.mapbox_progression_view import MapboxProgressionsComponent
from gui.shared import EVENT_BUS_SCOPE

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.common.filter_popover import VehiclesFilterPopover
    from gui.Scaleform.daapi.view.lobby.missions.regular.mission_details_container_view import MissionDetailsContainerView
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_filter_popover import MissionsFilterPopoverView
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_page import MissionsPage
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_token_popover import MissionsTokenPopover
    from gui.Scaleform.daapi.view.lobby.missions.regular.vehicle_selector import RegularMissionVehicleSelector
    from gui.Scaleform.daapi.view.lobby.missions.regular.vehicle_selector import RegularVehicleSelectorCarousel
    from gui.Scaleform.daapi.view.lobby.missions.regular.missions_views import MissionsGroupedView, MissionsMarathonView, MissionsCategoriesView, MissionsEventBoardsView, CurrentVehicleMissionsView
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_details_container_view import EventBoardsDetailsBrowserView, EventBoardsDetailsVehiclesView, EventBoardsDetailsAwardsView, EventBoardsDetailsBattleView
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_browser_overlay import EventBoardsBrowserOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_vehicles_overlay import EventBoardsVehiclesOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_battle_overlay import EventBoardsBattleOverlay
    from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_awards_overlay import EventBoardsAwardsOverlay
    return (ViewSettings(VIEW_ALIAS.LOBBY_MISSIONS, MissionsPage, 'missionsPage.swf', WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_MISSIONS, ScopeTemplates.LOBBY_SUB_SCOPE),
     ViewSettings(VIEW_ALIAS.LOBBY_MISSION_DETAILS, MissionDetailsContainerView, 'missionsDetails.swf', WindowLayer.TOP_SUB_VIEW, VIEW_ALIAS.LOBBY_MISSION_DETAILS, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, EventBoardsDetailsBrowserView, 'eventBoardsDetails.swf', WindowLayer.TOP_SUB_VIEW, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, EventBoardsDetailsVehiclesView, 'eventBoardsDetails.swf', WindowLayer.TOP_SUB_VIEW, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, EventBoardsDetailsAwardsView, 'eventBoardsDetails.swf', WindowLayer.TOP_SUB_VIEW, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ViewSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, EventBoardsDetailsBattleView, 'eventBoardsDetails.swf', WindowLayer.TOP_SUB_VIEW, EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, ScopeTemplates.LOBBY_SUB_SCOPE, True),
     ComponentSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_ALIAS, EventBoardsBrowserOverlay, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_ALIAS, EventBoardsVehiclesOverlay, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_ALIAS, EventBoardsBattleOverlay, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_ALIAS, EventBoardsAwardsOverlay, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS, MissionsGroupedView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS, DailyQuestsInjectorView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_MARATHON_VIEW_PY_ALIAS, MissionsMarathonView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS, BattlePassViewsHolderComponent, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MAPBOX_VIEW_PY_ALIAS, MapboxProgressionsComponent, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS, MissionsEventBoardsView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_CATEGORIES_VIEW_PY_ALIAS, MissionsCategoriesView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.CURRENT_VEHICLE_MISSIONS_VIEW_PY_ALIAS, CurrentVehicleMissionsView, ScopeTemplates.VIEW_SCOPE),
     ComponentSettings(QUESTS_ALIASES.MISSIONS_VEHICLE_SELECTOR_ALIAS, RegularMissionVehicleSelector, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(QUESTS_ALIASES.VEHICLE_SELECTOR_CAROUSEL_ALIAS, RegularVehicleSelectorCarousel, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, MissionsFilterPopoverView, 'missionsFilterPopoverView.swf', WindowLayer.WINDOW, QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, MissionsTokenPopover, 'missionsTokenPopover.swf', WindowLayer.WINDOW, QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.VEHICLES_FILTER_POPOVER, VehiclesFilterPopover, 'vehiclesFiltersPopoverView.swf', WindowLayer.WINDOW, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, VIEW_ALIAS.VEHICLES_FILTER_POPOVER, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (MissionsPackageBusinessHandler(),)


class MissionsPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((QUESTS_ALIASES.MISSIONS_FILTER_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (QUESTS_ALIASES.MISSIONS_TOKEN_POPOVER_ALIAS, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOBBY_MISSIONS, self.__loadMissionsPageOrUpdateCurrentTab),
         (VIEW_ALIAS.LOBBY_MISSION_DETAILS, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_VIEW, self.loadViewByCtxEvent),
         (EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_VIEW, self.loadViewByCtxEvent))
        super(MissionsPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __loadMissionsPageOrUpdateCurrentTab(self, event):
        subView = self.findViewByAlias(WindowLayer.SUB_VIEW, VIEW_ALIAS.LOBBY_MISSIONS)
        if subView and subView.getCurrentTabAlias() == event.ctx.get('tab'):
            tabAlias = subView.getCurrentTabAlias()
            if tabAlias == QUESTS_ALIASES.MISSIONS_PREMIUM_VIEW_PY_ALIAS and 'subTab' in event.ctx:
                subView.currentTab.setDefaultTab(event.ctx['subTab'])
            elif tabAlias == QUESTS_ALIASES.BATTLE_PASS_MISSIONS_VIEW_PY_ALIAS:
                subView.currentTab.updateState(**event.ctx)
        else:
            self.loadViewByCtxEvent(event)
