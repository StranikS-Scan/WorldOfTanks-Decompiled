# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/CompanyListView.py
import BigWorld
from adisp import process
from shared_utils import safeCancelCallback
from constants import PREBATTLE_TYPE
from gui.prb_control.prb_helpers import PrbListener
from gui.shared import events, EVENT_BUS_SCOPE, rq_cooldown
from gui.Scaleform.daapi.view.lobby.prb_windows import companies_dps
from gui.Scaleform.daapi.view.meta.CompanyListMeta import CompanyListMeta
from gui.prb_control.context import prb_ctx
from gui.prb_control.settings import REQUEST_TYPE
from messenger.ext import channel_num_gen
from messenger.gui.Scaleform.view.lobby import MESSENGER_VIEW_ALIAS
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter

class CompanyListView(CompanyListMeta, PrbListener):

    def __init__(self):
        super(CompanyListView, self).__init__(self.proto.messages.getCompanyRoomName())
        self.__listDP = None
        self.__proxy = None
        self.__bwListCB = None
        return

    @proto_getter(PROTO_TYPE.MIGRATION)
    def proto(self):
        return None

    def setProxy(self, parent):
        self.__proxy = parent

    def getDivisionsList(self):
        return companies_dps.getDivisionsList()

    @process
    def createCompany(self):
        yield self.prbDispatcher.create(prb_ctx.CompanySettingsCtx(waitingID='prebattle/create'))

    @process
    def joinCompany(self, prbID):
        yield self.prbDispatcher.join(prb_ctx.JoinCompanyCtx(prbID, waitingID='prebattle/join'))

    def refreshCompaniesList(self, owner, isNotInBattle, division):
        self.__requestCompaniesList(isNotInBattle, division, owner)

    def requestPlayersList(self, prbID):
        self.__requestRoster(prbID)

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return channel_num_gen.getClientID4LazyChannel(self.proto.messages.getCompanyRoomName())

    def onPrbListReceived(self, prebattles):
        self.__proxy.as_hideWaitingS()
        if self.__listDP is not None:
            self.__listDP.buildList(prebattles)
            self.__listDP.refresh()
        return

    def onPrbRosterReceived(self, prbID, roster):
        if self.__listDP is not None:
            idx = self.__listDP.setPlayers(prbID, roster)
            self.__listDP.refresh()
            self.as_showPlayersListS(idx)
        return

    def _populate(self):
        super(CompanyListView, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__listDP = companies_dps.CompaniesDataProvider()
        self.__listDP.setFlashObject(self.as_getSearchDPS())
        self.startPrbListening()
        self.as_setDefaultFilterS('', False, 0)
        self.__requestCompaniesList()

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopPrbListening()
        if self.__listDP is not None:
            self.__listDP._dispose()
            self.__listDP = None
        self.__proxy = None
        self.__clearCallback()
        super(CompanyListView, self)._dispose()
        return

    def __requestCompaniesList(self, isNotInBattle=False, division=0, owner=''):
        ctx = prb_ctx.RequestCompaniesCtx(isNotInBattle, division, owner)

        @process
        def _rq():
            self.__clearCallback()
            yield self.prbDispatcher.sendPrbRequest(ctx)

        rqID = (rq_cooldown.REQUEST_SCOPE.PRB_CONTROL, ctx.getRequestType())
        if rq_cooldown.isRequestInCoolDown(*rqID):
            self.__bwListCB = BigWorld.callback(rq_cooldown.getRequestCoolDown(*rqID), _rq)
        else:
            _rq()

    @process
    def __requestRoster(self, prbID):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.GetPrbRosterCtx(prbID, PREBATTLE_TYPE.COMPANY))

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.PREBATTLES_LIST:
            self.as_setRefreshCoolDownS(event.coolDown)

    def __clearCallback(self):
        if self.__bwListCB is not None:
            safeCancelCallback(self.__bwListCB)
            self.__bwListCB = None
        return
