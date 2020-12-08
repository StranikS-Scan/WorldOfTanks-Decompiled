# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/NewYearTalismanObject.py
import AnimationSequence
import BigWorld
import Math
from NewYearTalismanBaseObject import NewYearTalismanBaseObject
from gui.Scaleform.managers.cursor_mgr import CursorManager
from uilogging.decorators import loggerTarget, loggerEntry, logOnMatch
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger
from vehicle_systems.stricted_loading import makeCallbackWeak
_EVENT_REVEAL_IN = 'ev_reveal_in'
_EVENT_REVEAL_IN_COMPLETE = 'ev_reveal_in_complete'
_PROGRESS_LEVEL = 'progress_level'
_SHOW_GIFT_IDLE = 'show_gift_idle'
_HANGAR_GIFT_IDLE = 'HangarGiftIdle'
_GIFT_IDLE_01 = 'GiftIdle01_'
_DELAY_GIFT_IDLE = 2.0
_GIFT_IDLE_NAMES_FORMAT = 'giftIdleL{grade}'

def getGiftIdleName(progressLevel):
    return _GIFT_IDLE_NAMES_FORMAT.format(grade=progressLevel)


class TalismanGradeIdleAnimation(object):
    __slots__ = ('__animator', '__isPlaying', '__weakref__', '__callbackId')

    def __init__(self):
        self.__isPlaying = False
        self.__animator = None
        self.__callbackId = None
        return

    @property
    def isPlaying(self):
        return self.__isPlaying

    def clear(self):
        self.__clearCallback()
        self.__stopAnimation()
        self.__animator = None
        return

    def play(self, needDelay=False):
        self.__isPlaying = True
        self.__clearCallback()
        if needDelay:
            self.__callbackId = BigWorld.callback(_DELAY_GIFT_IDLE, self.__play)
        else:
            self.__startAnimation()

    def stop(self):
        self.__isPlaying = False
        self.__stopAnimation()

    def loadAnimationSequence(self, matrix, spaceID, resourceName):
        loader = AnimationSequence.Loader(resourceName, spaceID)
        BigWorld.loadResourceListBG((loader,), makeCallbackWeak(self.__onAnimationLoaded, resourceName, matrix))

    def __clearCallback(self):
        if self.__callbackId is not None:
            BigWorld.cancelCallback(self.__callbackId)
            self.__callbackId = None
        return

    def __play(self):
        if self.__isPlaying:
            self.__startAnimation()
        self.__callbackId = None
        return

    def __startAnimation(self):
        if self.__animator is None:
            return
        else:
            self.__animator.setEnabled(True)
            self.__animator.start()
            return

    def __stopAnimation(self):
        if self.__animator is None:
            return
        else:
            self.__animator.stop()
            self.__animator.setEnabled(False)
            return

    def __onAnimationLoaded(self, resourceName, matrix, resourceList):
        self.clear()
        self.__animator = resourceList[resourceName]
        self.__animator.bindToWorld(matrix)
        if self.__isPlaying:
            self.play()


@loggerTarget(logKey=NY_LOG_KEYS.NY_TALISMANS, loggerCls=NYLogger)
class NewYearTalismanObject(NewYearTalismanBaseObject):

    def __init__(self):
        super(NewYearTalismanObject, self).__init__()
        self.__gradeIdleAnimator = None
        return

    @loggerEntry
    def onEnterWorld(self, prereqs):
        super(NewYearTalismanObject, self).onEnterWorld(prereqs)
        self.__gradeIdleAnimator = TalismanGradeIdleAnimation()
        self._talismanController.talismanAdded(self)
        self._talismanController.onShowGiftLevelUpEffect += self.__onProgressLevelChanged

    def onLeaveWorld(self):
        self.__gradeIdleAnimator.clear()
        self.__gradeIdleAnimator = None
        self._talismanController.talismanRemoved(self)
        self._talismanController.onShowGiftLevelUpEffect -= self.__onProgressLevelChanged
        super(NewYearTalismanObject, self).onLeaveWorld()
        return

    def setAnimatorTrigger(self, triggerName):
        if self._animator is None:
            return
        elif triggerName == _SHOW_GIFT_IDLE and self._animator.getCurrNodeName() == _HANGAR_GIFT_IDLE:
            return
        else:
            super(NewYearTalismanObject, self).setAnimatorTrigger(triggerName)
            return

    def playGiftIdleAnimation(self):
        if self._animator is None:
            return
        else:
            currNodeName = self._animator.getCurrNodeName()
            needDelay = currNodeName != _HANGAR_GIFT_IDLE and not currNodeName.startswith(_GIFT_IDLE_01)
            self.__gradeIdleAnimator.play(needDelay)
            return

    def stopGiftIdleAnimation(self):
        self.__gradeIdleAnimator.stop()

    def _getTalismanState(self):
        if not self._talismanController.mouseEventsAvailable() or not self.__isInInventory():
            return 'unavailable'
        return 'received' if self.__isGiftReceived() else 'available'

    @logOnMatch(objProperty='_getTalismanState', needCall=True, matches={'received': NY_LOG_ACTIONS.NY_TALISMAN_CLICK_RECEIVED,
     'available': NY_LOG_ACTIONS.NY_TALISMAN_CLICK_AVAILABLE})
    def onMouseClick(self):
        if self.__isGiftReceived():
            return
        if not self._talismanController.mouseEventsAvailable():
            return
        if not self.__isInInventory():
            return
        self._talismanController.giftMoveTo(self.talismanName)

    def _onAnimatorEvent(self, eventName):
        if eventName == _EVENT_REVEAL_IN:
            self._stopCongratsEffect()

    def _addEdgeDetect(self):
        if not self._talismanController.mouseEventsAvailable():
            return
        if not self.__isGiftReceived() and self.__isInInventory():
            super(NewYearTalismanObject, self)._addEdgeDetect()

    def _delEdgeDetect(self):
        if not self.__isGiftReceived() and self.__isInInventory():
            super(NewYearTalismanObject, self)._delEdgeDetect()

    def _onAnimatorStarted(self):
        self._talismanController.talismanAnimatorStarted(self.talismanName)
        self.__onProgressLevelChanged(self._newYearController.getTalismanProgressLevel())

    def _hoverOutCursorType(self):
        return CursorManager.ARROW if self._talismanController.isInGiftConfirmState() else CursorManager.DRAG_OPEN

    def __loadGradeIdleAnimationSequence(self, progressLevel):
        giftIdleName = getattr(self, getGiftIdleName(progressLevel), None)
        if giftIdleName:
            self.__gradeIdleAnimator.loadAnimationSequence(Math.Matrix(self.matrix), self.spaceID, giftIdleName)
        return

    def __isGiftReceived(self):
        return self._newYearController.isTalismanToyTaken()

    def __isInInventory(self):
        inventory = [ item.getSetting() for item in self._newYearController.getTalismans(isInInventory=True) ]
        return self.talismanName in inventory

    def __onProgressLevelChanged(self, progressLevel):
        if self._animator is not None:
            self._animator.setIntParam(_PROGRESS_LEVEL, progressLevel)
            self.__loadGradeIdleAnimationSequence(progressLevel)
        return
