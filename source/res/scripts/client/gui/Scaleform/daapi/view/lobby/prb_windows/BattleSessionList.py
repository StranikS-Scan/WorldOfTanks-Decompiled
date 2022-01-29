# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/BattleSessionList.py
import typing
from adisp import process
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattlesListWindow import PrebattlesListWindow
from gui.Scaleform.daapi.view.meta.BattleSessionListMeta import BattleSessionListMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control import formatters
from gui.prb_control.entities.battle_session.legacy.ctx import JoinBattleSessionCtx
from gui.prb_control.entities.battle_session.legacy.requester import AutoInvitesRequester
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import FocusEvent
from gui.shared.utils.functions import getArenaShortName
from helpers import dependency
from messenger.ext import channel_num_gen
from messenger.m_constants import LAZY_CHANNEL
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from gui.prb_control.items.prb_seqs import AutoInviteItem

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)
class BattleSessionList(PrebattlesListWindow, BattleSessionListMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    __webCtrl = dependency.descriptor(IWebController)

    def __init__(self, ctx=None):
        super(BattleSessionList, self).__init__(LAZY_CHANNEL.SPECIAL_BATTLES)
        self.__listRequester = AutoInvitesRequester()

    def requestToJoinTeam(self, prbID, prbType):
        item = self.__listRequester.getItem(prbID)
        if self.lobbyContext.isAnotherPeriphery(item.peripheryID):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY), ctx={'prbID': prbID}), scope=EVENT_BUS_SCOPE.LOBBY)
        else:
            self.__requestToJoin(prbID, prbType)

    def getClientID(self):
        return channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES)

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.getClientID()}))

    def _populate(self):
        super(BattleSessionList, self)._populate()
        self.addListener(events.HideWindowEvent.HIDE_SPECIAL_BATTLE_WINDOW, self.__hideWindow, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__listRequester.start(self.__onBSListReceived)
        self.__listRequester.request()

    def _dispose(self):
        self.__listRequester.stop()
        self.removeListener(events.HideWindowEvent.HIDE_SPECIAL_BATTLE_WINDOW, self.__hideWindow, scope=EVENT_BUS_SCOPE.LOBBY)
        super(BattleSessionList, self)._dispose()

    def __hideWindow(self, _):
        self.destroy()

    @process
    def __requestToJoin(self, prbID, prbType):
        yield self.prbDispatcher.join(JoinBattleSessionCtx(prbID, prbType, 'prebattle/join'))

    def __onBSListReceived(self, sessions):
        result = []
        clanDBID = self.__webCtrl.getClanDbID()
        for bs in sessions:
            detachment, vehicleLvl, _ = formatters.getBattleSessionDetachment(bs.description, clanDBID)
            if bs.prbType == PREBATTLE_TYPE.CLAN:
                startTime = self.__getClanBattleStartTime(bs)
            else:
                startTime = formatters.getBattleSessionStartTimeString(bs.startTime)
            result.append({'prbID': bs.prbID,
             'prbType': bs.prbType,
             'descr': formatters.getPrebattleFullDescription(bs.description),
             'opponents': formatters.getPrebattleOpponentsString(bs.description),
             'startTime': startTime,
             'unitName': detachment,
             'vehicleLevel': vehicleLvl})

        self.as_refreshListS(result)

    def __getClanBattleStartTime(self, battleSession):
        arenaName = getArenaShortName(battleSession.arenaTypeID) or ''
        peripheryName = self.lobbyContext.getPeripheryName(battleSession.peripheryID, checkAnother=False, useShortName=True)
        if peripheryName is None:
            peripheryName = ''
        startTimeString = formatters.getShortPrebattleStartTimeString(battleSession.startTime)
        return backport.text(R.strings.prebattle.title.battleSession.clanBattle.startTime(), startTime=startTimeString, peripheryName=peripheryName, arenaName=arenaName)
