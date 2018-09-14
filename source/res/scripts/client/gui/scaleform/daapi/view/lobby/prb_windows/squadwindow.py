# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadWindow.py
from constants import PREBATTLE_TYPE
from gui.prb_control.settings import FUNCTIONAL_FLAG
from gui.Scaleform.daapi.view.meta.SquadWindowMeta import SquadWindowMeta
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.prb_control.context import unit_ctx
from gui.prb_control.formatters import messages
from gui.shared import events, EVENT_BUS_SCOPE
from gui.prb_control import settings

@stored_window(DATA_TYPE.UNIQUE_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class SquadWindow(SquadWindowMeta):

    def __init__(self, ctx = None):
        super(SquadWindow, self).__init__()
        self._isInvitesOpen = ctx.get('isInvitesOpen', False)

    def getPrbType(self):
        return PREBATTLE_TYPE.SQUAD

    def onWindowClose(self):
        self.prbDispatcher.doLeaveAction(unit_ctx.LeaveUnitCtx(waitingID='prebattle/leave', flags=FUNCTIONAL_FLAG.UNDEFINED))

    def onWindowMinimize(self):
        self.destroy()

    @property
    def squadViewComponent(self):
        return self.components.get(PREBATTLE_ALIASES.SQUAD_VIEW_PY)

    def onUnitFlagsChanged(self, flags, timeLeft):
        self.as_enableWndCloseBtnS(not self.unitFunctional.getFlags().isInQueue())

    def onUnitPlayerOnlineStatusChanged(self, pInfo):
        if pInfo.isOffline():
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_OFFLINE
        else:
            key = settings.UNIT_NOTIFICATION_KEY.PLAYER_ONLINE
        self.__addPlayerNotification(key, pInfo)

    def onUnitPlayerAdded(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_ADDED, pInfo)

    def onUnitPlayerRemoved(self, pInfo):
        if not pInfo.isInvite():
            self.__addPlayerNotification(settings.UNIT_NOTIFICATION_KEY.PLAYER_REMOVED, pInfo)

    def onUnitPlayerBecomeCreator(self, pInfo):
        if pInfo.isCurrentPlayer():
            self._showLeadershipNotification()
        chat = self.chat
        if chat:
            chat.as_addMessageS(messages.getUnitPlayerNotification(settings.UNIT_NOTIFICATION_KEY.GIVE_LEADERSHIP, pInfo))

    def _populate(self):
        super(SquadWindow, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.HideWindowEvent.HIDE_UNIT_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        super(SquadWindow, self)._dispose()

    def _showLeadershipNotification(self):
        pass

    def __handleSquadWindowHide(self, _):
        self.destroy()

    def __addPlayerNotification(self, key, pInfo):
        chat = self.chat
        if chat and not pInfo.isCurrentPlayer():
            chat.as_addMessageS(messages.getUnitPlayerNotification(key, pInfo))
