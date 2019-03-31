# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/Prebattle.py
# Compiled at: 2011-07-19 14:41:51
import BigWorld, constants
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG, LOG_ERROR
from helpers.i18n import makeString
from gui import SystemMessages
from gui.Scaleform.windows import UIInterface
from gui.Scaleform.Waiting import Waiting
from PlayerEvents import g_playerEvents
from account_helpers.AccountPrebattle import AccountPrebattle
import MusicController

class Prebattle(UIInterface):
    TYPES_ORDERED = (('heavyTank', '#item_types:vehicle/tags/heavy_tank/name'),
     ('mediumTank', '#item_types:vehicle/tags/medium_tank/name'),
     ('lightTank', '#item_types:vehicle/tags/light_tank/name'),
     ('AT-SPG', '#item_types:vehicle/tags/at-spg/name'),
     ('SPG', '#item_types:vehicle/tags/spg/name'))
    DIVISIONS_ORDERED = (constants.PREBATTLE_COMPANY_DIVISION.JUNIOR,
     constants.PREBATTLE_COMPANY_DIVISION.MIDDLE,
     constants.PREBATTLE_COMPANY_DIVISION.CHAMPION,
     constants.PREBATTLE_COMPANY_DIVISION.ABSOLUTE)

    def populateUI(self, proxy):
        UIInterface.populateUI(self, proxy)
        self.createTime = 0
        self.__timerCallback = None
        self.__queueCallback = None
        self.__inited = False
        self.uiHolder.movie.backgroundAlpha = 0.6
        self.uiHolder.addExternalCallback('ExitClick', self.onExitButtonClick)
        self.uiHolder.addExternalCallback('StartClick', self.onStartButtonClick)
        g_playerEvents.onQueueInfoReceived += self.onQueueInfoReceived
        g_playerEvents.onArenaCreated += self.onStartBattle
        g_playerEvents.onVehicleLockChanged += self.__lockChange
        self.__updateQueueInfo()
        self.__updateTimer()
        self.uiHolder._updateFightButton()
        if (AccountPrebattle.isSquad() or AccountPrebattle.isCompany()) and not AccountPrebattle.isCreator():
            self.call('prebattle.showExit', [False])
        self.call('prebattle.setType', [AccountPrebattle.getBattleType()])
        MusicController.g_musicController.play(MusicController.MUSIC_EVENT_LOBBY)
        MusicController.g_musicController.play(MusicController.AMBIENT_EVENT_LOBBY)
        return

    def dispossessUI(self):
        self.__stopUpdateScreen()
        g_playerEvents.onQueueInfoReceived -= self.onQueueInfoReceived
        g_playerEvents.onArenaCreated -= self.onStartBattle
        g_playerEvents.onVehicleLockChanged -= self.__lockChange
        self.uiHolder.removeExternalCallbacks('ExitClick', 'StartClick')
        UIInterface.dispossessUI(self)

    def __stopUpdateScreen(self):
        if self.__timerCallback is not None:
            BigWorld.cancelCallback(self.__timerCallback)
            self.__timerCallback = None
        if self.__queueCallback is not None:
            BigWorld.cancelCallback(self.__queueCallback)
            self.__queueCallback = None
        return

    def __del__(self):
        LOG_DEBUG('PrebattleHandler deleted')

    def __updateQueueInfo(self):
        self.__queueCallback = None
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'requestQueueInfo'):
            if AccountPrebattle.isCompany():
                qType = constants.QUEUE_TYPE.COMPANIES
            else:
                qType = constants.QUEUE_TYPE.RANDOMS
            currPlayer.requestQueueInfo(qType)
            self.__queueCallback = BigWorld.callback(5, self.__updateQueueInfo)
        return

    def __updateTimer(self):
        self.__timerCallback = None
        self.__timerCallback = BigWorld.callback(1, self.__updateTimer)
        textLabel = makeString('#menu:prebattle/timerLabel')
        timeLabel = '%d:%02d' % divmod(self.createTime, 60)
        self.call('prebattle.setTimer', [textLabel, timeLabel])
        self.createTime += 1
        return

    def onQueueInfoReceived(self, randomsQueueInfo, companiesQueueInfo):
        if AccountPrebattle.isCompany():
            self.call('prebattle.setPlayers', [makeString('#menu:prebattle/groupsLabel'), sum(companiesQueueInfo['divisions'])])
            vDivisions = companiesQueueInfo['divisions']
            if vDivisions is not None:
                data = ['#menu:prebattle/typesCompaniesTitle']
                vClassesLen = len(vDivisions)
                for vDivision in Prebattle.DIVISIONS_ORDERED:
                    data.append('#menu:prebattle/CompaniesTitle/%s' % constants.PREBATTLE_COMPANY_DIVISION_NAMES[vDivision])
                    data.append(vDivisions[vDivision] if vDivision < vClassesLen else 0)

                self.call('prebattle.setListByType', data)
            self.call('prebattle.showStart', [constants.IS_DEVELOPMENT])
        else:
            self.call('prebattle.setPlayers', [makeString('#menu:prebattle/playersLabel'), sum(randomsQueueInfo['levels'])])
            vehLevels = randomsQueueInfo['levels']
            vehLevels = vehLevels[:] if vehLevels is not None else []
            vehLevels.reverse()
            vehLevels.insert(0, '#menu:prebattle/levelsTitle')
            self.call('prebattle.setListByLevel', vehLevels[:-1])
            vClasses = randomsQueueInfo['classes']
            if vClasses is not None:
                data = ['#menu:prebattle/typesTitle']
                vClassesLen = len(vClasses)
                for vClass, message in Prebattle.TYPES_ORDERED:
                    data.append(message)
                    idx = constants.VEHICLE_CLASS_INDICES[vClass]
                    data.append(vClasses[idx] if idx < vClassesLen else 0)

                self.call('prebattle.setListByType', data)
            self.call('prebattle.showStart', constants.IS_DEVELOPMENT and [sum(randomsQueueInfo['levels']) > 1])
        if not self.__inited:
            self.__inited = True
            Waiting.hide('loadPage')
        return

    def onExitButtonClick(self, callbackId):

        def readyCallback(code, type):
            if code < 0:
                LOG_ERROR('Server return error for squad %s ready request: responseCode=%s' % (type, code))

        if AccountPrebattle.isSquad() or AccountPrebattle.isCompany():
            if AccountPrebattle.isCreator():
                BigWorld.player().prb_teamNotReady(1, lambda code: readyCallback(code, 'team'))
            else:
                BigWorld.player().prb_notReady(constants.PREBATTLE_ACCOUNT_STATE.NOT_READY, lambda code: readyCallback(code, 'player'))
        elif hasattr(BigWorld.player(), 'dequeue'):
            BigWorld.player().dequeue()

    def onStartBattle(self):
        self.__stopUpdateScreen()

    def __lockChange(self, id, lock):
        from AccountCommands import LOCK_REASON
        if g_currentVehicle.vehicle.inventoryId == id and lock == LOCK_REASON.NONE:
            self.showHangar()

    def showHangar(self):
        self.uiHolder.movie.invoke(('loadHangar',))

    def onStartButtonClick(self, callbackId):
        currPlayer = BigWorld.player()
        if currPlayer is not None and hasattr(currPlayer, 'createArenaFromQueue'):
            currPlayer.createArenaFromQueue()
        return
