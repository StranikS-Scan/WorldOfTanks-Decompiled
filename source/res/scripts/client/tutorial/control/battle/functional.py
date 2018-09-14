# Embedded file name: scripts/client/tutorial/control/battle/functional.py
import time
import weakref
import BigWorld
import Math
import TriggersManager
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from gui.battle_control import avatar_getter
from tutorial import g_tutorialWeaver
from tutorial.control.battle import aspects
from tutorial.control.battle.context import BattleClientCtx
from tutorial.control.battle.context import ExtendedBattleClientCtx
from tutorial.control.context import SOUND_EVENT, GlobalStorage, GLOBAL_VAR
from tutorial.control.functional import FunctionalEffect, FunctionalScene, FunctionalChapterInfo, FunctionalConditions, FunctionalShowDialogEffect
from tutorial.data.chapter import ChapterProgress
from tutorial.logger import LOG_ERROR, LOG_DEBUG, LOG_CURRENT_EXCEPTION, LOG_REQUEST

def _leaveArena():
    player = BigWorld.player()
    if hasattr(player, 'leaveArena'):
        player.leaveArena()


class _IMarker(object):

    def update(self, *args, **kwargs):
        pass

    def clear(self):
        pass


class IDirectionIndicator(object):

    def track(self, position):
        pass

    def setShape(self, shape):
        pass

    def setDistance(self, distance):
        pass

    def setPosition(self, position):
        pass

    def remove(self):
        pass


class _DirectionIndicatorCtrl(_IMarker):

    def __init__(self, indicator, shapes, position):
        super(_DirectionIndicatorCtrl, self).__init__()
        self.__shapes = shapes
        shape = self.__shapes[0]
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        if g_settingsCore.getSetting('isColorBlind'):
            shape = self.__shapes[1]
        self.__indicator = indicator
        self.__indicator.setShape(shape)
        self.__indicator.track(position)
        g_settingsCore.onSettingsChanged += self.__as_onSettingsChanged

    def update(self, distance, position = None):
        self.__indicator.setDistance(distance)
        if position is not None:
            self.__indicator.setPosition(position)
        return

    def clear(self):
        LOG_DEBUG('_DirectionIndicatorCtrl.clear', hex(id(self)))
        if self.__indicator is not None:
            self.__indicator.remove()
        self.__indicator = None
        from account_helpers.settings_core.SettingsCore import g_settingsCore
        g_settingsCore.onSettingsChanged -= self.__as_onSettingsChanged
        return

    def __as_onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            shape = self.__shapes[0]
            if diff['isColorBlind']:
                shape = self.__shapes[1]
            if self.__indicator is not None:
                self.__indicator.setShape(shape)
        return


class _AimMarker(_IMarker):

    def __init__(self, typeID, triggerID, marker2D, marker3D, dIndicator = None):
        self.__typeID = typeID
        self.__triggerID = triggerID
        self.__marker2D = marker2D
        self.__marker3D = marker3D
        self.__dIndicator = dIndicator

    def update(self, manager):
        distance = manager.getDistanceToTrigger(self.__typeID, self.__triggerID)
        self.__marker2D.update(distance)
        if self.__dIndicator is not None:
            self.__dIndicator.update(distance)
        return

    def clear(self):
        if self.__marker2D is not None:
            self.__marker2D.clear()
        self.__marker2D = None
        if self.__marker3D is not None:
            self.__marker3D.clear()
        self.__marker3D = None
        if self.__dIndicator is not None:
            self.__dIndicator.clear()
        self.__dIndicator = None
        return


class _AreaMarker(_AimMarker):

    def __init__(self, typeID, triggerID, worldMarker2D, minimapMarker2D, worldMarker3D, groundMarker3D, dIndicator = None):
        super(_AreaMarker, self).__init__(typeID, triggerID, worldMarker2D, worldMarker3D, dIndicator)
        self.__groundMarker = groundMarker3D
        self.__minimapMarker = minimapMarker2D

    def clear(self):
        if self.__groundMarker is not None:
            self.__groundMarker.clear()
        self.__groundMarker = None
        if self.__minimapMarker is not None:
            self.__minimapMarker.clear()
        self.__minimapMarker = None
        super(_AreaMarker, self).clear()
        return


class _StaticWorldMarker2D(_IMarker):

    def __init__(self, vm, data, position, distance):
        super(_StaticWorldMarker2D, self).__init__()
        self.__vmRef = weakref.ref(vm)
        offset = data.get('offset', Math.Vector3(0, 0, 0))
        _, self.__handle = vm.createStaticMarker(Math.Vector3(position[:]) + offset, 'StaticObjectMarker')
        if self.__handle is not -1:
            vm.invokeMarker(self.__handle, 'init', [data.get('shape', 'arrow'),
             data.get('min-distance', 0),
             data.get('max-distance', 0),
             distance])

    def update(self, distance):
        vm = self.__vmRef()
        if vm is not None and self.__handle is not -1:
            vm.invokeMarker(self.__handle, 'setDistance', [distance])
        return

    def clear(self):
        LOG_DEBUG('_StaticWorldMarker2D.clear', self.__handle)
        vm = self.__vmRef()
        if vm is not None:
            vm.destroyStaticMarker(self.__handle)
        self.__vmRef = None
        self.__handle = -1
        return


class _StaticMinimapMarker2D(_IMarker):

    def __init__(self, markerID, minimap, data, position):
        super(_StaticMinimapMarker2D, self).__init__()
        self.__minimapRef = weakref.ref(minimap)
        self.__handle = minimap.addBackEntry(markerID, data.get('entry-name'), position[:], data.get('entry-type'))

    def update(self):
        pass

    def clear(self):
        LOG_DEBUG('_StaticMinimapMarker2D.clear', self.__handle)
        minimap = self.__minimapRef()
        if minimap is not None and self.__handle:
            minimap.removeBackEntry(self.__handle)
        self.__minimapRef = None
        self.__handle = None
        return


class _StaticObjectMarker3D(_IMarker):

    def __init__(self, data, position):
        super(_StaticObjectMarker3D, self).__init__()
        path = data.get('path')
        offset = data.get('offset', Math.Vector3(0, 0, 0))
        self.__model = None
        if path is not None:
            try:
                self.__model = BigWorld.Model(path)
                self.__model.position = Math.Vector3(position[:]) + offset
                self.__model.castsShadow = False
            except ValueError:
                LOG_CURRENT_EXCEPTION()
                LOG_ERROR('Model not found', path)
                return
            except AttributeError:
                LOG_CURRENT_EXCEPTION()
                return

            BigWorld.addModel(self.__model)
            action = data.get('action')
            if action is not None and len(action):
                try:
                    self.__model.action(action)()
                except ValueError:
                    LOG_ERROR('Action not found', path, action)

        return

    def update(self):
        pass

    def clear(self):
        LOG_DEBUG('_StaticObjectMarker3D.clear', self.__model)
        if self.__model is not None:
            BigWorld.delModel(self.__model)
        self.__model = None
        return


class _VehicleMarker(_IMarker):

    def __init__(self, vehicleID, minimap, period, dIndicator = None):
        super(_VehicleMarker, self).__init__()
        self.__vehicleID = vehicleID
        self.__minimapRef = weakref.ref(minimap)
        self.__period = period
        self.__nextTime = BigWorld.time()
        self.__dIndicator = dIndicator

    def update(self, manager):
        minimap = self.__minimapRef()
        vehicle = BigWorld.entities.get(self.__vehicleID)
        if vehicle is not None and vehicle.isStarted and not vehicle.isPlayer:
            if self.__nextTime <= BigWorld.time():
                if minimap is not None:
                    minimap.showActionMarker(self.__vehicleID, 'attack')
                self.__nextTime = BigWorld.time() + self.__period
            if self.__dIndicator is not None:
                vPosition = vehicle.position
                vector = vPosition - BigWorld.camera().position
                self.__dIndicator.update(vector.length, vPosition)
        return

    def clear(self):
        LOG_DEBUG('_VehicleMarker.clear', self.__vehicleID)
        if self.__dIndicator is not None:
            self.__dIndicator.clear()
        self.__dIndicator = None
        self.__vehicleID = -1
        self.__minimapRef = None
        self.__period = -1
        return


class _MarkersStorage(object):
    __markers = {}

    @classmethod
    def addMarker(cls, markerID, marker):
        cls.__markers[markerID] = marker

    @classmethod
    def removeMarker(cls, markerID):
        return cls.__markers.pop(markerID, None)

    @classmethod
    def hasMarker(cls, markerID):
        return markerID in cls.__markers

    @classmethod
    def hasMarkers(cls):
        return len(cls.__markers)

    @classmethod
    def updateMarkers(cls, manager):
        if not manager.isEnabled:
            return
        for marker in cls.__markers.itervalues():
            marker.update(manager)

    @classmethod
    def clear(cls):
        while len(cls.__markers):
            _, marker = cls.__markers.popitem()
            marker.clear()


class FunctionalShowMarker(FunctionalEffect):

    def triggerEffect(self):
        data = self.getTarget()
        if _MarkersStorage.hasMarker(data.getID()):
            LOG_DEBUG('Markers is showing', data.getID())
            return
        else:
            marker = self.__makeEffect(data)
            if marker is not None:
                _MarkersStorage.addMarker(data.getID(), marker)
            return

    def __makeEffect(self, data):
        typeID = data.getTypeID()
        entityID = self._tutorial.getVars().get(data.getVarRef())
        marker = None
        root = self._gui.getGuiRoot()
        vMarkers = getattr(root, 'markersManager', None)
        minimap = getattr(root, 'minimap', None)
        if vMarkers is None:
            LOG_ERROR('Markers manager is not defined')
            return
        elif minimap is None:
            LOG_ERROR('Minimap is not defined')
            return
        else:
            if typeID is TriggersManager.TRIGGER_TYPE.AIM:
                marker = self.__make4Aim(typeID, entityID, vMarkers, data)
            elif typeID is TriggersManager.TRIGGER_TYPE.AREA:
                marker = self.__make4Area(typeID, entityID, vMarkers, minimap, data)
            elif typeID is TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE:
                marker = self.__make4Vehicle(entityID, vMarkers, minimap, data)
            return marker

    def __make4Aim(self, typeID, triggerID, vMarkers, data):
        tManager = TriggersManager.g_manager
        if tManager is None or not tManager.isEnabled():
            LOG_ERROR('TriggersManager is not defined or is not enabled')
            return
        else:
            position = tManager.getTriggerPosition(typeID, triggerID)
            distance = tManager.getDistanceToTrigger(typeID, triggerID)
            if position is None:
                LOG_ERROR('Can not determine position of object', triggerID)
                return
            indicatorCtrl = None
            if data.isIndicatorCreate():
                indicator = self._gui._getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found')
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('green', 'green'), position)
            return _AimMarker(typeID, triggerID, _StaticWorldMarker2D(vMarkers, data.getWorldData(), position, distance), _StaticObjectMarker3D(data.getModelData(), position), indicatorCtrl)

    def __make4Area(self, typeID, triggerID, vMarkers, minimap, data):
        tManager = TriggersManager.g_manager
        if tManager is None or not tManager.isEnabled():
            LOG_ERROR('TriggersManager is not defined or is not enabled')
            return
        else:
            position = tManager.getTriggerPosition(typeID, triggerID)
            distance = tManager.getDistanceToTrigger(typeID, triggerID)
            if position is None:
                LOG_ERROR('Can not determine position of object', triggerID)
                return
            indicatorCtrl = None
            if data.isIndicatorCreate():
                indicator = self._gui._getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found', triggerID)
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('green', 'green'), position)
            return _AreaMarker(typeID, triggerID, _StaticWorldMarker2D(vMarkers, data.getWorldData(), position, distance), _StaticMinimapMarker2D(data.getID(), minimap, data.getMinimapData(), position), _StaticObjectMarker3D(data.getModelData(), position), _StaticObjectMarker3D(data.getGroundData(), position), indicatorCtrl)

    def __make4Vehicle(self, vehicleID, _, minimap, data):
        if vehicleID is None:
            LOG_ERROR('Vehicle not found', vehicleID)
            return
        else:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is None:
                LOG_ERROR('Vehicle not found', vehicleID)
                return
            indicatorCtrl = None
            if data.isIndicatorCreate():
                indicator = self._gui._getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found')
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('red', 'purple'), vehicle.position)
            return _VehicleMarker(vehicleID, minimap, data.getPeriod(), indicatorCtrl)


class FunctionalRemoveMarker(FunctionalEffect):

    def triggerEffect(self):
        marker = _MarkersStorage.removeMarker(self._effect.getTargetID())
        if marker is not None:
            marker.clear()
        return


class FunctionalNextTaskEffect(FunctionalEffect):

    def triggerEffect(self):
        task = self.getTarget()
        if task is not None:
            flagID = task.getFlagID()
            flag = None
            if flagID is not None:
                flag = self._tutorial.getFlags().isActiveFlag(flagID)
            if self._gui.playEffect('NextTask', [task.getID(), task.getText(), flag]):
                self._sound.play(SOUND_EVENT.TASK_FAILED if flag is False else SOUND_EVENT.TASK_COMPLETED)
        else:
            LOG_ERROR('Task not found', self._effect.getTargetID())
        return


class FunctionalShowHintEffect(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is not None:
            data = [hint.getID(), hint.getText()]
            data.extend(self._getImagePaths(hint))
            if self._gui.playEffect('ShowHint', data):
                speakID = hint.getSpeakID()
                if speakID is not None and len(speakID):
                    self._sound.play(SOUND_EVENT.SPEAKING, sndID=speakID)
        else:
            LOG_ERROR('Hint not found', self._effect.getTargetID())
        return

    def _getImagePaths(self, hint):
        if hint.hasImageRef():
            image = self._data.getHasIDEntity(hint.getImage())
        else:
            image = hint.getImage()
        return image.getImagePaths(self._tutorial.getVars())


class FunctionalTeleportEffect(FunctionalEffect):

    def triggerEffect(self):
        data = self.getTarget()
        if data is None:
            LOG_ERROR('Teleport marker not found', self._effect.getTargetID())
            return
        else:
            typeID = data.getTypeID()
            pointID = self._tutorial.getVars().get(data.getVarRef())
            if pointID is None:
                LOG_ERROR('Point not found', pointID)
                return
            tManager = TriggersManager.g_manager
            if tManager is None or not tManager.isEnabled():
                LOG_ERROR('TriggersManager is not defined or is not enabled')
                return
            position = tManager.getTriggerPosition(typeID, pointID)
            if position is None:
                LOG_ERROR('Can not determine position of object', pointID)
                return
            teleport = getattr(BigWorld.player(), 'teleportVehicle', None)
            if teleport is None:
                LOG_ERROR('BigWorld.player().teleportVehicle not found')
                return
            world = data.getWorldData()
            teleport(position + world.get('offset', Math.Vector3(0, 0, 0)), world.get('yaw', 0.0))
            return


class FunctionalDisableCameraZoomEffect(FunctionalEffect):
    CAMERA_START_DIST = 20

    def triggerEffect(self):
        weaver = g_tutorialWeaver
        if weaver.findPointcut(aspects.AltModeTogglePointcut) is -1:
            weaver.weave(pointcut=aspects.AltModeTogglePointcut, avoid=True)
        if weaver.findPointcut(aspects.ArcadeCtrlMouseEventsPointcut) is -1:
            weaver.weave(pointcut=aspects.ArcadeCtrlMouseEventsPointcut, aspects=[aspects.MouseScrollIgnoreAspect])
        if weaver.findPointcut(aspects.CameraUpdatePointcut) is -1:
            BigWorld.player().inputHandler.ctrl.camera.setCameraDistance(self.CAMERA_START_DIST)
            self._cameraUpdatePointIdx = weaver.weave(pointcut=aspects.CameraUpdatePointcut, aspects=[aspects.CameraZoomModeIgnoreAspect])


class FunctionalEnableCameraZoomEffect(FunctionalEffect):

    def triggerEffect(self):
        weaver = g_tutorialWeaver
        weaver.clear(idx=weaver.findPointcut(aspects.AltModeTogglePointcut))
        weaver.clear(idx=weaver.findPointcut(aspects.ArcadeCtrlMouseEventsPointcut))
        weaver.clear(idx=weaver.findPointcut(aspects.CameraUpdatePointcut))


class FunctionalRequestBonusEffect(FunctionalEffect):

    def triggerEffect(self):
        self._bonuses.request(chapterID=self._effect.getTargetID())


class FunctionalNextChapterEffect(FunctionalEffect):

    def __init__(self, effect):
        super(FunctionalNextChapterEffect, self).__init__(effect)
        self.__finishTime = 0
        self.__nextChapter = None
        return

    def triggerEffect(self):
        exitEntity = self.getTarget()
        if exitEntity is not None:
            self.__nextChapter = exitEntity.getNextChapter()
            if self.__nextChapter is None or not len(self.__nextChapter):
                self.__nextChapter = self._descriptor.getNextChapterID(BattleClientCtx.fetch().completed)
            if self.__nextChapter is None:
                LOG_DEBUG('Next chapter not found')
                self._tutorial._funcScene.setExit(exitEntity)
                return
            delay = exitEntity.getNextDelay()
            if self._tutorial._currentChapter != self.__nextChapter:
                self._sound.play(SOUND_EVENT.NEXT_CHAPTER)
                self._sound.goToNextChapter()
                if delay > 0:
                    self.__finishTime = BigWorld.time() + delay
                else:
                    self._gui.clear()
                    self._tutorial.goToNextChapter(self.__nextChapter)
        else:
            LOG_ERROR('Exit not found', self._effect.getTargetID())
        return

    def isStillRunning(self):
        isFinish = BigWorld.time() >= self.__finishTime
        if isFinish and self.__nextChapter is not None:
            self._gui.clear()
            self._tutorial.goToNextChapter(self.__nextChapter)
        return not isFinish

    def isInstantaneous(self):
        return False


class FunctionalShowBattleDialogEffect(FunctionalShowDialogEffect):

    def triggerEffect(self):
        player = BigWorld.player()
        if hasattr(player, 'moveVehicle'):
            player.moveVehicle(0, False)
        super(FunctionalShowBattleDialogEffect, self).triggerEffect()


class FunctionalShowGreeting(FunctionalEffect):

    def triggerEffect(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None and arena.period in [ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE]:
            greeting = self.getTarget()
            if greeting is not None:
                if self._gui.playEffect('ShowGreeting', greeting.getData()):
                    speakID = greeting.getSpeakID()
                    if speakID is not None:
                        self._sound.play(SOUND_EVENT.SPEAKING, sndID=speakID)
            else:
                LOG_ERROR('Greeting not found', self._effect.getTargetID())
        return

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        result = arena is not None and arena.period in [ARENA_PERIOD.WAITING, ARENA_PERIOD.PREBATTLE]
        if not result:
            self._gui.stopEffect('ShowGreeting', self._effect.getTargetID())
        return result


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._cache.setRefused(True).write()
        avatar_getter.leaveArena()

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalBattleChapterInfo(FunctionalChapterInfo):

    def __init__(self):
        super(FunctionalBattleChapterInfo, self).__init__()
        chapter = self._tutorial._data
        chapterID = chapter.getID()
        self._progress = []
        self._stepMask = -1
        progress = chapter.getHasIDEntity(chapterID)
        if progress is None:
            LOG_ERROR('Chapter progress not found', chapterID)
        else:
            for conditions in progress:
                func = FunctionalConditions(conditions)
                ok = func.allConditionsOk()
                self._progress.append((func, ok))

        self._gui.setChapterInfo(chapter.getTitle(), chapter.getDescription())
        descriptor = self._descriptor
        chapterIdx = descriptor.getChapterIdx(chapterID)
        localCtx = BattleClientCtx.fetch().setChapterIdx(chapterIdx)
        self._gui.setTrainingPeriod(descriptor.getChapterIdx(chapterID), descriptor.getNumberOfChapters())
        self._gui.setTrainingProgress(descriptor.getProgress(localCtx.completed))
        return

    def invalidate(self):
        offset = 0
        mask = 0
        for conditions, wasOk in self._progress:
            ok = conditions.allConditionsOk()
            if ok:
                bit = ChapterProgress.PROGRESS_FLAG_COMPLETED
            elif wasOk:
                bit = ChapterProgress.PROGRESS_FLAG_FAILED
            else:
                bit = ChapterProgress.PROGRESS_FLAG_UNDEFINED
            mask |= bit << offset
            offset += 2

        if self._stepMask is not mask:
            self._stepMask = mask
            self._gui.setChapterProgress(len(self._progress), mask)


class FunctionalBattleScene(FunctionalScene):
    _vehTypeName = GlobalStorage(GLOBAL_VAR.PLAYER_VEHICLE_NAME, None)

    def __init__(self, scene):
        super(FunctionalBattleScene, self).__init__(scene)
        self._exitTime = 0
        self._exitEntity = None
        self._arenaFinished = False
        return

    def enter(self):
        g_playerEvents.onArenaPeriodChange += self.__pe_onArenaPeriodChange
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None and arena.period is ARENA_PERIOD.BATTLE:
            self.__requestRequiredData()
        if self._vehTypeName is None:
            vehType = getattr(BigWorld.player(), 'vehicleTypeDescriptor', None)
            if vehType is not None:
                self._vehTypeName = vehType.name
            else:
                LOG_ERROR('Player\\s vehicle not found')
        for item in self._scene.getGuiItems():
            self._gui.setItemProps(item.getTargetID(), item.getProps(), revert=True)

        self._gui.show()
        return

    def leave(self):
        super(FunctionalBattleScene, self).leave()
        _MarkersStorage.clear()
        g_playerEvents.onArenaPeriodChange -= self.__pe_onArenaPeriodChange
        self._cache.setLocalCtx(ExtendedBattleClientCtx.fetch().makeRecord())
        self._exitTime = 0
        self._exitEntity = None
        return

    def reload(self):
        _MarkersStorage.clear()

    def update(self):
        super(FunctionalBattleScene, self).update()
        if _MarkersStorage.hasMarkers():
            tManager = TriggersManager.g_manager
            if tManager is None or not tManager.isEnabled():
                LOG_ERROR('TriggersManager is not defined or is not enabled')
                return
            _MarkersStorage.updateMarkers(tManager)
        if self._arenaFinished and self.__isDelayPerformed():
            _leaveArena()
        return

    def setExit(self, exitEntity):
        self._exitEntity = exitEntity
        if exitEntity.isSpeakOver():
            self._exitTime = 0
        else:
            self._exitTime = BigWorld.time() + exitEntity.getFinishDelay()

    def __isDelayPerformed(self):
        result = True
        if self._exitEntity and self._exitEntity.isSpeakOver():
            result = not self._sound.isPlaying(SOUND_EVENT.SPEAKING)
            if result:
                self._sound.setMuted(True)
                self._exitTime = BigWorld.time() + self._exitEntity.getFinishDelay()
                self._exitEntity = None
        if self._exitTime > 0:
            result = self._exitTime < BigWorld.time()
        return result

    def __requestRequiredData(self):
        localCtx = BattleClientCtx.fetch()
        if localCtx.startedAt == 0.0:
            localCtx.setStartedAt(time.time())
        if localCtx.accCompleted < 0:
            player = BigWorld.player()
            if player is None or not hasattr(player, 'requestAccountStats'):
                LOG_DEBUG('Stats method not found', player)
                return
            LOG_REQUEST('Avatar.requestAccountStats')
            player.requestAccountStats(['tutorialsCompleted'], self.__onReceiveAccountStats)
        return

    def __onReceiveAccountStats(self, stats):
        BattleClientCtx.fetch().setAccCompleted(stats.get('tutorialsCompleted', 0))

    def __pe_onArenaPeriodChange(self, period, *args):
        if period is ARENA_PERIOD.BATTLE:
            self.__requestRequiredData()
        elif period is ARENA_PERIOD.AFTERBATTLE:
            self._arenaFinished = True
            if self.__isDelayPerformed():
                _leaveArena()
