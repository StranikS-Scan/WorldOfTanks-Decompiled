# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSummaryWindow.py
import BigWorld
from adisp import process
from debug_utils import LOG_ERROR
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.genConsts.FORTIFICATION_ALIASES import FORTIFICATION_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.clubs import events_dispatcher as club_events
from gui.shared import event_dispatcher as shared_events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers.i18n import makeString as _ms
from gui import makeHtmlString
from gui.clans.clan_helpers import ClanListener
from gui.clans.formatters import getClanRoleString
from gui.shared import g_itemsCache
from gui.shared.fortifications import isStartingScriptDone
from gui.shared.ClanCache import ClanInfo
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getAbsoluteUrl
from gui.shared.view_helpers.emblems import ClubEmblemsHelper, ClanEmblemsHelper
from gui.clans.settings import CLAN_CONTROLLER_STATES
from gui.clubs.ClubsController import g_clubsCtrl
from gui.clubs.contexts import GetPlayerInfoCtx
from gui.Scaleform.daapi.view.meta.ProfileSummaryWindowMeta import ProfileSummaryWindowMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import events

class ProfileSummaryWindow(ProfileSummaryWindowMeta, ClubEmblemsHelper, ClanEmblemsHelper, ClanListener):

    def __init__(self, *args):
        super(ProfileSummaryWindow, self).__init__(*args)
        self.__rating = 0

    def getGlobalRating(self, databaseID):
        if databaseID is not None and not self.__rating:
            self._receiveRating(databaseID)
        return self.__rating

    def openClanStatistic(self):
        if g_lobbyContext.getServerSettings().clanProfile.isEnabled():
            clanID, _ = g_itemsCache.items.getClanInfo(self._userID)
            if clanID != 0:
                shared_events.showClanProfileWindow(clanID)
        elif self.__isFortClanProfileAvailable():
            self.fireEvent(events.LoadViewEvent(FORTIFICATION_ALIASES.FORT_CLAN_STATISTICS_WINDOW_ALIAS), EVENT_BUS_SCOPE.LOBBY)
        else:
            LOG_ERROR('Fort Clan Profile Statistics is Unavailable for current user profile')

    def openClubProfile(self, clubDbID):
        club_events.showClubProfile(clubDbID)

    def onClubEmblem32x32Received(self, clubDbID, emblem):
        if emblem:
            path = self.getMemoryTexturePath(emblem)
            self.as_setClubEmblemS(path)

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if emblem:
            path = self.getMemoryTexturePath(emblem)
            self.as_setClanEmblemS(path)

    def onClanStateChanged(self, oldStateID, newStateID):
        self._requestClanInfo()

    def onAccountClanProfileChanged(self, profile):
        self._requestClanInfo()

    def onAccountClanInfoReceived(self, info):
        self._requestClanInfo()

    def _populate(self):
        super(ProfileSummaryWindow, self)._populate()
        self.startClanListening()
        self._requestClanInfo()
        self._requestClubInfo()

    def _dispose(self):
        self.stopClanListening()
        super(ProfileSummaryWindow, self)._dispose()

    def _requestClanInfo(self):
        if self.clansCtrl.isEnabled():
            isShowClanProfileBtnVisible = True
        else:
            isShowClanProfileBtnVisible = self.__isFortClanProfileAvailable()
        clanDBID, clanInfo = g_itemsCache.items.getClanInfo(self._userID)
        if clanInfo is not None:
            clanInfo = ClanInfo(*clanInfo)
            clanData = {'id': clanDBID,
             'header': clanInfo.getClanName(),
             'topLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_POST),
             'topValue': text_styles.main(getClanRoleString(clanInfo.getMembersFlags())),
             'bottomLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_JOINDATE),
             'bottomValue': text_styles.main(BigWorld.wg_getLongDateFormat(clanInfo.getJoiningTime()))}
            btnParams = self._getClanBtnParams(isShowClanProfileBtnVisible)
            clanData.update(btnParams)
            self.as_setClanDataS(clanData)
            self.requestClanEmblem32x32(clanDBID)
        return

    @process
    def _requestClubInfo(self):
        if g_clubsCtrl.getState().isAvailable():
            result = yield g_clubsCtrl.sendRequest(GetPlayerInfoCtx(self._userID), allowDelay=True)
            if result.isSuccess() and result.data:
                pInfo = result.data
                clubDbID = pInfo.getClubDbID()
                if pInfo.isInLadder():
                    leagueLabel = makeHtmlString('html_templates:lobby/cyberSport/league', 'leagueInfoWithIcon', ctx={'icon': getAbsoluteUrl(pInfo.getLadderChevron()),
                     'league': pInfo.getLeagueString(),
                     'division': pInfo.getDivisionString()})
                else:
                    leagueLabel = text_styles.main('--')
                self.as_setClubDataS({'id': clubDbID,
                 'header': pInfo.getClubUserName(),
                 'topLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_POST),
                 'topValue': text_styles.main(pInfo.getRoleString()),
                 'bottomLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_LADDER),
                 'bottomValue': leagueLabel,
                 'btnLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_BTNLABEL),
                 'btnEnabled': True,
                 'btnVisible': True})
                self.requestClubEmblem32x32(clubDbID, pInfo.getEmblem32x32())

    @process
    def _receiveRating(self, databaseID):
        req = g_itemsCache.items.dossiers.getUserDossierRequester(int(databaseID))
        self.__rating = yield req.getGlobalRating()

    def _getClanBtnParams(self, isVisible):
        if self.clansCtrl.isAvailable():
            btnEnabled = True
            btnTooltip = None
        else:
            btnEnabled = False
            btnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_UNAVAILABLE
        return {'btnLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_BTNLABEL),
         'btnEnabled': btnEnabled,
         'btnVisible': isVisible,
         'btnTooltip': btnTooltip}

    def __isFortClanProfileAvailable(self):
        return self._databaseID is None and isStartingScriptDone()
