# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ServerStats.py
import logging
import BigWorld
import constants
from wg_async import wg_await, wg_async
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.impl.dialogs.builders import ResSimpleDialogBuilder
from gui.impl.dialogs.dialogs import showSimple
from gui.impl.gen import R
from gui.impl.pub.dialog_window import DialogFlags
from gui.prb_control.entities.base.legacy.listener import ILegacyListener
from helpers import dependency
from helpers import i18n
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY, REQUEST_RATE
from gui import GUI_SETTINGS
from gui.shared import events
from gui.shared.utils.functions import makeTooltip
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.ServerStatsMeta import ServerStatsMeta
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IServerStatsController, IReloginController
_logger = logging.getLogger(__name__)

class ServerStats(ServerStatsMeta, ILegacyListener):
    serverStats = dependency.descriptor(IServerStatsController)
    reloginCtrl = dependency.descriptor(IReloginController)
    connectionMgr = dependency.descriptor(IConnectionManager)
    _settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(ServerStats, self).__init__()
        self.__isListSelected = False

    @wg_async
    def relogin(self, peripheryID):
        confirmationType = 'changePeripheryAndRemember'
        if g_preDefinedHosts.isRoamingPeriphery(peripheryID):
            _logger.debug('g_preDefinedHosts.isRoamingPeriphery(%(peripheryID)s)', peripheryID)
            confirmationType = 'changeRoamingPeriphery'
        builder = ResSimpleDialogBuilder()
        builder.setFlags(DialogFlags.TOP_FULLSCREEN_WINDOW)
        builder.setMessagesAndButtons(R.strings.dialogs.dyn(confirmationType))
        success = yield wg_await(showSimple(builder.buildInLobby()))
        if success:
            BigWorld.callback(0.0, lambda : self.reloginCtrl.doRelogin(peripheryID, self.__onReloing))
        else:
            self.as_changePeripheryFailedS()

    def startListenCsisUpdate(self, startListen):
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST:
            if startListen:
                g_preDefinedHosts.startCSISUpdate()
            else:
                g_preDefinedHosts.stopCSISUpdate()
                self._updateServersList()
        if startListen:
            g_preDefinedHosts.requestPing(True)

    def _populate(self):
        super(ServerStats, self)._populate()
        self._serversDP = ServersDataProvider()
        self._serversDP.setFlashObject(self.as_getServersDPS())
        if constants.IS_SHOW_SERVER_STATS:
            self._updateCurrentServerInfo()
        self._updateServersList()
        self._updateRoamingCtrl()
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
            g_preDefinedHosts.startCSISUpdate()
        g_preDefinedHosts.onCsisQueryStart += self.__onServersUpdate
        g_preDefinedHosts.onCsisQueryComplete += self.__onServersUpdate
        g_preDefinedHosts.onPingPerformed += self.__onServersUpdate
        self.serverStats.onStatsReceived += self.__onStatsReceived
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateRoamingCtrl, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateRoamingCtrl, scope=EVENT_BUS_SCOPE.LOBBY)
        self.serverStats.onStatsReceived -= self.__onStatsReceived
        g_preDefinedHosts.stopCSISUpdate()
        g_preDefinedHosts.onCsisQueryComplete -= self.__onServersUpdate
        g_preDefinedHosts.onCsisQueryStart -= self.__onServersUpdate
        g_preDefinedHosts.onPingPerformed -= self.__onServersUpdate
        self._serversDP.fini()
        self._serversDP = None
        super(ServerStats, self)._dispose()
        return

    def _updateCurrentServerInfo(self):
        if self.connectionMgr.serverUserName:
            tooltipBody = i18n.makeString('#tooltips:header/info/players_online_full/body')
            tooltipFullData = makeTooltip('#tooltips:header/info/players_online_full/header', tooltipBody % {'servername': self.connectionMgr.serverUserName})
            self.as_setServerStatsInfoS(tooltipFullData)
        self.__onStatsReceived()

    def _updateServersList(self):
        result = []
        simpleHostList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        if simpleHostList:
            for idx, (hostName, name, csisStatus, peripheryID) in enumerate(simpleHostList):
                result.append({'label': name,
                 'data': hostName,
                 'id': peripheryID,
                 'csisStatus': csisStatus})

        if self.connectionMgr.peripheryID == 0:
            result.insert(0, {'label': self.connectionMgr.serverUserName,
             'id': 0,
             'csisStatus': HOST_AVAILABILITY.IGNORED,
             'data': self.connectionMgr.url})
        if not self.__isListSelected:
            self.__isListSelected = True
            index = 0
            if self.connectionMgr.peripheryID != 0:
                for idx, (hostName, name, csisStatus, peripheryID) in enumerate(simpleHostList):
                    if hostName == self.connectionMgr.url:
                        index = idx
                        break

            self.as_setSelectedServerIndexS(index)
        self._serversDP.rebuildList(result)

    def _updateRoamingCtrl(self, event=None):
        isRoamingCtrlDisabled = False
        if self.prbDispatcher:
            isRoamingCtrlDisabled = self.prbDispatcher.getEntity().hasLockedState()
        self.as_disableRoamingDDS(isRoamingCtrlDisabled)

    def __onStatsReceived(self):
        if constants.IS_SHOW_SERVER_STATS:
            self.as_setServerStatsS(*self.serverStats.getFormattedStats())

    def __onServersUpdate(self, _=None):
        self._updateServersList()

    def __onReloing(self, isCompleted):
        if not isCompleted:
            self.as_changePeripheryFailedS()
