# Embedded file name: scripts/client/tutorial/control/offbattle/triggers.py
from PlayerEvents import g_playerEvents
from constants import JOIN_FAILURE_NAMES
from gui.ClientUpdateManager import g_clientUpdateManager
from tutorial.control.context import GlobalStorage, GLOBAL_FLAG
from tutorial.control.offbattle.functional import ContentChangedEvent
from tutorial.control.triggers import _Trigger
from tutorial.control.offbattle.context import OffBattleClientCtx
__all__ = ['TutorialQueueTrigger', 'AllBonusesTrigger']

class TutorialQueueTrigger(_Trigger):
    _inQueue = GlobalStorage(GLOBAL_FLAG.IN_QUEUE, False)

    def __init__(self, triggerID, popUpID):
        super(TutorialQueueTrigger, self).__init__(triggerID)
        self._event = ContentChangedEvent(popUpID)

    def run(self):
        if not self.isSubscribed:
            g_playerEvents.onTutorialEnqueued += self.__pe_onTutorialEnqueued
            g_playerEvents.onTutorialDequeued += self.__pe_onTutorialDequeued
            g_playerEvents.onTutorialEnqueueFailure += self.__pe_onTutorialEnqueueFailure
            g_playerEvents.onArenaJoinFailure += self.__pe_onArenaJoinFailure
            g_playerEvents.onKickedFromArena += self.__pe_onKickedFromArena
            self.isSubscribed = True
        super(TutorialQueueTrigger, self).run()

    def isOn(self, *args):
        return self._inQueue

    def clear(self):
        self._gui.hideWaiting('queue')
        if self.isSubscribed:
            g_playerEvents.onTutorialEnqueued -= self.__pe_onTutorialEnqueued
            g_playerEvents.onTutorialDequeued -= self.__pe_onTutorialDequeued
            g_playerEvents.onTutorialEnqueueFailure -= self.__pe_onTutorialEnqueueFailure
            g_playerEvents.onArenaJoinFailure -= self.__pe_onArenaJoinFailure
            g_playerEvents.onKickedFromArena -= self.__pe_onKickedFromArena
        self.isSubscribed = False
        self._inQueue = False
        super(TutorialQueueTrigger, self).clear()

    def __pe_onTutorialEnqueued(self, queueNumber, queueLen, avgWaitingTime):
        self._event.fire(avgWaitingTime)
        if not self._inQueue:
            self._inQueue = True
            self.toggle(isOn=True)

    def __pe_onTutorialDequeued(self):
        if self._inQueue:
            self._inQueue = False
            self.toggle(isOn=False)

    def __pe_onTutorialEnqueueFailure(self, errorCode, errorStr):
        if errorCode in JOIN_FAILURE_NAMES:
            text = '#system_messages:arena_start_errors/join/{0:>s}'.format(JOIN_FAILURE_NAMES[errorCode])
        else:
            text = errorStr
        self._gui.showI18nMessage(text, msgType='Error')
        self._tutorial.refuse()

    def __pe_onArenaJoinFailure(self, errorCode, errorStr):
        self._tutorial.refuse()

    def __pe_onKickedFromArena(self, errorCode):
        self._tutorial.refuse()


class AllBonusesTrigger(_Trigger):

    def __init__(self, triggerID, setVarID):
        super(AllBonusesTrigger, self).__init__(triggerID)
        self._setVarID = setVarID
        self._battleSnap = OffBattleClientCtx.fetch(self._cache).completed
        self._statsSnap = self._bonuses.getCompleted()

    def run(self):
        self.isRunning = True
        if not self.isSubscribed:
            self.isSubscribed = True
            g_clientUpdateManager.addCallbacks({'stats.tutorialsCompleted': self.onTutorialCompleted})
        self.toggle(isOn=self.isOn(self._bonuses.getCompleted()))

    def isOn(self, completed):
        return completed & self._battleSnap == self._battleSnap

    def clear(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.isSubscribed = False
        self.isRunning = False

    def onTutorialCompleted(self, completed):
        if completed is not None:
            self._tutorial.getVars().set(self._setVarID, completed - self._statsSnap)
            self._bonuses.setCompleted(completed)
            if self.isOn(completed):
                self.toggle(isOn=True)
        return
