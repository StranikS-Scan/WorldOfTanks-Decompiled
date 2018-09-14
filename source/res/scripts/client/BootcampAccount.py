# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BootcampAccount.py
import cPickle
import AccountCommands
import BattleReplay
from Account import PlayerAccount
from PlayerEvents import g_playerEvents as events
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP
from bootcamp.Bootcamp import g_bootcamp
from bootcamp.BootCampEvents import g_bootcampEvents

class PlayerBootcampAccount(PlayerAccount):

    def onBecomePlayer(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.stop()
        super(PlayerBootcampAccount, self).onBecomePlayer()
        if g_bootcamp is not None:
            g_bootcamp.setAccount(self)
        g_bootcampEvents.onBootcampBecomePlayer()
        g_bootcamp.showActionWaitWindow()
        return

    def onBecomeNonPlayer(self):
        super(PlayerBootcampAccount, self).onBecomeNonPlayer()
        g_bootcampEvents.onBootcampBecomeNonPlayer()
        g_bootcamp.hideActionWaitWindow()
        if g_bootcamp is not None:
            g_bootcamp.setAccount(None)
        return

    @staticmethod
    def finishBootcamp():
        LOG_DEBUG_DEV_BOOTCAMP('finishBootcamp called')
        g_bootcamp.finishBootcamp()

    def showGUI(self, bootcampCtxStr):
        LOG_DEBUG_DEV_BOOTCAMP('showGUI called')
        g_bootcamp.hideActionWaitWindow()
        bootcampCtx = cPickle.loads(bootcampCtxStr)
        self.databaseID = bootcampCtx['databaseID']
        currentLesson = bootcampCtx['lessonNum']
        isBattleLesson = bootcampCtx['isBattleLesson']
        g_bootcamp.setContext(bootcampCtx)
        events.isPlayerEntityChanging = False
        firstRun = currentLesson == 0 and not g_bootcamp.isRunning()
        events.onBootcampShowGUI(firstRun)
        if g_bootcamp.isRunning():
            g_bootcamp.setAccount(self)
            g_bootcamp.onBattleLessonFinished(currentLesson, bootcampCtx['lessonResults'])
        elif not g_bootcamp.isManualStart():
            g_bootcamp.start(currentLesson, isBattleLesson)

    def enqueueBootcamp(self, lessonId):
        if events.isPlayerEntityChanging:
            return
        self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_BOOTCAMP, lessonId, 0, 0)

    def dequeueBootcamp(self):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt3(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_BOOTCAMP, 0, 0, 0)

    def onBootcampEnqueued(self, number, queueLen, avgWaitingTime):
        LOG_DEBUG_DEV_BOOTCAMP('onBootcampEnqueued', number, queueLen, avgWaitingTime)
        self.isInBootcampQueue = True
        events.onBootcampEnqueued(number, queueLen, avgWaitingTime)


BootcampAccount = PlayerBootcampAccount
