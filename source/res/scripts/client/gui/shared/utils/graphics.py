# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/graphics.py
import typing
from collections import namedtuple
import BigWorld
from account_helpers.settings_core.settings_constants import GRAPHICS
from shared_utils import CONST_CONTAINER, findFirst
if typing.TYPE_CHECKING:
    from typing import Tuple
MIN_SCREEN_WIDTH = 1024
MIN_SCREEN_HEIGHT = 768
MIN_COLOR_DEPTH = 23
MAX_SCALE_STEP = 1
ScaleSettings = namedtuple('ScaleSettings', ('width', 'height', 'scales'))
_DEFAULT_SCALE = (0.0, 1.0)
_SCALES = (ScaleSettings(1920, 1200, _DEFAULT_SCALE),
 ScaleSettings(2048, 1546, (0.0, 1.0, 1.25, 1.5)),
 ScaleSettings(2560, 1600, (0.0, 1.0, 1.25, 1.5, 1.75)),
 ScaleSettings(3200, 2048, (0.0, 1.0, 1.25, 1.5, 1.75, 2.0)),
 ScaleSettings(4096, 2160, (0.0, 1.0, 1.25, 1.5, 1.75, 2.0)))
VideoMode = namedtuple('VideoMode', 'index width height colorDepth label refreshRate')
WindowSize = namedtuple('WindowSize', 'width height refreshRate')
BorderlessSize = namedtuple('BorderlessSize', 'behaviour posX posY width height monitor')
SCALE_PREFIX = ('auto', 'x%d')

class GRAPHICS_SETTINGS(CONST_CONTAINER):
    pass


class GRAPHICS_SETTINGS_STATUS(CONST_CONTAINER):
    NONE = 0
    MAJOR_CHANGED = 1
    MINOR_CHANGED = 2


class _GraphicsStatus(object):

    def __init__(self, value):
        self.__value = value

    def isReset(self):
        return self.__value == GRAPHICS_SETTINGS_STATUS.MAJOR_CHANGED

    def isShowWarning(self):
        return self.__value == GRAPHICS_SETTINGS_STATUS.MINOR_CHANGED

    @classmethod
    def markProcessed(cls):
        BigWorld.resetGraphicsSettingsStatus()


def getStatus():
    return _GraphicsStatus(BigWorld.graphicsSettingsStatus())


def isVideoModeSuitable(mode):
    return mode.width >= MIN_SCREEN_WIDTH and mode.height >= MIN_SCREEN_HEIGHT and mode.colorDepth >= MIN_COLOR_DEPTH


def getSuitableVideoModes():
    result = []
    currentVideoMode = BigWorld.videoModeIndex()
    for monitorModes in BigWorld.listVideoModesAllMonitors():
        modes = []
        for mode in monitorModes:
            m = VideoMode(*mode)
            if isVideoModeSuitable(m) or m.index == currentVideoMode:
                modes.append(m)

        result.append(modes)

    return tuple(result)


def getSuitableWindowSizes():
    result = []
    for idx, monitorModes in enumerate(getSuitableVideoModes()):
        maxSize = WindowSize(*BigWorld.getMaxWindowedResolution(idx))
        modes = []
        for mode in monitorModes:
            if mode.width <= maxSize.width and mode.height <= maxSize.height:
                modes.append(WindowSize(mode.width, mode.height, mode.refreshRate))

        if maxSize not in modes:
            modes.append(maxSize)
        result.append(modes)

    return tuple(result)


def getSuitableBorderlessSizes():
    result = []
    for idx, monitorModes in enumerate(getSuitableVideoModes()):
        maxSize = WindowSize(*BigWorld.getMaxBorderlessResolution(idx))
        modes = []
        for mode in monitorModes:
            if mode.width <= maxSize.width and mode.height <= maxSize.height:
                modes.append(WindowSize(mode.width, mode.height, mode.refreshRate))

        if maxSize not in modes:
            modes.append(maxSize)
        result.append(modes)

    return tuple(result)


GraphicSetting = namedtuple('GraphicSetting', 'label value options hint advanced needRestart isArray delayed')

def getGraphicsSetting(settingName):
    setting = BigWorld.graphicSetting(settingName)
    return None if setting is None else GraphicSetting(*setting)


def getGraphicPresetSettingsByName(presetName):
    presets = getGraphicsSetting(GRAPHICS.PRESETS).options
    return findFirst(lambda preset: preset['key'] == presetName, presets, {})


def getGraphicPresetSettingsByIndex(presetIndex):
    presets = getGraphicsSetting(GRAPHICS.PRESETS).options
    return findFirst(lambda preset: preset['index'] == presetIndex, presets, {})


def getCurrentGraphicPresetName():
    presets = getGraphicsSetting(GRAPHICS.PRESETS)
    return presets.options[presets.value]['key']


def getGraphicsPresets(presetIdx=None):
    return BigWorld.getGraphicsPreset(presetIdx) if presetIdx is not None else BigWorld.getGraphicsPresets()


def getGraphicsPresetsIndices():
    return BigWorld.getGraphicsPresetsIndices()


def getGraphicSettingImages(settingName):
    result = {}
    data = getGraphicsSetting(settingName)
    if data is not None:
        for idx, (label, supported, _, _) in enumerate(data.options):
            if supported:
                result[idx] = '../maps/icons/settings/%s/%s.png' % (settingName, str(label).replace(' ', '_'))

    return result


def getGraphicSettingColorSettingsFiletersImages():
    result = {}
    data = getGraphicsSetting('COLOR_GRADING_TECHNIQUE')
    imgPath = '../maps/icons/settings/colorSettings/filterTypes/%s.png'
    if data is not None:
        for idx, (label, supported, _, _) in enumerate(data.options):
            if supported:
                result[idx] = imgPath % str(label).replace(' ', '_')

    return result


def getResolution():
    from gui.shared.utils.monitor_settings import g_monitorSettings
    currWindowSize = g_monitorSettings.currentWindowSize
    width = currWindowSize.width if currWindowSize.width > 0 else MIN_SCREEN_WIDTH
    height = currWindowSize.height if currWindowSize.height > 0 else MIN_SCREEN_HEIGHT
    return WindowSize(min(width, MIN_SCREEN_WIDTH), min(height, MIN_SCREEN_HEIGHT), currWindowSize.refreshRate)


def getInterfaceScalesList(size):
    screenWidth, screenHeight = size
    scaleSetting = None
    for value in _SCALES:
        if screenWidth <= value.width or screenHeight <= value.height:
            scaleSetting = value
            break

    if scaleSetting is None:
        maxScale = int(max(min(float(screenWidth) / MIN_SCREEN_WIDTH, float(screenHeight) / MIN_SCREEN_HEIGHT), 1.0))
        result = [0]
        result.extend([ 1.0 + MAX_SCALE_STEP * stepIdx for stepIdx in xrange(0, maxScale) ])
    else:
        result = scaleSetting.scales
    return result


def onInterfaceScaleChanged(scale):
    BigWorld.onInterfaceScaleChanged(scale)


def getNativeResolutionIndex():
    from gui.shared.utils.monitor_settings import g_monitorSettings
    nativeResolution = BigWorld.getNativeScreenResolution(g_monitorSettings.currentMonitor)
    result = []
    for modes in getSuitableVideoModes():
        resolutions = set()
        for mode in modes:
            resolutions.add((mode.width, mode.height))

        result.append(sorted(tuple(resolutions)))

    idx = -1
    for idx, (w, h) in enumerate(result[g_monitorSettings.currentMonitor]):
        if w == nativeResolution[0] and h == nativeResolution[1]:
            return idx

    return idx


def isGammaSupported():
    from gui.shared.utils.monitor_settings import g_monitorSettings
    isFullscreen = g_monitorSettings.isFullscreen()
    if isFullscreen:
        cVideoMode = g_monitorSettings.currentVideoMode
        nativeResolution = BigWorld.getNativeScreenResolution(g_monitorSettings.currentMonitor)
        if nativeResolution is not None:
            isNativeSelected = cVideoMode.width == nativeResolution[0] and cVideoMode.height == nativeResolution[1]
        else:
            isNativeSelected = False
        return isNativeSelected
    else:
        return isRendererPipelineDeferred()
        return


def isRendererPipelineDeferred():
    pipelineType = BigWorld.getGraphicsSetting('RENDER_PIPELINE')
    return pipelineType == 0
