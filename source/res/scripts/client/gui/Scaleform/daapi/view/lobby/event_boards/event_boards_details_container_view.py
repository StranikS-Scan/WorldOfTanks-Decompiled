# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_boards/event_boards_details_container_view.py
from gui.shared import events, event_bus_handlers, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.EventBoardsDetailsContainerViewMeta import EventBoardsDetailsContainerViewMeta
from gui.Scaleform.genConsts.EVENTBOARDS_ALIASES import EVENTBOARDS_ALIASES
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.event_boards_controllers import IEventBoardController

class EventBoardsDetailsContainerView(EventBoardsDetailsContainerViewMeta):
    eventsController = dependency.descriptor(IEventBoardController)
    __metaclass__ = event_bus_handlers.EventBusListener
    _linkage = None
    _extra = {}

    def __init__(self, ctx=None):
        super(EventBoardsDetailsContainerView, self).__init__()
        self.ctx = ctx
        eventID = ctx.get('eventID')
        self.eventData = self.eventsController.getEventsSettingsData().getEvent(eventID)

    def closeView(self):
        self.destroy()

    def _populate(self):
        super(EventBoardsDetailsContainerView, self)._populate()
        data = {'linkage': self._linkage,
         'title': text_styles.superPromoTitle(self.eventData.getName())}
        data.update(self._extra)
        self.as_setInitDataS(data)

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(EventBoardsDetailsContainerView, self)._onRegisterFlashComponent(viewPy, alias)
        viewPy.setOpener(self)

    @event_bus_handlers.eventBusHandler(events.HideWindowEvent.HIDE_MISSION_DETAILS_VIEW, EVENT_BUS_SCOPE.LOBBY)
    def __handleDetailsClose(self, _):
        """ We may need to close details externally when it already open.
        """
        self.destroy()


class EventBoardsDetailsBrowserView(EventBoardsDetailsContainerView):
    _linkage = EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BROWSER_LINKAGE


class EventBoardsDetailsVehiclesView(EventBoardsDetailsContainerView):
    _linkage = EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_VEHICLES_LINKAGE


class EventBoardsDetailsAwardsView(EventBoardsDetailsContainerView):
    _linkage = EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_AWARDS_LINKAGE
    _extra = {'bgWidth': 753,
     'bgHeight': 509}


class EventBoardsDetailsBattleView(EventBoardsDetailsContainerView):
    _linkage = EVENTBOARDS_ALIASES.EVENTBOARDS_DETAILS_BATTLE_LINKAGE
    _extra = {'bgWidth': 753,
     'bgHeight': 549}
