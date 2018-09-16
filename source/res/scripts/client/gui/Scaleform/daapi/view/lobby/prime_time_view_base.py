# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prime_time_view_base.py
import operator
import constants
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.PrimeTimeMeta import PrimeTimeMeta
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import actions
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events
from helpers import dependency
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE, HOST_AVAILABILITY
from shared_utils import findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IReloginController
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier, SimpleNotifier
_PING_MAX_VALUE = 999

class PrimeTimeViewBase(LobbySubView, PrimeTimeMeta, Notifiable, IPreQueueListener):
    relogin = dependency.descriptor(IReloginController)
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, ctx=None):
        super(PrimeTimeViewBase, self).__init__()
        self.__serversList = None
        self.__allServersList = None
        self._isEnabled = False
        return

    def closeView(self):
        self.__close()

    def selectServer(self, idx):
        vo = self.__serversDP.getVO(idx)
        self.__serversDP.setSelectedID(vo['id'])
        self.__serversDP.refresh()

    def apply(self):
        selectedID = self.__serversDP.getSelectedID()
        if selectedID == self.connectionMgr.peripheryID:
            self.__continue()
        else:
            self.relogin.doRelogin(selectedID, extraChainSteps=self.__getExtraSteps())

    def _populate(self):
        super(PrimeTimeViewBase, self)._populate()
        self.__serversDP = self._getAllServersDP()
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
        self.addNotificators(PeriodicNotifier(self.__getPeriodUpdateTime, self.__onPeriodUpdate), SimpleNotifier(self.__getSimpleUpdateTime, self.__onSimpleUpdate))
        self.startNotification()

    def _dispose(self):
        self.stopNotification()
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

    def _getAllServersDP(self):
        raise NotImplementedError

    def _prepareData(self, serverList, serverName, serverTimeLeft):
        raise NotImplementedError

    def _getPrbActionName(self, isEnabled):
        raise NotImplementedError

    def _getPrbForcedActionName(self):
        raise NotImplementedError

    def _getTimeLeft(self, pID):
        raise NotImplementedError

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming(), withShortName=True)
        if self.connectionMgr.isStandalone():
            hostsList.insert(0, (self.connectionMgr.url,
             self.connectionMgr.serverUserName,
             self.connectionMgr.serverUserNameShort,
             HOST_AVAILABILITY.IGNORED,
             0))
        serversList = []
        availableServersList = []
        for hostName, name, shortName, csisStatus, peripheryID in hostsList:
            primeTimeStatus, timeLeft, _ = self._getController().getPrimeTimeStatus(peripheryID)
            pingValue, _ = g_preDefinedHosts.getHostPingData(hostName)
            pingValue = min(pingValue, _PING_MAX_VALUE)
            if primeTimeStatus in (PRIME_TIME_STATUS.AVAILABLE, PRIME_TIME_STATUS.NOT_AVAILABLE):
                isAvailable = primeTimeStatus == PRIME_TIME_STATUS.AVAILABLE
                periphery = {'label': name,
                 'id': peripheryID,
                 'csisStatus': csisStatus,
                 'data': hostName,
                 'enabled': isAvailable,
                 'timeLeft': timeLeft,
                 'shortname': shortName,
                 'pingValue': pingValue}
                serversList.append(periphery)
                if isAvailable:
                    availableServersList.append(periphery)

        self.__allServersList = serversList
        if availableServersList:
            self._isEnabled = True
            serversList = availableServersList
        else:
            self._isEnabled = False
        self.__serversList = serversList
        self.__serversDP.rebuildList(serversList)
        self.__updateServer()

    def __updateData(self):
        selectedIdx = self.__serversDP.getSelectedIdx()
        serverItem = None if not self.__serversList else self.__serversList[selectedIdx]
        selectedItem = self.__serversDP.getVO(selectedIdx)
        currentServerName = '' if not selectedItem else selectedItem['label']
        timeLeft = 0 if not serverItem else serverItem['timeLeft']
        self.as_setDataS(self._prepareData(self.__serversList, currentServerName, timeLeft))
        return

    def __updateServer(self):
        if self.__serversDP.getSelectedIdx() == -1:
            currentServerID = self.connectionMgr.peripheryID
            if findFirst(lambda s: s['id'] == currentServerID, self.__serversList) is not None:
                self.__serversDP.setSelectedID(currentServerID)
            else:
                bestServer = self.__serversDP.getDefaultSelectedServer(self.__serversList)
                for server in self.__serversList:
                    if server['shortname'] == bestServer:
                        self.__serversDP.setSelectedID(server['id'])

        return

    def __onServersUpdate(self, *args):
        self.__updateList()
        self.__updateData()

    def __onControllerUpdated(self):
        self.__updateList()
        self.__updateData()
        self.startNotification()

    def __getExtraSteps(self):

        def onLobbyInit():
            actions.SelectPrb(PrbAction(self._getPrbActionName(self._isEnabled))).invoke()

        return [actions.OnLobbyInitedAction(onInited=onLobbyInit)]

    def __getPeriodUpdateTime(self):
        return self._getTimeLeft(self.__serversDP.getSelectedID())

    def __onPeriodUpdate(self):
        self.__updateList()
        self.__updateData()

    def __getSimpleUpdateTime(self):
        timeLeftList = filter(None, map(operator.itemgetter('timeLeft'), self.__allServersList))
        return min(timeLeftList) if timeLeftList else 0

    def __onSimpleUpdate(self):
        self.__updateList()
        self.__updateData()

    @process
    def __continue(self):
        result = yield self.prbDispatcher.doSelectAction(PrbAction(self._getPrbForcedActionName()))
        if result:
            self.__close()
