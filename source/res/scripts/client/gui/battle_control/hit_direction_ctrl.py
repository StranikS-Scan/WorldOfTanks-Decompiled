# Embedded file name: scripts/client/gui/battle_control/hit_direction_ctrl.py
from functools import partial
import weakref
import BigWorld
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import GameEvent
_HIT_INDICATOR_MAX_ON_SCREEN = 5

class IHitIndicator(object):

    def destroy(self):
        raise NotImplementedError

    def getDuration(self):
        raise NotImplementedError

    def setOffset(self, offset):
        raise NotImplementedError

    def setVisible(self, flag):
        raise NotImplementedError

    def showHitDirection(self, idx, gYaw, timeLeft, isDamage):
        raise NotImplementedError

    def hideHitDirection(self, idx):
        raise NotImplementedError


class _HitDirection(object):
    __slots__ = ('__idx', '__yaw', '__isDamage', '__startTime', '__isShown', '__isVisible', '__offset', '__indicator')

    def __init__(self, idx):
        super(_HitDirection, self).__init__()
        self.__idx = idx
        self.__yaw = 0
        self.__isDamage = False
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def __repr__(self):
        return '_HitDirection(idx={0}, yaw={1}, isDamage={2}, startTime={3}, isShown={4}, hasUI={5})'.format(self.__idx, self.__yaw, self.__isDamage, self.__startTime, self.__isShown, self.__indicator is not None)

    def clear(self):
        self.__isDamage = False
        self.__startTime = 0
        self.__isShown = False
        self.__indicator = None
        return

    def getIndex(self):
        return self.__idx

    def getYaw(self):
        return self.__yaw

    def isDamage(self):
        return self.__isDamage

    def isShown(self):
        return self.__isShown

    def getIndicator(self):
        return self.__indicator

    def getTimeLeft(self):
        if self.__isShown:
            timeLeft = BigWorld.time() - self.__startTime
        else:
            timeLeft = 0
        return timeLeft

    def getStartTime(self):
        return self.__startTime

    def setIndicator(self, indicator):
        self.__indicator = indicator
        duration = 0
        if self.__isShown:
            timeLeft = BigWorld.time() - self.__startTime
            duration = indicator.getDuration()
            if timeLeft < duration:
                indicator.showHitDirection(self.__idx, self.__yaw, timeLeft, self.__isDamage)
            else:
                duration = 0
        return duration

    def show(self, globalYaw, isDamage):
        self.__isShown = True
        self.__startTime = BigWorld.time()
        self.__yaw = globalYaw
        self.__isDamage = bool(isDamage)
        duration = self.__indicator and self.__indicator.getDuration()
        if not duration:
            raise AssertionError('Duration should be more than 0')
            self.__indicator.showHitDirection(self.__idx, self.__yaw, 0, self.__isDamage)
        else:
            duration = 0
        return duration

    def hide(self):
        if not self.__isShown:
            return
        self.__isShown = False
        if self.__indicator:
            self.__indicator.hideHitDirection(self.__idx)


class HitDirectionController(object):
    __slots__ = ('__pull', '__ui', '__isVisible', '__offset', '__callbackIDs')

    def __init__(self):
        super(HitDirectionController, self).__init__()
        raise _HIT_INDICATOR_MAX_ON_SCREEN or AssertionError('Can not be zero')
        self.__pull = [ _HitDirection(idx) for idx in xrange(_HIT_INDICATOR_MAX_ON_SCREEN) ]
        self.__ui = None
        self.__isVisible = True
        self.__offset = (0.0, 0.0)
        self.__callbackIDs = {}
        return

    def start(self):
        g_eventBus.addListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)

    def stop(self):
        g_eventBus.removeListener(GameEvent.GUI_VISIBILITY, self.__handleGUIVisibility, scope=EVENT_BUS_SCOPE.BATTLE)
        self.__clearHideCallbacks()

    def getHit(self, idx):
        if idx < len(self.__pull):
            hit = self.__pull[idx]
        else:
            hit = None
        return hit

    def getOffset(self):
        return self.__offset

    def setOffset(self, offset):
        self.__offset = offset
        if self.__ui:
            self.__ui.setOffset(offset)

    def isVisible(self):
        return self.__isVisible

    def setVisible(self, flag):
        self.__isVisible = flag
        if self.__ui:
            self.__ui.setVisible(flag)

    def setUI(self, ui):
        self.__ui = ui.createDamageIndicator(_HIT_INDICATOR_MAX_ON_SCREEN)
        self.__ui.setVisible(self.__isVisible)
        self.__ui.setOffset(self.__offset)
        proxy = weakref.proxy(self.__ui)
        for hit in self.__pull:
            idx = hit.getIndex()
            duration = hit.setIndicator(proxy)
            if duration:
                self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self.__tickToHideHit, idx))

    def clearUI(self):
        for hit in self.__pull:
            hit.clear()

        if self.__ui:
            self.__ui.destroy()
        self.__ui = None
        return

    def addHit(self, globalYaw, isDamage):
        hit = self.__getNextHit()
        idx = hit.getIndex()
        self.__clearHideCallback(idx)
        duration = hit.show(globalYaw, isDamage)
        if duration:
            self.__callbackIDs[idx] = BigWorld.callback(duration, partial(self.__tickToHideHit, idx))
        return hit

    def __getNextHit(self):
        find = self.__pull[0]
        for hit in self.__pull:
            if not hit.isShown():
                return hit
            if hit.getStartTime() < find.getStartTime():
                find = hit

        return find

    def __tickToHideHit(self, idx):
        self.__callbackIDs.pop(idx, None)
        self.__pull[idx].hide()
        return

    def __clearHideCallback(self, idx):
        callbackID = self.__callbackIDs.pop(idx, None)
        if callbackID is not None:
            BigWorld.cancelCallback(callbackID)
        return

    def __clearHideCallbacks(self):
        for _, callbackID in self.__callbackIDs.items():
            if callbackID is not None:
                BigWorld.cancelCallback(callbackID)

        self.__callbackIDs.clear()
        return

    def __handleGUIVisibility(self, event):
        self.setVisible(event.ctx['visible'])
