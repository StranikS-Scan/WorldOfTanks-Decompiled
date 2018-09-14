# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanPersonalInvitesView.py
import BigWorld
from gui.clans import formatters
from gui.clans.clan_controller import g_clanCtrl
from gui.clans.clan_helpers import ClanPersonalInvitesPaginator, ClanListener
from gui.clans.items import ClanCommonData, formatField, isValueAvailable
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLAN_INVITE_STATES
from gui.Scaleform.daapi.view.lobby.clans.invites.ClanInvitesViewWithTable import ClanInvitesAbstractDataProvider
from gui.Scaleform.daapi.view.meta.ClanPersonalInvitesViewMeta import ClanPersonalInvitesViewMeta
from gui.Scaleform.genConsts.CLANS_ALIASES import CLANS_ALIASES
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.events import CoolDownEvent
from gui.shared.utils.functions import makeTooltip
from gui.shared.view_helpers import CooldownHelper
from gui.shared.utils import getPlayerDatabaseID
from helpers.i18n import makeString as _ms

class ClanPersonalInvitesView(ClanPersonalInvitesViewMeta, ClanListener):
    __coolDownRequests = [CLAN_REQUESTED_DATA_TYPE.ACCEPT_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES]

    def __init__(self):
        super(ClanPersonalInvitesView, self).__init__()
        self._paginator = ClanPersonalInvitesPaginator(g_clanCtrl, getPlayerDatabaseID(), [CLAN_INVITE_STATES.ACTIVE])
        self._cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.CLAN)

    def declineAllSelectedInvites(self):
        self._paginator.declineList(self.dataProvider.getCheckedIDs())

    def acceptInvite(self, dbID):
        self._paginator.accept(int(dbID))

    def declineInvite(self, dbID):
        self._paginator.decline(int(dbID))

    def showMore(self):
        if not self._paginator.isInProgress():
            self.showWaiting(True)
            self._paginator.right()

    def setSelectAllInvitesCheckBoxSelected(self, checked):
        self.dataProvider.setSelectAll(checked)
        self._updateDeclineSelectedGroup()

    def setInviteSelected(self, dbID, checked):
        self.dataProvider.setCheckedID(dbID, checked)
        self._updateDeclineSelectedGroup()

    def onSortChanged(self, dataProvider, sort):
        order = sort[0][1]
        secondSort = tuple(((item, order) for item in self._getSecondSortFields()))
        if not self._paginator.isInProgress():
            self.showWaiting(True)
            self._paginator.sort(sort + secondSort)

    def onAccountInvitesReceived(self, invites):
        super(ClanPersonalInvitesView, self).onAccountInvitesReceived(invites)
        self._enableRefreshBtn(True)

    def showWaiting(self, show):
        if show:
            self._parentWnd.as_showWaitingS(CLANS.CLANPERSONALINVITESWINDOW_LOADING, {})
        elif not self._paginator.isInProgress():
            self._parentWnd.as_hideWaitingS()

    def refreshTable(self):
        self._enableRefreshBtn(False)
        self.showWaiting(True)
        self._paginator.refresh()

    def _createSearchDP(self):
        return PersonalInvitesDataProvider(self)

    def _onAttachedToWindow(self):
        super(ClanPersonalInvitesView, self)._onAttachedToWindow()
        self.showWaiting(True)
        self.setSelectAllInvitesCheckBoxSelected(False)
        self._updateDeclineSelectedText(0)
        self._cooldown.start()
        self._paginator.onListUpdated += self._onListUpdated
        self._paginator.onListItemsUpdated += self._onListItemsUpdated
        self._paginator.reset()

    def _populate(self):
        super(ClanPersonalInvitesView, self)._populate()
        self.startClanListening()

    def _dispose(self):
        self._paginator.onListUpdated -= self._onListUpdated
        self._paginator.onListItemsUpdated -= self._onListItemsUpdated
        self._cooldown.stop()
        self._cooldown = None
        self.stopClanListening()
        g_clanCtrl.clearClanCommonDataCache()
        super(ClanPersonalInvitesView, self)._dispose()
        return

    def _onCooldownHandle(self, isInCooldown):
        self.showWaiting(isInCooldown)

    def _onListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        self._updateSortField(self._paginator.getLastSort())
        status, data = result
        if status is True:
            self._enableRefreshBtn(False)
            if len(data) == 0:
                self.as_showDummyS(CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_PERSONAL_INVITES)
                self.dataProvider.rebuildList(None, False)
            else:
                g_clanCtrl.updateClanCommonDataCache([ ClanCommonData.fromClanPersonalInviteWrapper(item) for item in data ])
                self.dataProvider.rebuildList(data, self._paginator.canMoveRight())
                self.as_hideDummyS()
        else:
            self._enableRefreshBtn(True, toolTip=CLANS.CLANINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_ENABLEDTRYTOREFRESH)
            self.as_showDummyS(CLANS_ALIASES.INVITE_WINDOW_DUMMY_SERVER_ERROR)
        self._updateDeclineSelectedGroup()
        self.showWaiting(False)
        return

    def _onListItemsUpdated(self, paginator, items):
        self.dataProvider.refreshItems(items)
        self._updateDeclineSelectedGroup()
        if not self._paginator.isInProgress():
            self.showWaiting(False)

    def _updateDeclineSelectedGroup(self):
        hasInvites = self.dataProvider.itemsCount() > 0
        self._updateDeclineSelectedText(self.dataProvider.selectedCount())
        self.as_setSelectAllCheckboxStateS(self.dataProvider.areAllSelected(), hasInvites)

    def _updateDeclineSelectedText(self, count):
        self.as_setDeclineAllSelectedInvitesStateS(_ms(CLANS.CLANPERSONALINVITESWINDOW_DECLINESELECTED, count=count), False if count == 0 or self._paginator.isInProgress() else True)

    def _getSecondSortFields(self):
        return ('createdAt',)

    def _makeHeaders(self):
        return [self._packHeaderColumnData('clanName', CLANS.CLANPERSONALINVITESWINDOW_TABLE_CLANNAME, 233, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_CLANNAME, textAlign='left', enabled=True),
         self._packHeaderColumnData('message', '', 73, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_MESSAGE, RES_ICONS.MAPS_ICONS_CLANS_INVITESWINDOW_ICON_STATISTICS_CLAN_INVITE_098, enabled=True),
         self._packHeaderColumnData('personalRating', '', 98, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_RATING, RES_ICONS.MAPS_ICONS_STATISTIC_RATING24, enabled=True),
         self._packHeaderColumnData('battlesCount', '', 98, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_BATTLESCOUNT, RES_ICONS.MAPS_ICONS_STATISTIC_BATTLES24, enabled=True),
         self._packHeaderColumnData('wins', '', 98, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_WINS, RES_ICONS.MAPS_ICONS_STATISTIC_WINS24, enabled=True),
         self._packHeaderColumnData('awgExp', '', 98, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_AWGEXP, RES_ICONS.MAPS_ICONS_STATISTIC_AVGEXP24, enabled=True),
         self._packHeaderColumnData('status', CLANS.CLANPERSONALINVITESWINDOW_TABLE_STATUS, 160, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_INVITES_STATUS, enabled=True),
         self._packHeaderColumnData('actions', CLANS.CLANPERSONALINVITESWINDOW_TABLE_ACTIONS, 132, CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_TABLE_REQUESTS_ACTIONS, enabled=False)]

    def _makeTexts(self):
        texts = super(ClanPersonalInvitesView, self)._makeTexts()
        texts.append({'alias': CLANS_ALIASES.INVITE_WINDOW_DUMMY_NO_PERSONAL_INVITES,
         'title': CLANS.CLANPERSONALINVITESWINDOW_NOINVITES})
        return texts

    def _enableRefreshBtn(self, enable, toolTip = None):
        if enable:
            self.as_updateButtonRefreshStateS(True, makeTooltip(body=_ms(toolTip or CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_ENABLED)))
        else:
            self.as_updateButtonRefreshStateS(False, makeTooltip(body=_ms(toolTip or CLANS.CLANPERSONALINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_DISABLED)))


class PersonalInvitesDataProvider(ClanInvitesAbstractDataProvider):

    def __init__(self, proxy):
        super(PersonalInvitesDataProvider, self).__init__(proxy)
        self._selectedCount = 0

    def selectedCount(self):
        return self._selectedCount

    def areAllSelected(self):
        for item in self.collection:
            if self._isDataRow(item) and not item['checked']:
                return False

        return True

    def setSelectAll(self, select):
        self._selectedCount = 0
        for item in self.collection:
            if self._isDataRow(item) and item['enabled']:
                item['checked'] = select
                self.getExtraData(item['dbID'])['checked'] = select
                if select:
                    self._selectedCount += 1

        self.refresh()

    def setCheckedID(self, dbID, checked):
        self.getVOByDbID(dbID)['checked'] = checked
        self.getExtraData(dbID)['checked'] = checked
        self._selectedCount += 1 if checked else -1
        self.refresh()

    def getCheckedIDs(self):
        return [ item['dbID'] for item in self.collection if self._isDataRow(item) and item['checked'] ]

    def getStatusByDbID(self, dbID):
        return self.getExtraData(dbID)['status']

    def buildList(self, cache, showMoreButton = False):
        super(PersonalInvitesDataProvider, self).buildList(cache, showMoreButton)
        self._invalidateSelectedCount()

    def refreshItems(self, items):
        super(PersonalInvitesDataProvider, self).refreshItems(items)
        self._invalidateSelectedCount()

    def invalidateItems(self):
        for item in self.collection:
            if self._isDataRow(item):
                item['checked'] = self.getExtraData(item['dbID'])['checked']
                item['actions'] = self.__buildActionsSection(self.getStatusByDbID(item['dbID']))

    def _invalidateSelectedCount(self):
        self._selectedCount = 0
        for item in self.collection:
            if self._isDataRow(item) and item['checked']:
                self._selectedCount += 1

    def _buildExtraData(self, item, prevExtra):
        checked = False
        if item.getStatus() == CLAN_INVITE_STATES.ACTIVE and prevExtra:
            checked = prevExtra.get('checked', False)
        return {'status': item.getStatus(),
         'checked': checked}

    def _makeVO(self, item, extraData):
        isChecked = extraData['checked']
        status = item.getStatus()
        outcome = {'dbID': item.getDbID(),
         'checked': isChecked,
         'clanVO': {'fullName': formatField(getter=item.getClanFullName),
                    'clanName': formatField(getter=item.getClanName),
                    'clanAbbrev': formatField(getter=item.getClanAbbrev),
                    'dbID': item.getClanDbID(),
                    'isActive': item.isClanActive()},
         'personalRating': formatField(getter=item.getPersonalRating, formatter=BigWorld.wg_getIntegralFormat),
         'battlesCount': formatField(getter=item.getBattlesCount, formatter=BigWorld.wg_getIntegralFormat),
         'wins': formatField(getter=item.getBattleXpAvg, formatter=lambda value: BigWorld.wg_getNiceNumberFormat(value) + '%'),
         'awgExp': formatField(getter=item.getBattlesPerformanceAvg, formatter=BigWorld.wg_getIntegralFormat),
         'status': {'text': self._makeInviteStateString(item),
                    'tooltip': self._makeTooltip(body=self._makeRequestTooltip(status=item.getStatus(), user=formatField(getter=item.getSenderName), date=formatField(getter=item.getUpdatedAt, formatter=formatters.formatShortDateShortTimeString)))},
         'enabled': status == CLAN_INVITE_STATES.ACTIVE or status == CLAN_INVITE_STATES.ERROR,
         'canShowContextMenu': True,
         'messageTooltip': self._makeTooltip(body=item.getComment() if isValueAvailable(getter=item.getComment) else str()),
         'actions': self.__buildActionsSection(item.getStatus())}
        return outcome

    def __buildActionsSection(self, inviteStatus):
        acceptButtonEnabled = False
        declineButtonEnabled = False
        acceptButtonVisible = False
        declineButtonVisible = False
        acceptButtonTooltip = None
        clanHasFreeSpaces = True
        clanAcceptJoinRequests = True
        if inviteStatus == CLAN_INVITE_STATES.ACTIVE:
            declineButtonVisible = True
            acceptButtonVisible = True
            declineButtonEnabled = self.isActionsAllowed()
            if not clanAcceptJoinRequests:
                acceptButtonTooltip = CLANS.CLANINVITESWINDOW_HEADER_TOOLTIPS_RECRUITEMENTSTOPPED
            elif not clanHasFreeSpaces:
                acceptButtonTooltip = CLANS.CLANINVITESWINDOW_TOOLTIPS_TABLE_CANTSENDINVITE_BODY
            else:
                acceptButtonEnabled = self.isActionsAllowed()
        return {'acceptButtonEnabled': acceptButtonEnabled,
         'declineButtonEnabled': declineButtonEnabled,
         'acceptButtonVisible': acceptButtonVisible,
         'declineButtonVisible': declineButtonVisible,
         'acceptButtonTooltip': self._makeTooltip(body=_ms(acceptButtonTooltip))}
