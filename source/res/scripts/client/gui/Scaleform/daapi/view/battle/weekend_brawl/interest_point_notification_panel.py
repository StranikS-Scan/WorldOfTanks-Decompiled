# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/weekend_brawl/interest_point_notification_panel.py
from collections import namedtuple
import logging
import BigWorld
import BattleReplay
from ReplayEvents import g_replayEvents
from gui.battle_control.battle_constants import UNDEFINED_VEHICLE_ID, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.points_of_interest_ctrl import IPointOfInterestListener
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.daapi.view.meta.InterestPointNotificationPanelMeta import InterestPointNotificationPanelMeta
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import PointOfInterestEvent
from gui.shared.formatters import text_styles
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from weekend_brawl_common import POIActivityStatus, UNKNOWN_TIME, EMPTY_POI_ID
_logger = logging.getLogger(__name__)
_STR_PATH = R.strings.weekend_brawl.interestPointNotificationPanel
_CAPTURED_DURATION = 2
_PointParams = namedtuple('_PointParams', ('status', 'vehicleID'))
_PointParams.__new__.__defaults__ = (POIActivityStatus.ACTIVE, UNDEFINED_VEHICLE_ID)

def _isPlayerTeam(vehicleID):
    return vehicleID != UNDEFINED_VEHICLE_ID


class _TimerHelper(object):
    __slots__ = ('_viewRef', '_pointProperties', '_pointParams')
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, viewRef):
        self._viewRef = viewRef
        self._pointProperties = None
        self._pointParams = {}
        return

    def destroy(self):
        self._hideTimer()
        self._viewRef = None
        self._pointProperties = None
        self._pointParams = {}
        return

    def setProperties(self, properties):
        self._pointProperties = properties

    def initPoints(self, pointID, status):
        self._pointParams[pointID] = _PointParams(status)

    def update(self, pointID, newState, vehicleID, startTime):
        if pointID not in self._pointParams:
            return
        if self._isNeededShow(pointID, newState, vehicleID):
            self._showTimer(pointID, vehicleID, startTime)
        elif self._isNeededHide(pointID, newState, vehicleID):
            self._hideTimer()
        self._pointParams[pointID] = _PointParams(newState, vehicleID)

    def updateControllingVehicle(self, value):
        raise NotImplementedError

    def changeSpeed(self):
        for pointID, pointParams in self._pointParams.iteritems():
            vehicleID = pointParams.vehicleID
            if self._isNeededShow(pointID, pointParams.status, vehicleID):
                self._updateWithNewSpeed(pointID, vehicleID)

    def _showTimer(self, pointID, vehicleID, startTime):
        raise NotImplementedError

    def _hideTimer(self):
        raise NotImplementedError

    def _updateWithNewSpeed(self, pointID, vehicleID):
        raise NotImplementedError

    def _isNeededShow(self, pointID, state, vehicleID):
        return False

    def _isNeededHide(self, pointID, state, vehicleID=UNDEFINED_VEHICLE_ID):
        return False

    def _isPlayer(self, vehicleID):
        controllingVehicleID = self._sessionProvider.shared.vehicleState.getControllingVehicleID()
        if controllingVehicleID != UNDEFINED_VEHICLE_ID:
            return controllingVehicleID == vehicleID
        else:
            player = BigWorld.player()
            if player is None:
                _logger.error('Actual player is None')
                return False
            attachedVehicle = player.getVehicleAttached()
            return vehicleID == attachedVehicle.id if attachedVehicle is not None else False

    def _getPointOfInterestCtrl(self):
        return self._sessionProvider.dynamic.pointsOfInterest

    def _getSpeed(self):
        return BattleReplay.g_replayCtrl.playbackSpeed if self._sessionProvider.isReplayPlaying else 1.0


class _CapturingTimer(_TimerHelper):
    __slots__ = ()

    def updateControllingVehicle(self, value):
        poiCtrl = self._getPointOfInterestCtrl()
        points = poiCtrl.getCapturingPoints()
        for pointID, vehicleID, startTime in points:
            self.update(pointID, POIActivityStatus.CAPTURING, vehicleID, startTime)

    def _showTimer(self, pointID, vehicleID, startTime):
        self.__startCapturing(pointID, vehicleID, startTime)

    def _hideTimer(self):
        self._viewRef.as_setCapturingStateS('', isPlayerTeam=False, timeLeft=0, timeTotal=UNKNOWN_TIME)

    def _updateWithNewSpeed(self, pointID, vehicleID):
        self.__startCapturing(pointID, vehicleID)

    def _isNeededShow(self, pointID, state, vehicleID):
        return state == POIActivityStatus.CAPTURING and not self._isPlayer(vehicleID)

    def _isNeededHide(self, pointID, state, vehicleID=UNDEFINED_VEHICLE_ID):
        return self._pointParams[pointID].status == POIActivityStatus.CAPTURING

    def __startCapturing(self, pointID, vehicleID, startTime=UNKNOWN_TIME):
        isPlayerTeam = _isPlayerTeam(vehicleID)
        poiCtrl = self._getPointOfInterestCtrl()
        label = '' if poiCtrl.isAbilityAvailable() else self.__getCapturingLabel(vehicleID)
        timeTotal = self._pointProperties.captureTime
        if startTime == UNKNOWN_TIME:
            startTime = poiCtrl.getStartTime(pointID)
        timeLeft = startTime + timeTotal - BigWorld.serverTime()
        speed = self._getSpeed()
        self._viewRef.as_setCapturingStateS(label, isPlayerTeam, min(timeLeft, timeTotal), timeTotal, speed)

    def __getCapturingLabel(self, vehicleID):
        if _isPlayerTeam(vehicleID):
            battleCtx = self._sessionProvider.getCtx()
            playerName = battleCtx.getPlayerFullName(vehicleID, showVehShortName=False, showRegion=False)
            return backport.text(_STR_PATH.ally.capturing(), playerName=text_styles.goldTextTitle(playerName))
        return backport.text(_STR_PATH.enemy.capturing())


class _CooldownTimer(_TimerHelper):
    __slots__ = ()

    def __init__(self, viewRef):
        super(_CooldownTimer, self).__init__(viewRef)
        self.__addListeners()

    def destroy(self):
        self.__removeListeners()
        super(_CooldownTimer, self).destroy()

    def updateControllingVehicle(self, value):
        pointID = value.poiID
        if pointID != EMPTY_POI_ID:
            return
        poiCtrl = self._getPointOfInterestCtrl()
        state = poiCtrl.getPointStatus(pointID)
        startTime = poiCtrl.getStartTime(pointID)
        self.update(pointID, state, value.vehicleID, startTime)

    def _showTimer(self, pointID, vehicleID, startTime):
        self.__startCooldown(pointID, vehicleID, startTime)

    def _hideTimer(self):
        self._viewRef.as_setCooldownStateS(timeLeft=0, timeTotal=UNKNOWN_TIME)

    def _updateWithNewSpeed(self, pointID, vehicleID):
        self.__showCooldown(pointID)

    def _isNeededShow(self, pointID, state, vehicleID):
        return state == POIActivityStatus.COOLDOWN

    def _isNeededHide(self, pointID, state, vehicleID=UNDEFINED_VEHICLE_ID):
        return self._pointParams[pointID].status == POIActivityStatus.COOLDOWN

    def __startCooldown(self, pointID, _, startTime):
        if self.__isShowCaptured(pointID):
            self.__capturedSuccess(pointID)
        poiCtrl = self._getPointOfInterestCtrl()
        if poiCtrl.isInPoint(pointID):
            return
        self.__showCooldown(pointID, startTime)

    def __showCooldown(self, pointID, startTime=UNKNOWN_TIME):
        totalTime = self._pointProperties.cooldown
        if startTime == UNKNOWN_TIME:
            poiCtrl = self._getPointOfInterestCtrl()
            startTime = poiCtrl.getStartTime(pointID)
        timeLeft = min(startTime + totalTime - BigWorld.serverTime(), totalTime)
        speed = self._getSpeed()
        self._viewRef.as_setCooldownStateS(timeLeft, totalTime, speed)

    def __isShowCaptured(self, pointID):
        params = self._pointParams[pointID]
        vehicleID = params.vehicleID
        prevState = params.status
        return not self._isPlayer(vehicleID) and prevState == POIActivityStatus.CAPTURING

    def __capturedSuccess(self, pointID):
        params = self._pointParams[pointID]
        isPlayerTeam = _isPlayerTeam(params.vehicleID)
        label = self.__getCapturedLabel(isPlayerTeam)
        speed = self._getSpeed()
        self._viewRef.as_setCapturedStateS(label, isPlayerTeam, _CAPTURED_DURATION, speed)

    def __onEnterIntoPoint(self, event):
        ctx = event.ctx
        pointID = ctx.poiID
        if self._pointParams[pointID].status == POIActivityStatus.COOLDOWN:
            self._hideTimer()

    def __onLeavePoint(self, event):
        pointID = event.ctx.poiID
        pointParams = self._pointParams.get(pointID)
        if pointParams is None:
            return
        else:
            if pointParams.status == POIActivityStatus.COOLDOWN:
                poiCtrl = self._getPointOfInterestCtrl()
                startTime = poiCtrl.getStartTime(pointID)
                self.__showCooldown(pointID, startTime)
            return

    def __addListeners(self):
        g_eventBus.addListener(PointOfInterestEvent.ENTER_INTO_POINT, self.__onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.addListener(PointOfInterestEvent.LEAVE_POINT, self.__onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)

    def __removeListeners(self):
        g_eventBus.removeListener(PointOfInterestEvent.ENTER_INTO_POINT, self.__onEnterIntoPoint, scope=EVENT_BUS_SCOPE.BATTLE)
        g_eventBus.removeListener(PointOfInterestEvent.LEAVE_POINT, self.__onLeavePoint, scope=EVENT_BUS_SCOPE.BATTLE)

    @staticmethod
    def __getCapturedLabel(isPlayerTeam):
        labelID = _STR_PATH.ally.captured() if isPlayerTeam else _STR_PATH.enemy.captured()
        return backport.text(labelID)


class InterestPointNotificationPanel(InterestPointNotificationPanelMeta, IPointOfInterestListener):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __helpers = [_CapturingTimer, _CooldownTimer]

    def __init__(self):
        super(InterestPointNotificationPanel, self).__init__()
        self.__stateProcessors = self.__createHelpers()

    def _populate(self):
        super(InterestPointNotificationPanel, self)._populate()
        self.__addListeners()

    def getPointProperties(self, properties):
        pointProperties = properties
        for processor in self.__stateProcessors:
            processor.setProperties(pointProperties)

    def addPoint(self, pointID, status):
        for processor in self.__stateProcessors:
            processor.initPoints(pointID, status)

    def updateState(self, pointID, newState, startTime, vehicleID=UNDEFINED_VEHICLE_ID):
        for processor in self.__stateProcessors:
            processor.update(pointID, newState, vehicleID, startTime)

    def _dispose(self):
        self.__removeListeners()
        self.__destroyHelpers()
        super(InterestPointNotificationPanel, self)._dispose()

    def __addListeners(self):
        stateCtrl = self.__getVehicleStateCtrl()
        if stateCtrl is not None:
            stateCtrl.onVehicleStateUpdated += self.__onVehicleStateUpdated
            stateCtrl.onPostMortemSwitched += self.__onPostMortemSwitched
        g_replayEvents.onPause += self.__onReplayPaused
        return

    def __removeListeners(self):
        stateCtrl = self.__sessionProvider.shared.vehicleState
        if stateCtrl is not None:
            stateCtrl.onPostMortemSwitched -= self.__onPostMortemSwitched
            stateCtrl.onVehicleStateUpdated -= self.__onVehicleStateUpdated
        g_replayEvents.onPause -= self.__onReplayPaused
        return

    def __onReplayPaused(self, _):
        for processor in self.__stateProcessors:
            processor.changeSpeed()

    def __onVehicleStateUpdated(self, state, value):
        ctrl = self.__getVehicleStateCtrl()
        if ctrl is None:
            return
        else:
            if ctrl.isInPostmortem and state == VEHICLE_VIEW_STATE.POINT_OF_INTEREST:
                for processor in self.__stateProcessors:
                    processor.updateControllingVehicle(value)

            return

    def __onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.as_setIsPostmortemS(isPostmortem=True)

    def __getPointOfInterestCtrl(self):
        return self.__sessionProvider.dynamic.pointsOfInterest

    def __getVehicleStateCtrl(self):
        return self.__sessionProvider.shared.vehicleState

    def __createHelpers(self):
        return [ itmClazz(self) for itmClazz in self.__helpers ]

    def __destroyHelpers(self):
        while self.__stateProcessors:
            item = self.__stateProcessors.pop()
            item.destroy()

        self.__stateProcessors = None
        return
