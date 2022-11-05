# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prime_time_view_base.py
import time
import constants
from adisp import adisp_process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.prime_time_servers_data_provider import PrimeTimesServersDataProvider
from gui.Scaleform.daapi.view.meta.PrimeTimeMeta import PrimeTimeMeta
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.impl import backport
from gui.impl.gen import R
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared import actions, event_dispatcher
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.formatters import text_styles
from gui.shared.formatters.servers import makePingStatusIcon
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency, time_utils
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE, HOST_AVAILABILITY
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
_PING_MAX_VALUE = 999

def _emptyFmt(*_):
    pass


def _makeServerString(serverInfo, isServerNameShort=False):
    server = text_styles.neutral(text_styles.concatStylesToSingleLine(serverInfo.getShortName() if isServerNameShort else serverInfo.getName(), ' (', text_styles.neutral(serverInfo.getPingValue()), makePingStatusIcon(serverInfo.getPingStatus()), ')'))
    return backport.text(R.strings.menu.primeTime.server(), server=server)


class ServerListItemPresenter(object):
    _RES_ROOT = None

    def __init__(self, periodsController, inListID, hostName, name, shortName, csisStatus, peripheryID):
        self.orderID = inListID
        self.__hostName = hostName
        self.__name = name
        self.__csisStatus = csisStatus
        self.__peripheryID = peripheryID
        self.__shortName = shortName
        self.__invalidationTime = 0
        self.__primeTimeStatus = None
        self.__timeLeft = None
        self.__isAvailable = None
        self.__pingStatus = 0
        self.__pingValue = 0
        self.__periodsController = periodsController
        self.__invalidatePrimeTimeStatus()
        self.invalidatePingData()
        return

    @classmethod
    def deltaFormatter(cls, delta):
        return text_styles.neutral(backport.getTillTimeStringByRClass(delta, cls._RES_ROOT.timeLeft))

    @classmethod
    def statusDeltaFormatter(cls, delta):
        return backport.getTillTimeStringByRClass(delta, cls._RES_ROOT.timeLeft)

    def asDict(self):
        return {'label': self.__name,
         'id': self.__peripheryID,
         'csisStatus': self.__csisStatus,
         'data': self.__hostName,
         'enabled': self.isEnabled(),
         'timeLeft': self.getTimeLeft(),
         'shortname': self.__shortName,
         'pingValue': self.__pingValue,
         'pingStatus': self.__pingStatus,
         'tooltip': self._buildTooltip(self.__peripheryID)}

    def isActive(self):
        return self.__getPrimeTimeStatus() in (PrimeTimeStatus.AVAILABLE, PrimeTimeStatus.NOT_AVAILABLE)

    def isAvailable(self):
        return self.__getPrimeTimeStatus() == PrimeTimeStatus.AVAILABLE

    def isEnabled(self):
        return self.isActive()

    def getTimeLeft(self):
        self.__invalidatePrimeTimeStatus()
        return self.__timeLeft

    def getPeripheryID(self):
        return self.__peripheryID

    def getName(self):
        return self.__name

    def getShortName(self):
        return self.__shortName

    def getPingStatus(self):
        return self.__pingStatus

    def getPingValue(self):
        return self.__pingValue

    def invalidatePingData(self):
        pingValue, self.__pingStatus = g_preDefinedHosts.getHostPingData(self.__hostName)
        self.__pingValue = min(pingValue, _PING_MAX_VALUE)

    def _buildTooltip(self, peripheryID):
        periodInfo = self.__periodsController.getPeriodInfo(peripheryID=peripheryID)
        params = periodInfo.getVO(withBNames=True, deltaFmt=self.deltaFormatter)
        params['serverName'] = self.getName()
        tooltip = backport.text(self._RES_ROOT.dyn(periodInfo.periodType.value, self._RES_ROOT.undefined)(), **params)
        return {'tooltip': text_styles.main(tooltip),
         'specialArgs': [],
         'specialAlias': None,
         'isSpecial': None}

    def _getIsAvailable(self):
        self.__invalidatePrimeTimeStatus()
        return self.__isAvailable

    def __getPrimeTimeStatus(self):
        self.__invalidatePrimeTimeStatus()
        return self.__primeTimeStatus

    def __invalidatePrimeTimeStatus(self):
        currTime = int(time_utils.getCurrentLocalServerTimestamp())
        if self.__invalidationTime < currTime:
            primeTimeData = self.__periodsController.getPrimeTimeStatus(peripheryID=self.__peripheryID)
            self.__primeTimeStatus, self.__timeLeft, self.__isAvailable = primeTimeData
            self.__invalidationTime = currTime

    def __cmp__(self, other):
        return self.orderID - other.orderID


class StubPresenterClass(ServerListItemPresenter):

    def _buildTooltip(self, peripheryID):
        pass


class PrimeTimeViewBase(LobbySubView, PrimeTimeMeta, Notifiable, IPreQueueListener):
    _RES_ROOT = None
    _serverPresenterClass = StubPresenterClass
    _reloginController = dependency.descriptor(IReloginController)
    _connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, *_):
        super(PrimeTimeViewBase, self).__init__()
        self.__serversDP = None
        self._allServers = {}
        return

    def closeView(self):
        self.__close()

    def selectServer(self, idx):
        vo = self.__serversDP.getVO(idx)
        self.__serversDP.setSelectedID(vo['id'])
        self.__updateSelectedServerData()

    def apply(self):
        selectedID = self.__serversDP.getSelectedID()
        if selectedID == self._connectionMgr.peripheryID:
            self.__continue()
        else:
            self._reloginController.doRelogin(selectedID, extraChainSteps=self.__getExtraSteps())

    def _populate(self):
        super(PrimeTimeViewBase, self)._populate()
        self._initView()

    def _dispose(self):
        self._clearView()
        super(PrimeTimeViewBase, self)._dispose()

    def _initView(self):
        self.__serversDP = self.__buildDataProvider()
        self.__serversDP.setFlashObject(self.as_getServersDPS())
        self.__updateServersList()
        self.__updateSelectedServer()
        self.__updateSelectedServerData()
        self._startControllerListening()
        if not constants.IS_CHINA:
            if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
                g_preDefinedHosts.startCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart += self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete += self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed += self.__onServersUpdate
        self.addNotificators(PeriodicNotifier(self.__getInfoUpdatePeriod, self.__onNotifierTriggered, periods=(time_utils.ONE_MINUTE,)))
        self.startNotification()

    def _clearView(self):
        self.clearNotification()
        self._stopControllerListening()
        if not constants.IS_CHINA:
            g_preDefinedHosts.stopCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart -= self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete -= self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed -= self.__onServersUpdate
        self.__serversDP.fini()
        self.__serversDP = None
        self._allServers = {}
        return

    def _isAlertBGVisible(self):
        return not self._hasAvailableServers()

    def _hasAvailableServers(self):
        return any((server.isAvailable() for server in self._getActualServers()))

    def _getActualServers(self):
        activeServers = []
        availableServers = []
        for server in self._allServers.values():
            if server.isActive():
                activeServers.append(server)
                if server.isAvailable():
                    availableServers.append(server)

        return sorted(availableServers if availableServers else activeServers)

    def _getController(self):
        raise NotImplementedError

    def _getPrbActionName(self):
        raise NotImplementedError

    def _getPrbForcedActionName(self):
        raise NotImplementedError

    def _getServerText(self, serverList, serverInfo, isServerNameShort=False):
        return _makeServerString(serverInfo, isServerNameShort) if len(serverList) == 1 else backport.text(R.strings.menu.primeTime.servers())

    def _getStatusText(self):
        resSection = self._RES_ROOT.statusText
        periodInfo = self._getController().getPeriodInfo()
        timeFmt = backport.getShortTimeFormat if periodInfo.primeDelta < time_utils.ONE_DAY else None
        params = periodInfo.getVO(withBNames=True, deltaFmt=self._serverPresenterClass.statusDeltaFormatter, timeFmt=timeFmt or _emptyFmt, dateFmt=backport.getShortDateFormat if timeFmt is None else _emptyFmt)
        params['serverName'] = self._connectionMgr.serverUserNameShort
        return backport.text(resSection.dyn(periodInfo.periodType.value, resSection.undefined)(), **params)

    def _getTimeText(self, serverInfo):
        if serverInfo is None:
            return ''
        else:
            resSection = self._RES_ROOT.timeText
            periodInfo = self._getController().getPeriodInfo(peripheryID=serverInfo.getPeripheryID())
            params = periodInfo.getVO(withBNames=True, deltaFmt=serverInfo.deltaFormatter)
            params['serverName'] = serverInfo.getName()
            return backport.text(resSection.dyn(periodInfo.periodType.value, resSection.undefined)(), **params)

    def _getWarningIcon(self):
        if self._getController().hasAvailablePrimeTimeServers():
            icon = R.images.gui.maps.icons.library.icon_clock_100x100()
        else:
            icon = R.images.gui.maps.icons.library.icon_alert_90x84()
        return backport.image(icon)

    def _prepareData(self, serverList, serverInfo):
        isSingleServer = len(serverList) == 1
        return {'warningIconSrc': self._getWarningIcon(),
         'status': text_styles.grandTitle(self._getStatusText()),
         'serversText': text_styles.expText(self._getServerText(serverList, serverInfo)),
         'timeText': text_styles.expText(self._getTimeText(serverInfo)),
         'showAlertBG': self._isAlertBGVisible(),
         'serversDDEnabled': not isSingleServer,
         'serverDDVisible': not isSingleServer}

    def _startControllerListening(self):
        self._getController().onUpdated += self._onControllerUpdated

    def _stopControllerListening(self):
        self._getController().onUpdated -= self._onControllerUpdated

    def __getExtraSteps(self):

        def onLobbyInit():
            actions.SelectPrb(PrbAction(self._getPrbActionName())).invoke()

        return [actions.OnLobbyInitedAction(onInited=onLobbyInit)]

    def __getInfoUpdatePeriod(self):
        minimumTime = 0
        for serverInfo in self._allServers.values():
            timeLeft = serverInfo.getTimeLeft()
            if serverInfo.isActive() and timeLeft > 0:
                if timeLeft < minimumTime or minimumTime == 0:
                    minimumTime = timeLeft

        return minimumTime

    def __onServersUpdate(self, *_):
        self.__invalidateServersPing()
        self.__updateServersList()
        self.__updateSelectedServerData()

    def _onControllerUpdated(self, *_):
        if not self.__tryGoToHangar():
            self.__updateServersList()
            self.__updateSelectedServerData()
            self.startNotification()

    def __onNotifierTriggered(self):
        if not self.__tryGoToHangar():
            self.__updateServersList()
            self.__updateSelectedServerData()

    def __buildDataProvider(self):
        primeTimesForDay = self._getController().getPrimeTimesForDay(time.time(), groupIdentical=False)
        return PrimeTimesServersDataProvider(primeTimesForDay=primeTimesForDay)

    def __buildServersList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self._connectionMgr.isStandalone():
            hostsList.insert(0, (self._connectionMgr.url,
             self._connectionMgr.serverUserName,
             self._connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        for idx, serverData in enumerate(hostsList):
            serverPresenter = self._serverPresenterClass(self._getController(), idx, *serverData)
            self._allServers[serverPresenter.getPeripheryID()] = serverPresenter

    @adisp_process
    def __continue(self):
        result = yield self.prbDispatcher.doSelectAction(PrbAction(self._getPrbForcedActionName()))
        if result:
            self.__close()

    def __close(self):
        self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_HANGAR)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __invalidateServersPing(self):
        for server in self._allServers.values():
            server.invalidatePingData()

    def __tryGoToHangar(self):
        if self._allServers[self._connectionMgr.peripheryID].isAvailable():
            self.__continue()
            return True
        if not self._getActualServers():
            event_dispatcher.showHangar()
            return True
        return False

    def __updateServersDP(self):
        actualServers = sorted(self._getActualServers())
        currentSet = set((s.get('id') for s in self.__serversDP.collection))
        actualSet = set((s.getPeripheryID() for s in actualServers))
        self.__serversDP.rebuildList((server.asDict() for server in actualServers))
        if currentSet != actualSet:
            primeTimesForDay = self._getController().getPrimeTimesForDay(time.time(), groupIdentical=False)
            self.__serversDP.updatePrimeTimes(primeTimesForDay)
            self.__serversDP.setSelectedID(None)
            self.__updateSelectedServer()
            self.__serversDP.resetSelectedIndex()
        return

    def __updateServersList(self):
        if not self._allServers:
            self.__buildServersList()
        self.__updateServersDP()

    def __updateSelectedServer(self):
        actualServers = sorted(self._getActualServers())
        if self.__serversDP.getSelectedIdx() == -1:
            currentServerID = self._connectionMgr.peripheryID
            if any((s.getPeripheryID() == currentServerID for s in actualServers)):
                self.__serversDP.setSelectedID(currentServerID)
            else:
                bestPeripheryID = self.__serversDP.getDefaultSelectedServer([ s.asDict() for s in actualServers ])
                for server in actualServers:
                    if server.getPeripheryID() == bestPeripheryID:
                        self.__serversDP.setSelectedID(bestPeripheryID)

        self.__serversDP.refresh()

    def __updateSelectedServerData(self):
        serverPresenter = self._allServers.get(self.__serversDP.getSelectedID())
        self.as_setDataS(self._prepareData(self._getActualServers(), serverPresenter))
