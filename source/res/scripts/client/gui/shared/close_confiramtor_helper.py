# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/close_confiramtor_helper.py
import adisp
from async import async, await
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.prb_control.entities.base.ctx import LeavePrbAction

class CloseConfirmatorsHelper(object):
    __slots__ = ('__closeConfirmator',)
    _lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__closeConfirmator = None
        return

    def getRestrictedEvents(self):
        return [events.ViewEventType.LOAD_VIEW,
         events.ViewEventType.LOAD_GUI_IMPL_VIEW,
         events.ReferralProgramEvent.SHOW_REFERRAL_PROGRAM_WINDOW,
         events.RallyWindowEvent.ON_CLOSE,
         events.PrbInvitesEvent.ACCEPT,
         events.PrbActionEvent.SELECT,
         events.PrbActionEvent.LEAVE,
         events.TrainingEvent.RETURN_TO_TRAINING_ROOM,
         events.TrainingEvent.SHOW_TRAINING_LIST,
         events.CustomizationEvent.SHOW]

    def getRestrictedSfViews(self):
        return [VIEW_ALIAS.VEHICLE_COMPARE,
         VIEW_ALIAS.LOBBY_STORE,
         VIEW_ALIAS.LOBBY_PROFILE,
         VIEW_ALIAS.LOBBY_BARRACKS,
         VIEW_ALIAS.LOBBY_MISSIONS,
         VIEW_ALIAS.LOBBY_RESEARCH,
         VIEW_ALIAS.WIKI_VIEW,
         VIEW_ALIAS.BROWSER_VIEW,
         VIEW_ALIAS.VEHICLE_PREVIEW,
         VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW]

    def getRestrictedGuiImplViews(self):
        return [R.views.lobby.dog_tags.DogTagsView(), R.views.lobby.detachment.PersonalCase()]

    def start(self, closeConfirmator):
        self.__closeConfirmator = closeConfirmator
        self._lobbyContext.addHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        for event in self.getRestrictedEvents():
            g_eventBus.addRestriction(event, self.__confirmEvent, scope=EVENT_BUS_SCOPE.LOBBY)

    def stop(self):
        self.__closeConfirmator = None
        self._lobbyContext.deleteHeaderNavigationConfirmator(self.__confirmHeaderNavigation)
        for event in self.getRestrictedEvents():
            g_eventBus.removeRestriction(event, self.__confirmEvent, scope=EVENT_BUS_SCOPE.LOBBY)

        return

    @adisp.async
    @async
    def __confirmEvent(self, event, callback):
        if event.eventType == events.ViewEventType.LOAD_VIEW:
            if event.alias not in self.getRestrictedSfViews():
                callback(True)
                return
        if event.eventType == events.ViewEventType.LOAD_GUI_IMPL_VIEW:
            if event.alias not in self.getRestrictedGuiImplViews():
                callback(True)
                return
        if event.eventType == events.PrbActionEvent.LEAVE:
            if isinstance(event.action, LeavePrbAction):
                if event.action.ignoreConfirmation:
                    callback(True)
                    return
        result = yield await(self.__closeConfirmator())
        callback(result)

    @adisp.async
    @async
    def __confirmHeaderNavigation(self, callback):
        result = yield await(self.__closeConfirmator())
        callback(result)
