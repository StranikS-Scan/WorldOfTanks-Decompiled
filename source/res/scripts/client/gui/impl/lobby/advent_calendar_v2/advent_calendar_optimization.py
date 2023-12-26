# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_optimization.py
import logging
import BigWorld
import AnimationSequence
import WebBrowser
from skeletons.gui.impl import IGuiLoader
from helpers import dependency, isPlayerAccount
from collections import namedtuple
from skeletons.gui.shared.utils import IHangarSpace
AdventWindowOptimizationProcessorSettings = namedtuple('AdventWindowOptimizationProcessorSettings', ('windowsVisibilityPredicateFunction',))
AdventWindowOptimizationSettings = namedtuple('AdventWindowOptimizationSettings', ('disableWindowsVisibility', 'disableExternalCacheDownloading', 'disableAnimationSequenceUpdate', 'disable3dSceneDrawing', 'windowOptimizationProcessorSettings'))
AdventWindowOptimizationSettings.__new__.func_defaults = (None,) * len(AdventWindowOptimizationSettings._fields)
_logger = logging.getLogger(__name__)

class _AdventWindowOptimizationProcessor(object):
    _guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, settings=None):
        self.__hiddenWindowsUids = []
        self.__settings = settings
        self._handlers = {'disableWindowsVisibility': self._switchWindowsVisibility,
         'disableExternalCacheDownloading': self._switchExternalCacheDownloading,
         'disableAnimationSequenceUpdate': self._switchAnimationSequence,
         'disable3dSceneDrawing': self._switch3dSceneDrawing}

    def getHandlers(self):
        return self._handlers

    def _switchWindowsVisibility(self, value):
        if not value and self.__hiddenWindowsUids:
            _logger.debug('Start showing windows with ids, %s', self.__hiddenWindowsUids)
            for windowUid in self.__hiddenWindowsUids:
                window = self._guiLoader.windowsManager.getWindow(windowUid)
                if window is not None and window.isHidden():
                    window.show()

            self.__releaseHiddenWindows()
        else:
            windows = self._getWindows()
            if not windows:
                _logger.error("Couldn't find any open windows")
                return
            _logger.debug('Start hiding windows, %s', windows)
            for window in windows:
                windowId = window.uniqueID
                if self._guiLoader.windowsManager.getWindow(windowId) is not None and not window.isHidden():
                    window.hide()
                    self.__hiddenWindowsUids.append(windowId)

        return

    def _switchExternalCacheDownloading(self, value):
        _logger.info('Switching pauseExternalCache to , %s', value)
        WebBrowser.pauseExternalCache(not value)

    def _switchAnimationSequence(self, value):
        if self._canApplySettings:
            _logger.info('Switching setEnableAnimationSequenceUpdate to , %s', value)
            AnimationSequence.setEnableAnimationSequenceUpdate(value)

    def _switch3dSceneDrawing(self, value):
        if self._canApplySettings:
            _logger.info('Switching worldDrawEnabled to , %s', value)
            BigWorld.worldDrawEnabled(value)

    def _getWindows(self):
        predicatFunction = (lambda x: True) if self.__settings is None else self.__settings.windowsVisibilityPredicateFunction
        return self._guiLoader.windowsManager.findWindows(predicatFunction)

    @staticmethod
    def _canApplySettings():
        return isPlayerAccount() and dependency.instance(IHangarSpace).spaceInited

    def __releaseHiddenWindows(self):
        self.__hiddenWindows = []


class AdventWindowOptimizationManager(object):
    _windowOptimizationProcessor = _AdventWindowOptimizationProcessor

    def __init__(self, settings):
        self.__settings = settings
        self.__processor = self._windowOptimizationProcessor(self.__settings.windowOptimizationProcessorSettings)

    def start(self):
        self._switchSettings(True)

    def fini(self):
        _logger.info('Destruction of the controller AdventWindowOptimizationManager')
        self._switchSettings(False)
        self.__settings = None
        self.__processor = None
        return

    def _switchSettings(self, managerState):
        for settingName, handler in self.__processor.getHandlers().items():
            settingValue = getattr(self.__settings, settingName)
            if settingValue is not None:
                switchState = settingValue if managerState else not settingValue
                handler(switchState)

        return
