# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootCampEvents.py
import Event

class _BootCampEvents(object):

    def __init__(self):
        self.__manager = Event.EventManager()
        self.onBootcampBecomePlayer = self._createEvent()
        self.onBootcampBecomeNonPlayer = self._createEvent()
        self.onBootcampStarted = self._createEvent()
        self.onBootcampFinished = self._createEvent()
        self.onIntroVideoStop = self._createEvent()
        self.onOutroVideoStop = self._createEvent()
        self.onIntroVideoLoaded = self._createEvent()
        self.onBootcampGoNext = self._createEvent()
        self.onUIStateChanged = self._createEvent()
        self.onBattleAction = self._createEvent()
        self.onArenaLoadCompleted = self._createEvent()
        self.onArenaStarted = self._createEvent()
        self.onGarageLessonFinished = self._createEvent()
        self.onBattleLessonFinished = self._createEvent()
        self.onRequestBootcampFinish = self._createEvent()
        self.onBattleLoaded = self._createEvent()
        self.onResultScreenFinished = self._createEvent()
        self.onBCGUIComponentLifetime = self._createEvent()
        self.onBattleComponentVisibility = self._createEvent()
        self.onRequestBootcampMessageWindowClose = self._createEvent()
        self.onBattleFinishAnimationComplete = self._createEvent()
        self.onGameplayChoice = self._createEvent()

    def destroy(self):
        self.__manager.clear()

    def _createEvent(self):
        return Event.Event(self.__manager)


g_bootcampEvents = _BootCampEvents()
