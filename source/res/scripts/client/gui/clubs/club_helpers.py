# Embedded file name: scripts/client/gui/clubs/club_helpers.py
import BigWorld
from adisp import process
from constants import PREBATTLE_TYPE
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.clubs import interfaces
from gui.clubs.contexts import GetClubsCtx, JoinClubBattleCtx
from gui.clubs.items import ClubListItem
from gui.clubs.settings import OTHER_CLUB_SUBSCRIPTION, MY_CLUB_SUBSCRIPTION, CLIENT_CLUB_STATE as _CCS
from gui.shared.utils.ListPaginator import ListPaginator

def isClubsEnabled():
    return g_lobbyContext.getServerSettings().isClubsEnabled()


def getClientClubsMgr():
    return getattr(BigWorld.player(), 'clubs', None)


def isSeasonInProgress():
    clubsMgr = getClientClubsMgr()
    return hasattr(clubsMgr, 'isSeasonInProgress') and clubsMgr.isSeasonInProgress()


def getClubUnit(clubDBID):
    clubsMgr = getClientClubsMgr()
    return hasattr(clubsMgr, 'getClubUnit') and clubsMgr.getClubUnit(clubDBID)


def isRelatedToClubs():
    clubsMgr = getClientClubsMgr()
    return hasattr(clubsMgr, 'isRelatedToClubs') and clubsMgr.isRelatedToClubs()


class ClubListener(interfaces.IClubListener):

    @property
    def clubsCtrl(self):
        from gui.clubs.ClubsController import g_clubsCtrl
        return g_clubsCtrl

    @property
    def clubsState(self):
        return self.clubsCtrl.getState()

    def startClubListening(self, clubDbID = None, subscriptionType = OTHER_CLUB_SUBSCRIPTION):
        self.clubsCtrl.addListener(self)
        if clubDbID is not None:
            self.clubsCtrl.addClubListener(clubDbID, self, subscriptionType)
        return

    def stopClubListening(self, clubDbID = None):
        if clubDbID is not None:
            self.clubsCtrl.removeClubListener(clubDbID, self)
        self.clubsCtrl.removeListener(self)
        return

    def _onClubsStateChanged(self, state):
        self.onAccountClubStateChanged(state)


class MyClubListener(ClubListener):

    def __init__(self):
        self.__listedClubDbID = None
        return

    def getClub(self):
        if self.__listedClubDbID is not None:
            return self.clubsCtrl.getClub(self.__listedClubDbID)
        else:
            return

    def startMyClubListening(self, forceResync = False):
        self.clubsCtrl.addListener(self, forceResync=forceResync)
        self._onClubsStateChanged(self.clubsCtrl.getState())

    def stopMyClubListening(self):
        if self.__listedClubDbID is not None:
            self.clubsCtrl.removeClubListener(self.__listedClubDbID, self)
        self.clubsCtrl.removeListener(self)
        return

    def _onClubsStateChanged(self, state):
        if state.getStateID() in (_CCS.HAS_CLUB, _CCS.SENT_APP):
            self.__listedClubDbID = state.getClubDbID()
            self.clubsCtrl.addClubListener(self.__listedClubDbID, self, MY_CLUB_SUBSCRIPTION)
        elif self.__listedClubDbID is not None:
            self.clubsCtrl.removeClubListener(self.__listedClubDbID, self)
            self.__listedClubDbID = None
        self.onAccountClubStateChanged(state)
        return


class ClubListPaginator(ListPaginator):

    @process
    def _request(self):
        result = yield self._requester.sendRequest(GetClubsCtx(self._offset, self._count, onlyOpened=True, waitingID='clubs/club/list'), allowDelay=True)
        if result.isSuccess():
            self.onListUpdated(self._selectedID, True, True, map(ClubListItem.build, reversed(result.data or [])))


@process
def tryToConnectClubBattle(club, joinTime):
    from gui import DialogsInterface, SystemMessages
    from gui.prb_control.dispatcher import g_prbLoader
    from gui.Scaleform.daapi.view.dialogs.rally_dialog_meta import UnitConfirmDialogMeta
    yield lambda callback: callback(None)
    if not club:
        LOG_ERROR('Invalid club info to join unit', club, joinTime)
        return
    clubDbID = club.getClubDbID()
    if club.hasActiveUnit():
        peripheryID = club.getUnitInfo().peripheryID
        if g_lobbyContext.isAnotherPeriphery(peripheryID):
            if g_lobbyContext.isPeripheryAvailable(peripheryID):
                result = yield DialogsInterface.showDialog(UnitConfirmDialogMeta(PREBATTLE_TYPE.CLUBS, 'changePeriphery', messageCtx={'host': g_lobbyContext.getPeripheryName(peripheryID)}))
                if result:
                    g_prbLoader.getPeripheriesHandler().join(peripheryID, JoinClubBattleCtx(clubDbID, joinTime, allowDelay=True, waitingID='clubs/joinClubUnit'))
            else:
                SystemMessages.pushI18nMessage('#system_messages:periphery/errors/isNotAvailable', type=SystemMessages.SM_TYPE.Error)
            return
    yield g_prbLoader.getDispatcher().join(JoinClubBattleCtx(clubDbID, joinTime, waitingID='clubs/joinClubUnit'))
