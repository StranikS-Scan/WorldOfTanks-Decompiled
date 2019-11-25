# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/graphics.py
import math
from collections import namedtuple
import BigWorld
from shared_utils import CONST_CONTAINER
MIN_SCREEN_WIDTH = 1024
MIN_SCREEN_HEIGHT = 768
MIN_COLOR_DEPTH = 23
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
        maxSize = WindowSize(*BigWorld.wg_getMaxWindowedResolution(idx))
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
        maxSize = WindowSize(*BigWorld.wg_getMaxBorderlessResolution(idx))
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


def getInterfaceScalesList(size, powerOfTwo=True):
    result = [SCALE_PREFIX[0]]
    if powerOfTwo:
        scale = max(min(int(math.log(max(size[0] / getResolution().width, 1.0), 2)), int(math.log(max(size[1] / getResolution().height, 1.0), 2))), 0)
        for i in xrange(scale + 1):
            result.append(SCALE_PREFIX[1] % 2 ** i)

    else:
        scale = min(int(size[0] / MIN_SCREEN_WIDTH), int(size[1] / MIN_SCREEN_HEIGHT))
        for i in xrange(1, scale):
            result.append(SCALE_PREFIX[1] % i)

    return result


def onInterfaceScaleChanged(scale):
    BigWorld.onInterfaceScaleChanged(scale)


def getNativeResolutionIndex():
    from gui.shared.utils.monitor_settings import g_monitorSettings
    nativeResolution = BigWorld.wg_getNativeScreenResoulution(g_monitorSettings.currentMonitor)
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
        nativeResolution = BigWorld.wg_getNativeScreenResoulution(g_monitorSettings.currentMonitor)
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
