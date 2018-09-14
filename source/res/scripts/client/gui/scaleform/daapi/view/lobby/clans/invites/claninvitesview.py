# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanInvitesView.py
import BigWorld
from gui.clans import formatters
from gui.clans.items import formatField, isValueAvailable
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesAbstractDataProvider
from gui.Scaleform.daapi.view.meta.ClanInvitesViewMeta import ClanInvitesViewMeta
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesWindowAbstractTabView import *
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from debug_utils import LOG_DEBUG

class ClanInvitesView(ClanInvitesViewMeta):

    def __init__(self):
        super(ClanInvitesView, self).__init__()

    @property
    def allInvitesPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL)

    @property
    def actualInvitesPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL)

    @property
    def expiredInvitesPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED)

    @property
    def processedInvitesPaginator(self):
        return self._getPaginatorByFilterName(CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED)

    def _populate(self):
        super(ClanInvitesView, self)._populate()

    def _onAttachedToWindow(self):
        super(ClanInvitesView, self)._onAttachedToWindow()
        self.allInvitesPaginator.onListUpdated += self._onListUpdated
        self.allInvitesPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.actualInvitesPaginator.onListUpdated += self._onListUpdated
        self.actualInvitesPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.expiredInvitesPaginator.onListUpdated += self._onListUpdated
        self.expiredInvitesPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.processedInvitesPaginator.onListUpdated += self._onListUpdated
        self.processedInvitesPaginator.onListItemsUpdated += self._onListItemsUpdated
        self.filterBy(self.currentFilterName)

    def _dispose(self):
        self.allInvitesPaginator.onListUpdated -= self._onListUpdated
        self.allInvitesPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self.actualInvitesPaginator.onListUpdated -= self._onListUpdated
        self.actualInvitesPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self.expiredInvitesPaginator.onListUpdated -= self._onListUpdated
        self.expiredInvitesPaginator.onListItemsUpdated -= self._onListItemsUpdated
        self.processedInvitesPaginator.onListUpdated -= self._onListUpdated
        self.processedInvitesPaginator.onListItemsUpdated -= self._onListItemsUpdated
        super(ClanInvitesView, self)._dispose()

    def _createSearchDP(self):
        return InviteDataProvider(self)

    def _getViewAlias(self):
        return CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS

    def _getDummyByFilterName(self, filterName):
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_ALL
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_ACTUAL
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_EXPIRED
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_PROCESSED
        LOG_DEBUG('Unexpected behaviour: no dummy for filter', filterName)
        return CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_ALL

    def _getDefaultFilterName(self):
        return CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED

    def _getDefaultSortFields(self):
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
            return (('personalRating', False),)
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL or self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            return (('sent', False),)
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            return (('status', False),)
        return (('status', False),)

    def _getSecondSortFields(self):
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            return ('updatedAt',)
        else:
            return ('createdAt',)

    def _makeFilters(self):
        return [{'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ALL, value=self.formatInvitesCount(self.allInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ACTUAL, value=self.formatInvitesCount(self.actualInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_EXPIRED, value=self.formatInvitesCount(self.expiredInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_HASANSWER, value=self.formatInvitesCount(self.processedInvitesPaginator))}]

    def _makeTexts(self):
        texts = super(ClanInvitesView, self)._makeTexts()
        inviteText = _ms(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_TEXT, invite=text_styles.main(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_INVITE))
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_ALL,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_TITLE,
         'text': inviteText})
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_ACTUAL,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESACTUAL_TITLE,
         'text': inviteText})
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_EXPIRED,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESEXPIRED_TITLE,
         'text': inviteText})
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_INVITES_PROCESSED,
         'title': CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESPROCESSED_TITLE,
         'text': inviteText})
        return texts

    def _makeHeaders(self):
        return [self._packHeaderColumnData('userName', CLANS.CLANINVITESWINDOW_TABLE_USERNAME, 225, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_USERNAME, textAlign='left'),
         self._packHeaderColumnData('message', '', 73, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_MESSAGE, RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_ICON_STATISTICS_CLAN_INVITE_098),
         self._packHeaderColumnData('personalRating', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_PERSONALRATING, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         self._packHeaderColumnData('battlesCount', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_BATTLESCOUNT, RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
         self._packHeaderColumnData('wins', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_WINS, RES_ICONS.MAPS_ICONS_STATISTIC_WINS24),
         self._packHeaderColumnData('awgExp', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_AWGEXP, RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
         self._packHeaderColumnData('status', CLANS.CLANINVITESWINDOW_TABLE_STATUS, 150, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_STATUS),
         self._packHeaderColumnData('sent', CLANS.CLANINVITESWINDOW_TABLE_SENT, 150, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_SENT)]


class InviteDataProvider(ClanInvitesAbstractDataProvider):

    def __init__(self, proxy):
        super(InviteDataProvider, self).__init__(proxy)

    def _makeVO(self, item, extra):
        return {'dbID': item.getDbID(),
         'userInfo': {'userName': formatField(getter=item.getAccountName),
                      'dbID': item.getAccountDbID()},
         'personalRating': formatField(getter=item.getPersonalRating, formatter=BigWorld.wg_getIntegralFormat),
         'battlesCount': formatField(getter=item.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat),
         'wins': formatField(getter=item.getBattlesPerformanceAvg, formatter=lambda value: BigWorld.wg_getNiceNumberFormat(value) + '%'),
         'awgExp': formatField(getter=item.getBattleXpAvg, formatter=BigWorld.wg_getIntegralFormat),
         'status': {'text': self._makeInviteStateString(item),
                    'tooltip': self._makeTooltip(body=self._makeRequestTooltip(status=item.getStatus(), user=formatField(getter=item.getSenderName), date=formatField(getter=item.getUpdatedAt, formatter=formatters.formatShortDateShortTimeString)))},
         'canShowContextMenu': True,
         'messageTooltip': self._makeTooltip(body=item.getComment() if isValueAvailable(getter=item.getComment) else str()),
         'sent': formatField(getter=item.getCreatedAt, formatter=formatters.formatShortDateShortTimeString)}
