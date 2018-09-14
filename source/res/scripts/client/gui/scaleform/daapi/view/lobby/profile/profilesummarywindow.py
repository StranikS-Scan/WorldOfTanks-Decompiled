# Python bytecode 2.7 (decompiled from Python 2.7)
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
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui import makeHtmlString
from gui.clans.clan_helpers import ClanListener
from gui.clans.formatters import getClanRoleString
from gui.shared import g_itemsCache
from gui.shared.fortifications import isStartingScriptDone
from gui.shared.ClanCache import ClanInfo
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import getAbsoluteUrl, makeTooltip
from gui.shared.view_helpers.emblems import ClubEmblemsHelper, ClanEmblemsHelper
from gui.clubs.contexts import GetPlayerInfoCtx
from gui.Scaleform.daapi.view.meta.ProfileSummaryWindowMeta import ProfileSummaryWindowMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from gui.shared import events
from skeletons.gui.clubs import IClubsController

class ProfileSummaryWindow(ProfileSummaryWindowMeta, ClubEmblemsHelper, ClanEmblemsHelper, ClanListener):
    clubsCtrl = dependency.descriptor(IClubsController)

    def __init__(self, *args):
        super(ProfileSummaryWindow, self).__init__(*args)
        self.__rating = 0

    def getGlobalRating(self, databaseID):
        if databaseID is not None and not self.__rating:
            self._receiveRating(databaseID)
        return self.__rating

    def openClanStatistic(self):
        if g_lobbyContext.getServerSettings().clanProfile.isEnabled():
            clanID, clanInfo = g_itemsCache.items.getClanInfo(self._userID)
            if clanID != 0:
                clanInfo = ClanInfo(*clanInfo)
                shared_events.showClanProfileWindow(clanID, clanInfo.getClanAbbrev())
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
        if self.clubsCtrl.getState().isAvailable():
            result = yield self.clubsCtrl.sendRequest(GetPlayerInfoCtx(self._userID), allowDelay=True)
            if result.isSuccess() and result.data:
                pInfo = result.data
                clubDbID = pInfo.getClubDbID()
                if pInfo.isInLadder():
                    leagueLabel = makeHtmlString('html_templates:lobby/cyberSport/league', 'leagueInfoWithIcon', ctx={'icon': getAbsoluteUrl(pInfo.getLadderChevron()),
                     'league': pInfo.getLeagueString(),
                     'division': pInfo.getDivisionString()})
                else:
                    leagueLabel = text_styles.main('--')
                clubDataVO = {'id': clubDbID,
                 'header': pInfo.getClubUserName(),
                 'topLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_POST),
                 'topValue': text_styles.main(pInfo.getRoleString()),
                 'bottomLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_LADDER),
                 'bottomValue': leagueLabel}
                clubDataVO.update(self._getClubProfileButtonParams(True))
                self.as_setClubDataS(clubDataVO)
                self.requestClubEmblem32x32(clubDbID, pInfo.getEmblem32x32())

    def _getClubProfileButtonParams(self, isEnabled):
        buttonParams = {'btnEnabled': isEnabled,
         'btnVisible': True,
         'btnLabel': _ms(PROFILE.PROFILE_SUMMARY_CLUB_BTNLABEL)}
        if not isEnabled:
            buttonParams['btnTooltip'] = makeTooltip(attention='#menu:header/account/popover/crewButton/disabledTooltip')
        return buttonParams

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
