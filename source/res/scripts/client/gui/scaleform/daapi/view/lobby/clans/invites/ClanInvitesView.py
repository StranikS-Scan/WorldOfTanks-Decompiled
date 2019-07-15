# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanInvitesView.py
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import formatters
from gui.clans.items import formatField, isValueAvailable
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesAbstractDataProvider
from gui.Scaleform.daapi.view.meta.ClanInvitesViewMeta import ClanInvitesViewMeta
from gui.clans.settings import CLAN_INVITE_STATES
from gui.impl import backport
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from debug_utils import LOG_DEBUG

class ClanInvitesView(ClanInvitesViewMeta):

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

    def onClanInvitesCountReceived(self, clanDbID, invitesCount):
        super(ClanInvitesView, self).onClanInvitesCountReceived(clanDbID, invitesCount)
        if self.actualInvitesPaginator.isSynced():
            self._enableRefreshBtn(True)

    def _onAttachedToWindow(self):
        super(ClanInvitesView, self)._onAttachedToWindow()
        self.filterBy(self.currentFilterName)

    def _createSearchDP(self):
        return InviteDataProvider(self)

    def _getViewAlias(self):
        return CLANS_ALIASES.CLAN_PROFILE_INVITES_VIEW_ALIAS

    def _showDummyByFilterName(self, filterName):
        inviteText = _ms(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_TEXT, invite=text_styles.main(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_INVITE))
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_TITLE, inviteText)
        if filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESACTUAL_TITLE, inviteText)
        elif filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESEXPIRED_TITLE, inviteText)
        elif filterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED:
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITESPROCESSED_TITLE, inviteText)
        else:
            LOG_DEBUG('Unexpected behaviour: no dummy for filter', filterName)
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_NOINVITES_TITLE, inviteText)

    def _getDefaultFilterName(self):
        return CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED

    def _getDefaultSortFields(self):
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL:
            return (('personalRating', False),)
        if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL or self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED:
            return (('sent', False),)
        return (('status', False),) if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED else (('status', False),)

    def _getSecondSortFields(self):
        return ('updatedAt',) if self.currentFilterName == CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED else ('createdAt',)

    def _makeFilters(self):
        return [{'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ALL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ALL, value=self.formatInvitesCount(self.allInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_ACTUAL,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_ACTUAL, value=self.formatInvitesCount(self.actualInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_EXPIRED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_EXPIRED, value=self.formatInvitesCount(self.expiredInvitesPaginator))},
         {'alias': CLANS_ALIASES.INVITE_WINDOW_FILTER_PROCESSED,
          'text': _ms(CLANS.CLANINVITESWINDOW_FILTERS_HASANSWER, value=self.formatInvitesCount(self.processedInvitesPaginator))}]

    def _makeHeaders(self):
        return [self._packHeaderColumnData('userName', CLANS.CLANINVITESWINDOW_TABLE_USERNAME, 225, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_USERNAME, textAlign='left', defaultSortDirection='ascending'),
         self._packHeaderColumnData('message', '', 73, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_MESSAGE, RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_ICON_STATISTICS_CLAN_INVITE_098),
         self._packHeaderColumnData('personalRating', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_PERSONALRATING, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24),
         self._packHeaderColumnData('battlesCount', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_BATTLESCOUNT, RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24),
         self._packHeaderColumnData('wins', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_WINS, RES_ICONS.MAPS_ICONS_STATISTIC_WINS24),
         self._packHeaderColumnData('awgExp', '', 98, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_AWGEXP, RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24),
         self._packHeaderColumnData('status', CLANS.CLANINVITESWINDOW_TABLE_STATUS, 150, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_STATUS),
         self._packHeaderColumnData('sent', CLANS.CLANINVITESWINDOW_TABLE_SENT, 150, CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_INVITES_SENT)]


class InviteDataProvider(ClanInvitesAbstractDataProvider):

    def _makeVO(self, item, extra):
        return {'dbID': item.getDbID(),
         'userInfo': {'userName': formatField(getter=item.getAccountName),
                      'dbID': item.getAccountDbID()},
         'personalRating': formatField(getter=item.getPersonalRating, formatter=backport.getIntegralFormat),
         'battlesCount': formatField(getter=item.getBattlesCount, formatter=backport.getIntegralFormat),
         'wins': formatField(getter=item.getBattlesPerformanceAvg, formatter=lambda value: backport.getNiceNumberFormat(value) + '%'),
         'awgExp': formatField(getter=item.getBattleXpAvg, formatter=backport.getIntegralFormat),
         'status': {'text': self._makeInviteStateString(item),
                    'tooltip': self._makeTooltip(body=self._makeRequestTooltip(status=item.getStatus(), user=formatField(getter=item.getSenderName), date=formatField(getter=item.getUpdatedAt, formatter=formatters.formatShortDateShortTimeString)))},
         'canShowContextMenu': True,
         'messageTooltip': self._makeTooltip(body=item.getComment() if isValueAvailable(getter=item.getComment) else str()),
         'sent': formatField(getter=item.getCreatedAt, formatter=formatters.formatShortDateShortTimeString)}

    def _makeRequestTooltip(self, status, date, user=None):
        if status == CLAN_INVITE_STATES.ACCEPTED:
            return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_INVITEACCEPTED)), text_styles.main(date), text_styles.main(''), text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_BYUSER)), text_styles.stats(user))
        if status == CLAN_INVITE_STATES.DECLINED or status == CLAN_INVITE_STATES.DECLINED_RESENT:
            return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_INVITEDECLINED)), text_styles.main(date), text_styles.main(''), text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_BYUSER)), text_styles.stats(user))
        return text_styles.concatStylesToMultiLine(text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_INVITESENT)), text_styles.main(date), text_styles.main(''), text_styles.standard(_ms(CLANS.CLANINVITESWINDOW_TOOLTIPS_INVITE_SENDER)), text_styles.stats(user)) if status == CLAN_INVITE_STATES.ACTIVE or status == CLAN_INVITE_STATES.EXPIRED or status == CLAN_INVITE_STATES.EXPIRED_RESENT else None
