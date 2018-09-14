# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/cyberSport/ClubLadderView.py
import BigWorld
from adisp import process
from debug_utils import LOG_DEBUG
from helpers.i18n import makeString as _ms
from gui.clubs.club_helpers import isSeasonInProgress
from gui.clubs.contexts import GetClubsContendersCtx
from gui.clubs.events_dispatcher import showClubProfile
from gui.clubs.formatters import getDivisionString, getLeagueString
from gui.clubs.items import ClubContenderItem
from gui.clubs.settings import getLadderChevron64x64, getLadderChevron256x256
from gui.clubs.settings import CLIENT_CLUB_STATE
from gui.Scaleform.daapi.view.lobby.cyberSport.ClubProfileWindow import ClubPage
from gui.Scaleform.daapi.view.meta.StaticFormationLadderViewMeta import StaticFormationLadderViewMeta
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.WAITING import WAITING
from gui.Scaleform.locale.CYBERSPORT import CYBERSPORT
from gui.shared.formatters import text_styles
from gui.shared.view_helpers.emblems import ClubEmblemsHelper

class ClubLadderView(StaticFormationLadderViewMeta, ClubPage, ClubEmblemsHelper):

    def __init__(self):
        super(ClubLadderView, self).__init__()
        self._clubDbID = None
        self._owner = None
        self._clubEmblems = {}
        self._hasLadderInfo = False
        self._requestedIconIDs = []
        return

    def onClubUpdated(self, club):
        if club is not None:
            self._initializeGui(club)
        return

    def showFormationProfile(self, clubDbID):
        showClubProfile(long(clubDbID))

    def onClubsSeasonStateChanged(self, seasonState):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club is not None:
            self.as_updateHeaderDataS(self.__packHeaderData(club))
            self.__setLadderData(club)
        return

    def onClubLadderInfoChanged(self, ladderInfo):
        club = self.clubsCtrl.getClub(self._clubDbID)
        if club is not None:
            self.as_updateHeaderDataS(self.__packHeaderData(club))
            self.__setLadderData(club)
        return

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        self._clubEmblems[clubDbID] = emblem
        if clubDbID in self._requestedIconIDs:
            self.as_onUpdateClubIconS(clubDbID, self.getMemoryTexturePath(emblem))

    def updateClubIcons(self, ids):
        self._requestedIconIDs = ids
        self.__updateIcons()

    def __updateIcons(self):
        iconsMap = {}
        if self._clubEmblems:
            for clubDbID, emblem in self._clubEmblems.iteritems():
                if clubDbID in self._requestedIconIDs:
                    iconsMap[clubDbID] = self.getMemoryTexturePath(emblem)

        self.as_onUpdateClubIconsS({'iconsMap': iconsMap})

    def _initializeGui(self, club):
        self.as_setLadderStateS(self.__packLadderState(club))
        self.as_updateHeaderDataS(self.__packHeaderData(club))
        self.__setLadderData(club)

    def _populate(self):
        super(ClubLadderView, self)._populate()

    def _dispose(self):
        super(ClubLadderView, self)._dispose()
        self.clearClub()
        self._clubDbID = None
        self._owner = None
        self._clubEmblems = None
        self._hasLadderInfo = None
        self._requestedIconIDs = None
        return

    @process
    def __setLadderData(self, club):
        if club.wasInRatedBattleThisSeason():
            self.showWaiting(WAITING.CLUBS_CLUB_GET)
            results = yield self.clubsCtrl.sendRequest(GetClubsContendersCtx(club.getClubDbID()), allowDelay=True)
            if results.isSuccess():
                self._hasLadderInfo = True
                clubs = map(ClubContenderItem.build, results.data)
                self.as_updateLadderDataS(self.__packLadderData(clubs))
            else:
                self._hasLadderInfo = False
            self.hideWaiting()
        else:
            yield lambda callback = None: callback
        self.as_setLadderStateS(self.__packLadderState(club))
        return

    def __packLadderState(self, club):
        if not isSeasonInProgress():
            showStateMessage = True
            title = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERSTATUS_NOSEASON
            message = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERMSG_NOSEASON
        elif not club.wasInRatedBattleThisSeason() or not self._hasLadderInfo:
            showStateMessage = True
            title = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERSTATUS_NOBATTLES
            message = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERMSG_NOBATTLES
        else:
            showStateMessage = False
            title = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERSTATUS_INLADDER
            message = CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERMSG_INLADDER
        return {'showStateMessage': showStateMessage,
         'stateMessage': {'title': text_styles.middleTitle(title),
                          'message': text_styles.main(message),
                          'iconPath': getLadderChevron256x256()}}

    def __packHeaderData(self, club):
        ladderInfo = club.getLadderInfo()
        return {'divisionName': self.__getDivisionText(ladderInfo),
         'divisionPositionText': self.__getPositionText(ladderInfo),
         'formationIconPath': getLadderChevron64x64(ladderInfo.division) if ladderInfo.isInLadder() else '',
         'tableHeader': self.__packTableHeaders(),
         'clubDBID': self._clubDbID}

    def __getDivisionText(self, ladderInfo):
        if ladderInfo.isInLadder():
            divisionStr = getDivisionString(ladderInfo.division)
            leagueStr = getLeagueString(ladderInfo.getLeague())
            return text_styles.highTitle(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_DIVISIONNAME_TEXT, division=divisionStr, league=leagueStr))
        return ''

    def __getPositionText(self, ladderInfo):
        if ladderInfo.isInLadder():
            fmtPosition = text_styles.middleTitle(str(ladderInfo.position))
            fmtPoint = text_styles.middleTitle(str(ladderInfo.getRatingPoints()))
            return text_styles.standard(_ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_DIVISIONPOSITION_TEXT, place=fmtPosition, points=fmtPoint))
        return ''

    def __packTableHeaders(self):
        return [self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERPLACE_TEXT, 70, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERPLACE, fieldName='placeSortValue', sortOrder=1),
         self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERPOINTS_TEXT, 75, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERPOINTS, fieldName='pointsSortValue', sortOrder=2),
         self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERFORMATIONNAME_TEXT, 470, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERFORMATIONNAME, fieldName='formationNameSortValue', sortType='string'),
         self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERBATTLESCOUNT_TEXT, 80, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERBATTLESCOUNT, fieldName='battlesCountSortValue'),
         self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERWINSPERCENT_TEXT, 80, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERWINPERCENT, fieldName='winPercentSortValue'),
         self.__packTableHeaderItem(CYBERSPORT.STATICFORMATION_LADDERVIEW_LADDERTABLE_HEADERSHOWFORMATIONPROFILE_TEXT, 180, tooltip=TOOLTIPS.STATICFORMATIONLADDERVIEW_TABLE_HEADERSHOWFORMATIONPROFILE)]

    def __packTableHeaderItem(self, label, buttonWidth, tooltip = '', fieldName = '', sortOrder = 0, sortType = 'numeric'):
        return {'label': text_styles.standard(label),
         'toolTip': tooltip,
         'sortOrder': sortOrder,
         'id': fieldName,
         'buttonWidth': buttonWidth,
         'sortType': sortType}

    def __packLadderData(self, clubs):
        formations = []
        clubsState = self.clubsCtrl.getState()
        if clubsState.getStateID() == CLIENT_CLUB_STATE.HAS_CLUB:
            myClubDbID = clubsState.getClubDbID()
        else:
            myClubDbID = None
        club = self.clubsCtrl.getClub(self._clubDbID)
        ladderInfo = club.getLadderInfo()
        if club and ladderInfo.isInLadder():
            for clubInfo in sorted(clubs, key=lambda club: club.ladderRank):
                self.requestClubEmblem32x32(clubInfo.clubDBID, clubInfo.clubEmblemUrl)
                battlesCount = BigWorld.wg_getNiceNumberFormat(clubInfo.battlesCount)
                winsPercent = 0
                if clubInfo.battlesCount > 0:
                    winsPercent = clubInfo.winsCount / float(clubInfo.battlesCount) * 100
                winsPercentStr = BigWorld.wg_getNiceNumberFormat(winsPercent) + '%'
                clubName = clubInfo.clubName
                ladderPoints = clubInfo.getRatingPoints(ladderInfo.getDivision())
                emblem = self._clubEmblems.get(clubInfo.clubDBID, None)
                texturePath = self.getMemoryTexturePath(emblem) if emblem else ''
                formations.append({'formationId': clubInfo.clubDBID,
                 'showProfileBtnText': _ms(CYBERSPORT.STATICFORMATION_LADDERVIEW_SHOWFORMATIONPROFILEBTN_TEXT),
                 'showProfileBtnTooltip': TOOLTIPS.STATICFORMATIONLADDERVIEW_SHOWFORMATIONPROFILEBTN,
                 'emblemIconPath': texturePath,
                 'place': text_styles.standard(str(clubInfo.ladderRank)),
                 'placeSortValue': clubInfo.ladderRank,
                 'points': text_styles.middleTitle(str(ladderPoints)),
                 'pointsSortValue': ladderPoints,
                 'formationName': text_styles.highTitle(clubName),
                 'formationNameSortValue': clubName,
                 'battlesCount': text_styles.stats(battlesCount),
                 'battlesCountSortValue': clubInfo.battlesCount,
                 'winPercent': text_styles.stats(winsPercentStr),
                 'winPercentSortValue': winsPercent,
                 'isCurrentTeam': self._clubDbID == clubInfo.clubDBID,
                 'isMyClub': myClubDbID == clubInfo.clubDBID})

        return {'formations': formations}
