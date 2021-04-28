# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/timer_helpers.py
import logging
import BigWorld
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES as _TIMER_TYPES
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import PointOfInterestEvent
from helpers import dependency
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
from soft_exception import SoftException
from weekend_brawl_common import VehiclePOIStatus, POIActivityStatus, UNKNOWN_TIME
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.weekend_brawl.timersPanel.interestPoint
_MAIN_TIMER_LEVEL = 'warning'

class _PointOfInterestTimerHelper(object):
    __slots__ = ('_idx', '_viewRef', '_value', '_isVisible')
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, view, idx):
        self._idx = idx
        self._isVisible = False
        self._viewRef = view
        self._value = None
        self._addListeners()
        return

    def destroy(self):
        if self._isVisible:
            self._hideTimer()
        self._removeListeners()
        self._viewRef = None
        self._value = None
        return

    def getIdx(self):
        return self._idx

    def getTimerTypeID(self):
        raise NotImplementedError

    def getData(self):
        return (self.getTimerTypeID(),
         self._getDuration(),
         self._getLevel(),
         self._getFinishTime(),
         self._getStartTime())

    def showText(self):
        pass

    def update(self, newValue):
        isNeedActivated = self._isNeedToShow(newValue)
        if isNeedActivated:
            self._showTimer(newValue)
        elif self._isVisible:
            self._hideTimer()

    def _addListeners(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self.__onPostMortemSwitched
        g_playerEvents.onRoundFinished += self.__onRoundFinished
        g_eventBus.addListener(PointOfInterestEvent.ENTER_INTO_POINT, self._onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(PointOfInterestEvent.LEAVE_POINT, self._onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _removeListeners(self):
        ctrl = self._sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onPostMortemSwitched
        g_playerEvents.onRoundFinished -= self.__onRoundFinished
        g_eventBus.removeListener(PointOfInterestEvent.ENTER_INTO_POINT, self._onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(PointOfInterestEvent.LEAVE_POINT, self._onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)
        return

    def _isNeedToShow(self, newValue):
        return False

    def _getLevel(self):
        raise NotImplementedError

    def _getStartTime(self):
        return UNKNOWN_TIME

    def _getFinishTime(self):
        finishTime = self._value.endTime
        return finishTime if finishTime != UNKNOWN_TIME else BigWorld.serverTime() + self._getDuration()

    def _getDuration(self):
        return UNKNOWN_TIME

    def _initParams(self, newValue):
        self._value = newValue
        self._isVisible = True

    def _showTimer(self, newValue):
        self._initParams(newValue)
        self._viewRef.showTimer(self.getIdx())

    def _hideTimer(self):
        self._viewRef.removeTimer(self.getIdx())
        self._isVisible = False

    def _onEnterIntoPoint(self, event):
        pass

    def _onLeavePoint(self, event):
        self._hideTimer()

    def _isInPoint(self, pointID):
        poiCtrl = self._sessionProvider.dynamic.pointsOfInterest
        return False if poiCtrl is None else poiCtrl.isInPoint(pointID)

    def _getPointStatus(self, pointID):
        point = BigWorld.entity(pointID)
        return point.activityStatus.statusID if point is not None else None

    def _isVehicleAlive(self):
        vehicle = self._sessionProvider.shared.vehicleState.getControllingVehicle()
        return vehicle is not None and vehicle.isAlive()

    def __onPostMortemSwitched(self, *args):
        self._hideTimer()

    def __onRoundFinished(self, winnerTeam, reason):
        self._hideTimer()


class CapturingTimer(_PointOfInterestTimerHelper):
    __slots__ = ('_duration',)

    def __init__(self, view, idx):
        super(CapturingTimer, self).__init__(view, idx)
        self._duration = 0

    def getTimerTypeID(self):
        return _TIMER_TYPES.INTEREST_POINT_CAPTURING

    def showText(self):
        description = backport.text(_STR_PATH.capturing())
        self._viewRef.as_setTimerTextS(self.getTimerTypeID(), '', description)

    def _isNeedToShow(self, newValue):
        return newValue.vehicleStatus == VehiclePOIStatus.CAPTURING

    def _getLevel(self):
        return _MAIN_TIMER_LEVEL

    def _getFinishTime(self):
        return self._value.endTime

    def _getStartTime(self):
        return max(self._value.endTime - self._duration, BigWorld.serverTime())

    def _getDuration(self):
        return self._duration

    def _initParams(self, newValue):
        super(CapturingTimer, self)._initParams(newValue)
        point = BigWorld.entity(self._value.poiID)
        self._duration = point.captureTime


class BlockedCapturingTimer(_PointOfInterestTimerHelper):
    __slots__ = ()

    def getTimerTypeID(self):
        return _TIMER_TYPES.INTEREST_POINT_BLOCKED

    def showText(self):
        title = backport.text(_STR_PATH.cantCapture())
        self._viewRef.as_setSecondaryTimerTextS(self.getTimerTypeID(), title)

    def _addListeners(self):
        super(BlockedCapturingTimer, self)._addListeners()
        g_eventBus.addListener(PointOfInterestEvent.START_COOLDOWN, self.__onStartCooldown, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(PointOfInterestEvent.END_COOLDOWN, self.__onEndCooldown, scope=EVENT_BUS_SCOPE.BATTLE)

    def _removeListeners(self):
        super(BlockedCapturingTimer, self)._removeListeners()
        g_eventBus.removeListener(PointOfInterestEvent.START_COOLDOWN, self.__onStartCooldown, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(PointOfInterestEvent.END_COOLDOWN, self.__onEndCooldown, scope=EVENT_BUS_SCOPE.BATTLE)

    def _isNeedToShow(self, newValue):
        if not self._isInPoint(newValue.poiID):
            return False
        else:
            if newValue.prevVehicleStatus is None:
                validStatuses = VehiclePOIStatus.AFTER_CAPTURE_RANGE
            else:
                validStatuses = VehiclePOIStatus.EQUIPMENT_OWNER
            return self.__isValidStateToShow(newValue, validStatuses)

    def _getLevel(self):
        return _TIMER_TYPES.WARNING_VIEW

    def _onEnterIntoPoint(self, event):
        ctx = event.ctx
        if self.__isValidStateToShow(ctx, VehiclePOIStatus.AFTER_CAPTURE_RANGE):
            self._showTimer(ctx)

    def __isValidStateToShow(self, value, states):
        if value.vehicleStatus not in states:
            return False
        pointStatus = self._getPointStatus(value.poiID)
        return pointStatus in POIActivityStatus.ACTIVE_RANGE

    def __onStartCooldown(self, event):
        if self._isVisible:
            self._hideTimer()

    def __onEndCooldown(self, event):
        poiCtrl = self._sessionProvider.dynamic.pointsOfInterest
        if poiCtrl is None:
            return
        else:
            ctx = event.ctx
            if poiCtrl.isInPoint(ctx.poiID) and poiCtrl.isInvader() and self._isVehicleAlive():
                self._showTimer(ctx)
            return


class VehicleCooldownTimer(_PointOfInterestTimerHelper):
    __slots__ = ()

    def getTimerTypeID(self):
        return _TIMER_TYPES.INTEREST_POINT_BLOCKED

    def showText(self):
        title = backport.text(_STR_PATH.blocked())
        self._viewRef.as_setSecondaryTimerTextS(self.getTimerTypeID(), title)

    def _isNeedToShow(self, newValue):
        return newValue.vehicleStatus == VehiclePOIStatus.COOLDOWN

    def _getLevel(self):
        return _TIMER_TYPES.WARNING_VIEW

    def _onEnterIntoPoint(self, event):
        ctx = event.ctx
        if not self._isNeedToShow(ctx):
            return
        pointStatus = self._getPointStatus(ctx.poiID)
        if pointStatus in POIActivityStatus.ACTIVE_RANGE:
            self._showTimer(ctx)


class _HelperWithCallback(_PointOfInterestTimerHelper):
    __slots__ = ('_delayedCB', '_delayTime')

    def __init__(self, view, idx):
        super(_HelperWithCallback, self).__init__(view, idx)
        self._delayTime = 0
        self._delayedCB = None
        return

    def start(self):
        self._delayedCB = BigWorld.callback(self._delayTime, self._delayedFunc)

    def destroy(self):
        self.__clearCallback()
        super(_HelperWithCallback, self).destroy()

    def _showTimer(self, newValue):
        super(_HelperWithCallback, self)._showTimer(newValue)
        self.start()

    def _hideTimer(self):
        self.__clearCallback()
        super(_HelperWithCallback, self)._hideTimer()

    def _delayedFunc(self):
        raise NotImplementedError

    def __clearCallback(self):
        if self._delayedCB is not None:
            BigWorld.cancelCallback(self._delayedCB)
            self._delayedCB = None
        return


class CapturedTimer(_HelperWithCallback):
    __slots__ = ()
    _DURATION = 2

    def __init__(self, view, idx):
        super(CapturedTimer, self).__init__(view, idx)
        self._delayTime = self._DURATION

    def getTimerTypeID(self):
        return _TIMER_TYPES.INTEREST_POINT_CAPTURED

    def showText(self):
        description = backport.text(_STR_PATH.captured())
        self._viewRef.as_setSecondaryTimerTextS(self.getTimerTypeID(), '', description)

    def _isNeedToShow(self, newValue):
        return newValue.vehicleStatus == VehiclePOIStatus.CAPTURED and newValue.prevVehicleStatus == VehiclePOIStatus.CAPTURING

    def _getLevel(self):
        return _TIMER_TYPES.WARNING_VIEW

    def _getDuration(self):
        return self._DURATION

    def _delayedFunc(self):
        self._viewRef.removeTimer(self.getIdx())
        self._delayedCB = None
        return


class PointCooldownTimer(_HelperWithCallback):
    __slots__ = ('_endTime', '_duration')
    _DELAYED = 3

    def __init__(self, view, idx):
        super(PointCooldownTimer, self).__init__(view, idx)
        self._endTime = UNKNOWN_TIME
        self._duration = 0

    def getTimerTypeID(self):
        return _TIMER_TYPES.INTEREST_POINT_COOLDOWN

    def showText(self):
        description = backport.text(_STR_PATH.cooldown())
        self._viewRef.as_setTimerTextS(self.getTimerTypeID(), '', description)

    def update(self, newValue):
        if self.__isNeedDelayedActivate(newValue):
            self._delayTime = self._DELAYED
            self._initParams(newValue)
            self.start()
        elif self._isNeedToShow(newValue):
            self._showTimer(newValue)
        elif not self.__isNeedToHold(newValue):
            self._hideTimer()

    def _addListeners(self):
        super(PointCooldownTimer, self)._addListeners()
        g_eventBus.addListener(PointOfInterestEvent.START_COOLDOWN, self.__onStartCooldown, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(PointOfInterestEvent.END_COOLDOWN, self.__onEndCooldown, scope=EVENT_BUS_SCOPE.BATTLE)

    def _removeListeners(self):
        super(PointCooldownTimer, self)._removeListeners()
        g_eventBus.removeListener(PointOfInterestEvent.START_COOLDOWN, self.__onStartCooldown, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(PointOfInterestEvent.END_COOLDOWN, self.__onEndCooldown, scope=EVENT_BUS_SCOPE.BATTLE)

    def _isNeedToShow(self, newValue):
        point = BigWorld.entity(newValue.poiID)
        return False if point is None else point.activityStatus.statusID == POIActivityStatus.COOLDOWN

    def _getLevel(self):
        return _MAIN_TIMER_LEVEL

    def _getFinishTime(self):
        return self._endTime

    def _getDuration(self):
        return self._duration - self._delayTime

    def _getStartTime(self):
        return self._endTime - self._duration

    def _initParams(self, newValue):
        self._value = newValue
        point = BigWorld.entity(self._value.poiID)
        if point is None:
            raise SoftException('Point of Interest is not found')
        self._duration = point.cooldown
        if point.activityStatus.statusID != POIActivityStatus.COOLDOWN:
            self._endTime = BigWorld.serverTime() + self._duration
        else:
            self._endTime = point.activityStatus.endTime
        self._isVisible = True
        return

    def _delayedFunc(self):
        self._viewRef.showTimer(self.getIdx())
        self._delayedCB = None
        return

    def _showTimer(self, newValue):
        self._delayTime = 0
        self._initParams(newValue)
        self._viewRef.showTimer(self.getIdx())

    def _hideTimer(self):
        super(PointCooldownTimer, self)._hideTimer()
        self._delayTime = 0

    def _onEnterIntoPoint(self, event):
        ctx = event.ctx
        pointStatus = self._getPointStatus(ctx.poiID)
        if pointStatus == POIActivityStatus.COOLDOWN:
            self._showTimer(ctx)

    def __onStartCooldown(self, event):
        ctx = event.ctx
        if self._isVisible or not self._isInPoint(ctx.poiID) or not self._isVehicleAlive():
            return
        self._showTimer(ctx)

    def __onEndCooldown(self, event):
        ctx = event.ctx
        if self._isInPoint(ctx.poiID):
            self._hideTimer()

    def __isNeedDelayedActivate(self, newValue):
        return newValue.vehicleStatus == VehiclePOIStatus.CAPTURED and newValue.prevVehicleStatus == VehiclePOIStatus.CAPTURING and self._isVehicleAlive()

    def __isNeedToHold(self, newValue):
        if not self._isInPoint(newValue.poiID) or not self._isVehicleAlive():
            return False
        else:
            point = BigWorld.entity(newValue.poiID)
            return False if point is None else self._isVisible and point.activityStatus.statusID == POIActivityStatus.COOLDOWN
