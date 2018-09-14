# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanRequestsView.py
import BigWorld
from gui.clans import formatters
from gui.clans.items import formatField, isValueAvailable
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLAN_INVITE_STATES
from gui.clans.contexts import AcceptApplicationCtx, DeclineApplicationCtx, CreateInviteCtx
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesAbstractDataProvider
from gui.Scaleform.daapi.view.meta.ClanRequestsViewMeta import ClanRequestsViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesWindowAbstractTabView import *
from gui.shared.events import CoolDownEvent
from gui.shared.view_helpers import CooldownHelper
from debug_utils import LOG_DEBUG
from helpers.i18n import makeString as _ms

class ClanRequestsView(ClanRequestsViewMeta):
    __coolDownRequests = [CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS,
     CLAN_REQUESTED_DATA_TYPE.CREATE_INVITES,
     CLAN_REQUESTED_DATA_TYPE.ACCEPT_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES]

    def __init__(self):
        super(ClanRequestsView, self).__init__()
        self._cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.CLAN)

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

    def _populate(self):
        super(ClanRequestsView, self)._populate()

    def _onAttachedToWindow(self):
        super(ClanRequestsView, self)._onAttachedToWindow()
        self._cooldown.start()
        self.actualRequestsPaginator.onListUpdated += self._onListUpdated
        self.actualRequestsPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.expiredRequestsPaginator.onListUpdated += self._onListUpdated
        self.expiredRequestsPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.processedRequestsPaginator.onListUpdated += self._onListUpdated
        self.processedRequestsPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.filterBy(self.currentFilterName)

    def _dispose(self):
        self.actualRequestsPaginator.onListUpdated -= self._onListUpdated
        self.actualRequestsPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self.expiredRequestsPaginator.onListUpdated -= self._onListUpdated
        self.expiredRequestsPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self.processedRequestsPaginator.onListUpdated -= self._onListUpdated
        self.processedRequestsPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self._cooldown.stop()
        self._cooldown = None
        super(ClanRequestsView, self)._dispose()
        return

    def _onCooldownHandle(self, isInCooldown):
        self.dataProvider.allowActions(not isInCooldown)

    def _getViewAlias(self):
        return CLANS_ALIASES.CLAN_PROFILE_REQUESTS_VIEW_ALIAS

    def _getDummyByFilterName(self, filterName):
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_ACTUAL
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_EXPIRED
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_PROCESSED
        LOG_DEBUG('Unexpected behaviour: no dummy for filter', filterName)
        return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_ACTUAL

    def _getDefaultFilterName(self):
        return CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL

    def _getDefaultSortFields(self):
        return (('status', False),)

    def _getSecondSortFields(self):
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            return ('updatedAt',)
        else:
            return ('createdAt',)

    def _createSearchDP(self):
        return RequestDataProvider(self)

    def _makeFilters(self):
        return [{'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ACTUAL, value=self.formatInvitesCount(self.actualRequestsPaginator))}, {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_EXPIRED, value=self.formatInvitesCount(self.expiredRequestsPaginator))}, {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_PROCESSED, value=self.formatInvitesCount(self.processedRequestsPaginator))}]

    def _makeTexts(self):
        texts = super(ClanRequestsView, self)._makeTexts()
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_ACTUAL,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOACTUALREQUESTS_TITLE,
         'text': CLANS.CLANINVITESWINDOW_DUMMY_NOACTUALREQUESTS_TEXT})
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_EXPIRED,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOEXPIREDREQUESTS_TITLE,
         'text': CLANS.CLANINVITESWINDOW_DUMMY_NOEXPIREDREQUESTS_TITLE})
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_PROCESSED,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOPROCESSEDREQUESTS_TITLE})
        return texts

    def _makeHeaders(self):
        return [self._packHeaderColumnData('userName', CLANS.CLANINVITESWINDOW_TABLE_USERNAME, 225, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_USERNAME, textAlign='left'),
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

    def getStatusByDbID(self, dbID):
        return self.getExtraData(dbID)

    def _buildExtraData(self, item, prevExtra):
        return item.getStatus()

    def _makeVO(self, item, extraData):
        return {'dbID': item.getDbID(),
         'userInfo': {'userName': item.getAccountName(),
                      'dbID': item.getAccountDbID()},
         'personalRating': formatField(getter=item.getPersonalRating, formatter=BigWorld.wg_getIntegralFormat),
         'battlesCount': formatField(getter=item.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat),
         'wins': formatField(getter=item.getBattlesPerformanceAvg, formatter=lambda value: BigWorld.wg_getNiceNumberFormat(value) + '%'),
         'awgExp': formatField(getter=item.getBattleXpAvg, formatter=BigWorld.wg_getIntegralFormat),
         'status': {'text': self._makeInviteStateString(item),
                    'tooltip': self._makeTooltip(body=self._makeRequestTooltip(status=item.getStatus(), user=formatField(getter=item.getSenderName), date=formatField(getter=item.getUpdatedAt, formatter=formatters.formatShortDateShortTimeString)))},
         'canShowContextMenu': True,
         'messageTooltip': self._makeTooltip(body=item.getComment() if isValueAvailable(getter=item.getComment) else str()),
         'actions': self.__buildActionsSection(item.getStatus())}

    def invalidateItems(self):
        for item in self.collection:
            if self._isDataRow(item):
                item['actions'] = self.__buildActionsSection(self.getStatusByDbID(item['dbID']))

    def __buildActionsSection(self, inviteStatus):
        acceptButtonEnabled = False
        declineButtonEnabled = False
        inviteButtonEnabled = False
        acceptButtonVisible = False
        declineButtonVisible = False
        inviteButtonVisible = False
        inviteButtonTooltip = None
        acceptButtonTooltip = None
        clanHasFreeSpaces = self.proxy.clanInfo.hasFreePlaces()
        if self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            if inviteStatus == CLAN_INVITE_STATES.ACTIVE:
                declineButtonVisible = True
                acceptButtonVisible = True
                declineButtonEnabled = self.isActionsAllowed()
                if not clanHasFreeSpaces:
                    acceptButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTSENDINVITE_BODY
                else:
                    acceptButtonEnabled = self.isActionsAllowed()
        elif self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            if inviteStatus == CLAN_INVITE_STATES.EXPIRED:
                inviteButtonVisible = True
                if not clanHasFreeSpaces:
                    inviteButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTACCEPTREQUEST_BODY
                else:
                    inviteButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_INVITEBUTTON
                    inviteButtonEnabled = self.isActionsAllowed()
        elif self.proxy.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            if inviteStatus == CLAN_INVITE_STATES.DECLINED:
                inviteButtonVisible = True
                if not clanHasFreeSpaces:
                    inviteButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTACCEPTREQUEST_BODY
                else:
                    inviteButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_INVITEBUTTON
                    inviteButtonEnabled = self.isActionsAllowed()
        return {'acceptButtonEnabled': acceptButtonEnabled,
         'declineButtonEnabled': declineButtonEnabled,
         'inviteButtonEnabled': inviteButtonEnabled,
         'acceptButtonVisible': acceptButtonVisible,
         'declineButtonVisible': declineButtonVisible,
         'inviteButtonVisible': inviteButtonVisible,
         'inviteButtonText': _ms(CLANS.CLANINVITESWINDOW_TABLE_INVITEBUTTON),
         'inviteButtonTooltip': self._makeTooltip(body=_ms(inviteButtonTooltip)),
         'acceptButtonTooltip': self._makeTooltip(body=_ms(acceptButtonTooltip))}
