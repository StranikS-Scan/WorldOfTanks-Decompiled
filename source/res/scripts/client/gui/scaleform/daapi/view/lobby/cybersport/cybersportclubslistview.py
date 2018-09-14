# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/CyberSportClubsListView.py
import operator
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
from gui.prb_control.prb_helpers import UnitListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.view_helpers import ClubEmblemsHelper
from helpers.i18n import makeString as _ms
from gui.Scaleform.locale.RES_ICONS import RES_ICONS

def _createHeader(label, buttonWidth, iconSource = None):
    return {'label': label,
     'buttonWidth': buttonWidth,
     'iconSource': iconSource,
     'enabled': False}


def _getColumnHeaders(isSearch):
    if isSearch:
        nameColumn = 'clubName'
    else:
        nameColumn = 'captain'
    return [_createHeader('', 54, RES_ICONS.MAPS_ICONS_LIBRARY_CYBERSPORT_LADDERICON),
     _createHeader('', 58, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
     _createHeader('#cybersport:window/unit/unitListView/%s' % nameColumn, 152),
     _createHeader(CYBERSPORT.WINDOW_UNIT_UNITLISTVIEW_DESCRIPTION, 220),
     _createHeader(CYBERSPORT.WINDOW_UNIT_UNITLISTVIEW_PLAYERS, 76)]


class CyberSportClubsListView(CyberSportUnitsListMeta, UnitListener, ClubListener, ClubEmblemsHelper):

    def __init__(self):
        super(CyberSportClubsListView, self).__init__()
        self._isBackButtonClicked = False
        self._navigationCooldown = None
        self._isInSearchMode = False
        self.__paginator = self._getPaginator()
        return

    def onUnitFunctionalInited(self):
        self.unitFunctional.setEntityType(PREBATTLE_TYPE.CLUBS)

    def getPyDataProvider(self):
        return ClubsDataProvider()

    def getCoolDownRequests(self):
        return [CLUB_REQUEST_TYPE.GET_CLUBS, CLUB_REQUEST_TYPE.FIND_CLUBS]

    def canBeClosed(self, callback):
        self._isBackButtonClicked = True
        callback(True)

    def loadPrevious(self):
        self.__paginator.right()

    def loadNext(self):
        self.__paginator.left()

    def refreshTeams(self):
        self.__paginator.refresh()

    def searchTeams(self, name):
        if name:
            self._isInSearchMode = True
            self._searchDP.useClubName()
            self.__paginator = self._getPaginator(name)
            self.__paginator.reset()
        else:
            self._isInSearchMode = False
            self._searchDP.useCreatorName()
            self.__paginator = self._getPaginator()
            self.__paginator.refresh()
        self._setCreateButtonData()

    def _getPaginator(self, pattern = None):
        if not pattern:
            return self.unitFunctional.getClubsPaginator()
        else:
            return self.unitFunctional.getClubsFinder(pattern)

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
        if self.unitFunctional.getEntityType() != PREBATTLE_TYPE.NONE:
            self.unitFunctional.setEntityType(PREBATTLE_TYPE.CLUBS)
        paginator = self.unitFunctional.getClubsPaginator()
        paginator.onListUpdated += self.__onClubsListUpdated
        finder = self.unitFunctional.getClubsFinder()
        finder.onListUpdated += self.__onClubsFoundListUpdated
        self.as_setSearchResultTextS(_ms(CYBERSPORT.WINDOW_CLUBSLISTVIEW_FOUNDTEAMS), _ms(CYBERSPORT.WINDOW_CLUBSLISTVIEW_FOUNDTEAMSDESCRIPTION), None)
        self.addListener(events.CoolDownEvent.CLUB, self._handleSetClubCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self._checkCoolDowns()
        self._setCreateButtonData()
        self.__paginator.reset()
        return

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.CLUB, self._handleSetClubCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        paginator = self.unitFunctional.getClubsPaginator()
        if paginator is not None:
            paginator.onListUpdated -= self.__onClubsListUpdated
        finder = self.unitFunctional.getClubsFinder()
        if finder is not None:
            finder.onListUpdated -= self.__onClubsFoundListUpdated
        self.stopClubListening()
        self.stopUnitListening()
        if self._isBackButtonClicked:
            unit_ext.destroyListReq()
            self._isBackButtonClicked = False
        self._cancelNavigationCooldown()
        self._isInSearchMode = False
        super(CyberSportClubsListView, self)._dispose()
        return

    def _onUserActionReceived(self, _, user):
        self.__updateView(user)

    def _handleSetClubCoolDown(self, event):
        if event.requestID in self.getCoolDownRequests() and event.coolDown > 0:
            self._setCoolDowns(event.coolDown, event.requestID)

    def _checkCoolDowns(self):
        cooldowns = {}
        for requestID in self.getCoolDownRequests():
            cooldowns[requestID] = self.clubsCtrl.getRequestCtrl().getCooldownTime(requestID)

        if len(cooldowns):
            requestID, cooldown = max(cooldowns.items(), key=operator.itemgetter(1))
            if cooldown > 0:
                self._setCoolDowns(cooldown, requestID)

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
         'createBtnEnabled': createBtnEnabled,
         'columnHeaders': _getColumnHeaders(self._isInSearchMode),
         'searchByNameEnable': True})
        return

    def __setNavigationData(self, isCooldown = False):
        self.as_updateNavigationBlockS({'previousVisible': True,
         'previousEnabled': not isCooldown and self.__paginator.canMoveLeft(),
         'nextVisible': True,
         'nextEnabled': not isCooldown and self.__paginator.canMoveRight(),
         'icon': RES_ICONS.MAPS_ICONS_STATISTIC_RATING24})

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
            self._checkCoolDowns()
        else:
            selectedIdx = self._searchDP.updateList(selectedID, result)
        if selectedIdx is not None:
            self.as_selectByIndexS(selectedIdx)
        return

    def __onClubsFoundListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        if not result:
            text = '\n'.join([text_styles.middleTitle(CYBERSPORT.WINDOW_UNITLISTVIEW_NOSEARCHRESULTS_HEADER), text_styles.standard(CYBERSPORT.WINDOW_UNITLISTVIEW_NOSEARCHRESULTS_DESCRIPTION)])
            self.__onClubsListUpdated(None, True, False, [])
            self.as_noSearchResultsS(text, True)
        else:
            self.__onClubsListUpdated(selectedID, isFullUpdate, isReqInCoolDown, result)
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
