# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prime_time_view_base.py
import time
import constants
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.prime_time_servers_data_provider import PrimeTimesServersDataProvider
from gui.Scaleform.daapi.view.meta.PrimeTimeMeta import PrimeTimeMeta
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import actions
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE, HOST_AVAILABILITY
from shared_utils import findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
_PING_MAX_VALUE = 999

class ServerListItemPresenter(object):
    _periodsController = None

    def __init__(self, inListID, hostName, name, shortName, csisStatus, peripheryID):
        self.orderID = inListID
        self.__hostName = hostName
        self.__name = name
        self.__csisStatus = csisStatus
        self.__peripheryID = peripheryID
        self._shortName = shortName
        self.__invalidationTime = 0
        self.__primeTimeStatus = None
        self.__timeLeft = None
        self.__isAvailable = None
        self.__pingStatus = 0
        self.__pingValue = 0
        self.__invalidatePrimeTimeStatus()
        self.invalidatePingData()
        return

    def asDict(self):
        return {'label': self.__name,
         'id': self.__peripheryID,
         'csisStatus': self.__csisStatus,
         'data': self.__hostName,
         'enabled': self.isEnabled(),
         'timeLeft': self.getTimeLeft(),
         'shortname': self._shortName,
         'pingValue': self.__pingValue,
         'pingStatus': self.__pingStatus,
         'tooltip': self._buildTooltip()}

    def isActive(self):
        return self.__getPrimeTimeStatus() in (PRIME_TIME_STATUS.AVAILABLE, PRIME_TIME_STATUS.NOT_AVAILABLE)

    def isAvailable(self):
        return self.__getPrimeTimeStatus() == PRIME_TIME_STATUS.AVAILABLE

    def isEnabled(self):
        return self.isAvailable()

    def getTimeLeft(self):
        self.__invalidatePrimeTimeStatus()
        return self.__timeLeft

    def getPeripheryID(self):
        return self.__peripheryID

    def getName(self):
        return self.__name

    def getPingStatus(self):
        return self.__pingStatus

    def getPingValue(self):
        return self.__pingValue

    def invalidatePingData(self):
        pingValue, self.__pingStatus = g_preDefinedHosts.getHostPingData(self.__hostName)
        self.__pingValue = min(pingValue, _PING_MAX_VALUE)

    def _buildTooltip(self):
        raise NotImplementedError

    def _getIsAvailable(self):
        self.__invalidatePrimeTimeStatus()
        return self.__isAvailable

    def __getPrimeTimeStatus(self):
        self.__invalidatePrimeTimeStatus()
        return self.__primeTimeStatus

    def __invalidatePrimeTimeStatus(self):
        currTime = int(time_utils.getCurrentLocalServerTimestamp())
        if self.__invalidationTime < currTime:
            primeTimeData = self._periodsController.getPrimeTimeStatus(self.__peripheryID)
            self.__primeTimeStatus, self.__timeLeft, self.__isAvailable = primeTimeData
            self.__invalidationTime = currTime

    def __cmp__(self, other):
        return self.orderID - other.orderID


class StubPresenterClass(object):
    pass


class PrimeTimeViewBase(LobbySubView, PrimeTimeMeta, Notifiable, IPreQueueListener):
    relogin = dependency.descriptor(IReloginController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _serverPresenterClass = StubPresenterClass

    def __init__(self, *_):
        super(PrimeTimeViewBase, self).__init__()
        self.__serversList = None
        self.__allServers = {}
        self._isEnabled = False
        return

    def closeView(self):
        self.__close()

    def selectServer(self, idx):
        vo = self.__serversDP.getVO(idx)
        self.__serversDP.setSelectedID(vo['id'])
        self.__serversDP.refresh()
        self.__updateData()

    def apply(self):
        selectedID = self.__serversDP.getSelectedID()
        if selectedID == self._connectionMgr.peripheryID:
            self.__continue()
        else:
            self.relogin.doRelogin(selectedID, extraChainSteps=self.__getExtraSteps())

    def _populate(self):
        super(PrimeTimeViewBase, self)._populate()
        self.__serversDP = self.__buildDataProvider()
        self.__serversDP.setFlashObject(self.as_getServersDPS())
        self.__updateList()
        self.__updateData()
        self._getController().onUpdated += self.__onControllerUpdated
        if not constants.IS_CHINA:
            if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
                g_preDefinedHosts.startCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart += self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete += self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed += self.__onServersUpdate
        self.addNotificators(PeriodicNotifier(self.__getInfoUpdatePeriod, self.__onNotifierTriggered, periods=(time_utils.ONE_MINUTE,)))
        self.startNotification()

    def _dispose(self):
        self.clearNotification()
        self._getController().onUpdated -= self.__onControllerUpdated
        if not constants.IS_CHINA:
            g_preDefinedHosts.stopCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart -= self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete -= self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed -= self.__onServersUpdate
        self.__serversDP.fini()
        self.__serversDP = None
        self.__serversList = None
        super(PrimeTimeViewBase, self)._dispose()
        return

    def _getController(self):
        raise NotImplementedError

    def _prepareData(self, serverList, serverInfo):
        raise NotImplementedError

    def _getPrbActionName(self):
        raise NotImplementedError

    def _getPrbForcedActionName(self):
        raise NotImplementedError

    def __buildDataProvider(self):
        primeTimesForDay = self._getController().getPrimeTimesForDay(time.time(), groupIdentical=False)
        return PrimeTimesServersDataProvider(primeTimesForDay=primeTimesForDay)

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self._connectionMgr.isStandalone():
            hostsList.insert(0, (self._connectionMgr.url,
             self._connectionMgr.serverUserName,
             self._connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        serversList = []
        availableServersList = []
        for idx, serverData in enumerate(hostsList):
            serverPresenter = self._serverPresenterClass(idx, *serverData)
            self.__allServers[serverPresenter.getPeripheryID()] = serverPresenter
            if serverPresenter.isActive():
                periphery = serverPresenter.asDict()
                serversList.append(periphery)
                if serverPresenter.isAvailable():
                    availableServersList.append(periphery)

        if availableServersList:
            self._isEnabled = True
            serversList = availableServersList
        else:
            self._isEnabled = False
        self.__serversList = serversList
        self.__serversDP.rebuildList(serversList)
        self.__updateSelectedServer()

    def __updateData(self):
        serverPresenter = self.__allServers.get(self.__serversDP.getSelectedID())
        self.as_setDataS(self._prepareData(self.__serversList, serverPresenter))

    def __updateSelectedServer(self):
        if self.__serversDP.getSelectedIdx() == -1:
            currentServerID = self._connectionMgr.peripheryID
            if findFirst(lambda s: s['id'] == currentServerID, self.__serversList) is not None:
                self.__serversDP.setSelectedID(currentServerID)
            else:
                bestServer = self.__serversDP.getDefaultSelectedServer(self.__serversList)
                for server in self.__serversList:
                    if server['shortname'] == bestServer:
                        self.__serversDP.setSelectedID(server['id'])

        return

    def __onServersUpdate(self, *_):
        self.__invalidateServersPing()
        self.__updateList()
        self.__updateData()

    def __onControllerUpdated(self, *_):
        if not self.__tryGoToHangar():
            self.__updateList()
            self.__updateData()
            self.startNotification()

    def __onNotifierTriggered(self):
        if not self.__tryGoToHangar():
            self.__updateList()
            self.__updateData()

    def __invalidateServersPing(self):
        for server in self.__allServers.values():
            server.invalidatePingData()

    def __getInfoUpdatePeriod(self):
        minimumTime = 0
        for serverInfo in self.__allServers.values():
            timeLeft = serverInfo.getTimeLeft()
            if serverInfo.isActive() and timeLeft > 0:
                if timeLeft < minimumTime or minimumTime == 0:
                    minimumTime = timeLeft

        return minimumTime

    def __getExtraSteps(self):

        def onLobbyInit():
            actions.SelectPrb(PrbAction(self._getPrbActionName())).invoke()

        return [actions.OnLobbyInitedAction(onInited=onLobbyInit)]

    def __tryGoToHangar(self):
        if self.__allServers[self._connectionMgr.peripheryID].isAvailable():
            self.__continue()
            return True
        return False

    @process
    def __continue(self):
        result = yield self.prbDispatcher.doSelectAction(PrbAction(self._getPrbForcedActionName()))
        if result:
            self.__close()
