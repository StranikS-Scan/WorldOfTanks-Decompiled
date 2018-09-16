# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/battle/functional.py
import time
import weakref
import BigWorld
import Math
import TriggersManager
from constants import ARENA_PERIOD
from PlayerEvents import g_playerEvents
from gui.battle_control import avatar_getter
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.battle_session import IBattleSessionProvider
from tutorial.control import g_tutorialWeaver
from tutorial.control.battle import aspects
from tutorial.control.battle.context import BattleClientCtx
from tutorial.control.battle.context import ExtendedBattleClientCtx
from tutorial.control.context import SOUND_EVENT, GlobalStorage, GLOBAL_VAR
from tutorial.control.functional import FunctionalEffect, FunctionalScene
from tutorial.control.functional import FunctionalChapterContext
from tutorial.control.functional import FunctionalConditions
from tutorial.control.functional import FunctionalShowDialogEffect
from tutorial.data.chapter import ChapterProgress
from tutorial.gui import GUI_EFFECT_NAME
from tutorial.logger import LOG_ERROR
from tutorial.logger import LOG_DEBUG
from tutorial.logger import LOG_CURRENT_EXCEPTION
from tutorial.logger import LOG_REQUEST

class _IMarker(object):

    def update(self, *args, **kwargs):
        pass

    def clear(self):
        pass


class _DirectionIndicatorCtrl(_IMarker):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, indicator, shapes, position):
        super(_DirectionIndicatorCtrl, self).__init__()
        self.__shapes = shapes
        shape = self.__shapes[0]
        if self.settingsCore.getSetting('isColorBlind'):
            shape = self.__shapes[1]
        self.__indicator = indicator
        self.__indicator.setShape(shape)
        if position is not None:
            self.__indicator.track(position)
        self.settingsCore.onSettingsChanged += self.__as_onSettingsChanged
        return

    def update(self, distance, position=None):
        self.__indicator.setDistance(distance)
        if position is not None:
            self.__indicator.setPosition(position)
        return

    def clear(self):
        LOG_DEBUG('_DirectionIndicatorCtrl.clear', hex(id(self)))
        if self.__indicator is not None:
            self.__indicator.remove()
        self.__indicator = None
        self.settingsCore.onSettingsChanged -= self.__as_onSettingsChanged
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

    def __init__(self, typeID, triggerID, marker2D, marker3D, dIndicator=None):
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

    def __init__(self, typeID, triggerID, worldMarker2D, minimapMarker2D, worldMarker3D, groundMarker3D, dIndicator=None):
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

    def __init__(self, objectID, markers2D, data, position, distance):
        super(_StaticWorldMarker2D, self).__init__()
        offset = data.get('offset', Math.Vector3(0, 0, 0))
        if markers2D.addStaticObject(objectID, Math.Vector3(position[:]) + offset):
            markers2D.setupStaticObject(objectID, data.get('shape', 'arrow'), data.get('min-distance', 0), data.get('max-distance', 0), distance, data.get('color', 'green'))
            self.__objectID = objectID
            self.__markers2D = weakref.ref(markers2D)
        else:
            self.__objectID = ''
            self.__markers2D = lambda : None

    def update(self, distance):
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            markers2D.setDistanceToObject(self.__objectID, distance)
        return

    def clear(self):
        LOG_DEBUG('_StaticWorldMarker2D.clear', self.__objectID)
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            markers2D.delStaticObject(self.__objectID)
        self.__objectID = ''
        self.__markers2D = lambda : None
        return


class _StaticMinimapMarker2D(_IMarker):

    def __init__(self, markerID, minimap, position):
        super(_StaticMinimapMarker2D, self).__init__()
        if markerID and minimap.addTarget(markerID, position[:]):
            self.__markerID = markerID
            self.__minimap = weakref.ref(minimap)
        else:
            self.__markerID = ''
            self.__minimap = lambda : None

    def update(self):
        pass

    def clear(self):
        LOG_DEBUG('_StaticMinimapMarker2D.clear', self.__markerID)
        minimap = self.__minimap()
        if minimap is not None and self.__markerID:
            minimap.delTarget(self.__markerID)
        self.__markerID = ''
        self.__minimap = None
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
            if action:
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
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicleID, period, dIndicator=None):
        super(_VehicleMarker, self).__init__()
        self.__vehicleID = vehicleID
        self.__period = period
        self.__nextTime = BigWorld.time()
        self.__dIndicator = dIndicator

    def update(self, manager):
        feedback = self.sessionProvider.shared.feedback
        vehicle = BigWorld.entities.get(self.__vehicleID)
        if vehicle is not None and vehicle.isStarted and not vehicle.isPlayerVehicle:
            if self.__nextTime <= BigWorld.time():
                if feedback is not None:
                    feedback.showActionMarker(self.__vehicleID, mMarker='attack')
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
        while cls.__markers:
            _, marker = cls.__markers.popitem()
            marker.clear()


class FunctionalShowMarker(FunctionalEffect):

    def triggerEffect(self):
        data = self.getTarget()
        if _MarkersStorage.hasMarker(data.getID()):
            LOG_DEBUG('Markers is showing', data.getID())
            return False
        else:
            marker = self.__makeEffect(data)
            if marker is not None:
                _MarkersStorage.addMarker(data.getID(), marker)
            return True

    def __makeEffect(self, data):
        typeID = data.getTypeID()
        entityID = self._tutorial.getVars().get(data.getVarRef())
        marker = None
        markers2D = self._gui.getMarkers2DPlugin()
        minimap = self._gui.getMinimapPlugin()
        if markers2D is None:
            LOG_ERROR('Markers manager is not defined')
            return
        elif minimap is None:
            LOG_ERROR('Minimap is not defined')
            return
        else:
            if typeID is TriggersManager.TRIGGER_TYPE.AIM:
                marker = self.__make4Aim(typeID, entityID, markers2D, data)
            elif typeID is TriggersManager.TRIGGER_TYPE.AREA:
                marker = self.__make4Area(typeID, entityID, markers2D, minimap, data)
            elif typeID is TriggersManager.TRIGGER_TYPE.AIM_AT_VEHICLE:
                marker = self.__make4Vehicle(entityID, data)
            return marker

    def __make4Aim(self, typeID, triggerID, markers2D, data):
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
                indicator = self._gui.getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found')
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('green', 'green'), position)
            return _AimMarker(typeID, triggerID, _StaticWorldMarker2D(triggerID, markers2D, data.getWorldData(), position, distance), _StaticObjectMarker3D(data.getModelData(), position), indicatorCtrl)

    def __make4Area(self, typeID, triggerID, markers2D, minimap, data):
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
                indicator = self._gui.getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found', triggerID)
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('green', 'green'), position)
            return _AreaMarker(typeID, triggerID, _StaticWorldMarker2D(triggerID, markers2D, data.getWorldData(), position, distance), _StaticMinimapMarker2D(data.getID(), minimap, position), _StaticObjectMarker3D(data.getModelData(), position), _StaticObjectMarker3D(data.getGroundData(), position), indicatorCtrl)

    def __make4Vehicle(self, vehicleID, data):
        if vehicleID is None:
            LOG_ERROR('Vehicle not found', vehicleID)
            return
        else:
            vehicle = BigWorld.entities.get(vehicleID)
            if vehicle is not None:
                position = vehicle.position
            else:
                position = None
            indicatorCtrl = None
            if data.isIndicatorCreate():
                indicator = self._gui.getDirectionIndicator()
                if indicator is None:
                    LOG_ERROR('Directional indicator not found')
                else:
                    indicatorCtrl = _DirectionIndicatorCtrl(indicator, ('red', 'purple'), position)
            return _VehicleMarker(vehicleID, data.getPeriod(), indicatorCtrl)


class FunctionalRemoveMarker(FunctionalEffect):

    def triggerEffect(self):
        marker = _MarkersStorage.removeMarker(self._effect.getTargetID())
        if marker is not None:
            marker.clear()
        return True


class FunctionalNextTaskEffect(FunctionalEffect):

    def triggerEffect(self):
        task = self.getTarget()
        if task is not None:
            flagID = task.getFlagID()
            flag = None
            if flagID is not None:
                flag = self._tutorial.getFlags().isActiveFlag(flagID)
                if flag:
                    soundID = SOUND_EVENT.TASK_COMPLETED
                else:
                    soundID = SOUND_EVENT.TASK_FAILED
            else:
                soundID = SOUND_EVENT.TASK_COMPLETED
            if self._gui.playEffect(GUI_EFFECT_NAME.NEXT_TASK, [task.getID(), task.getText(), flag]):
                self._sound.play(soundID)
                return True
        else:
            LOG_ERROR('Task not found', self._effect.getTargetID())
        return False


class FunctionalShowHintEffect(FunctionalEffect):

    def triggerEffect(self):
        hint = self.getTarget()
        if hint is not None:
            data = [hint.getID(), hint.getText()]
            data.extend(self._getImagePaths(hint))
            if self._gui.playEffect(GUI_EFFECT_NAME.SHOW_HINT, data):
                speakID = hint.getSpeakID()
                if speakID:
                    self._sound.play(SOUND_EVENT.SPEAKING, sndID=speakID)
                return True
        else:
            LOG_ERROR('Hint not found', self._effect.getTargetID())
        return False

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
            return False
        else:
            typeID = data.getTypeID()
            pointID = self._tutorial.getVars().get(data.getVarRef())
            if pointID is None:
                LOG_ERROR('Point not found', pointID)
                return False
            tManager = TriggersManager.g_manager
            if tManager is None or not tManager.isEnabled():
                LOG_ERROR('TriggersManager is not defined or is not enabled')
                return False
            position = tManager.getTriggerPosition(typeID, pointID)
            if position is None:
                LOG_ERROR('Can not determine position of object', pointID)
                return False
            teleport = getattr(BigWorld.player(), 'teleportVehicle', None)
            if teleport is None:
                LOG_ERROR('BigWorld.player().teleportVehicle not found')
                return False
            world = data.getWorldData()
            teleport(position + world.get('offset', Math.Vector3(0, 0, 0)), world.get('yaw', 0.0))
            return True


class FunctionalDisableCameraZoomEffect(FunctionalEffect):
    CAMERA_START_DIST = 20

    def __init__(self, effect):
        super(FunctionalDisableCameraZoomEffect, self).__init__(effect)
        self._cameraUpdatePointIdx = -1

    def triggerEffect(self):
        weaver = g_tutorialWeaver
        if weaver.findPointcut(aspects.AltModeTogglePointcut) == -1:
            weaver.weave(pointcut=aspects.AltModeTogglePointcut, avoid=True)
        if weaver.findPointcut(aspects.ArcadeCtrlMouseEventsPointcut) == -1:
            weaver.weave(pointcut=aspects.ArcadeCtrlMouseEventsPointcut, aspects=(aspects.MouseScrollIgnoreAspect,))
        if weaver.findPointcut(aspects.CameraUpdatePointcut) == -1:
            BigWorld.player().inputHandler.ctrl.camera.setCameraDistance(self.CAMERA_START_DIST)
            self._cameraUpdatePointIdx = weaver.weave(pointcut=aspects.CameraUpdatePointcut, aspects=(aspects.CameraZoomModeIgnoreAspect,))
        return True


class FunctionalEnableCameraZoomEffect(FunctionalEffect):

    def triggerEffect(self):
        weaver = g_tutorialWeaver
        weaver.clear(idx=weaver.findPointcut(aspects.AltModeTogglePointcut))
        weaver.clear(idx=weaver.findPointcut(aspects.ArcadeCtrlMouseEventsPointcut))
        weaver.clear(idx=weaver.findPointcut(aspects.CameraUpdatePointcut))
        return True


class FunctionalRequestBonusEffect(FunctionalEffect):

    def triggerEffect(self):
        self._bonuses.request(chapterID=self._effect.getTargetID())
        return True


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
            if not self.__nextChapter:
                self.__nextChapter = self._descriptor.getNextChapterID(BattleClientCtx.fetch().completed)
            if self.__nextChapter is None:
                LOG_DEBUG('Next chapter not found')
                self._funcScene.setExit(exitEntity)
                return False
            delay = exitEntity.getNextDelay()
            if self._tutorial._currentChapter != self.__nextChapter:
                self._sound.play(SOUND_EVENT.NEXT_CHAPTER)
                self._sound.goToNextChapter()
                if delay > 0:
                    self.__finishTime = BigWorld.time() + delay
                else:
                    self._gui.clear()
                    self._tutorial.goToNextChapter(self.__nextChapter)
            return True
        else:
            LOG_ERROR('Exit not found', self._effect.getTargetID())
            return False

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
        return super(FunctionalShowBattleDialogEffect, self).triggerEffect()


class FunctionalShowGreeting(FunctionalEffect):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def triggerEffect(self):
        if self.sessionProvider.arenaVisitor.isArenaNotStarted():
            greeting = self.getTarget()
            if greeting is not None:
                if self._gui.playEffect(GUI_EFFECT_NAME.SHOW_GREETING, greeting.getData()):
                    speakID = greeting.getSpeakID()
                    if speakID is not None:
                        self._sound.play(SOUND_EVENT.SPEAKING, sndID=speakID)
                    return True
            else:
                LOG_ERROR('Greeting not found', self._effect.getTargetID())
            return False
        else:
            return

    def isInstantaneous(self):
        return False

    def isStillRunning(self):
        result = self.sessionProvider.arenaVisitor.isArenaNotStarted()
        if not result:
            self._gui.stopEffect(GUI_EFFECT_NAME.SHOW_GREETING, self._effect.getTargetID())
        return result


class FunctionalRefuseTrainingEffect(FunctionalEffect):

    def triggerEffect(self):
        self._cache.setRefused(True).write()
        avatar_getter.leaveArena()
        return True

    def isStillRunning(self):
        return True

    def isInstantaneous(self):
        return False


class FunctionalBattleChapterContext(FunctionalChapterContext):

    def __init__(self):
        super(FunctionalBattleChapterContext, self).__init__()
        chapter = self._data
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
        super(FunctionalBattleChapterContext, self).invalidate()
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
                LOG_ERROR('Players vehicle not found')
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
            avatar_getter.leaveArena()
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
                avatar_getter.leaveArena()
