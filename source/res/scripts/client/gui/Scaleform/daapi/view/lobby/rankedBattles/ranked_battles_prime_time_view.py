# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/rankedBattles/ranked_battles_prime_time_view.py
import random
import operator
import constants
from adisp import process
from gui import GUI_SETTINGS
from gui.Scaleform import MENU
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.RankedBattlesPrimeTimeMeta import RankedBattlesPrimeTimeMeta
from gui.Scaleform.daapi.view.servers_data_provider import ServersDataProvider
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import actions
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared.formatters import icons, text_styles
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from predefined_hosts import g_preDefinedHosts, REQUEST_RATE, HOST_AVAILABILITY
from shared_utils import findFirst
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IRankedBattlesController
from skeletons.gui.game_control import IReloginController
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier, SimpleNotifier

class RankedBattlesPrimeTimeView(LobbySubView, RankedBattlesPrimeTimeMeta, Notifiable, IPreQueueListener):
    relogin = dependency.descriptor(IReloginController)
    connectionMgr = dependency.descriptor(IConnectionManager)
    rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, ctx=None):
        super(RankedBattlesPrimeTimeView, self).__init__()
        self.__serversList = None
        self.__allServersList = None
        self.__isEnabled = False
        return

    def closeView(self):
        self.__close()

    def selectServer(self, idx):
        vo = self.__serversDP.getVO(idx)
        self.__serversDP.setSelectedID(vo['id'])
        self.__updateData()

    def apply(self):
        selectedID = self.__serversDP.getSelectedID()
        if selectedID == self.connectionMgr.peripheryID:
            self.__continue()
        else:
            self.relogin.doRelogin(selectedID, extraChainSteps=self.__getExtraSteps())

    def _populate(self):
        super(RankedBattlesPrimeTimeView, self)._populate()
        self.__serversDP = ServersDataProvider()
        self.__serversDP.setFlashObject(self.as_getServersDPS())
        self.__updateList()
        self.__updateData()
        if not constants.IS_CHINA:
            if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.ALWAYS:
                g_preDefinedHosts.startCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart += self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete += self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed += self.__onServersUpdate
        self.rankedController.onUpdated += self.__onRankedUpdated
        self.addNotificators(PeriodicNotifier(self.__getPeriodUpdateTime, self.__onPeriodUpdate), SimpleNotifier(self.__getSimpleUpdateTime, self.__onSimpleUpdate))
        self.startNotification()

    def _dispose(self):
        self.stopNotification()
        self.clearNotification()
        self.rankedController.onUpdated -= self.__onRankedUpdated
        if not constants.IS_CHINA:
            g_preDefinedHosts.stopCSISUpdate()
            g_preDefinedHosts.onCsisQueryStart -= self.__onServersUpdate
            g_preDefinedHosts.onCsisQueryComplete -= self.__onServersUpdate
            g_preDefinedHosts.onPingPerformed -= self.__onServersUpdate
        self.__serversDP.fini()
        self.__serversDP = None
        self.__serversList = None
        super(RankedBattlesPrimeTimeView, self)._dispose()
        return

    def __close(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateList(self):
        hostsList = g_preDefinedHosts.getSimpleHostsList(g_preDefinedHosts.hostsWithRoaming())
        if self.connectionMgr.peripheryID == 0:
            hostsList.insert(0, (self.connectionMgr.url,
             self.connectionMgr.serverUserName,
             HOST_AVAILABILITY.IGNORED,
             0))
        serversList = []
        availableServersList = []
        for hostName, name, csisStatus, peripheryID in hostsList:
            primeTimeStatus, timeLeft = self.rankedController.getPrimeTimeStatus(peripheryID)
            if primeTimeStatus in (PRIME_TIME_STATUS.AVAILABLE, PRIME_TIME_STATUS.NOT_AVAILABLE):
                isAvailable = primeTimeStatus == PRIME_TIME_STATUS.AVAILABLE
                periphery = {'label': name,
                 'id': peripheryID,
                 'csisStatus': csisStatus,
                 'data': hostName,
                 'enabled': isAvailable,
                 'timeLeft': timeLeft}
                serversList.append(periphery)
                if isAvailable:
                    availableServersList.append(periphery)

        self.__allServersList = serversList
        if availableServersList:
            self.__isEnabled = True
            serversList = availableServersList
        else:
            self.__isEnabled = False
        self.__serversList = serversList
        self.__serversDP.rebuildList(serversList)
        self.__updateServer()

    def __updateData(self):
        selectedIdx = self.__serversDP.getSelectedIdx()
        serverItem = self.__serversList[selectedIdx]
        selectedItem = self.__serversDP.getVO(selectedIdx)
        currentServerName = selectedItem['label']
        if len(self.__serversList) == 1:
            serverDDName = text_styles.concatStylesToSingleLine(text_styles.main(currentServerName), '  ', selectedItem['pingValue'])
            serversDDEnabled = False
            serverDDVisible = False
        else:
            serverDDName = ''
            serversDDEnabled = True
            serverDDVisible = True
        serverDDLabel = text_styles.highTitle(_ms(RANKED_BATTLES.PRIMETIME_SERVERS, server=serverDDName))
        if self.__isEnabled:
            timeLeftStr = time_utils.getTillTimeString(serverItem['timeLeft'], MENU.HEADERBUTTONS_BATTLE_TYPES_RANKED_AVAILABILITY)
            status = text_styles.main(_ms(RANKED_BATTLES.PRIMETIME_STATUS_THISENABLE, server=currentServerName, time=text_styles.warning(timeLeftStr)))
            mainBackground = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_PRIMETIME_PRIME_TIME_BACK_DEFAULT
        else:
            status = '{} {}'.format(icons.alert(-3), text_styles.main(_ms(RANKED_BATTLES.PRIMETIME_STATUS_DISABLE)))
            mainBackground = RES_ICONS.MAPS_ICONS_RANKEDBATTLES_PRIMETIME_PRIME_TIME_BACK_BW
        self.as_setDataS({'calendarTooltip': makeTooltip(RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_HEADER, RANKED_BATTLES.RANKEDBATTLEVIEW_STATUSBLOCK_CALENDARBTNTOOLTIP_BODY),
         'calendarIcon': RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR,
         'title': _ms(RANKED_BATTLES.PRIMETIME_TITLE),
         'apply': _ms(RANKED_BATTLES.PRIMETIME_APPLYBTN),
         'mainBackground': mainBackground,
         'status': status,
         'serverDDLabel': serverDDLabel,
         'serversDDEnabled': serversDDEnabled,
         'serverDDVisible': serverDDVisible})
        self.as_setSelectedServerIndexS(selectedIdx)

    def __updateServer(self):
        if self.__serversDP.getSelectedIdx() == -1:
            currentServerID = self.connectionMgr.peripheryID
            if findFirst(lambda s: s['id'] == currentServerID, self.__serversList) is not None:
                self.__serversDP.setSelectedID(currentServerID)
            else:
                server = random.choice(self.__serversList)
                self.__serversDP.setSelectedID(server['id'])
        return

    def __onServersUpdate(self, *args):
        self.__updateList()
        self.__updateData()

    def __onRankedUpdated(self):
        self.__updateList()
        self.__updateData()
        self.startNotification()

    def __getExtraSteps(self):
        if self.__isEnabled:
            prbAction = PREBATTLE_ACTION_NAME.RANKED
        else:
            prbAction = PREBATTLE_ACTION_NAME.RANKED_FORCED

        def onLobbyInit():
            actions.SelectPrb(PrbAction(prbAction)).invoke()

        return [actions.OnLobbyInitedAction(onInited=onLobbyInit)]

    def __getTimeLeft(self, pID):
        primeTime = self.rankedController.getPrimeTimes().get(pID)
        currentSeason = self.rankedController.getCurrentSeason()
        _, timeLeft = primeTime.getAvailability(time_utils.getCurrentLocalServerTimestamp(), currentSeason.getCycleEndDate())
        return timeLeft

    def __getPeriodUpdateTime(self):
        return self.__getTimeLeft(self.__serversDP.getSelectedID())

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
        result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANKED_FORCED))
        if result:
            self.__close()
