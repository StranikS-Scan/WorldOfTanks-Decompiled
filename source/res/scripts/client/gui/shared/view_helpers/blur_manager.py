# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/blur_manager.py
import typing
import GUI
import logging
import weakref
from collections import deque
from gui.app_loader import sf_lobby, sf_battle
from helpers import dependency
from ids_generators import Int32IDGenerator
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
if typing.TYPE_CHECKING:
    from Math import Vector4
    from typing import Deque
    from _weakref import ReferenceType
_DEFAULT_BLUR_ANIM_REPEAT_COUNT = 10
_logger = logging.getLogger(__name__)
_idsGenerator = Int32IDGenerator()

class CachedBlur(object):
    __slots__ = ('_blurId', '_enabled', '_fadeTime', '_rectangles', '_ownLayer', '_blurAnimRepeatCount', '__weakref__', '_prevBlurRadius')

    def __init__(self, enabled=False, fadeTime=0, ownLayer=None, blurAnimRepeatCount=_DEFAULT_BLUR_ANIM_REPEAT_COUNT, blurRadius=None):
        self._blurId = next(_idsGenerator)
        self._rectangles = {}
        self._enabled = enabled
        self._fadeTime = fadeTime
        self._ownLayer = ownLayer
        self._blurAnimRepeatCount = blurAnimRepeatCount
        _manager.registerBlur(self)
        if blurRadius is not None:
            self._prevBlurRadius = _manager.getBlurRadius()
            _manager.setBlurRadius(blurRadius)
        else:
            self._prevBlurRadius = None
        return

    def fini(self):
        _manager.unregisterBlur(self)
        self._blurId = None
        if self._prevBlurRadius is not None:
            _manager.setBlurRadius(self._prevBlurRadius)
            self._prevBlurRadius = None
        return

    def __del__(self):
        if self._blurId is not None:
            self.fini()
        return

    def enable(self):
        self._switchEnabled(True)

    def disable(self):
        self._switchEnabled(False)

    def addRect(self, blurRect):
        rectId = next(_idsGenerator)
        if rectId not in self._rectangles:
            self._rectangles[rectId] = blurRect
        else:
            _logger.error('There is already added rectangular with the same rect id %d', rectId)
        _manager.addRect(self, blurRect, rectId)
        return rectId

    def changeRect(self, rectId, blurRect):
        self._rectangles[rectId] = blurRect
        _manager.addRect(self, blurRect, rectId)

    def removeRect(self, rectId):
        self._rectangles.pop(rectId)
        _manager.removeRect(self, rectId)

    @property
    def blurId(self):
        return self._blurId

    @property
    def enabled(self):
        return self._enabled

    @property
    def fadeTime(self):
        return self._fadeTime

    @property
    def rectangles(self):
        return self._rectangles

    @property
    def ownLayer(self):
        return self._ownLayer

    @property
    def isLayerBlur(self):
        return bool(self._ownLayer)

    @property
    def blurAnimRepeatCount(self):
        return self._blurAnimRepeatCount

    def _switchEnabled(self, enabled):
        self._enabled = enabled
        _manager.switchEnabled(self, enabled)


class _BlurManager(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    __slots__ = ('_cache',)
    _cache = deque()
    _globalBlur = GUI.WGUIBackgroundBlur()

    def registerBlur(self, blur):
        self._cache.append(weakref.ref(blur))
        self._resetGlobalBlur()
        self._validateCache()
        if blur.enabled:
            self.switchEnabled(blur, True)

    def unregisterBlur(self, blur):
        if self._isBlurInCache(blur):
            isActiveBlur = blur is self._activeBlur()
            self._cache.remove(weakref.ref(blur))
            if isActiveBlur:
                if blur.enabled:
                    self._globalBlur.enable = False
                self._restoreLastAdded()
            if not self._hasEnabledLayerBlur():
                self._resetLayerBlur()

    def addRect(self, blur, blurRect, rectId):
        if self._isBlurInCache(blur) and blur is self._activeBlur():
            self._globalBlur.addRect(rectId, blurRect)

    def removeRect(self, blur, rectId):
        if self._isBlurInCache(blur) and blur is self._activeBlur():
            self._globalBlur.removeRect(rectId)

    def switchEnabled(self, blur, enabled):
        if self._isBlurInCache(blur) and blur is self._activeBlur():
            self._globalBlur.enable = enabled
            self._globalBlur.fadeTime = blur.fadeTime
            self._handleLayersBlur(blur)

    def getBlurRadius(self):
        return self._globalBlur.blurRadius

    def setBlurRadius(self, value):
        self._globalBlur.blurRadius = value

    @sf_lobby
    def _lobby(self):
        return None

    @sf_battle
    def _battle(self):
        return None

    def _restoreLastAdded(self):
        activeBlur = self._activeBlur()
        if activeBlur is not None:
            for rectId, rect in activeBlur.rectangles.iteritems():
                self._globalBlur.addRect(rectId, rect)

            self._globalBlur.fadeTime = 0
            self._globalBlur.enable = activeBlur.enabled
            self._handleLayersBlur(activeBlur)
        else:
            self._resetGlobalBlur()
        return

    def _handleLayersBlur(self, blur):
        if blur.isLayerBlur:
            if blur.enabled:
                self._setLayerBlur(blur)
            else:
                self._resetLayerBlur()

    def _setLayerBlur(self, blur):
        if self._lobby is not None:
            self._lobby.blurBackgroundViews(blur.ownLayer, blur.blurAnimRepeatCount)
        elif self._battle is not None:
            self._battle.blurBackgroundViews(blur.ownLayer, blur.blurAnimRepeatCount)
        return

    def _resetGlobalBlur(self):
        self._globalBlur.enable = False
        self._globalBlur.fadeTime = 0
        self._globalBlur.removeAllRects()

    def _resetLayerBlur(self):
        if self._lobby is not None:
            self._lobby.unblurBackgroundViews()
        elif self._battle is not None:
            self._battle.unblurBackgroundViews()
        return

    def _activeBlur(self):
        blurRef = findFirst(lambda ref: ref() is not None, self._cache.__reversed__())
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

        return len(toDelete) > 0

    def _hasEnabledLayerBlur(self):
        for itemRef in self._cache:
            if itemRef is not None:
                item = itemRef()
                if item and item.isLayerBlur and item.enabled:
                    return True

        return False

    def _isBlurInCache(self, blur):
        if weakref.ref(blur) in self._cache:
            return True
        logging.error("Blur instance with id %s isn't found in cache (not registered or already deleted)", blur.blurId)
        return False


_manager = _BlurManager()
