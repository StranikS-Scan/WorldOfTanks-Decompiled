# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/__init__.py
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.server_events.EventsWindow import EventsWindow
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsCurrentTab import QuestsCurrentTab
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsLadderTab import QuestsLadderTab
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsPersonalWelcomeView import QuestsPersonalWelcomeView
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsSeasonAwardsWindow import QuestsSeasonAwardsWindow
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsContentTabs import QuestsContentTabs
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsSeasonsView import QuestsSeasonsView
    from gui.Scaleform.daapi.view.lobby.server_events.QuestsTileChainsView import FalloutQuestsTileChainsView, RandomQuestsTileChainsView
    from gui.Scaleform.daapi.view.lobby.server_events.TutorialHangarQuestDetails import TutorialHangarQuestDetails
    from gui.Scaleform.daapi.view.lobby.server_events.TutorialQuestsTab import TutorialQuestsTab
    from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
    return (GroupedViewSettings(VIEW_ALIAS.EVENTS_WINDOW, EventsWindow, 'questsWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, QuestsSeasonAwardsWindow, 'questsSeasonAwardsWindow.swf', ViewTypes.WINDOW, 'pqSeasonAwards', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.BEGINNER_QUESTS_VIEW_ALIAS, TutorialQuestsTab, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.COMMON_QUESTS_VIEW_ALIAS, QuestsCurrentTab, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.LADDER_QUESTS_VIEW_ALIAS, QuestsLadderTab, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.PERSONAL_WELCOME_VIEW_ALIAS, QuestsPersonalWelcomeView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.SEASONS_VIEW_ALIAS, QuestsSeasonsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.RANDOM_TILE_CHAINS_VIEW_ALIAS, RandomQuestsTileChainsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.FALLOUT_TILE_CHAINS_VIEW_ALIAS, FalloutQuestsTileChainsView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.TUTORIAL_HANGAR_QUEST_DETAILS_PY_ALIAS, TutorialHangarQuestDetails, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(QUESTS_ALIASES.QUESTS_CONTENT_TABS_PY_ALIAS, QuestsContentTabs, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_PackageBusinessHandler(),)


class _PackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.EVENTS_WINDOW, self.__showEventWindow), (VIEW_ALIAS.QUESTS_SEASON_AWARDS_WINDOW, self.loadViewByCtxEvent))
        super(_PackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showEventWindow(self, event):
        container = self._app.containerManager.getContainer(ViewTypes.WINDOW)
        window = container.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.EVENTS_WINDOW})
        self.loadViewByCtxEvent(event)
        if window is not None:
            window.navigate(event.ctx.get('eventType'), event.ctx.get('eventID'))
        return
