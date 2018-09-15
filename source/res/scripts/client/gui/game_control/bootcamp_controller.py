# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/bootcamp_controller.py
import BigWorld
from account_helpers.AccountSettings import CURRENT_VEHICLE, AccountSettings
from helpers import dependency
from skeletons.gui.game_control import IBootcampController
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.battle_results import IBattleResultsService
from gui.Scaleform.Waiting import Waiting
from bootcamp.BootCampEvents import g_bootcampEvents
from PlayerEvents import g_playerEvents
from bootcamp.Bootcamp import g_bootcamp
from debug_utils import LOG_ERROR

class BootcampController(IBootcampController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self):
        super(BootcampController, self).__init__()
        self.__inBootcamp = False
        self.__automaticStart = False
        self.__inBootcampAccount = False
        g_bootcampEvents.onBootcampBecomePlayer += self.__onBootcampBecomePlayer
        g_bootcampEvents.onBootcampBecomeNonPlayer += self.__onBootcampBecomeNonPlayer
        g_bootcampEvents.onBootcampStarted += self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished += self.__onExitBootcamp
        g_playerEvents.onAvatarBecomePlayer += self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer += self.__onAvatarBecomeNonPlayer

    def startBootcamp(self, inBattle):
        if g_playerEvents.isPlayerEntityChanging:
            return
        if self.__inBootcamp:
            LOG_ERROR('Trying to startBootcamp - is already started')
            return
        if not inBattle:
            self.__doStartBootcamp()

    def stopBootcamp(self, inBattle):
        if g_playerEvents.isPlayerEntityChanging:
            return
        if not self.__inBootcamp:
            LOG_ERROR('Trying to stop bootcamp - is already stopped')
            return
        if inBattle:
            g_bootcamp.requestBootcampFinishFromBattle = True
            self.sessionProvider.exit()
        else:
            self.__doStopBootcamp()

    @property
    def replayCtrl(self):
        return g_bootcamp.replayCtrl

    def isInBootcamp(self):
        return self.__inBootcamp

    def hasFinishedBootcampBefore(self):
        return g_bootcamp.getParameters().get('completed', 0) > 0

    def runCount(self):
        return g_bootcamp.getParameters().get('runCount', 0)

    def needAwarding(self):
        return g_bootcamp.getParameters().get('needAwarding', False)

    def isInBootcampAccount(self):
        return self.__inBootcampAccount

    def fini(self):
        g_bootcampEvents.onBootcampBecomePlayer -= self.__onBootcampBecomePlayer
        g_bootcampEvents.onBootcampBecomeNonPlayer -= self.__onBootcampBecomeNonPlayer
        g_bootcampEvents.onBootcampStarted -= self.__onEnterBootcamp
        g_bootcampEvents.onBootcampFinished -= self.__onExitBootcamp
        g_playerEvents.onAvatarBecomePlayer -= self.__onAvatarBecomePlayer
        g_playerEvents.onAvatarBecomeNonPlayer -= self.__onAvatarBecomeNonPlayer

    def onLobbyInited(self, event):
        if self.__automaticStart:
            self.__doStartBootcamp()
            self.__automaticStart = False

    def setAutomaticStart(self, enable):
        self.__automaticStart = enable

    def enqueueBootcamp(self):
        if g_bootcamp.isRunning():
            BigWorld.player().enqueueBootcamp(g_bootcamp.getLessonNum())

    def dequeueBootcamp(self):
        BigWorld.player().dequeueBootcamp()

    def showActionWaitWindow(self):
        g_bootcamp.showActionWaitWindow()

    def hideActionWaitWindow(self):
        g_bootcamp.hideActionWaitWindow()

    def getLessonNum(self):
        return g_bootcamp.getLessonNum()

    def __onEnterBootcamp(self):
        self.__inBootcamp = True

    def __onExitBootcamp(self):
        self.__inBootcamp = False

    def __doStartBootcamp(self):
        BigWorld.player().startBootcampCmd()

    def __doStopBootcamp(self):
        BigWorld.player().base.requestBootcampQuit(AccountSettings.getFavorites(CURRENT_VEHICLE))

    def __onBootcampBecomePlayer(self):
        self.__inBootcampAccount = True
        Waiting.hide('login')

    def __onBootcampBecomeNonPlayer(self):
        self.__inBootcampAccount = False

    def __onAvatarBecomePlayer(self):
        self.battleResults.onResultPosted -= self.__onBattleResultsPosted

    def __onAvatarBecomeNonPlayer(self):
        self.battleResults.onResultPosted += self.__onBattleResultsPosted

    def __onBattleResultsPosted(self, reusableInfo, composer):
        g_bootcamp.setBattleResultsReusableInfo(reusableInfo)
