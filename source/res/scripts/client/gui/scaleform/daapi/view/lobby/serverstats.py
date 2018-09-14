# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/ServerStats.py
import BigWorld
import constants
from adisp import process
from debug_utils import LOG_DEBUG
from helpers import i18n
from ConnectionManager import connectionManager
from predefined_hosts import g_preDefinedHosts, HOST_AVAILABILITY, REQUEST_RATE
from gui import GUI_SETTINGS, game_control, DialogsInterface, makeHtmlString
from gui.prb_control.prb_helpers import PrbListener
from gui.shared import events
from gui.shared.utils.functions import makeTooltip
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.view.meta.ServerStatsMeta import ServerStatsMeta

class ServerStats(ServerStatsMeta, PrbListener):

    def __init__(self):
        super(ServerStats, self).__init__()
        self.__serversList = []
        self.__isGuiUpdateSuppressed = False

    @process
    def relogin(self, peripheryID):
        self.__isGuiUpdateSuppressed = True
        if g_preDefinedHosts.isRoamingPeriphery(peripheryID):
            success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
        else:
            success = yield DialogsInterface.showI18nConfirmDialog('changePeriphery')
        if success:
            game_control.g_instance.relogin.doRelogin(peripheryID)
        self.__isGuiUpdateSuppressed = False
        self.as_setPeripheryChangingS(success)

    def isCSISUpdateOnRequest(self):
        return GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST

    def startListenCsisUpdate(self, startListenCsis):
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST:
            if startListenCsis:
                g_preDefinedHosts.startCSISUpdate()
            else:
                g_preDefinedHosts.stopCSISUpdate()
                self._updateServersList()

    def getServers(self):
        return self.__serversList

    def _populate(self):
        super(ServerStats, self)._populate()
        if constants.IS_SHOW_SERVER_STATS:
            self._updateCurrentServerInfo()
        self._updateServersList()
        self._updateRoamingCtrl()
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
            g_preDefinedHosts.startCSISUpdate()
        g_preDefinedHosts.onCsisQueryStart += self.__onCsisUpdate
        g_preDefinedHosts.onCsisQueryComplete += self.__onCsisUpdate
        game_control.g_instance.serverStats.onStatsReceived += self.__onStatsReceived
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateRoamingCtrl, scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.__clearServersList()
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self._updateRoamingCtrl, scope=EVENT_BUS_SCOPE.LOBBY)
        game_control.g_instance.serverStats.onStatsReceived -= self.__onStatsReceived
        g_preDefinedHosts.stopCSISUpdate()
        g_preDefinedHosts.onCsisQueryComplete -= self.__onCsisUpdate
        g_preDefinedHosts.onCsisQueryStart -= self.__onCsisUpdate
        super(ServerStats, self)._dispose()

    def _updateCurrentServerInfo(self):
        from ConnectionManager import connectionManager
        if connectionManager.serverUserName:
            tooltipBody = i18n.makeString('#tooltips:header/info/players_online_full/body')
            tooltipFullData = makeTooltip('#tooltips:header/info/players_online_full/header', tooltipBody % {'servername': connectionManager.serverUserName})
            self.as_setServerStatsInfoS(tooltipFullData)
        self.__onStatsReceived(game_control.g_instance.serverStats.getStats())

    def _updateServersList(self):
        self.__serversList = []
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        for key, name, csisStatus, peripheryID in hostsList:
            self.__serversList.append({'label': self.__wrapServerName(name),
             'id': peripheryID,
             'csisStatus': csisStatus,
             'selected': connectionManager.peripheryID == peripheryID})

        if connectionManager.peripheryID == 0:
            self.__serversList.insert(0, {'label': self.__wrapServerName(connectionManager.serverUserName),
             'id': 0,
             'csisStatus': HOST_AVAILABILITY.IGNORED,
             'selected': True})
        if not self.__isGuiUpdateSuppressed:
            self.as_setServersListS(self.__serversList)

    def _updateRoamingCtrl(self, event = None):
        isRoamingCtrlDisabled = False
        if self.prbDispatcher:
            for func in self.prbDispatcher.getFunctionalCollection().getIterator():
                if func.hasLockedState():
                    isRoamingCtrlDisabled = True
                    break

        self.as_disableRoamingDDS(isRoamingCtrlDisabled)

    def __onStatsReceived(self, stats):
        if constants.IS_SHOW_SERVER_STATS:
            self.as_setServerStatsS(*game_control.g_instance.serverStats.getFormattedStats())

    def __onCsisUpdate(self, response = None):
        self._updateServersList()

    def __clearServersList(self):
        while len(self.__serversList):
            self.__serversList.pop().clear()

    def __wrapServerName(self, name):
        if constants.IS_CHINA:
            return makeHtmlString('html_templates:lobby/serverStats', 'serverName', {'name': name})
        return name
