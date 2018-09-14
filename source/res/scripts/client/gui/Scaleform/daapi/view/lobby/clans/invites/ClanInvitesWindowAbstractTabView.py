# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/clans/invites/ClanInvitesWindowAbstractTabView.py
import weakref
from gui.Scaleform.daapi.view.meta.ClanInvitesWindowAbstractTabViewMeta import ClanInvitesWindowAbstractTabViewMeta
from gui.Scaleform.locale.CLANS import CLANS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans.clan_helpers import ClanListener, showClanInviteSystemMsg
from gui.clans.settings import CLAN_INVITE_STATES, CLAN_REQUESTED_DATA_TYPE
from gui.shared.events import CoolDownEvent
from gui.shared.view_helpers import CooldownHelper
from helpers.i18n import makeString as _ms
from gui.shared.utils.functions import makeTooltip

class _RefreshBtnStateController(object):
    __coolDownRequests = [CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS,
     CLAN_REQUESTED_DATA_TYPE.CREATE_INVITES,
     CLAN_REQUESTED_DATA_TYPE.ACCEPT_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_APPLICATION,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE,
     CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES]

    def __init__(self, view):
        super(_RefreshBtnStateController, self).__init__()
        self.__view = weakref.proxy(view)
        self.__cooldown = CooldownHelper(self.__coolDownRequests, self._onCooldownHandle, CoolDownEvent.CLAN)
        self.__isEnabled = False
        self.__tooltip = None
        self.__isInCooldown = False
        return

    def start(self):
        self.__cooldown.start()

    def stop(self):
        self.__cooldown.stop()
        self.__cooldown = None
        return

    def setEnabled(self, enable, toolTip=None):
        self.__isEnabled = enable
        self.__tooltip = toolTip
        if not self.__isInCooldown:
            self._updateState()

    def _onCooldownHandle(self, isInCooldown):
        self.__isInCooldown = isInCooldown
        self._updateState()

    def _updateState(self):
        if self.__isEnabled:
            self.__view.as_updateButtonRefreshStateS(not self.__cooldown.isInCooldown(), makeTooltip(body=_ms(self.__tooltip or CLANS.CLANINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_ENABLED)))
        else:
            self.__view.as_updateButtonRefreshStateS(False, makeTooltip(body=_ms(self.__tooltip or CLANS.CLANINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_DISABLED)))


class ClanInvitesWindowAbstractTabView(ClanInvitesWindowAbstractTabViewMeta, ClanListener):

    def __init__(self):
        super(ClanInvitesWindowAbstractTabView, self).__init__()
        self.__filterName = self._getDefaultFilterName()
        self.__refreshBtnController = _RefreshBtnStateController(self)

    @property
    def paginatorsController(self):
        return self._parentWnd.paginatorsController

    @property
    def currentFilterName(self):
        return self.__filterName

    @property
    def clanInfo(self):
        return self._parentWnd.clanInfo

    def onMembersListChanged(self, members):
        self.resyncClanInfo()

    def onClanInfoReceived(self, clanDbID, clanInfo):
        paginator = self._getCurrentPaginator()
        if paginator.isSynced():
            self._onListUpdated(None, True, True, (paginator.getLastStatus(), paginator.getLastResult()))
        return

    def resyncClanInfo(self, force=False):
        return self._parentWnd.resyncClanInfo(force=force)

    def showMore(self):
        self._sendShowMoreRequest(self._getCurrentPaginator())

    def refreshTable(self):
        self._enableRefreshBtn(False)
        self.paginatorsController.markPanginatorsAsUnSynced(self._getViewAlias())
        self._sendRefreshRequest(self._getCurrentPaginator())
        self.resyncClanInfo()

    def filterBy(self, filterName):
        self.__filterName = filterName
        paginator = self._getCurrentPaginator()
        if paginator.isSynced():
            self._onListUpdated(None, True, True, (paginator.getLastStatus(), paginator.getLastResult()))
        else:
            self._sendRefreshRequest(paginator)
        return

    def onSortChanged(self, dataProvider, sort):
        order = sort[0][1]
        secondSort = tuple(((item, order) for item in self._getSecondSortFields()))
        self._sendSortRequest(self._getCurrentPaginator(), sort + secondSort)

    def formatInvitesCount(self, paginator):
        return self._parentWnd.formatInvitesCount(paginator)

    def showWaiting(self, show):
        self._parentWnd.showWaiting(show)

    def _getViewAlias(self):
        raise NotImplementedError

    def _showDummyByFilterName(self, filterName):
        raise NotImplementedError

    def _getDefaultFilterName(self):
        raise NotImplementedError

    def _makeFilters(self):
        raise NotImplementedError

    def _getSecondSortFields(self):
        return tuple()

    def _onListUpdated(self, selectedID, isFullUpdate, isReqInCoolDown, result):
        self._updateFiltersState()
        paginator = self._getCurrentPaginator()
        status, data = result
        if status is True:
            if len(data) == 0:
                self._updateSortField(None)
                self._showDummyByFilterName(self.currentFilterName)
                self.dataProvider.rebuildList(None, False)
            else:
                self._updateSortField(paginator.getLastSort() or self._getDefaultSortFields())
                self.dataProvider.rebuildList(data, paginator.canMoveRight())
                self.as_hideDummyS()
        else:
            self._updateSortField(None)
            self._enableRefreshBtn(True, toolTip=CLANS.CLANINVITESWINDOW_TOOLTIPS_REFRESHBUTTON_ENABLEDTRYTOREFRESH)
            self._showDummy(CLANS.CLANINVITESWINDOW_DUMMY_SERVERERROR_TITLE, CLANS.CLANINVITESWINDOW_DUMMY_SERVERERROR_TEXT, RES_ICONS.MAPS_ICONS_LIBRARY_ALERTBIGICON, alignCenter=False)
        self.showWaiting(False)
        return

    def _onListItemsUpdated(self, paginator, items):
        currentPaginator = self._getCurrentPaginator()
        if currentPaginator == paginator:
            self.dataProvider.refreshItems(items)
        for item in items:
            status = item.getStatus()
            msgArgs = None
            if status == CLAN_INVITE_STATES.EXPIRED_RESENT or status == CLAN_INVITE_STATES.DECLINED_RESENT:
                msgArgs = (True, None)
            elif status == CLAN_INVITE_STATES.ERROR:
                msgArgs = (False, item.getStatusCode())
            if msgArgs:
                showClanInviteSystemMsg(item.getAccountName(), *msgArgs)

        return

    def _getPaginatorByFilterName(self, filterName):
        return self.paginatorsController.getPanginator(self._getViewAlias(), filterName)

    def _getCurrentPaginator(self):
        return self._getPaginatorByFilterName(self.currentFilterName)

    def _sendResetRequest(self, paginator):
        if not paginator.isInProgress():
            self.showWaiting(True)
            paginator.reset()

    def _sendShowMoreRequest(self, paginator):
        if not paginator.isInProgress():
            self.showWaiting(True)
            paginator.right()

    def _sendRefreshRequest(self, paginator):
        self.showWaiting(True)
        if not paginator.isInProgress():
            paginator.refresh()
        else:
            self.showWaiting(False)

    def _sendSortRequest(self, paginator, sort):
        if not paginator.isInProgress():
            self.showWaiting(True)
            paginator.sort(sort)

    def _populate(self):
        self.startClanListening()
        super(ClanInvitesWindowAbstractTabView, self)._populate()

    def _dispose(self):
        self.__refreshBtnController.stop()
        self.stopClanListening()
        super(ClanInvitesWindowAbstractTabView, self)._dispose()

    def _onAttachedToWindow(self):
        super(ClanInvitesWindowAbstractTabView, self)._onAttachedToWindow()
        self.__refreshBtnController.setEnabled(False)
        self.__refreshBtnController.start()

    def _makeData(self):
        data = super(ClanInvitesWindowAbstractTabView, self)._makeData()
        data['filters'] = self._makeFilters()
        data['defaultFilter'] = self._getDefaultFilterName()
        return data

    def _updateFiltersState(self):
        for item in self._makeFilters():
            self.as_updateFilterStateS(item)

    def _enableRefreshBtn(self, enable, toolTip=None):
        self.__refreshBtnController.setEnabled(enable, toolTip)
