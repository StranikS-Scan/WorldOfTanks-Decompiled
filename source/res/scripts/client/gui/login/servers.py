# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/Servers.py
import BigWorld
import Settings
from gui import GUI_SETTINGS
from Event import Event
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE

class Servers(object):
    onServersStatusChanged = Event()

    def __init__(self, loginPreferences):
        self._loginPreferences = loginPreferences
        s = Settings.g_instance
        g_preDefinedHosts.readScriptConfig(s.scriptConfig, s.userPrefs)
        g_preDefinedHosts.onCsisQueryStart += self.__onServerUpdate
        g_preDefinedHosts.onPingPerformed += self.__onServerUpdate
        g_preDefinedHosts.onCsisQueryComplete += self.__onServerUpdate
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
            g_preDefinedHosts.startCSISUpdate()
        g_preDefinedHosts.requestPing()
        self._serverList = []
        self._selectedServerIdx = 0
        self.updateServerList()

    def fini(self):
        g_preDefinedHosts.stopCSISUpdate()
        g_preDefinedHosts.onCsisQueryStart -= self.__onServerUpdate
        g_preDefinedHosts.onPingPerformed -= self.__onServerUpdate
        g_preDefinedHosts.onCsisQueryComplete -= self.__onServerUpdate
        self._serverList = None
        return

    def updateServerList(self):
        self._setServerList(g_preDefinedHosts.shortList())

    def _setServerList(self, baseServerList):
        self._serverList = []
        self._selectedServerIdx = 0
        serverName = self._loginPreferences['server_name']
        for idx, (hostName, friendlyName, csisStatus, _) in enumerate(baseServerList):
            if serverName == hostName:
                self._selectedServerIdx = idx
            self._serverList.append({'label': friendlyName,
             'data': hostName,
             'csisStatus': csisStatus})

    def startListenCsisQuery(self, startListen):
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ON_REQUEST:
            if startListen:
                g_preDefinedHosts.startCSISUpdate()
            else:
                g_preDefinedHosts.stopCSISUpdate()
        if startListen:
            g_preDefinedHosts.requestPing(True)

    @property
    def serverList(self):
        return self._serverList

    @property
    def selectedServerIdx(self):
        return self._selectedServerIdx

    @property
    def selectedServer(self):
        return self._serverList[self._selectedServerIdx] if self._selectedServerIdx < len(self._serverList) else None

    def __onServerUpdate(self, _=None):
        self.updateServerList()
        self.onServersStatusChanged(self._serverList)


class DevelopmentServers(Servers):

    def __init__(self, loginPreferences):
        Servers.__init__(self, loginPreferences)
        BigWorld.serverDiscovery.changeNotifier = self.updateServerList
        BigWorld.serverDiscovery.searching = 1

    def fini(self):
        Servers.fini(self)
        BigWorld.serverDiscovery.searching = 0

    def updateServerList(self):

        def _serverDottedHost(ip):
            return '%d.%d.%d.%d' % (ip >> 24 & 255,
             ip >> 16 & 255,
             ip >> 8 & 255,
             ip >> 0 & 255)

        def _serverNetName(details):
            name = _serverDottedHost(details.ip)
            if details.port:
                name += ':%d' % details.port
                return name

        def _serverNiceName(details):
            name = details.hostName
            if not name:
                name = _serverNetName(details)
            elif details.port:
                name += ':%d' % details.port
            if details.ownerName:
                name += ' (' + details.ownerName + ')'
            return name

        servers = [ (_serverNiceName(server), server.serverString) for server in BigWorld.serverDiscovery.servers ]
        baseServerList = g_preDefinedHosts.shortList()
        for friendlyName, hostName in servers:
            if not g_preDefinedHosts.predefined(hostName):
                baseServerList.append((hostName,
                 friendlyName,
                 g_preDefinedHosts.getDefaultCSISStatus(),
                 None))

        self._setServerList(baseServerList)
        return
