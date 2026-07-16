# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/w2gt/w2gt_plugin.py
from __future__ import absolute_import
import enum
from collections import defaultdict
from collections import namedtuple
import typing
import BigWorld
import Math
from Event import Event, EventManager
from account_helpers.settings_core.settings_constants import GAME
from chat_commands_consts import MarkerType
from constants import ARENA_PERIOD, W2GT_STAGES
from gui.battle_control import avatar_getter
from gui.battle_control.controllers.w2gt.w2gt_helper import isPointInsidePolygonByRayTracing
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from typing import Optional, List, Dict, Callable
    from gui.battle_control.controllers.w2gt.w2gt_data_mgr import W2GTDataMgr
    from helpers.server_settings import _W2GTConfig
_CALL_INTERVAL = 0.5
_W2GT_BATTLE_ZONE_TYPE = 'W2GT_BATTLE_ZONE'

class STAGE(enum.IntEnum):
    WAITING = 0
    ONGOING = 1
    ARRIVAL = 2
    FINISHED = 3

    @classmethod
    def hasValue(cls, value):
        return value in [ item.value for item in cls ]


_STAGE_MAP = {STAGE.ONGOING: W2GT_STAGES.STAGE1,
 STAGE.ARRIVAL: W2GT_STAGES.STAGE2}

class _StageData(namedtuple('_StageData', ('stage', 'ctx', 'startTime'))):

    def __new__(cls, **kwargs):
        defaults = dict(stage=STAGE.WAITING, ctx={}, startTime=0)
        defaults.update(kwargs)
        return super(_StageData, cls).__new__(cls, **defaults)

    def getCtx(self, name):
        return self.ctx.get(name)

    def passedTime(self):
        return BigWorld.serverTime() - self.startTime if self.startTime > 0 else 0

    def getNextStageStartTime(self, stageTimeLimit):
        if self.startTime <= 0:
            return 0
        return self.startTime - stageTimeLimit if self.passedTime() > stageTimeLimit else 0


class _SubPlugin(object):
    _STAGE = STAGE.WAITING
    _NEXT_STAGE = STAGE.FINISHED
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, permanentPlugin):
        self.__eManager = EventManager()
        self.onStageChanged = Event(self.__eManager)
        self.onReadyToDestroy = Event(self.__eManager)
        self._permanentPlugin = permanentPlugin
        self._isReadyToDestroy = None
        self._isDestroyed = False
        self.__stage = None
        self.__stageData = None
        self.__dataMgr = None
        self.__durationCallbackID = None
        self.__isActive = False
        return

    @property
    def dataMgr(self):
        return self.__dataMgr

    @property
    def stage(self):
        return self.__stage

    @property
    def isActive(self):
        return self.__isActive

    @isActive.setter
    def isActive(self, value):
        self.__isActive = value

    @property
    def isReadyToDestroy(self):
        return self._isReadyToDestroy

    @property
    def config(self):
        return self.__dataMgr.config

    def initialize(self, period, dataMgr, stageData):
        self._preInitialize(dataMgr, stageData)
        self.__activate(period)

    def updateStage(self, period, stage):
        if self.__stage != stage:
            self.__stage = stage
        self.__activate(period)

    def update(self):
        if not self.__isActive:
            return
        self._update()

    def canDestroy(self):
        return True

    def beforeDestroy(self):
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged

    def destroy(self):
        self.__inactivate()
        self.__eManager.clear()
        self.__dataMgr = None
        self.__stageData = None
        self._permanentPlugin = None
        self._isReadyToDestroy = True
        self._isDestroyed = True
        return

    @property
    def _ownVehicle(self):
        playerVehicleID = avatar_getter.getPlayerVehicleID()
        return BigWorld.entity(playerVehicleID)

    @property
    def _ownPosition(self):
        return self._ownVehicle.position

    @property
    def _isEnabled(self):
        return bool(self.__settingsCore.getSetting(GAME.W2GT_ENABLE))

    def _onEnableChanged(self, isEnabled):
        pass

    def _getActionTime(self):
        timeLimit = self.config.getTimeLimitByStage(_STAGE_MAP.get(self._STAGE))
        return timeLimit - self.__stageData.passedTime()

    def _preInitialize(self, dataMgr, stageData):
        self.__stage = stageData.stage
        self.__dataMgr = dataMgr
        self.__stageData = stageData
        self._isReadyToDestroy = False
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged

    def _onActivate(self):
        pass

    def _update(self):
        pass

    def _finishStage(self):
        self.__inactivate()
        timeLimit = self.config.getTimeLimitByStage(_STAGE_MAP.get(self._STAGE))
        startTime = self.__stageData.getNextStageStartTime(timeLimit)
        nextStage = self._getNextStage()
        self.onStageChanged(nextStage, self._buildExitContext(nextStage), startTime)

    def _buildExitContext(self, nextStage):
        return None

    def _getNextStage(self):
        return self._NEXT_STAGE

    def __onSettingsChanged(self, diff):
        if GAME.W2GT_ENABLE in diff:
            self._onEnableChanged(diff.get(GAME.W2GT_ENABLE, False))

    def __activate(self, period):
        if self.__isActive is False and period == ARENA_PERIOD.BATTLE:
            self.__isActive = self.__runStageCooldown()
            if self.__isActive:
                self._onActivate()

    def __inactivate(self):
        if self.__isActive:
            self.__isActive = False
            self.__clearDurationCallback()

    def __runStageCooldown(self):
        if self.stage != STAGE.WAITING and self.__durationCallbackID is None:
            actionTime = self._getActionTime()
            if actionTime > 0.0:
                self.__durationCallbackID = BigWorld.callback(actionTime, self._finishStage)
                return True
            self._finishStage()
        return False

    def __clearDurationCallback(self):
        if self.__durationCallbackID:
            BigWorld.cancelCallback(self.__durationCallbackID)
            self.__durationCallbackID = None
        return


class _SubPluginOngoing(_SubPlugin):
    _STAGE = STAGE.ONGOING
    _NEXT_STAGE = STAGE.ARRIVAL

    def __init__(self, permanentPlugin):
        super(_SubPluginOngoing, self).__init__(permanentPlugin)
        self.__selectedZoneID = None
        return

    def _update(self):
        vehPosition = self._ownPosition
        for zone in self.dataMgr.zones:
            if isPointInsidePolygonByRayTracing((vehPosition.x, vehPosition.z), zone.area2D):
                self.__selectedZoneID = zone.zoneID
                self._finishStage()
                return

    def _finishStage(self):
        if self.__selectedZoneID is None:
            self._NEXT_STAGE = STAGE.FINISHED
        super(_SubPluginOngoing, self)._finishStage()
        return

    def _buildExitContext(self, nextStage):
        return {'selectedZoneID': self.__selectedZoneID}


class _SubPluginArrival(_SubPlugin):
    _STAGE = STAGE.ARRIVAL
    _NEXT_STAGE = STAGE.FINISHED

    def __init__(self, permanentPlugin):
        super(_SubPluginArrival, self).__init__(permanentPlugin)
        self.__selectedZoneID = None
        return

    def _preInitialize(self, dataMgr, stageData):
        super(_SubPluginArrival, self)._preInitialize(dataMgr, stageData)
        self.__selectedZoneID = stageData.getCtx('selectedZoneID')

    def _buildExitContext(self, nextStage):
        return {'selectedZoneID': self.__selectedZoneID}


class _PermanentPlugin(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        self.__dataMgr = None
        self.__stage = None
        self.__zonesPinsIDs = None
        self.__isRandomEventActive = False
        return

    @property
    def _isEnabled(self):
        return bool(self.__settingsCore.getSetting(GAME.W2GT_ENABLE)) and not self.__isRandomEventActive

    def initialize(self, dataMgr):
        self.__dataMgr = dataMgr
        self.__zonesPinsIDs = defaultdict(list)
        self.__initializeGui()
        self.__updateZones()
        self.__settingsCore.onSettingsChanged += self.__onSettingsChanged
        mapZones = self.__sessionProvider.shared.mapZones
        if mapZones:
            mapZones.onMarkerToZoneAdded += self.__onRandomEventStarted

    def clear(self):
        mapZones = self.__sessionProvider.shared.mapZones
        if mapZones:
            mapZones.onMarkerToZoneAdded -= self.__onRandomEventStarted
        self.__settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.__dataMgr = None
        self.__stage = None
        self.__zonesPinsIDs.clear()
        self.__zonesPinsIDs = None
        return

    def updateStage(self, stage):
        if self.__stage == stage:
            return
        self.__stage = stage
        if stage == STAGE.FINISHED:
            self.__finishGui()
        else:
            self.__updateZones()

    def __onSettingsChanged(self, diff):
        if GAME.W2GT_ENABLE in diff:
            self.__onEnableChanged()

    def __onRandomEventStarted(self, zoneMarker, matrix):
        self.__isRandomEventActive = True
        self.__updateZones()

    def __onEnableChanged(self):
        self.__updateZones()

    def __updateZones(self):
        isActivateAllZones = self.__stage < STAGE.ONGOING
        isZonesVisibleOnMinimap = self._isEnabled
        for zoneMarkers in self.__zonesPinsIDs.values():
            for zoneMarker in zoneMarkers:
                component = self.__getComponent(zoneMarker, MarkerType.ZONE_MARKER_TYPE)
                if component:
                    component.activeZone(isActivateAllZones)
                    component.changeVisibility(isZonesVisibleOnMinimap)

    def __initializeGui(self):
        markerCtrl = self.__sessionProvider.shared.areaMarker
        for zone in self.__dataMgr.zones:
            if not zone.area2D or not zone.center2D:
                continue
            matrixProvider = Math.Matrix()
            zoneMarker = markerCtrl.createMarker(matrixProvider, _W2GT_BATTLE_ZONE_TYPE)
            zoneMarkerID = markerCtrl.addMarker(zoneMarker, polygon=zone.area2D, zoneType=zone.zoneType, icon=zone.zoneType, iconX=zone.center2D[0], iconY=zone.center2D[1])
            self.__zonesPinsIDs[zone.zoneID].append(zoneMarkerID)

    def __finishGui(self):
        markerCtrl = self.__sessionProvider.shared.areaMarker
        for zoneMarkers in self.__zonesPinsIDs.values():
            for zoneMarker in zoneMarkers:
                markerCtrl.removeMarker(zoneMarker)

        self.__zonesPinsIDs.clear()

    def __getComponent(self, zoneMarkerID, bcMarkerType):
        markerCtrl = self.__sessionProvider.shared.areaMarker
        zoneMarker = markerCtrl.getMarkerById(zoneMarkerID)
        if zoneMarker is None:
            return
        else:
            for component in zoneMarker.components.values():
                if component.bcMarkerType == bcMarkerType:
                    return component

            return


_SUB_PLUGINS = {STAGE.WAITING: None,
 STAGE.ONGOING: _SubPluginOngoing,
 STAGE.ARRIVAL: _SubPluginArrival,
 STAGE.FINISHED: None}
_ARENA_PERIOD_TO_STAGE = {ARENA_PERIOD.WAITING: STAGE.WAITING,
 ARENA_PERIOD.PREBATTLE: STAGE.WAITING,
 ARENA_PERIOD.BATTLE: STAGE.ONGOING,
 ARENA_PERIOD.AFTERBATTLE: STAGE.FINISHED}

class W2GTPlugin(object):

    def __init__(self):
        self.__period = None
        self.__periodStartTime = None
        self.__stage = None
        self.__subPlugin = None
        self.__permanentPlugin = None
        self.__dataMgr = None
        self.__waitDestroying = None
        self.__notifier = None
        self.__eManager = EventManager()
        self.onStagePluginChanged = Event(self.__eManager)
        return

    def initialize(self, dataMgr, period, periodStartTime):
        self.__dataMgr = dataMgr
        self.__period = period
        self.__periodStartTime = periodStartTime
        self.__notifier = SimpleNotifier(lambda : _CALL_INTERVAL, self.__notify)
        self.__waitDestroying = []
        self.__permanentPlugin = _PermanentPlugin()
        self.__permanentPlugin.initialize(dataMgr)
        self.__setupStage(period)

    def updatePeriod(self, period):
        if self.__period == period:
            return
        self.__period = period
        if period in _ARENA_PERIOD_TO_STAGE:
            stageData = _StageData(stage=_ARENA_PERIOD_TO_STAGE[period])
            self.__updateStage(stageData)
            self.__updateSubPlugin(period, stageData)

    def setDestroyed(self):
        self.__updateStage(_StageData(stage=STAGE.FINISHED))

    def clear(self):
        self.__eManager.clear()
        self.__destroyWaitedSubPlugins()
        self.__waitDestroying = None
        self.__removeSubPlugin(force=True)
        self.__permanentPlugin.clear()
        self.__permanentPlugin = None
        self.__notifier.stopNotification()
        self.__notifier.clear()
        self.__notifier = None
        self.__stage = None
        self.__period = None
        self.__dataMgr.destroy()
        self.__dataMgr = None
        return

    def __setupStage(self, period):
        stageData = self.__getInitialStage(period)
        self.__updateStage(stageData)

    def __getInitialStage(self, period):
        progress = self.__dataMgr.progress
        if progress.isCapable and STAGE.hasValue(progress.stageID):
            stage = STAGE(progress.stageID)
            startTime = progress.startTime
            if stage == STAGE.WAITING and stage != _ARENA_PERIOD_TO_STAGE[period]:
                stage = STAGE.ONGOING
                startTime = self.__periodStartTime
            return _StageData(stage=stage, ctx=progress.ctx, startTime=startTime)
        stage = _ARENA_PERIOD_TO_STAGE.get(period, STAGE.WAITING)
        return _StageData(stage=stage)

    def __updateStage(self, stageData):
        stage = stageData.stage
        if self.__stage > stage or self.__stage == STAGE.FINISHED:
            return
        self.__stage = stage
        self.__changeSubPlugin(self.__period, stageData)
        self.__permanentPlugin.updateStage(stage)
        ctx = {} if self.__stage == STAGE.FINISHED else stageData.ctx
        self.onStagePluginChanged(self.__stage.value, ctx)

    def __changeSubPlugin(self, period, stageData):
        subPluginCls = _SUB_PLUGINS.get(stageData.stage)
        isFinished = self.__stage == STAGE.FINISHED
        if subPluginCls is None:
            self.__removeSubPlugin(force=isFinished)
            return
        else:
            if self.__subPlugin and isinstance(self.__subPlugin, subPluginCls):
                self.__updateSubPlugin(period, stageData)
            else:
                self.__removeSubPlugin(force=isFinished)
                self.__addSubPlugin(subPluginCls, period, stageData)
            return

    def __addSubPlugin(self, subPluginCls, period, stageData):
        if self.__subPlugin is None:
            self.__subPlugin = subPluginCls(self.__permanentPlugin)
            self.__subPlugin.onStageChanged += self.__onSubPluginStageChanged
            self.__subPlugin.initialize(period, self.__dataMgr, stageData)
            self.__notifier.startNotification()
        return

    def __removeSubPlugin(self, force=False):
        if self.__subPlugin:
            self.__notifier.stopNotification()
            self.__subPlugin.onStageChanged -= self.__onSubPluginStageChanged
            self.__subPlugin.beforeDestroy()
            if self.__subPlugin.canDestroy() or force:
                self.__subPlugin.onReadyToDestroy -= self.__destroyWaitedSubPlugins
                self.__subPlugin.destroy()
            else:
                self.__waitDestroying.append(self.__subPlugin)
                self.__subPlugin.onReadyToDestroy += self.__destroyWaitedSubPlugins
            self.__subPlugin = None
        return

    def __updateSubPlugin(self, period, stageData):
        if self.__subPlugin:
            self.__subPlugin.updateStage(period, stageData.stage)

    def __notify(self):
        if self.__subPlugin:
            self.__subPlugin.update()

    def __destroyWaitedSubPlugins(self):
        subPlugins = self.__waitDestroying[:]
        for subPlugin in subPlugins:
            if subPlugin.isReadyToDestroy:
                subPlugin.onReadyToDestroy -= self.__destroyWaitedSubPlugins
                subPlugin.destroy()
                self.__waitDestroying.remove(subPlugin)

    def __onSubPluginStageChanged(self, stage, ctx, startTime=0):
        self.__updateStage(_StageData(stage=stage, ctx=ctx, startTime=startTime))
