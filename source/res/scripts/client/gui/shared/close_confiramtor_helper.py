# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/close_confiramtor_helper.py
import adisp
from collections import namedtuple
from gui.game_control.links import URLMacros
from wg_async import wg_async, wg_await
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
RestrictedEvent = namedtuple('RestrictedEvent', ('name', 'scope'))

class CloseConfirmatorsHelper(object):
    __slots__ = ('__closeConfirmator', '_restrictedUrls', '_restrictedEvents', '_restrictedSfViews', '_restrictedGuiImplViews')
    _lobbyContext = dependency.descriptor(ILobbyContext)
    ADD_HEADER_NAV_CONFIRMATOR = True

    def __init__(self):
        self.__closeConfirmator = None
        self._restrictedUrls = set()
        self._restrictedEvents = self.getRestrictedEvents()
        self._restrictedSfViews = self.getRestrictedSfViews()
        self._restrictedGuiImplViews = self.getRestrictedGuiImplViews()
        self.__parseRestrictedUrls()
        return

    def getRestrictedEvents(self):
        return [RestrictedEvent(events.ViewEventType.LOAD_VIEW, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.ViewEventType.LOAD_GUI_IMPL_VIEW, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.RallyWindowEvent.ON_CLOSE, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.PrbInvitesEvent.ACCEPT, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.PrbActionEvent.SELECT, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.PrbActionEvent.LEAVE, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.TrainingEvent.RETURN_TO_TRAINING_ROOM, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.TrainingEvent.SHOW_TRAINING_LIST, EVENT_BUS_SCOPE.LOBBY),
         RestrictedEvent(events.CustomizationEvent.SHOW, EVENT_BUS_SCOPE.LOBBY)]

    def getRestrictedSfViews(self):
        return [VIEW_ALIAS.VEHICLE_COMPARE,
         VIEW_ALIAS.LOBBY_STORE,
         VIEW_ALIAS.LOBBY_PROFILE,
         VIEW_ALIAS.LOBBY_BARRACKS,
         VIEW_ALIAS.LOBBY_MISSIONS,
         VIEW_ALIAS.LOBBY_RESEARCH,
         VIEW_ALIAS.WIKI_VIEW,
         VIEW_ALIAS.BROWSER_VIEW,
         VIEW_ALIAS.VEHICLE_PREVIEW]

    def getRestrictedGuiImplViews(self):
        return [R.views.lobby.dog_tags.DogTagsView()]

    def getRestrictedUrls(self):
        return []

    def start(self, closeConfirmator):
        self.__closeConfirmator = closeConfirmator
        if self.ADD_HEADER_NAV_CONFIRMATOR:
            self._lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        for event, scope in self._restrictedEvents:
            g_eventBus.addRestriction(event, self.__confirmEvent, scope=scope)

    def stop(self):
        self.__closeConfirmator = None
        if self.ADD_HEADER_NAV_CONFIRMATOR:
            self._lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        for event, scope in self.getRestrictedEvents():
            g_eventBus.removeRestriction(event, self.__confirmEvent, scope=scope)

        return

    def _addPlatoonCreationConfirmator(self):
        self._lobbyContext.addPlatoonCreationConfirmator(self.__confirmPlatoonCreation)

    def _deletePlatoonCreationConfirmator(self):
        self._lobbyContext.deletePlatoonCreationConfirmator(self.__confirmPlatoonCreation)

    @adisp.adisp_async
    @wg_async
    def __confirmEvent(self, event, callback):
        if event.eventType == events.ViewEventType.LOAD_VIEW:
            if event.alias not in self._restrictedSfViews:
                callback(True)
                return
        if event.eventType == events.ViewEventType.LOAD_GUI_IMPL_VIEW:
            if event.alias not in self._restrictedGuiImplViews:
                callback(True)
                return
        if event.eventType == events.PrbActionEvent.LEAVE:
            if isinstance(event.action, LeavePrbAction):
                if event.action.ignoreConfirmation:
                    callback(True)
                    return
        if event.eventType == events.BrowserEvent.BROWSER_CREATED:
            if event.ctx.get('url') not in self._restrictedUrls:
                callback(True)
                return
        result = yield wg_await(self.__closeConfirmator())
        callback(result)

    @adisp.adisp_process
    def __parseRestrictedUrls(self):
        for url in self.getRestrictedUrls():
            parsedUrl = yield URLMacros().parse(url)
            self._restrictedUrls.add(parsedUrl)

    @adisp.adisp_async
    @wg_async
    def __confirmHeaderNavigation(self, callback):
        result = yield wg_await(self.__closeConfirmator())
        callback(result)

    @adisp.adisp_async
    @wg_async
    def __confirmPlatoonCreation(self, callback):
        result = yield wg_await(self.__closeConfirmator())
        callback(result)
