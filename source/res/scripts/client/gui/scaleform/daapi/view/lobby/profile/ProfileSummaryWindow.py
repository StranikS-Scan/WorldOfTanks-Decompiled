# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/profile/ProfileSummaryWindow.py
from adisp import process
from festivity.festival.sounds import playSound
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher as shared_events
from helpers import dependency
from helpers.i18n import makeString as _ms
from gui.clans.clan_helpers import ClanListener
from gui.clans.formatters import getClanRoleString
from gui.shared.ClanCache import ClanInfo
from gui.shared.formatters import text_styles
from gui.shared.view_helpers.emblems import ClanEmblemsHelper
from gui.Scaleform.daapi.view.meta.ProfileSummaryWindowMeta import ProfileSummaryWindowMeta
from gui.Scaleform.locale.PROFILE import PROFILE
from skeletons.festival import IFestivalController

class ProfileSummaryWindow(ProfileSummaryWindowMeta, ClanEmblemsHelper, ClanListener):
    __festController = dependency.descriptor(IFestivalController)

    def __init__(self, *args):
        super(ProfileSummaryWindow, self).__init__(*args)
        self.__rating = 0

    def getGlobalRating(self, databaseID):
        if databaseID is not None and not self.__rating:
            self._receiveRating(databaseID)
        return self.__rating

    def openClanStatistic(self):
        if self.lobbyContext.getServerSettings().clanProfile.isEnabled():
            clanID, clanInfo = self.itemsCache.items.getClanInfo(self._userID)
            if clanID != 0:
                clanInfo = ClanInfo(*clanInfo)
                shared_events.showClanProfileWindow(clanID, clanInfo.getClanAbbrev())

    def onClanEmblem32x32Received(self, clanDbID, emblem):
        if emblem:
            path = self.getMemoryTexturePath(emblem)
            self.as_setClanEmblemS(path)

    def onClanEnableChanged(self, enabled):
        self._requestClanInfo()

    def onAccountClanProfileChanged(self, profile):
        self._requestClanInfo()

    def onAccountClanInfoReceived(self, info):
        self._requestClanInfo()

    def onDogtagRollover(self):
        playSound(backport.sound(R.sounds.ev_fest_hangar_token_zoom_on()))

    def onDogtagRollout(self):
        playSound(backport.sound(R.sounds.ev_fest_hangar_token_zoom_off()))

    def _populate(self):
        super(ProfileSummaryWindow, self)._populate()
        self.startClanListening()
        self._requestClanInfo()
        self._requestPlayerCard()

    def _dispose(self):
        self.stopClanListening()
        super(ProfileSummaryWindow, self)._dispose()

    def _requestClanInfo(self):
        isShowClanProfileBtnVisible = False
        if self.lobbyContext.getServerSettings().clanProfile.isEnabled():
            isShowClanProfileBtnVisible = True
        clanDBID, clanInfo = self.itemsCache.items.getClanInfo(self._userID)
        if clanInfo is not None:
            clanInfo = ClanInfo(*clanInfo)
            clanData = {'id': clanDBID,
             'header': clanInfo.getClanName(),
             'topLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_POST),
             'topValue': text_styles.main(getClanRoleString(clanInfo.getMembersFlags())),
             'bottomLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_JOINDATE),
             'bottomValue': text_styles.main(backport.getLongDateFormat(clanInfo.getJoiningTime()))}
            btnParams = self._getClanBtnParams(isShowClanProfileBtnVisible)
            clanData.update(btnParams)
            self.as_setClanDataS(clanData)
            self.requestClanEmblem32x32(clanDBID)
        return

    def _requestPlayerCard(self):
        dossier = self.itemsCache.items.getAccountDossier(self._databaseID)
        playerCard = dossier.getFestivalPlayerCard()
        if playerCard is None:
            return
        else:
            lastPlayerCard = self.__festController.getGlobalPlayerCard()
            self.__festController.setGlobalPlayerCard(playerCard)
            basisImg = backport.image(playerCard.getBasis().getIconResID())
            emblemImg = backport.image(playerCard.getEmblem().getIconResID())
            emblemSmallImg = backport.image(playerCard.getEmblem().getSmallIconResID())
            basisSmallImg = backport.image(playerCard.getBasis().getSmallIconResID())
            titleImg = backport.image(playerCard.getTitle().getIconResID())
            rankStr = backport.text(playerCard.getRank().getNameResID())
            translateStr = text_styles.counter(backport.text(R.strings.festival.dogtag.translate(), backport.text(playerCard.getTitle().getNameResID())))
            basisBackImg = backport.image(playerCard.getBasis().getBasisResID())
            truncateEndingStr = backport.text(R.strings.festival.dogtag.truncated())
            self.__festController.setGlobalPlayerCard(lastPlayerCard)
            self.as_setDogtagInfoS(isEnabled=self.__festController.isEnabled(), basisImg=basisImg, emblemImg=emblemImg, titleImg=titleImg, rankStr=rankStr, nickStr=self._userName, basisSmallImg=basisSmallImg, emblemSmallImg=emblemSmallImg, translateStr=translateStr, basisBackImg=basisBackImg, truncateEndingStr=truncateEndingStr)
            return

    @process
    def _receiveRating(self, databaseID):
        req = self.itemsCache.items.dossiers.getUserDossierRequester(int(databaseID))
        self.__rating = yield req.getGlobalRating()

    def _getClanBtnParams(self, isVisible):
        if self.webCtrl.isAvailable():
            btnEnabled = True
            btnTooltip = None
        else:
            btnEnabled = False
            btnTooltip = TOOLTIPS.HEADER_ACCOUNTPOPOVER_UNAVAILABLE
        return {'btnLabel': _ms(PROFILE.PROFILE_SUMMARY_CLAN_BTNLABEL),
         'btnEnabled': btnEnabled,
         'btnVisible': isVisible,
         'btnTooltip': btnTooltip}
