# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/bootcamp/BootcampMarkers.py
import weakref
import base64
import cPickle
from functools import partial
import math
import Math
import BigWorld
import SoundGroups
import Keys
import AnimationSequence
import TriggersManager
import BattleReplay
from gui import InputHandler
from account_helpers.settings_core import ISettingsCore
from BattleReplay import CallbackDataNames
from BootCampEvents import g_bootcampEvents
from BootcampConstants import UI_STATE
from BootcampGUI import getDirectionIndicator
from debug_utils_bootcamp import LOG_DEBUG_DEV_BOOTCAMP, LOG_ERROR_BOOTCAMP
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from skeletons.gui.game_control import IBootcampController
from vehicle_systems.stricted_loading import makeCallbackWeak

class _IMarker(object):

    def __init__(self):
        self.__switchedToSniperMode = False
        self.__switchedToHiddenMode = False

    @property
    def isSwitchedToSniperMode(self):
        return self.__switchedToSniperMode

    @isSwitchedToSniperMode.setter
    def isSwitchedToSniperMode(self, value):
        self.__switchedToSniperMode = value

    @property
    def isSwitchedToHiddenMode(self):
        return self.__switchedToHiddenMode

    @isSwitchedToHiddenMode.setter
    def isSwitchedToHiddenMode(self, value):
        self.__switchedToHiddenMode = value

    def update(self, *args, **kwargs):
        pass

    def clear(self):
        pass

    def setVisible(self, isVisible):
        pass


class _DirectionIndicatorCtrl(_IMarker):
    settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self, shapes, position):
        super(_DirectionIndicatorCtrl, self).__init__()
        self._indicator = None
        self.__shapes = shapes
        self.__position = position
        self.__isMarkerVisible = False
        return

    def getShape(self):
        return self.__shapes[1] if self.settingsCore.getSetting('isColorBlind') else self.__shapes[0]

    def attachGUI(self, indicator):
        self._indicator = indicator
        self._indicator.setShape(self.getShape())
        self._indicator.track(self.__position)
        self.__updateVisibility()
        self.settingsCore.onSettingsChanged += self.__as_onSettingsChanged

    def detachGUI(self):
        self.settingsCore.onSettingsChanged -= self.__as_onSettingsChanged
        if self._indicator is not None:
            self._indicator.remove()
            self._indicator = None
        return

    def update(self, distance, position=None):
        if self.__isMarkerVisible and self._indicator is not None:
            self._indicator.setDistance(distance)
            if position is not None:
                self._indicator.setPosition(position)
        self.__updateVisibility()
        return

    def clear(self):
        LOG_DEBUG_DEV_BOOTCAMP('_DirectionIndicatorCtrl.clear', hex(id(self)))
        if self._indicator is not None:
            self._indicator.remove()
            self._indicator = None
        return

    def setVisible(self, isVisible):
        if not self.__isMarkerVisible and isVisible:
            self.__updateVisibility()
        elif self.__isMarkerVisible and not isVisible:
            self.__isMarkerVisible = False
            if self._indicator is not None:
                self._indicator.setVisibility(False)
        return

    def __as_onSettingsChanged(self, diff):
        if 'isColorBlind' in diff:
            if self._indicator is not None:
                self._indicator.setShape(self.getShape())
        return

    def __updateVisibility(self):
        if self._indicator is not None:
            if not hasattr(BigWorld.player().inputHandler.ctrl, 'camera'):
                return
            self.__isMarkerVisible = not self.isSwitchedToHiddenMode
            if self.__isMarkerVisible:
                camera = BigWorld.player().inputHandler.ctrl.camera.camera
                camMat = Math.Matrix(camera.invViewMatrix)
                if camMat is not None:
                    view = camMat.applyV4Point(Math.Vector4(0, 0, 1, 0))
                    direction = self.__position - BigWorld.player().getOwnVehiclePosition()
                    dotProduct = direction.dot(view[0:3])
                    cosFov = math.cos(BigWorld.projection().fov / 2)
                    if dotProduct > cosFov * direction.length:
                        self.__isMarkerVisible = False
            self._indicator.setVisibility(self.__isMarkerVisible)
        return


class _AimMarker(object):

    def __init__(self, typeID, triggerID, marker2D, marker3D, dIndicator=None):
        super(_AimMarker, self).__init__()
        self.__typeID = typeID
        self.__triggerID = triggerID
        self.__marker2D = marker2D
        self.__marker3D = marker3D
        self.__dIndicator = dIndicator

    def switchToSniperMode(self, value):
        self.__marker2D.isSwitchedToSniperMode = value
        self.__marker3D.isSwitchedToSniperMode = value
        self.__dIndicator.isSwitchedToSniperMode = value

    def switchToHiddenMode(self, value):
        self.__marker2D.isSwitchedToHiddenMode = value
        self.__marker3D.isSwitchedToHiddenMode = value
        self.__dIndicator.isSwitchedToHiddenMode = value

    def attachGUI(self, markers2D, minimap):
        self.__marker2D.attachGUI(markers2D)
        indicator = getDirectionIndicator()
        if indicator is not None:
            self.__dIndicator.attachGUI(indicator)
        else:
            LOG_ERROR_BOOTCAMP('Directional indicator not found', self.__triggerID)
        return

    def detachGUI(self):
        self.__marker2D.detachGUI()
        self.__dIndicator.detachGUI()

    def update(self, distance):
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

    def setVisible(self, isVisible):
        self.__marker3D.setVisible(isVisible)
        self.__marker2D.setVisible(isVisible)
        self.__dIndicator.setVisible(isVisible)


class _AreaMarker(_AimMarker):

    def __init__(self, typeID, triggerID, position, worldMarker2D, minimapMarker2D, worldMarker3D, groundMarker3D, dIndicator=None):
        super(_AreaMarker, self).__init__(typeID, triggerID, worldMarker2D, worldMarker3D, dIndicator)
        self.__groundMarker = groundMarker3D
        self.__minimapMarker = minimapMarker2D
        self.__position = position

    def switchToSniperMode(self, value):
        super(_AreaMarker, self).switchToSniperMode(value)
        self.__groundMarker.isSwitchedToSniperMode = value
        self.__minimapMarker.isSwitchedToSniperMode = value

    def switchToHiddenMode(self, value):
        super(_AreaMarker, self).switchToHiddenMode(value)
        self.__groundMarker.isSwitchedToHiddenMode = value
        self.__minimapMarker.isSwitchedToHiddenMode = value

    def attachGUI(self, markers2D, minimap):
        super(_AreaMarker, self).attachGUI(markers2D, minimap)
        self.__minimapMarker.attachGUI(minimap)

    def detachGUI(self):
        super(_AreaMarker, self).detachGUI()
        self.__minimapMarker.detachGUI()

    def clear(self):
        if self.__groundMarker is not None:
            self.__groundMarker.clear()
        self.__groundMarker = None
        if self.__minimapMarker is not None:
            self.__minimapMarker.clear()
        self.__minimapMarker = None
        super(_AreaMarker, self).clear()
        return

    @property
    def position(self):
        return self.__position

    def setVisible(self, isVisible):
        super(_AreaMarker, self).setVisible(isVisible)
        self.__groundMarker.setVisible(isVisible)
        self.__minimapMarker.setVisible(isVisible)


class _StaticWorldMarker2D(_IMarker):

    def __init__(self, objectID, data, position, distance):
        super(_StaticWorldMarker2D, self).__init__()
        self.__initData = data
        self.__initPosition = position
        self.__objectID = objectID
        self.__distance = distance
        self.__visible = True
        self.__markers2D = lambda : None

    def attachGUI(self, markers2D):
        self.__markers2D = weakref.ref(markers2D)
        if self.__visible:
            if not self.addSetupStaticObject(markers2D, self.__objectID, self.__distance):
                self.__markers2D = lambda : None
                self.__objectID = ''

    def detachGUI(self):
        markers2D = self.__markers2D()
        if self.__visible:
            if markers2D is not None and self.__objectID:
                markers2D.delStaticObject(self.__objectID)
        self.__markers2D = lambda : None
        return

    def addSetupStaticObject(self, markers2D, objectID, distance):
        offset = self.__initData.get('offset', Math.Vector3(0, 0, 0))
        if markers2D.addStaticObject(objectID, Math.Vector3(self.__initPosition[:]) + offset):
            markers2D.setupStaticObject(objectID, self.__initData.get('shape', 'arrow'), self.__initData.get('min-distance', 0), self.__initData.get('max-distance', 0), distance, self.__initData.get('color', 'yellow'))
            return True
        return False

    def update(self, distance):
        markers2D = self.__markers2D()
        self.__distance = distance
        if markers2D is not None and self.__objectID:
            if self.__visible:
                markers2D.setDistanceToObject(self.__objectID, distance)
        return

    def clear(self):
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            markers2D.delStaticObject(self.__objectID)
        self.__objectID = ''
        self.__markers2D = lambda : None
        return

    def setVisible(self, isVisible):
        markers2D = self.__markers2D()
        if markers2D is not None and self.__objectID:
            if not self.__visible and isVisible:
                self.addSetupStaticObject(markers2D, self.__objectID, self.__distance)
            elif self.__visible and not isVisible:
                markers2D.delStaticObject(self.__objectID)
        self.__visible = isVisible
        return


class _StaticMinimapMarker2D(_IMarker):

    def __init__(self, markerID, position):
        super(_StaticMinimapMarker2D, self).__init__()
        self.__position = position[:]
        self.__markerID = markerID
        self.__minimap = lambda : None

    def attachGUI(self, minimap):
        if self.__markerID and minimap:
            if minimap.addTarget(self.__markerID, self.__position):
                self.__minimap = weakref.ref(minimap)

    def detachGUI(self):
        minimap = self.__minimap()
        if minimap is not None and self.__markerID:
            minimap.delTarget(self.__markerID)
        self.__minimap = lambda : None
        return

    def update(self):
        pass

    def clear(self):
        LOG_DEBUG_DEV_BOOTCAMP('_StaticMinimapMarker2D.clear', self.__markerID)
        minimap = self.__minimap()
        if minimap is not None and self.__markerID:
            minimap.delTarget(self.__markerID)
        self.__markerID = ''
        self.__minimap = None
        return


class _StaticObjectMarker3D(_IMarker):

    def __init__(self, data, position):
        super(_StaticObjectMarker3D, self).__init__()
        self.__path = data.get('path')
        offset = data.get('offset', Math.Vector3(0, 0, 0))
        self.__model = None
        self.__isMarkerVisible = True
        self.__action = data.get('action')
        self.__animator = None
        self.__modelOwner = None
        self.__destroyed = False
        if self.__path is not None:
            modelPosition = Math.Vector3(position[:]) + offset
            BigWorld.loadResourceListBG((self.__path,), makeCallbackWeak(self.__onModelLoaded, modelPosition))
        return

    def addMarkerModel(self):
        if self.__model is None or self.__modelOwner is not None:
            return
        else:
            self.__modelOwner = BigWorld.player()
            self.__modelOwner.addModel(self.__model)
            if self.__action:
                try:
                    clipResource = self.__model.deprecatedGetAnimationClipResource(self.__action)
                    spaceID = BigWorld.player().spaceID
                    loader = AnimationSequence.Loader(clipResource, spaceID)
                    animator = loader.loadSync()
                    animator.bindTo(AnimationSequence.ModelWrapperContainer(self.__model, spaceID))
                    animator.start()
                    self.__animator = animator
                except ValueError:
                    LOG_ERROR_BOOTCAMP('Action not found', self.__path, self.__action)
                except EnvironmentError:
                    LOG_ERROR_BOOTCAMP('Player not on the world')

            return

    def update(self):
        pass

    def clear(self):
        LOG_DEBUG_DEV_BOOTCAMP('_StaticObjectMarker3D.clear', self.__model)
        self.setVisible(False)
        self.__animator = None
        self.__model = None
        self.__destroyed = True
        return

    def setVisible(self, isVisible):
        if not self.__isMarkerVisible and isVisible:
            self.__isMarkerVisible = True
            self.addMarkerModel()
        elif not isVisible:
            self.__isMarkerVisible = False
            self.__animator = None
            if self.__modelOwner is not None and not self.__modelOwner.isDestroyed:
                self.__modelOwner.delModel(self.__model)
            self.__modelOwner = None
        return

    def __onModelLoaded(self, position, resourceRefs):
        if self.__destroyed:
            return
        if self.__path not in resourceRefs.failedIDs:
            self.__model = resourceRefs[self.__path]
            self.__model.position = position
            self.__model.castsShadow = False
            if self.__isMarkerVisible:
                self.addMarkerModel()
        else:
            LOG_ERROR_BOOTCAMP('Model not found', self.__path)


class BootcampMarkersManager(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    bootcamp = dependency.descriptor(IBootcampController)
    SHOW_SOUND_ID = 'bc_arrow_appears'
    HIDE_SOUND_ID = 'bc_arrow_disappears'
    STATIC_MARKER_DIST = 50

    def __init__(self):
        super(BootcampMarkersManager, self).__init__()
        self.__gui = None
        self.__entitiesParams = None
        self.__markersParams = None
        self.__markers = {}
        self.__markerEvents = {}
        self.__triggerID = 0
        self.__markerSoundShow = None
        self.__switchedToSniperMode = False
        self.__switchedToHiddenMode = False
        if BattleReplay.g_replayCtrl.isPlaying:
            self.replayCallbacks = []
        return

    def init(self, entitiesParams, bootcampGui):
        LOG_DEBUG_DEV_BOOTCAMP('BootcampMarkers.init')
        self.__entitiesParams = entitiesParams
        self.__gui = bootcampGui
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.addListener(self)
        g_bootcampEvents.onUIStateChanged += self._onUIStateChanged
        InputHandler.g_instance.onKeyDown += self._handleKeyEvent

    def clear(self):
        LOG_DEBUG_DEV_BOOTCAMP('BootcampMarkers.clear')
        g_bootcampEvents.onUIStateChanged -= self._onUIStateChanged
        InputHandler.g_instance.onKeyDown -= self._handleKeyEvent
        if not BattleReplay.g_replayCtrl.isPlaying:
            TriggersManager.g_manager.delListener(self)
        for marker in self.__markers.values():
            marker.clear()

        self.__markers.clear()
        self.__gui = None
        self.__entitiesParams = None
        if self.__markersParams is not None:
            self.__markersParams = None
        return

    def start(self):
        if self.__markerSoundShow is not None:
            self.__markerSoundShow.stop()
            self.__markerSoundShow = None
        return

    def afterScenery(self):
        if BattleReplay.g_replayCtrl.isPlaying:
            self.replayCallbacks = []
            self.replaySubscribe()

    def stop(self):
        self.__gui = None
        for marker in self.__markers.itervalues():
            marker.detachGUI()

        if BattleReplay.g_replayCtrl.isPlaying and self.bootcamp.replayCtrl:
            for eventName, callback in self.replayCallbacks:
                self.bootcamp.replayCtrl.delDataCallback(eventName, callback)

            self.replayCallbacks = []
        return

    def replayOnTriggerActivated(self, params):
        self.onTriggerActivated(params)

    def onTriggerActivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.serializeMethod(CallbackDataNames.BC_MARKERS_ONTRIGGERACTIVATED, (params,))
            self.__switchedToSniperMode = True
            for marker in self.__markers.itervalues():
                marker.switchToSniperMode(self.__switchedToSniperMode)

            return

    def onTriggerDeactivated(self, params):
        if params['type'] == TriggersManager.TRIGGER_TYPE.SNIPER_MODE:
            self.serializeMethod(CallbackDataNames.BC_MARKERS_ONTRIGGERDEACTIVATED, (params,))
            self.__switchedToSniperMode = False
            for marker in self.__markers.itervalues():
                marker.switchToSniperMode(self.__switchedToSniperMode)

    def getMarkerParams(self, name):
        if self.__markersParams is None:
            return
        else:
            for markerParams in self.__markersParams:
                if name == markerParams['name']:
                    return markerParams

            return

    def addMarker(self, params):
        if self.__markersParams is None:
            self.__markersParams = []
        for markerParams in self.__markersParams:
            if params['name'] == markerParams['name']:
                break
        else:
            self.__markersParams.append(params)

        return

    def showMarker(self, name):
        if self.__markersParams is None:
            return
        else:
            self.serializeMethod(CallbackDataNames.BC_MARKERS_SHOWMARKER, (name,))
            for markerParams in self.__markersParams:
                if name == markerParams['name']:
                    if name not in self.__markers:
                        self.__createMarker(markerParams)
                        if self.__markerSoundShow is not None:
                            self.__markerSoundShow.stop()
                            self.__markerSoundShow = None
                        self.__markerSoundShow = SoundGroups.g_instance.WWgetSoundPos(self.SHOW_SOUND_ID, 'marker_sound_' + name + '_' + self.SHOW_SOUND_ID, self.__markers[name].position)
                        if self.__markerSoundShow is not None:
                            self.__markerSoundShow.play()
                        else:
                            LOG_DEBUG_DEV_BOOTCAMP('Marker sound is None')
                    break

            return

    def hideMarker(self, name, silently=False):
        if self.__markersParams is None:
            return
        else:
            self.serializeMethod(CallbackDataNames.BC_MARKERS_HIDEMARKER, (name, silently))
            if name in self.__markers:
                if self.__markerSoundShow is not None:
                    self.__markerSoundShow.stop()
                    self.__markerSoundShow = None
                self.__markers[name].clear()
                del self.__markers[name]
                if not silently:
                    SoundGroups.g_instance.playSound2D(self.HIDE_SOUND_ID)
            return

    def update(self):
        for marker in self.__markers.values():
            pos = marker.position
            distance = int(round((pos - BigWorld.player().getOwnVehiclePosition()).length))
            marker.update(distance)

    def getActiveMarkers(self):
        return self.__markers

    def replaySubscribe(self):
        self.replayMethodSubscribe(CallbackDataNames.BC_MARKERS_ONTRIGGERACTIVATED, self.onTriggerActivated)
        self.replayMethodSubscribe(CallbackDataNames.BC_MARKERS_ONTRIGGERDEACTIVATED, self.onTriggerDeactivated)
        self.replayMethodSubscribe(CallbackDataNames.BC_MARKERS_SHOWMARKER, self.showMarker)
        self.replayMethodSubscribe(CallbackDataNames.BC_MARKERS_HIDEMARKER, self.hideMarker)

    def replayMethodSubscribe(self, eventName, method):
        callback = partial(self.replayMethodCall, method, eventName)
        if self.bootcamp.replayCtrl:
            self.bootcamp.replayCtrl.setDataCallback(eventName, callback)
        self.replayCallbacks.append((eventName, callback))

    def replayMethodCall(self, callMethod, eventName, binData):
        callMethod(*cPickle.loads(base64.b64decode(binData)))

    def serializeMethod(self, eventName, params):
        if BattleReplay.g_replayCtrl.isRecording:
            BattleReplay.g_replayCtrl.serializeCallbackData(eventName, (base64.b64encode(cPickle.dumps(params, -1)),))

    def _handleKeyEvent(self, event):
        if event.isKeyDown() and event.key == Keys.KEY_V:
            self.__switchedToHiddenMode = not self.__switchedToHiddenMode
            for marker in self.__markers.itervalues():
                marker.switchToHiddenMode(self.__switchedToHiddenMode)

    def _onUIStateChanged(self, state):
        if state == UI_STATE.START:
            if self.__gui is not None and self.__gui.inited:
                minimap = self.__gui.getMinimapPlugin()
                marker2D = self.__gui.getMarkers2DPlugin()
                for marker in self.__markers.itervalues():
                    marker.attachGUI(marker2D, minimap)

        elif state == UI_STATE.STOP:
            self.stop()
        return

    def __createMarker(self, markerParams):
        entityID = markerParams['style']
        data = self.__entitiesParams.getEntity(entityID)
        typeID = 1
        self.__triggerID += 1
        position = markerParams['position']
        if position is None:
            LOG_ERROR_BOOTCAMP('Can not determine position of object', self.__triggerID)
            return
        else:
            indicatorCtrl = None
            if data.isIndicatorCreate():
                worldData = data.getWorldData()
                offset = worldData.get('offset', Math.Vector3(0, 0, 0))
                indicatorCtrl = _DirectionIndicatorCtrl(('yellow', 'yellow'), Math.Vector3(position[:]) + offset)
            areaMarker = _AreaMarker(typeID, self.__triggerID, position, _StaticWorldMarker2D(self.__triggerID, data.getWorldData(), position, self.STATIC_MARKER_DIST), _StaticMinimapMarker2D(data.getID(), position), _StaticObjectMarker3D(data.getModelData(), position), _StaticObjectMarker3D(data.getGroundData(), position), indicatorCtrl)
            areaMarker.switchToSniperMode(self.__switchedToSniperMode)
            areaMarker.switchToHiddenMode(self.__switchedToHiddenMode)
            if self.__gui is not None and self.__gui.inited:
                minimap = self.__gui.getMinimapPlugin()
                marker2D = self.__gui.getMarkers2DPlugin()
                areaMarker.attachGUI(marker2D, minimap)
            self.__markers[markerParams['name']] = areaMarker
            return
