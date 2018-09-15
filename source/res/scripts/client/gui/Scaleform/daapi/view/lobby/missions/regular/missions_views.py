# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/missions/regular/missions_views.py
from adisp import process
from functools import partial
from gui.Scaleform.daapi.view.lobby.event_boards.event_helpers import checkEventExist
from gui.Scaleform.locale.EVENT_BOARDS import EVENT_BOARDS
from skeletons.gui.game_control import IReloginController
from gui.shared import actions
from gui import DialogsInterface
from gui.Scaleform.daapi.settings import BUTTON_LINKAGES
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.CurrentVehicleMissionsViewMeta import CurrentVehicleMissionsViewMeta
from gui.Scaleform.daapi.view.meta.MissionsEventBoardsViewMeta import MissionsEventBoardsViewMeta
from gui.Scaleform.daapi.view.meta.MissionsGroupedViewMeta import MissionsGroupedViewMeta
from gui.Scaleform.daapi.view.lobby.event_boards.event_boards_maintenance import EventBoardsMaintenance
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events import settings
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.server_events.formatters import isMarathon
from gui.shared import events, g_eventBus
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles, icons
from gui.event_boards.settings import expandGroup, isGroupMinimized
from helpers.i18n import makeString as _ms
from helpers import dependency
from gui.server_events.events_dispatcher import hideMissionDetails

class _GroupedMissionsView(MissionsGroupedViewMeta):
    """ Missions tab for quests combined in groups.
    """

    def clickActionBtn(self, actionID):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_STORE, ctx={'tabId': STORE_CONSTANTS.STORE_ACTIONS}), scope=EVENT_BUS_SCOPE.LOBBY)

    def expand(self, id, value):
        settings.expandGroup(id, value)
        if self._questsDP is not None:
            for blockData in self._questsDP.collection:
                if blockData.get('blockId') == id:
                    blockData['isCollapsed'] = settings.isGroupMinimized(id)

        return


class MissionsMarathonsView(_GroupedMissionsView):
    """ Missions tab for quests combined in marathons.
        Marathon is a special group with a final prise.
    """

    def dummyClicked(self, eventType):
        if eventType == 'OpenCategoriesEvent':
            showMissionsCategories()
        else:
            super(MissionsMarathonsView, self).dummyClicked(eventType)

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_MARATHONS

    @staticmethod
    def _getDummy():
        return {'iconSource': RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON,
         'htmlText': text_styles.main(_ms(QUESTS.MISSIONS_NOTASKSMARATHON_DUMMY_TEXT)),
         'alignCenter': False,
         'btnVisible': True,
         'btnLabel': '',
         'btnTooltip': '',
         'btnEvent': 'OpenCategoriesEvent',
         'btnLinkage': BUTTON_LINKAGES.BUTTON_LINK}

    def _getViewQuestFilter(self):
        return lambda q: isMarathon(q.getGroupID())


class MissionsEventBoardsView(MissionsEventBoardsViewMeta):

    def __init__(self):
        super(MissionsEventBoardsView, self).__init__()
        self.__eventsData = None
        self.__tableView = None
        self.__maintenance = None
        return

    @checkEventExist
    def orderClick(self, eventID):
        ctx = {'eventID': eventID,
         'title': _ms(EVENT_BOARDS.ORDERS_TITLE),
         'url': self.__eventsData.getEvent(eventID).getManual()}
        self.__openDetailsContainer(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_VIEW, ctx)

    @checkEventExist
    def techniqueClick(self, eventID):
        ctx = {'eventID': eventID}
        self.__openDetailsContainer(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_VIEW, ctx)

    @checkEventExist
    def awardClick(self, eventID):
        ctx = {'eventID': eventID}
        self.__openDetailsContainer(EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_LINKAGE, ctx)

    @process
    def serverClick(self, eventID, serverID):

        def doJoin():
            from gui.Scaleform.framework import g_entitiesFactories
            g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent('missions'), scope=EVENT_BUS_SCOPE.LOBBY)

        reloginCtrl = dependency.instance(IReloginController)
        success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            reloginCtrl.doRelogin(int(serverID), extraChainSteps=(actions.OnLobbyInitedAction(onInited=doJoin),))

    @checkEventExist
    @process
    def registrationClick(self, eventID):
        self.as_setWaitingVisibleS(True)
        yield self.eventsController.joinEvent(eventID)
        self.as_setWaitingVisibleS(False)
        self._onEventsUpdate()

    @checkEventExist
    @process
    def participateClick(self, eventID):
        eventData = self.__eventsData.getEvent(eventID)
        started = eventData.isStarted()
        self.as_setWaitingVisibleS(True)
        dialog = 'leaveEvent' if started else 'leaveStartedEvent'
        success = yield DialogsInterface.showI18nConfirmDialog(dialog)
        if success:
            yield self.eventsController.leaveEvent(eventID)
            self._onEventsUpdate()
        self.as_setWaitingVisibleS(False)

    @checkEventExist
    def expand(self, id, value):
        event = self.__eventsData.getEvent(id)
        expandGroup(event, value)
        if self._questsDP is not None:
            for blockData in self._questsDP.collection:
                if blockData.get('blockId') == id:
                    blockData['isCollapsed'] = isGroupMinimized(event)

        return

    def onRefresh(self):
        """
        Executes on maintenance refresh button click.
        """
        self._onEventsUpdate()

    def _populate(self):
        super(MissionsEventBoardsView, self)._populate()
        self.__eventsData = self.eventsController.getEventsSettingsData()
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    def _dispose(self):
        self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        if self.__maintenance:
            self.__maintenance.onRefresh -= self.onRefresh
        super(MissionsEventBoardsView, self)._dispose()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(MissionsEventBoardsView, self)._onRegisterFlashComponent(viewPy, alias)
        if isinstance(viewPy, EventBoardsMaintenance):
            self.__maintenance = viewPy
            viewPy.onRefresh += self.onRefresh

    def _invalidate(self, *args, **kwargs):
        super(MissionsEventBoardsView, self)._invalidate(*args, **kwargs)
        if self.__tableView is not None:
            self.__tableView.destroy()
        return

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_MARATHONS

    def _setMaintenance(self, visible):
        headerText = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON) + _ms(EVENT_BOARDS.MAINTENANCE_TITLE)
        bodyText = _ms(EVENT_BOARDS.MAINTENANCE_BODY)
        buttonText = _ms(EVENT_BOARDS.MAINTENANCE_UPDATE)
        self.as_setMaintenanceS(visible, headerText, bodyText, buttonText)

    @checkEventExist
    def __onFilterApply(self, eventID, leaderboardsID):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE, ctx={'eventID': eventID,
         'leaderboardID': int(leaderboardsID)}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onViewLoaded(self, view, *args, **kwargs):
        if view.settings.alias == EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_ALIAS:
            eventID = view.eventID
            if eventID is not None:
                eventData = self.__eventsData.getEvent(eventID)
                if eventData is not None:
                    view.setData(eventData, partial(self.__onFilterApply, eventID))
                else:
                    view.destroy()
                    self._setMaintenance(True)
        elif view.settings.alias == EVENTBOARDS_ALIASES.RESULT_FILTER_POPOVER_VEHICLES_ALIAS:
            view.setOpener(self)
        elif view.settings.alias == VIEW_ALIAS.LOBBY_EVENT_BOARDS_TABLE:
            self.__tableView = view
            view.onDisposed += self.__tableViewDisposed
        return

    def __tableViewDisposed(self, view):
        self.as_setPlayFadeInTweenEnabledS(False)
        view.onDisposed -= self.__tableViewDisposed
        self.__tableView = None
        hideMissionDetails()
        self._onEventsUpdate()
        return

    def __openDetailsContainer(self, viewAlias, ctx=None):
        g_eventBus.handleEvent(events.LoadViewEvent(viewAlias, ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)


class MissionsCategoriesView(_GroupedMissionsView):
    """ Missions tab for quests that don't fall within the marathon criteria.
    """

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_CATEGORIES

    def _getViewQuestFilter(self):
        return lambda q: not isMarathon(q.getGroupID())


class CurrentVehicleMissionsView(CurrentVehicleMissionsViewMeta):
    """ Missions tab for all quests from the other tabs that can be completed on the current vihicle.
    """

    def setBuilder(self, builder, filters):
        super(CurrentVehicleMissionsView, self).setBuilder(builder, filters)
        self._builder.onBlocksDataChanged += self.__onBlocksDataChanged

    @staticmethod
    def _getBackground():
        return RES_ICONS.MAPS_ICONS_MISSIONS_BACKGROUNDS_CURRENTVEHICLE

    def _dispose(self):
        self._builder.onBlocksDataChanged -= self.__onBlocksDataChanged
        super(CurrentVehicleMissionsView, self)._dispose()

    def __onBlocksDataChanged(self):
        self._builder.invalidateBlocks()
        self._filterMissions()
        self._onDataChangedNotify()
