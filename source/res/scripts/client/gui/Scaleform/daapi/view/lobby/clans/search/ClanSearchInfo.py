# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/search/ClanSearchInfo.py
import weakref
from adisp import adisp_process
from gui import SystemMessages
from gui.Scaleform.daapi.view.lobby.profile.ProfileUtils import HeaderItemsTypes, ProfileUtils
from gui.Scaleform.daapi.view.meta.ClanSearchInfoMeta import ClanSearchInfoMeta
from gui.Scaleform.locale.CLANS import CLANS
from gui.clans import formatters as clans_fmts
from gui.clans.clan_helpers import ClanListener
from gui.clans.data_wrapper.utils import formatField
from gui.clans.settings import CLIENT_CLAN_RESTRICTIONS, MAX_CLAN_MEMBERS_COUNT
from gui.impl import backport
from gui.shared import event_dispatcher as shared_events
from gui.shared.formatters import text_styles
from gui.shared.utils.functions import makeTooltip
from gui.shared.view_helpers import ClanEmblemsHelper
from gui.wgcg.base.contexts import CreateApplicationCtx
from helpers.i18n import makeString as _ms

def _packItemData(text, description, tooltip, icon):
    return {'type': HeaderItemsTypes.COMMON,
     'text': text,
     'description': _ms(description),
     'iconPath': ProfileUtils.getIconPath(icon),
     'tooltip': tooltip,
     'enabled': True}


class ClanSearchInfo(ClanSearchInfoMeta, ClanListener, ClanEmblemsHelper):

    def __init__(self):
        super(ClanSearchInfo, self).__init__()
        self.__dataProvider = None
        self.__selectedClan = None
        return

    def bindDataProvider(self, dataProvider):
        self.__dataProvider = weakref.proxy(dataProvider)

    def openClanProfile(self):
        shared_events.showClanProfileWindow(self.__selectedClan.getClanDbID(), self.__selectedClan.getClanAbbrev())

    def onAccountClanProfileChanged(self, profile):
        self._updateSetaledState()

    @adisp_process
    def sendRequest(self):
        self.as_setWaitingVisibleS(True)
        context = CreateApplicationCtx([self.__selectedClan.getClanDbID()])
        result = yield self.webCtrl.sendRequest(context, allowDelay=True)
        if result.isSuccess():
            SystemMessages.pushMessage(clans_fmts.getAppSentSysMsg(self.__selectedClan.getClanName(), self.__selectedClan.getClanAbbrev()))
        self._updateSetaledState()
        self.as_setWaitingVisibleS(False)

    def requestData(self, clanId):
        self.__selectedClan = self.__dataProvider.getClanInfo(clanId)
        self._updateDetailedInfo()
        self._updateClanEmblem()
        self._updateSetaledState()

    def onClanEmblem128x128Received(self, clanDbID, emblem):
        if clanDbID == self.__selectedClan.getClanDbID():
            self.as_setEmblemS(self.getMemoryTexturePath(emblem))

    def _populate(self):
        super(ClanSearchInfo, self)._populate()
        self.__initControls()

    def _updateClanEmblem(self):
        self.requestClanEmblem128x128(self.__selectedClan.getClanDbID())

    def _updateDetailedInfo(self):
        clanID = self.__selectedClan.getClanDbID()
        clanName = formatField(self.__selectedClan.getClanFullName)
        rating = formatField(getter=self.__selectedClan.getPersonalRating, formatter=backport.getIntegralFormat)
        battlesCount = formatField(getter=self.__selectedClan.getBattlesCount, formatter=backport.getIntegralFormat)
        wins = formatField(getter=self.__selectedClan.getBattleXpAvg, formatter=lambda value: backport.getNiceNumberFormat(value) + '%')
        avgExp = formatField(getter=self.__selectedClan.getBattlesPerformanceAvg, formatter=backport.getIntegralFormat)
        stats = [_packItemData(battlesCount, CLANS.SEARCH_INFO_STATS_BATTLES, CLANS.SEARCH_INFO_STATS_BATTLES_TOOLTIP, 'avgBattlesCount40x32.png'), _packItemData(wins, CLANS.SEARCH_INFO_STATS_WINS, CLANS.SEARCH_INFO_STATS_WINS_TOOLTIP, 'avgWins40x32.png'), _packItemData(avgExp, CLANS.SEARCH_INFO_STATS_AVGEXP, CLANS.SEARCH_INFO_STATS_AVGEXP_TOOLTIP, 'avgExp40x32.png')]
        self.as_setDataS({'clanId': clanID,
         'clanName': clanName,
         'ratingTitle': text_styles.main(CLANS.SEARCH_INFO_RATINGTITLE),
         'rating': text_styles.promoTitle(rating),
         'stats': stats})

    def _updateSetaledState(self):
        requestSentVisible = False
        sendRequestBtnVisible = True
        sendRequestBtnEnabled = True
        sendRequestTooltip = None
        reason = self.webCtrl.getLimits().canSendApplication(_ClanAdapter(self.__selectedClan)).reason
        if reason == CLIENT_CLAN_RESTRICTIONS.NO_RESTRICTIONS:
            pass
        elif reason == CLIENT_CLAN_RESTRICTIONS.OWN_CLAN:
            sendRequestBtnVisible = False
        elif reason == CLIENT_CLAN_RESTRICTIONS.ALREADY_IN_CLAN:
            sendRequestBtnVisible = False
        elif reason == CLIENT_CLAN_RESTRICTIONS.CLAN_IS_FULL:
            sendRequestBtnEnabled = False
            sendRequestTooltip = makeTooltip(CLANS.SEARCH_INFO_BANNED_TOOLTIP_HEADER, text_styles.error(_ms(CLANS.SEARCH_INFO_BANNED_TOOLTIP_BODY)))
        elif reason == CLIENT_CLAN_RESTRICTIONS.CLAN_INVITE_ALREADY_RECEIVED:
            sendRequestBtnEnabled = False
            sendRequestTooltip = CLANS.SEARCH_INFO_INVITEALREADYACHIEVED_TOOLTIP
        elif reason == CLIENT_CLAN_RESTRICTIONS.CLAN_APPLICATION_ALREADY_SENT:
            sendRequestBtnEnabled = False
            sendRequestTooltip = CLANS.SEARCH_INFO_REQUESTALREADYSENT_TOOLTIP
        elif reason == CLIENT_CLAN_RESTRICTIONS.SENT_INVITES_LIMIT_REACHED:
            sendRequestBtnEnabled = False
            sendRequestTooltip = CLANS.SEARCH_INFO_REQUESTSLIMITEXCEEDED_TOOLTIP
        elif reason == CLIENT_CLAN_RESTRICTIONS.CLAN_CONSCRIPTION_CLOSED:
            sendRequestBtnEnabled = False
            sendRequestTooltip = CLANS.SEARCH_INFO_REQUESTSARENOTACCEPTED_TOOLTIP
        elif reason == CLIENT_CLAN_RESTRICTIONS.FORBIDDEN_ACCOUNT_TYPE:
            sendRequestBtnEnabled = False
            sendRequestTooltip = makeTooltip(CLANS.SEARCH_INFO_FORBIDDENACCOUNTTYPE_TOOLTIP_HEADER, text_styles.error(_ms(CLANS.SEARCH_INFO_FORBIDDENACCOUNTTYPE_TOOLTIP_BODY)))
        else:
            sendRequestBtnVisible = False
        self.as_setStateDataS({'requestSentVisible': requestSentVisible,
         'sendRequestBtnVisible': sendRequestBtnVisible,
         'sendRequestBtnEnabled': sendRequestBtnEnabled,
         'sendRequestTooltip': sendRequestTooltip,
         'alertIconVisible': sendRequestBtnVisible and not sendRequestBtnEnabled})
        return

    def __initControls(self):
        self.as_setInitDataS({'ratingDescription': text_styles.stats(_ms(CLANS.SEARCH_INFO_RATINGDESCRIPTION)),
         'ratingTooltip': CLANS.SEARCH_INFO_RATINGDESCRIPTION_TOOLTIP,
         'requestSent': text_styles.success(_ms(CLANS.SEARCH_INFO_REQUESTSENT)),
         'clanProfileBtnLabel': _ms(CLANS.SEARCH_INFO_CLANPROFILEBTN),
         'sendRequestBtnLabel': _ms(CLANS.SEARCH_INFO_SENDREQUESTBTN)})
        self.as_setWaitingVisibleS(False)


class _ClanAdapter(object):

    def __init__(self, clanInfo):
        super(_ClanAdapter, self).__init__()
        self.__clanInfo = clanInfo

    def getDbID(self):
        return self.__clanInfo.getClanDbID()

    def canAcceptsJoinRequests(self):
        return self.__clanInfo.canAcceptsJoinRequests()

    def hasFreePlaces(self):
        return MAX_CLAN_MEMBERS_COUNT - self.__clanInfo.getMembersCount() > 0
