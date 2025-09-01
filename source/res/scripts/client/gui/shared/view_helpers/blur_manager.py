# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/blur_manager.py
import typing
from math import isnan
import GUI
import logging
import weakref
from collections import deque
from gui.app_loader.settings import APP_NAME_SPACE as _SPACE
from helpers import dependency
from ids_generators import Int32IDGenerator
from shared_utils import findFirst
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBlurEffect, IBlurController
if typing.TYPE_CHECKING:
    from Math import Vector4
_DEFAULT_BLUR_ANIM_REPEAT_COUNT = 10
_DEFAULT_UI_BLUR_RADIUS = 20
_logger = logging.getLogger(__name__)
_idsGenerator = Int32IDGenerator()

class BlurEffect(IBlurEffect):

    def __init__(self, manager, config):
        self._blurId = next(_idsGenerator)
        self._config = config
        self._manager = manager
        self._manager.registerBlur(self)

    @property
    def blurId(self):
        return self._blurId

    def fini(self):
        self._manager.unregisterBlur(self)
        self._manager = None
        return

    def enable(self):
        for config in self._config:
            config.enabled = True

        self._manager.updateBlur(self)

    def disable(self):
        for config in self._config:
            config.enabled = False

        self._manager.updateBlur(self)

    @property
    def config(self):
        return self._config

    def updateConfig(self, config):
        if set([ type(x) for x in config ]) != set([ type(x) for x in self._config ]):
            _logger.error("Can't update blur config with different blur types")
        self._config = config
        self._manager.updateBlur(self)


class BlurManager(object):

    def __init__(self):
        self._cache = deque()

    def fini(self):
        self.clear()

    def clear(self):
        activeBlur = self._activeBlur()
        if activeBlur is not None:
            for config in activeBlur.config:
                config.BLUR_CLS.unregister(blur=activeBlur, restoredBlur=None)

        self._cache.clear()
        return

    def registerBlur(self, blur):
        prevBlur = self._activeBlur()
        self._cache.append(weakref.ref(blur))
        for config in blur.config:
            config.BLUR_CLS.register(prevBlur=prevBlur, blur=blur)

        if prevBlur:
            for config in prevBlur.config:
                config.BLUR_CLS.register(prevBlur=prevBlur, blur=blur)

        self._validateCache()

    def unregisterBlur(self, blur):
        if self._isBlurInCache(blur):
            isActiveBlur = blur is self._activeBlur()
            self._cache.remove(weakref.ref(blur))
            if isActiveBlur:
                for config in blur.config:
                    config.BLUR_CLS.unregister(blur=blur, restoredBlur=self._activeBlur())

                prevBlur = self._activeBlur()
                if prevBlur is not None:
                    for config in prevBlur.config:
                        config.BLUR_CLS.apply(blur=prevBlur)

        return

    def updateBlur(self, blur):
        if self._isBlurInCache(blur) and blur is self._activeBlur():
            for config in blur.config:
                config.BLUR_CLS.apply(blur=blur)

    def _activeBlur(self):
        blurRef = findFirst(lambda ref: ref() is not None, reversed(self._cache))
        if blurRef is not None:
            return blurRef()
        else:
            self._validateCache()
            return

    def _validateCache(self):
        toDelete = []
        for itemRef in self._cache:
            if itemRef() is None:
                toDelete.append(itemRef)

        for item in toDelete:
            self._cache.remove(item)

        return bool(toDelete)

    def _isBlurInCache(self, blur):
        return True if weakref.ref(blur) in self._cache else False


class Blur(object):

    @classmethod
    def register(cls, prevBlur, blur):
        if prevBlur is not None:
            prevConfig = cls.getSpecificConfig(prevBlur.config)
            if prevConfig is not None:
                cls.disable(prevBlur)
        cls.apply(blur)
        return

    @classmethod
    def unregister(cls, blur, restoredBlur):
        specificConfig = cls.getSpecificConfig(blur.config)
        if specificConfig is not None:
            cls.disable(blur)
        if restoredBlur is not None:
            cls.apply(restoredBlur)
        return

    @classmethod
    def getSpecificConfig(cls, config):
        raise NotImplementedError

    @classmethod
    def apply(cls, blur):
        raise NotImplementedError

    @classmethod
    def disable(cls, blur):
        raise NotImplementedError


class ImmediateSceneBlur(Blur):

    @classmethod
    def getSpecificConfig(cls, config):
        return findFirst(lambda x: isinstance(x, ImmediateSceneBlurConfig), config)

    @classmethod
    def apply(cls, blur):
        specificConfig = ImmediateSceneBlur.getSpecificConfig(blur.config)
        if specificConfig is None:
            return
        else:
            spaceID = specificConfig.spaceID
            settings = specificConfig.settings
            GUI.enableBackgroundBlurFeature(spaceID, specificConfig.enabled)
            if not specificConfig.enabled:
                return
            GUI.setBackgroundBlurType(spaceID, settings['type'])
            GUI.setBlurDispatches(spaceID, settings['dispatches'])
            GUI.setBackgroundBlurApplianceType(spaceID, settings['applienceType'])
            GUI.setRadialApplianceBlurRadius(spaceID, settings['applienceRadius'])
            GUI.setBlurIntensity(spaceID, settings['intensity'])
            GUI.setBlurMipsCount(spaceID, settings['mipsCount'])
            GUI.setBlurAlphaParams(spaceID, settings['alphaParams']['center'], settings['alphaParams']['start'], settings['alphaParams']['end'])
            GUI.setBlurParams(spaceID, settings['params']['hstart'], settings['params']['hend'], settings['params']['vstart'], settings['params']['vend'])
            GUI.enableBlurDirection(spaceID, settings['direction']['top'], settings['direction']['right'], settings['direction']['bottom'], settings['direction']['left'])
            GUI.setHorizontalBlurParams(spaceID, settings['horizontalParams']['leftStart'], settings['horizontalParams']['leftEnd'], settings['horizontalParams']['rightStart'], settings['horizontalParams']['rightEnd'])
            GUI.setVerticalBlurParams(spaceID, settings['verticalParams']['topStart'], settings['verticalParams']['topEnd'], settings['verticalParams']['bottomStart'], settings['verticalParams']['bottomEnd'])
            GUI.setVerticalBlurAlphas(spaceID, settings['verticalAlphas']['topStart'], settings['verticalAlphas']['topEnd'], settings['verticalAlphas']['bottomStart'], settings['verticalAlphas']['bottomEnd'])
            GUI.setHorizontalBlurAlphas(spaceID, settings['horizontalAlphas']['leftStart'], settings['horizontalAlphas']['leftEnd'], settings['horizontalAlphas']['rightStart'], settings['horizontalAlphas']['rightEnd'])
            x, y = settings['center']
            width, height = GUI.screenResolution()
            if isnan(x):
                x = int(width / 2.0)
            if isnan(y):
                y = int(height / 2.0)
            GUI.setBlurCenter(spaceID, x, y)
            return

    @classmethod
    def disable(cls, blur):
        specificConfig = cls.getSpecificConfig(blur.config)
        if specificConfig is not None:
            GUI.enableBackgroundBlurFeature(specificConfig.spaceID, False)
        return


class SceneBlur(Blur):
    _globalBlur = GUI.WGUIBackgroundBlur()
    _rects = set()

    @classmethod
    def unregister(cls, blur, restoredBlur):
        specificConfig = cls.getSpecificConfig(blur.config)
        if specificConfig is not None:
            cls.disable(blur)
            cls._clearRects()
        if restoredBlur is not None:
            specificRestoredConfig = cls.getSpecificConfig(restoredBlur.config)
            if specificRestoredConfig is not None:
                specificRestoredConfig.fadeTime = 0
                cls.apply(restoredBlur)
        return

    @classmethod
    def getSpecificConfig(cls, config):
        return findFirst(lambda x: isinstance(x, SceneBlurConfig), config)

    @classmethod
    def apply(cls, blur):
        specificConfig = SceneBlur.getSpecificConfig(blur.config)
        if specificConfig is None:
            return
        else:
            cls._clearRects()
            SceneBlur._globalBlur.enable = specificConfig.enabled
            if not specificConfig.enabled:
                return
            SceneBlur._globalBlur.fadeTime = specificConfig.fadeTime
            if specificConfig.blurRadius is not None:
                SceneBlur._globalBlur.blurRadius = specificConfig.blurRadius
            for rect in specificConfig.rects:
                rectID = next(_idsGenerator)
                SceneBlur._rects.add(rectID)
                SceneBlur._globalBlur.addRect(rectID, rect)

            return

    @classmethod
    def disable(cls, blur):
        SceneBlur._globalBlur.enable = False

    @classmethod
    def _clearRects(cls):
        for id in SceneBlur._rects:
            SceneBlur._globalBlur.removeRect(id)

        SceneBlur._rects.clear()


class UILayerBlur(Blur):

    @classmethod
    def getSpecificConfig(cls, config):
        return findFirst(lambda x: isinstance(x, UILayerBlurConfig), config)

    @classmethod
    def apply(cls, blur):
        config = UILayerBlur.getSpecificConfig(blur.config)
        if config is None:
            return
        elif not config.enabled or config.ownLayer is None:
            return
        else:
            appLoader = dependency.instance(IAppLoader)
            lobby = appLoader.getApp(_SPACE.SF_LOBBY)
            battle = appLoader.getApp(_SPACE.SF_BATTLE)
            if lobby is not None:
                lobby.blurBackgroundViews(config.ownLayer, config.blurAnimRepeatCount, config.uiBlurRadius)
            elif battle is not None:
                battle.blurBackgroundViews(config.ownLayer, config.blurAnimRepeatCount, config.uiBlurRadius)
            return

    @classmethod
    def disable(cls, blur):
        appLoader = dependency.instance(IAppLoader)
        lobby = appLoader.getApp(_SPACE.SF_LOBBY)
        battle = appLoader.getApp(_SPACE.SF_BATTLE)
        if lobby is not None:
            lobby.unblurBackgroundViews()
        elif battle is not None:
            battle.unblurBackgroundViews()
        return


class ImmediateSceneBlurConfig(object):
    BLUR_CLS = ImmediateSceneBlur

    def __init__(self, enabled=False, spaceID=0, settings=None):
        self.enabled = enabled
        self.spaceID = spaceID
        self.settings = settings


class SceneBlurConfig(object):
    BLUR_CLS = SceneBlur

    def __init__(self, enabled=False, fadeTime=0, blurRadius=None, rects=None):
        self.enabled = enabled
        self.fadeTime = fadeTime
        self.blurRadius = blurRadius
        self.rects = rects


class UILayerBlurConfig(object):
    BLUR_CLS = UILayerBlur

    def __init__(self, enabled=False, ownLayer=None, blurAnimRepeatCount=_DEFAULT_BLUR_ANIM_REPEAT_COUNT, uiBlurRadius=_DEFAULT_UI_BLUR_RADIUS):
        self.enabled = enabled
        self.ownLayer = ownLayer
        self.blurAnimRepeatCount = blurAnimRepeatCount
        self.uiBlurRadius = uiBlurRadius


class CachedBlur(object):

    def __init__(self, enabled=False, fadeTime=0, ownLayer=None, blurAnimRepeatCount=_DEFAULT_BLUR_ANIM_REPEAT_COUNT, blurRadius=None, uiBlurRadius=_DEFAULT_UI_BLUR_RADIUS):
        blurCtrl = dependency.instance(IBlurController)
        self.__sceneBlurConfig = SceneBlurConfig(enabled, fadeTime, blurRadius, [])
        self.__blurConfig = (UILayerBlurConfig(enabled, ownLayer, blurAnimRepeatCount, uiBlurRadius), self.__sceneBlurConfig)
        self.__rects = {}
        self.__blur = blurCtrl.createBlur(self.__blurConfig)

    def fini(self):
        self.__blur.fini()

    def enable(self):
        self.__blur.enable()

    def disable(self):
        self.__blur.disable()

    def addRect(self, blurRect):
        id = next(_idsGenerator)
        self.__rects[id] = blurRect
        self.__updateRects()
        return id

    def changeRect(self, rectId, blurRect):
        self.__rects[rectId] = blurRect
        self.__updateRects()

    def removeRect(self, rectId):
        self.__rects.pop(rectId)
        self.__updateRects()

    @property
    def config(self):
        return self.__blur.config

    @property
    def enabled(self):
        return self.__sceneBlurConfig.enabled

    def __updateRects(self):
        self.__sceneBlurConfig.rects = self.__rects.values()
        self.__blur.updateConfig(self.__blurConfig)
