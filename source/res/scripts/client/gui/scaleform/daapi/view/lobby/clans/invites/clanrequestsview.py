# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanRequestsView.py
import BigWorld
from adisp import process
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters
from gui.clans.clan_helpers import isInClanEnterCooldown
from gui.clans.items import formatField, isValueAvailable
from gui.clans.contexts import AcceptApplicationCtx, DeclineApplicationCtx, CreateInviteCtx, AccountsInfoCtx
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesAbstractDataProvider
from gui.Scaleform.daapi.view.meta.ClanRequestsViewMeta import ClanRequestsViewMeta
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLAN_INVITE_STATES
from gui.shared.events import CoolDownEvent
from gui.shared.formatters import text_styles
from gui.shared.view_helpers import CooldownHelper
from debug_utils import LOG_DEBUG
from helpers.i18n import makeString as _ms

class ClanRequestsView(ClanRequestsViewMeta):

    def __init__(self):
        super(ClanRequestsView, self).__init__()
        self._cooldown = CooldownHelper([CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS,
         CLAN_REQUESTED_DATA_TYPE.CREATE_INVITES,
         CLAN_REQUESTED_DATA_TYPE.ACCEPT_APPLICATION,
         CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE,
         CLAN_REQUESTED_DATA_TYPE.DECLINE_APPLICATION,
         CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE,
         CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES,
         CLAN_REQUESTED_DATA_TYPE.CLAN_INVITES,
         CLAN_REQUESTED_DATA_TYPE.CLAN_MEMBERS_RATING], self._onCooldownHandle, CoolDownEvent.CLAN)

    @property
    def actualRequestsPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL)

    @property
    def expiredRequestsPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED)

    @property
    def processedRequestsPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED)

    def acceptRequest(self, applicationID):
        applicationID = int(applicationID)
        ctx = AcceptApplicationCtx(applicationID)
        self._getCurrentPaginator().accept(applicationID, ctx)

    def declineRequest(self, applicationID):
        applicationID = int(applicationID)
        ctx = DeclineApplicationCtx(applicationID)
        self._getCurrentPaginator().decline(applicationID, ctx)

    def sendInvite(self, dbId):
        dbId = int(dbId)
        paginator = self._getCurrentPaginator()
        requestWrapper = paginator.getInviteByDbID(dbId)
        ctx = CreateInviteCtx(requestWrapper.getClanDbID(), [requestWrapper.getAccountDbID()])
        self._getCurrentPaginator().resend(dbId, ctx)
        self._enableRefreshBtn(True)

    def onClanAppsCountReceived(self, clanDbID, appsCount):
        super(ClanRequestsView, self).onClanAppsCountReceived(clanDbID, appsCount)
        if self.actualRequestsPaginator.isSynced():
            self._enableRefreshBtn(True)

    def _onAttachedToWindow(self):
        super(ClanRequestsView, self)._onAttachedToWindow()
        self._cooldown.start()
        self.filterBy(self.currentFilterName)

    def _dispose(self):
        self._cooldown.stop()
        self._cooldown.stop()
        self._cooldown = None
        super(ClanRequestsView, self)._dispose()
        return

    def _onCooldownHandle(self, isInCooldown):
        self.dataProvider.allowActions(not isInCooldown)

    def _getViewAlias(self):
        return CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS

    def _showDummyByFilterName(self, filterName):
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOACTUALREQUESTS_TITLE)
        elif filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOEXPIREDREQUESTS_TITLE)
        elif filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOPROCESSEDREQUESTS_TITLE)
        else:
            LOG_DEBUG('Unexpected behaviour: no dummy for filter', filterName)
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOACTUALREQUESTS_TITLE)

    def _getDefaultFilterName(self):
        return CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL

    def _getDefaultSortFields(self):
        return (('status', False),)

    def _getSecondSortFields(self):
        return ('updatedAt',) if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED or self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED else ('createdAt',)

    def _createSearchDP(self):
        return RequestDataProvider(self)

    @process
    def _onListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        yield lambda callback: callback(None)
        status, data = result
        accountsInfo = tuple()
        if status is True and data:
            ctx = AccountsInfoCtx(tuple((item.getAccountDbID() for item in data)))
            accountsResponse = yield self.clansCtrl.sendRequest(ctx)
            if accountsResponse.isSuccess():
                accountsInfo = ctx.getDataObj(accountsResponse.data)
        self.dataProvider.setAccountsInfo(accountsInfo)
        super(ClanRequestsView, self)._onListUpdated(selectedID, isFullUpdate, isReqInCoolDown, result)

    def _makeFilters(self):
        return [{'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ACTUAL, value=self.formatInvitesCount(self.actualRequestsPaginator))}, {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_EXPIRED, value=self.formatInvitesCount(self.expiredRequestsPaginator))}, {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_PROCESSED, value=self.formatInvitesCount(self.processedRequestsPaginator))}]

    def _makeHeaders(self):
        return [self._packHeaderColumnData('userName', CLANS.CLANINVITESWINDOW_TABLE_USERNAME, 225, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_USERNAME, textAlign='left', defaultSortDirection='ascending'),
         self._packHeaderColumnData('message', '', 73, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_MESSAGE, RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_ICON_STATISTICS_CLAN_INVITE_098),
         self._packHeaderColumnData('personalRating', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_PERSONALRATING, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         self._packHeaderColumnData('battlesCount', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_BATTLESCOUNT, RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
         self._packHeaderColumnData('wins', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_WINS, RES_ICONS.MAPS_ICONS_STATISTIC_WINS24),
         self._packHeaderColumnData('awgExp', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_AWGEXP, RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
         self._packHeaderColumnData('status', CLANS.CLANINVITESWINDOW_TABLE_STATUS, 160, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_STATUS),
         self._packHeaderColumnData('actions', CLANS.CLANINVITESWINDOW_TABLE_ACTIONS, 140, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_ACTIONS, enabled=False)]


class RequestDataProvider(ClanInvitesAbstractDataProvider):

    def __init__(self, proxy):
        super(RequestDataProvider, self).__init__(proxy)
        self.__accountsInfo = {}

    def setAccountsInfo(self, acc_info):
        self.__accountsInfo = dict(((info.getDbID(), info) for info in acc_info))

    def getStatusByDbID(self, dbID):
        return self.getExtraData(dbID)

    def invalidateItems(self):
        for item in self.collection:
            if self._isDataRow(item):
                item['actions'] = self.__buildActionsSection(item['userInfo']['dbID'], self.getStatusByDbID(item['dbID']))

    def _buildExtraData(self, item, prevExtra):
        return item.getStatus()

    def _makeVO(self, item, extraData):
        accountDbId = item.getAccountDbID()
        return {'dbID': item.getDbID(),
         'userInfo': {'userName': item.getAccountName(),
                      'dbID': accountDbId},
         'personalRating': formatField(getter=item.getPersonalRating, formatter=BigWorld.wg_getIntegralFormat),
         'battlesCount': formatField(getter=item.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat),
         'wins': formatField(getter=item.getBattlesPerformanceAvg, formatter=lambda value: BigWorld.wg_getNiceNumberFormat(value) + '%'),
         'awgExp': formatField(getter=item.getBattleXpAvg, formatter=BigWorld.wg_getIntegralFormat),
         'status': {'text': self._makeInviteStateString(item),
                    'tooltip': self._makeTooltip(body=self._makeRequestTooltip(status=item.getStatus(), user=formatField(getter=item.getChangerName), date=formatField(getter=item.getUpdatedAt, formatter=formatters.formatShortDateShortTimeString)))},
         'canShowContextMenu': True,
         'messageTooltip': self._makeTooltip(body=item.getComment() if isValueAvailable(getter=item.getComment) else str()),
         'actions': self.__buildActionsSection(accountDbId, item.getStatus())}

    def _makeRequestTooltip(self, status, date, user=None):
        if status == CLAN_INVITE_STATES.ACCEPTED:
            return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_REQUESTACCEPTED)), text_styles.main(date), text_styles.main(''), text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_BYUSER)), text_styles.stats(user))
        if status == CLAN_INVITE_STATES.DECLINED or status == CLAN_INVITE_STATES.DECLINED_RESENT:
            return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_REQUESTDECLINED)), text_styles.main(date), text_styles.main(''), text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_BYUSER)), text_styles.stats(user))
        if status == CLAN_INVITE_STATES.EXPIRED or status == CLAN_INVITE_STATES.EXPIRED_RESENT:
            return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_REQUESTEXPIRED)), text_styles.main(date))
        return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_REQUEST_REQUESTSENT)), text_styles.main(date)) if status == CLAN_INVITE_STATES.ACTIVE else None

    def __buildActionsSection(self, accountDbId, inviteStatus):
        acceptButtonEnabled = False
        declineButtonEnabled = False
        inviteButtonEnabled = False
        acceptButtonVisible = False
        declineButtonVisible = False
        inviteButtonVisible = False
        invBtnTooltip = None
        acceptButtonTooltip = None
        clanHasFreeSpaces = self.proxy.clanInfo.hasFreePlaces()
        if self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            if inviteStatus == CLAN_INVITE_STATES.ACTIVE:
                declineButtonVisible = True
                acceptButtonVisible = True
                declineButtonEnabled = self.isActionsAllowed()
                if not clanHasFreeSpaces:
                    acceptButtonTooltip = self._makeTooltip(body=_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTSENDINVITE_BODY))
                else:
                    accInfo = self.__accountsInfo.get(accountDbId)
                    if accInfo and isInClanEnterCooldown(accInfo.getClanCooldownTill()):
                        acceptButtonTooltip = self._makeTooltip(body=_ms(text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTACCEPTREQUESTDUETOCD_BODY)), text_styles.main(formatters.formatShortDateShortTimeString(accInfo.getClanCooldownTill())))))
                    else:
                        acceptButtonEnabled = self.isActionsAllowed()
        elif self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            if inviteStatus == CLAN_INVITE_STATES.EXPIRED:
                inviteButtonVisible = True
                if not clanHasFreeSpaces:
                    invBtnTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTACCEPTREQUEST_BODY
                else:
                    invBtnTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_INVITEBUTTON
                    inviteButtonEnabled = self.isActionsAllowed()
        elif self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            if inviteStatus == CLAN_INVITE_STATES.DECLINED:
                inviteButtonVisible = True
                if not clanHasFreeSpaces:
                    invBtnTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTACCEPTREQUEST_BODY
                else:
                    invBtnTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_INVITEBUTTON
                    inviteButtonEnabled = self.isActionsAllowed()
        return {'acceptButtonEnabled': acceptButtonEnabled,
         'declineButtonEnabled': declineButtonEnabled,
         'inviteButtonEnabled': inviteButtonEnabled,
         'acceptButtonVisible': acceptButtonVisible,
         'declineButtonVisible': declineButtonVisible,
         'inviteButtonVisible': inviteButtonVisible,
         'inviteButtonText': _ms(CLANS.CLANINVITESWINDOW_TABLE_INVITEBUTTON),
         'inviteButtonTooltip': self._makeTooltip(body=_ms(invBtnTooltip)),
         'acceptButtonTooltip': acceptButtonTooltip}
