# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/CompaniesWindow.py
from adisp import process
from gui.Scaleform.daapi.view.lobby.prb_windows import companies_dps
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattlesListWindow import PrebattlesListWindow
from gui.Scaleform.managers.windows_stored_data import DATA_TYPE, TARGET_ID
from gui.Scaleform.managers.windows_stored_data import stored_window
from gui.prb_control.functional.company import CompanyListRequester
from gui.prb_control.functional.default import PrbRosterRequester
from gui.prb_control.settings import REQUEST_TYPE
from gui.prb_control.context import prb_ctx
from gui.shared import events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.CompaniesWindowMeta import CompaniesWindowMeta
from messenger.ext import channel_num_gen
from messenger.m_constants import LAZY_CHANNEL

@stored_window(DATA_TYPE.CAROUSEL_WINDOW, TARGET_ID.CHANNEL_CAROUSEL)

class CompaniesWindow(PrebattlesListWindow, CompaniesWindowMeta):

    def __init__(self):
        super(CompaniesWindow, self).__init__(LAZY_CHANNEL.COMPANIES)
        self.__listRequester = CompanyListRequester()
        self.__rosterRequester = PrbRosterRequester()
        self.__listDP = None
        return

    def getDivisionsList(self):
        return companies_dps.getDivisionsList()

    @process
    def createCompany(self):
        yield self.prbDispatcher.create(prb_ctx.CompanySettingsCtx(waitingID='prebattle/create'))

    @process
    def joinCompany(self, prbID):
        yield self.prbDispatcher.join(prb_ctx.JoinCompanyCtx(prbID, waitingID='prebattle/join'))

    def refreshCompaniesList(self, owner, isNotInBattle, division):
        self.__listRequester.request(prb_ctx.RequestCompaniesCtx(isNotInBattle, division, owner))

    def requestPlayersList(self, prbID):
        self.__rosterRequester.request(prbID)

    def showFAQWindow(self):
        self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_FAQ_WINDOW), scope=EVENT_BUS_SCOPE.LOBBY)

    def getClientID(self):
        return channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.COMPANIES)

    def onPreQueueFunctionalInited(self):
        self.as_disableCreateButtonS(True)

    def onPreQueueFunctionalFinished(self):
        self.as_disableCreateButtonS(False)

    def onPrbFunctionalInited(self):
        self.as_disableCreateButtonS(True)

    def onPrbFunctionalFinished(self):
        self.as_disableCreateButtonS(False)

    def onIntroUnitFunctionalInited(self):
        self.as_disableCreateButtonS(True)

    def onIntroUnitFunctionalFinished(self):
        self.as_disableCreateButtonS(False)

    def onUnitFunctionalInited(self):
        self.as_disableCreateButtonS(True)

    def onUnitFunctionalFinished(self):
        self.as_disableCreateButtonS(False)

    def _populate(self):
        super(CompaniesWindow, self)._populate()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__listDP = companies_dps.CompaniesDataProvider()
        self.__listDP.setFlashObject(self.as_getCompaniesListDPS())
        self.as_disableCreateButtonS(self.prbDispatcher.hasModalEntity())
        self.startGlobalListening()
        self.__listRequester.start(self.__onCompaniesListReceived)
        self.__rosterRequester.start(self.__onRosterReceived)
        self.as_setDefaultFilterS('', False, 0)
        if not self.__listRequester.isInCooldown():
            self.__listRequester.request(prb_ctx.RequestCompaniesCtx(False, 0, ''))
        else:
            self.as_setRefreshCoolDownS(self.__listRequester.getCooldown())

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopGlobalListening()
        self.__listRequester.stop()
        self.__rosterRequester.stop()
        if self.__listDP is not None:
            self.__listDP._dispose()
            self.__listDP = None
        super(CompaniesWindow, self)._dispose()
        return

    def __onCompaniesListReceived(self, prebattles):
        if self.__listDP is not None:
            self.__listDP.buildList(prebattles)
            self.__listDP.refresh()
        return

    def __onRosterReceived(self, prbID, roster):
        if self.__listDP is not None:
            idx = self.__listDP.setPlayers(prbID, roster)
            self.__listDP.refresh()
            self.as_showPlayersListS(idx)
        return

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.PREBATTLES_LIST:
            self.as_setRefreshCoolDownS(event.coolDown)
