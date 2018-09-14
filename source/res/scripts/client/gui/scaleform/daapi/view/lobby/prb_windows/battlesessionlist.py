# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BattleSessionList.py
from adisp import process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattlesListWindow import PrebattlesListWindow
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control import formatters
from gui.prb_control.context import prb_ctx
from gui.prb_control.functional.battle_session import AutoInvitesRequester
from gui.Scaleform.daapi.view.meta.BattleSessionListMeta import BattleSessionListMeta
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import FocusEvent
from messenger.ext import channel_num_gen
from messenger.m_constants import LAZY_CHANNEL

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class BattleSessionList(PrebattlesListWindow, BattleSessionListMeta):

    def __init__(self, ctx = None):
        super(BattleSessionList, self).__init__(LAZY_CHANNEL.SPECIAL_BATTLES)
        self.__listRequester = AutoInvitesRequester()

    def requestToJoinTeam(self, prbID, prbType):
        item = self.__listRequester.getItem(prbID)
        if g_lobbyContext.isAnotherPeriphery(item.peripheryID):
            self.fireEvent(events.LoadViewEvent(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, ctx={'prbID': prbID}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__requestToJoin(prbID, prbType)

    def getClientID(self):
        return channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES)

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.getClientID()}))

    def _populate(self):
        super(BattleSessionList, self)._populate()
        self.__listRequester.start(self.__onBSListReceived)
        self.__listRequester.request()

    def _dispose(self):
        self.__listRequester.stop()
        super(BattleSessionList, self)._dispose()

    @process
    def __requestToJoin(self, prbID, prbType):
        yield self.prbDispatcher.join(prb_ctx.JoinBattleSessionCtx(prbID, prbType, 'prebattle/join'))

    def __onBSListReceived(self, sessions):
        result = []
        for bs in sessions:
            result.append({'prbID': bs.prbID,
             'prbType': bs.prbType,
             'descr': formatters.getPrebattleFullDescription(bs.description),
             'opponents': formatters.getPrebattleOpponentsString(bs.description),
             'startTime': formatters.getBattleSessionStartTimeString(bs.startTime)})

        self.as_refreshListS(result)
