# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/CompaniesWindow.py
from adisp import process
from gui.Scaleform.daapi.view.lobby.prb_windows import companies_dps
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattlesListWindow import PrebattlesListWindow
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control.functional.default import PrbRosterRequester
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from gui.prb_control.context import prb_ctx
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.CompaniesWindowMeta import CompaniesWindowMeta
from gui.shared.events import FocusEvent
from messenger.ext import channel_num_gen
from messenger.gui.Scaleform.view import MESSENGER_VIEW_ALIAS
from messenger.m_constants import LAZY_CHANNEL

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class CompaniesWindow(PrebattlesListWindow, CompaniesWindowMeta):

    def __init__(self, ctx = None):
        super(CompaniesWindow, self).__init__(LAZY_CHANNEL.COMPANIES)
        self.__rosterRequester = PrbRosterRequester()
        self.__listDP = None
        return

    def getDivisionsList(self):
        return companies_dps.getDivisionsList()

    @process
    def createCompany(self):
        yield self.prbDispatcher.create(prb_ctx.CompanySettingsCtx(waitingID='prebattle/create', flags=FUNCTIONAL_FLAG.SWITCH))

    @process
    def joinCompany(self, prbID):
        yield self.prbDispatcher.join(prb_ctx.JoinCompanyCtx(prbID, waitingID='prebattle/join', flags=FUNCTIONAL_FLAG.SWITCH))

    def refreshCompaniesList(self, owner, isNotInBattle, division):
        self.__getCompaniesList(isNotInBattle, division, owner)

    def requestPlayersList(self, prbID):
        self.__rosterRequester.request(prbID)

    def showFAQWindow(self):
        self.fireEvent(events.LoadViewEvent(MESSENGER_VIEW_ALIAS.FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.COMPANIES)

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.getClientID()}))

    def onPrbListReceived(self, prebattles):
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
        super(CompaniesWindow, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__listDP = companies_dps.CompaniesDataProvider()
        self.__listDP.setFlashObject(self.as_getCompaniesListDPS())
        self.as_disableCreateButtonS(False)
        self.startGlobalListening()
        self.__rosterRequester.start(self.__onRosterReceived)
        self.as_setDefaultFilterS('', False, 0)
        self.__getCompaniesList()

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopGlobalListening()
        self.__rosterRequester.stop()
        if self.__listDP is not None:
            self.__listDP._dispose()
            self.__listDP = None
        super(CompaniesWindow, self)._dispose()
        return

    @process
    def __getCompaniesList(self, isNotInBattle = False, division = 0, owner = ''):
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.RequestCompaniesCtx(isNotInBattle, division, owner))

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.PREBATTLES_LIST:
            self.as_setRefreshCoolDownS(event.coolDown)
