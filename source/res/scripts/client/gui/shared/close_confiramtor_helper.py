# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/close_confiramtor_helper.py
import adisp
from wg_async import wg_async, wg_await
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import LeavePrbAction
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

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
         events.CustomizationEvent.SHOW,
         events.LobbySimpleEvent.SWITCH_NEW_YEAR_VIEW,
         events.LobbySimpleEvent.SHOW_LOOT_BOX_VIEW]

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

    def _addPlatoonCreationConfirmator(self):
        self._lobbyContext.addPlatoonCreationConfirmator(self.__confirmPlatoonCreation)

    def _deletePlatoonCreationConfirmator(self):
        self._lobbyContext.deletePlatoonCreationConfirmator(self.__confirmPlatoonCreation)

    @adisp.adisp_async
    @wg_async
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
        result = yield wg_await(self.__closeConfirmator())
        callback(result)

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
