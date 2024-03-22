# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/status_notifications/replay_components.py
import logging
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.Scaleform.daapi.view.battle.shared.status_notifications.components import StatusNotificationContainer, StatusNotificationsGroup
from gui.Scaleform.daapi.view.battle.shared.status_notifications.sn_items import TimerSN, TimeSnapshotHandler
from gui.Scaleform.daapi.view.battle.shared.timers_common import PrecisePythonTimer
_logger = logging.getLogger(__name__)

class CallbackPrecisePythonTimer(object):

    def __init__(self, tickCallback, endCallback):
        super(CallbackPrecisePythonTimer, self).__init__()
        self.tickCallback = tickCallback
        self.endCallback = endCallback

    def destroy(self):
        self.tickCallback = None
        self.endCallback = None
        return


class CallbackTruePythonTimer(PrecisePythonTimer):
    __slots__ = ('__short1stPeriodCbId', '__timeLeft', '__updateCallback')

    def __init__(self, viewObject, typeID, viewID, totalTime, finishTime, startTime=None, interval=1.0, secondInRow=False, **kwargs):
        super(CallbackTruePythonTimer, self).__init__(viewObject, typeID, viewID, totalTime, finishTime, startTime, interval, secondInRow, **kwargs)
        self.__timeLeft = None
        return

    def clear(self):
        self.__updateCallback = None
        self._viewObject.destroy()
        super(CallbackTruePythonTimer, self).clear()
        return

    def _hideView(self):
        if self._viewObject:
            self._viewObject.endCallback()

    def getTimeLeft(self):
        return self.__timeLeft

    def _setViewSnapshot(self, timeLeft):
        self.__timeLeft = timeLeft
        self._viewObject.tickCallback(timeLeft)

    def _showView(self, isBubble):
        pass


class _ReplaySnapshotHandler(TimeSnapshotHandler):

    def __init__(self, updateHandler):
        super(_ReplaySnapshotHandler, self).__init__(updateHandler)
        self.__ticker = None
        self.__finishTime = 0.0
        self.__totalTime = 0.0
        g_replayEvents.onPause += self.__onReplayPaused
        return

    def destroy(self):
        self.__destroyTicker()
        g_replayEvents.onPause -= self.__onReplayPaused
        super(_ReplaySnapshotHandler, self).destroy()

    def setTimeParams(self, totalTime, finishTime):
        super(_ReplaySnapshotHandler, self).setTimeParams(totalTime, finishTime)
        self.__totalTime = totalTime
        self.__finishTime = finishTime
        if BattleReplay.g_replayCtrl.playbackSpeed:
            self.__restartTicker()
        else:
            self.__destroyTicker()

    def __onReplayPaused(self, _):
        if BattleReplay.g_replayCtrl.playbackSpeed:
            self.__restartTicker()
        else:
            self.__destroyTicker()

    def __restartTicker(self):
        if self.__totalTime > 0:
            startTime = None
            if self.__ticker and self.__ticker.getTimeLeft() is not None:
                startTime = self.__totalTime - self.__ticker.getTimeLeft()
            self.__destroyTicker()
            self.__ticker = CallbackTruePythonTimer(viewObject=CallbackPrecisePythonTimer(self.__onTickerTick, self.__onTickerFinished), typeID=0, viewID=0, totalTime=self.__totalTime, finishTime=self.__finishTime, interval=BattleReplay.g_replayCtrl.playbackSpeed, startTime=startTime)
            self.__ticker.show()
        return

    def __onTickerTick(self, timeLeft):
        currTime = self.__totalTime - timeLeft
        self._updateHandler(currTime=currTime, totalTime=self.__totalTime, isUpdateRequired=True)

    def __onTickerFinished(self):
        self.__destroyTicker()
        self._updateHandler(currTime=0, totalTime=0, isUpdateRequired=True)

    def __destroyTicker(self):
        if self.__ticker:
            self.__ticker.clear()
            self.__ticker = None
        return


class ReplayStatusNotificationContainer(StatusNotificationContainer):

    def __init__(self, items, updateCallback):
        super(ReplayStatusNotificationContainer, self).__init__(items, updateCallback)
        itemUpdater = lambda item: item.setTimeHandler(_ReplaySnapshotHandler) if isinstance(item, TimerSN) else None
        for itm in self._items:
            if isinstance(itm, TimerSN):
                itemUpdater(itm)
            if isinstance(itm, StatusNotificationsGroup):
                itm.updateItems(itemUpdater)
