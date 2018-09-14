# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportClubsListView.py
import BigWorld
from adisp import process
from constants import PREBATTLE_TYPE
from gui.Scaleform.daapi.view.lobby.rally.rally_dps import ClubsDataProvider
from gui.Scaleform.daapi.view.meta.CyberSportUnitsListMeta import CyberSportUnitsListMeta
from gui.Scaleform.genConsts.CYBER_SPORT_ALIASES import CYBER_SPORT_ALIASES
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clubs.club_helpers import ClubListener
from gui.clubs import events_dispatcher as club_events
from gui.clubs.contexts import GetClubCtx
from gui.clubs.items import Club
from gui.clubs.settings import CLUB_REQUEST_TYPE, CLIENT_CLUB_STATE
from gui.prb_control.functional import unit_ext
from gui.Scaleform.framework import AppRef
from gui.prb_control.prb_helpers import UnitListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.view_helpers import ClubEmblemsHelper
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

class CyberSportClubsListView(CyberSportUnitsListMeta, UnitListener, ClubListener, ClubEmblemsHelper, AppRef):

    def __init__(self):
        super(CyberSportClubsListView, self).__init__()
        self._isBackButtonClicked = False
        self._navigationCooldown = None
        self.__paginator = self.unitFunctional.getClubsPaginator()
        return

    def onUnitFunctionalInited(self):
        self.unitFunctional.setPrbType(PREBATTLE_TYPE.CLUBS)

    def getPyDataProvider(self):
        return ClubsDataProvider()

    def getCoolDownRequests(self):
        return [CLUB_REQUEST_TYPE.GET_CLUBS]

    def canBeClosed(self, callback):
        self._isBackButtonClicked = True
        callback(True)

    def loadPrevious(self):
        self.__paginator.right()

    def loadNext(self):
        self.__paginator.left()

    def refreshTeams(self):
        self.__paginator.refresh()

    def getRallyDetails(self, index):
        self.__getDetails(index)

    def showRallyProfile(self, clubDBID):
        club_events.showClubProfile(clubDBID)

    def onClubEmblem64x64Received(self, clubDbID, emblem):
        vo = self._searchDP.collection[self._searchDP.selectedRallyIndex]
        selectedClubDBID = vo['cfdUnitID']
        if emblem and clubDbID == selectedClubDBID:
            self.as_updateRallyIconS(self.getMemoryTexturePath(emblem))

    def onAccountClubStateChanged(self, state):
        self.__refreshDetails(self._searchDP.selectedRallyIndex)
        self._setCreateButtonData()

    def onAccountClubRestrictionsChanged(self):
        self.__refreshDetails(self._searchDP.selectedRallyIndex)
        self._setCreateButtonData()

    def onClubCreated(self, clubDBID):
        club_events.showClubProfile(clubDBID)

    def onClubUpdated(self, club):
        self.__refreshDetails(self._searchDP.selectedRallyIndex)
        self._setCreateButtonData()

    def _populate(self):
        super(CyberSportClubsListView, self)._populate()
        self.startUnitListening()
        self.startClubListening()
        if self.unitFunctional.getPrbType() != PREBATTLE_TYPE.NONE:
            self.unitFunctional.setPrbType(PREBATTLE_TYPE.CLUBS)
        self.__paginator.onListUpdated += self.__onClubsListUpdated
        self.__paginator.reset()
        self.as_setSearchResultTextS(_ms(CYBERSPORT.WINDOW_CLUBSLISTVIEW_FOUNDTEAMS), _ms(CYBERSPORT.WINDOW_CLUBSLISTVIEW_FOUNDTEAMSDESCRIPTION), None)
        self.addListener(events.CoolDownEvent.CLUB, self._handleSetClubCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self._checkCoolDowns()
        self._setCreateButtonData()
        return

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.CLUB, self._handleSetClubCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__paginator is not None:
            self.__paginator.onListUpdated -= self.__onClubsListUpdated
            self.__paginator = None
        self.stopClubListening()
        self.stopUnitListening()
        if self._isBackButtonClicked:
            unit_ext.destroyListReq()
            self._isBackButtonClicked = False
        self._cancelNavigationCooldown()
        super(CyberSportClubsListView, self)._dispose()
        return

    def _onUserActionReceived(self, _, user):
        self.__updateView(user)

    def __setDetails(self, index, vo):
        linkage = CYBER_SPORT_ALIASES.COMMNAD_DETAILS_LINKAGE_JOIN_TO_STATIC
        self.as_setDetailsS({'viewLinkage': linkage,
         'data': vo})

    def __refreshDetails(self, idx):
        self.__getDetails(idx)

    def __updateView(self, user):
        self._searchDP.updateListItem(user.getID())
        self.__refreshDetails(self._searchDP.selectedRallyIndex)

    def __onClubsListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        if isFullUpdate:
            selectedIdx = self._searchDP.rebuildList(selectedID, result)
            self.__setNavigationData(isReqInCoolDown)
        else:
            selectedIdx = self._searchDP.updateList(selectedID, result)
        if selectedIdx is not None:
            self.as_selectByIndexS(selectedIdx)
        return

    @process
    def __getDetails(self, index):
        data = None
        yield lambda callback: callback(None)
        if index >= 0:
            vo = self._searchDP.collection[index]
            cfdUnitID = vo['cfdUnitID']
            result = yield self.clubsCtrl.sendRequest(GetClubCtx(cfdUnitID, waitingID='clubs/club/get'), allowDelay=True)
            if self.isDisposed():
                return
            if result.isSuccess():
                self._searchDP.selectedRallyIndex = index
                self.unitFunctional.getClubsPaginator().setSelectedID(cfdUnitID)
                club = Club(cfdUnitID, result.data)
                data = self._searchDP.getVO(club, self.clubsState, self.clubsCtrl.getProfile())
                self.requestClubEmblem64x64(cfdUnitID, club.getEmblem64x64())
            else:
                self._searchDP.selectedRallyIndex = -1
                self.unitFunctional.getClubsPaginator().setSelectedID(None)
        self.__setDetails(index, data)
        return

    def _handleSetClubCoolDown(self, event):
        if event.requestID in self.getCoolDownRequests() and event.coolDown > 0:
            self._setCoolDowns(event.coolDown, event.requestID)

    def _checkCoolDowns(self):
        for requestID in self.getCoolDownRequests():
            coolDown = self.clubsCtrl.getRequestCtrl().getCooldownTime(requestID)
            if coolDown > 0:
                self._setCoolDowns(coolDown, requestID)

    def _setCoolDowns(self, cooldown, requestID):
        self.as_setCoolDownS(cooldown, requestID)
        self.__setNavigationData(True)
        self._navigationCooldown = BigWorld.callback(cooldown, self._navigationCooldownCallback)

    def _navigationCooldownCallback(self):
        self._cancelNavigationCooldown()
        self.__setNavigationData()

    def _cancelNavigationCooldown(self):
        if self._navigationCooldown is not None:
            BigWorld.cancelCallback(self._navigationCooldown)
            self._navigationCooldown = None
        return

    def __setNavigationData(self, isCooldown = False):
        navigationData = {'previousVisible': True,
         'previousEnabled': not isCooldown,
         'nextVisible': True,
         'nextEnabled': not isCooldown,
         'icon': RES_ICONS.MAPS_ICONS_STATISTIC_RATING24}
        self.as_updateNavigationBlockS(navigationData)

    def _setCreateButtonData(self):
        headerDescription = CYBERSPORT.WINDOW_CLUBSLISTVIEW_DESCRIPTION
        headerTitle = CYBERSPORT.WINDOW_CLUBSLISTVIEW_TITLE
        createBtnTooltip = ''
        createBtnEnabled = True
        if self.clubsState.getStateID() == CLIENT_CLUB_STATE.HAS_CLUB:
            createBtnEnabled = False
            createBtnTooltip = TOOLTIPS.CYBERSPORT_UNITLIST_CREATEBTN_ALREADYINRALLY
            ownClub = self.clubsCtrl.getClub(self.clubsState.getClubDbID())
            if ownClub is not None and ownClub.getPermissions().isOwner():
                createBtnTooltip = TOOLTIPS.CYBERSPORT_UNITLIST_CREATEBTN_ALREADYRALLYOWNER
        self.as_setHeaderS({'title': headerTitle,
         'description': headerDescription,
         'createBtnLabel': CYBERSPORT.WINDOW_CLUBSLISTVIEW_CREATE_BTN,
         'createBtnTooltip': createBtnTooltip,
         'createBtnEnabled': createBtnEnabled})
        return
