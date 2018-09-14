# Embedded file name: scripts/client/gui/shared/utils/graphics.py
import BigWorld
import math
from collections import namedtuple
from debug_utils import LOG_WARNING
from gui.doc_loaders.GraphicsPresetsLoader import GraphicsPresetsLoader
from shared_utils import CONST_CONTAINER
from account_helpers.settings_core.settings_constants import GRAPHICS
import GUI
MIN_SCREEN_WIDTH = 1024
MIN_SCREEN_HEIGHT = 768
MIN_COLOR_DEPTH = 23
_g_graphSettingsIndices = None
_g_graphPresets = None
GraphicSetting = namedtuple('GraphicSetting', 'label value options hint advanced needRestart delayed')
VideoMode = namedtuple('VideoMode', 'index width height colorDepth label refreshRate')
WindowSize = namedtuple('WindowSize', 'width height refreshRate')
SCALE_PREFIX = ('auto', 'x%d')

class GRAPHICS_SETTINGS(CONST_CONTAINER):
    RENDER_PIPELINE = 'RENDER_PIPELINE'
    TEXTURE_QUALITY = 'TEXTURE_QUALITY'
    DECALS_QUALITY = 'DECALS_QUALITY'
    OBJECT_LOD = 'OBJECT_LOD'
    FAR_PLANE = 'FAR_PLANE'
    TERRAIN_QUALITY = 'TERRAIN_QUALITY'
    SHADOWS_QUALITY = 'SHADOWS_QUALITY'
    LIGHTING_QUALITY = 'LIGHTING_QUALITY'
    SPEEDTREE_QUALITY = 'SPEEDTREE_QUALITY'
    FLORA_QUALITY = 'FLORA_QUALITY'
    WATER_QUALITY = 'WATER_QUALITY'
    EFFECTS_QUALITY = 'EFFECTS_QUALITY'
    POST_PROCESSING_QUALITY = 'POST_PROCESSING_QUALITY'
    MOTION_BLUR_QUALITY = 'MOTION_BLUR_QUALITY'
    SNIPER_MODE_EFFECTS_QUALITY = 'SNIPER_MODE_EFFECTS_QUALITY'
    VEHICLE_DUST_ENABLED = 'VEHICLE_DUST_ENABLED'
    SNIPER_MODE_GRASS_ENABLED = 'SNIPER_MODE_GRASS_ENABLED'
    VEHICLE_TRACES_ENABLED = 'VEHICLE_TRACES_ENABLED'
    SNIPER_MODE_SWINGING_ENABLED = 'SNIPER_MODE_SWINGING_ENABLED'
    COLOR_GRADING_TECHNIQUE = 'COLOR_GRADING_TECHNIQUE'
    SEMITRANSPARENT_LEAVES_ENABLED = 'SEMITRANSPARENT_LEAVES_ENABLED'
    DRR_AUTOSCALER_ENABLED = GRAPHICS.DRR_AUTOSCALER_ENABLED


def __initPresetsData():
    global _g_graphPresets
    if _g_graphPresets is None:
        _g_graphPresets = GraphicsPresetsLoader()
        _g_graphPresets.load()
    return


def __initGraphicsSettingsData():
    global _g_graphSettingsIndices
    if _g_graphSettingsIndices is None:
        _g_graphSettingsIndices = dict(((data[0], idx) for idx, data in enumerate(BigWorld.graphicsSettings())))
    return


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
    for monitorModes in BigWorld.listVideoModesAllMonitors():
        modes = []
        for mode in monitorModes:
            m = VideoMode(*mode)
            if isVideoModeSuitable(m):
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


def getGraphicsSetting(settingName):
    __initGraphicsSettingsData()
    index = _g_graphSettingsIndices.get(settingName)
    if index is None:
        LOG_WARNING('Unknown graphics setting', settingName)
        return
    else:
        return GraphicSetting(*BigWorld.graphicsSettings()[index])


def getGraphicsPresets(presetIdx = None):
    __initPresetsData()
    if presetIdx is not None:
        return _g_graphPresets.getPreset(presetIdx)
    else:
        return [ _g_graphPresets.getPreset(key) for key in _g_graphPresets.getPresetsKeys() ]


def getGraphicsPresetsIndices():
    __initPresetsData()
    return dict(((key, idx) for idx, key in enumerate(_g_graphPresets.getPresetsKeys())))


def getGraphicSettingImages(settingName):
    result = {}
    data = getGraphicsSetting(settingName)
    if data is not None:
        for idx, (label, supported, _, _) in enumerate(data.options):
            if supported:
                result[idx] = '../maps/icons/settings/%s/%s.png' % (settingName, str(label).replace(' ', '_'))

    return result


def getResolution():
    currWindowSize = g_monitorSettings.currentWindowSize
    width = currWindowSize.width if currWindowSize.width > 0 else MIN_SCREEN_WIDTH
    height = currWindowSize.height if currWindowSize.height > 0 else MIN_SCREEN_HEIGHT
    return WindowSize(min(width, MIN_SCREEN_WIDTH), min(height, MIN_SCREEN_HEIGHT), currWindowSize.refreshRate)


def getInterfaceScalesList(size, powerOfTwo = True):
    result = [SCALE_PREFIX[0]]
    if powerOfTwo:
        scale = max(min(int(math.log(max(size[0] / getResolution().width, 1.0), 2)), int(math.log(max(size[1] / getResolution().height, 1.0), 2))), 0)
        for size in xrange(scale + 1):
            result.append(SCALE_PREFIX[1] % 2 ** size)

    else:
        scale = min(int(size[0] / MIN_SCREEN_WIDTH), int(size[1] / MIN_SCREEN_HEIGHT))
        for i in xrange(1, scale):
            result.append(SCALE_PREFIX[1] % i)

    return result


class MonitorSettings(object):

    def __init__(self):
        self.__suitableVideoModes = getSuitableVideoModes()
        self.__suitableWindowSizes = getSuitableWindowSizes()
        self.__monitorChanged = False
        self.__currentMonitorIdx = self.activeMonitor

    @property
    def windowSizes(self):
        return self.__suitableWindowSizes[self.activeMonitor]

    @property
    def currentWindowSize(self):
        return WindowSize(*map(int, BigWorld.wg_getCurrentResolution(True)))

    @property
    def videoModes(self):
        return self.__suitableVideoModes[self.activeMonitor]

    @property
    def currentVideoMode(self):
        for videoMode in self.videoModes:
            if videoMode.index == BigWorld.videoModeIndex():
                return videoMode

        return self.videoModes[0]

    def changeMonitor(self, monitorIdx):
        if self.__currentMonitorIdx != monitorIdx:
            self.__monitorChanged = True
        self.__currentMonitorIdx = monitorIdx
        BigWorld.wg_setActiveMonitorIndex(monitorIdx)

    def setFullscreen(self, isFullscreen):
        vm = self.currentVideoMode
        if vm is not None and isFullscreen != self.isFullscreen:
            BigWorld.changeVideoMode(vm.index, not isFullscreen)
        return

    def changeVideoMode(self, videoMode):
        cvm = self.currentVideoMode
        if not self.isMonitorChanged and cvm is not None and (videoMode.index != cvm or not self.isFullscreen):
            BigWorld.changeVideoMode(videoMode.index, False)
        return

    def changeWindowSize(self, width, height):
        if not self.isMonitorChanged and self.isFullscreen:
            self.setFullscreen(False)
        curWindowSize = self.currentWindowSize
        if curWindowSize.width != width or curWindowSize.height != height:
            BigWorld.resizeWindow(width, height)

    def setGlyphCache(self, scale = 1):
        textureSize = 1024 * math.ceil(scale)
        raise hasattr(GUI, 'wg_setGlyphCacheParams') or AssertionError('GUI.wg_setGlyphCacheParams() is not defined')
        GUI.wg_setGlyphCacheParams(1, textureSize, textureSize)

    @property
    def activeMonitor(self):
        return BigWorld.wg_getActiveMonitorIndex()

    @property
    def currentMonitor(self):
        return self.__currentMonitorIdx

    @property
    def isMonitorChanged(self):
        return self.__monitorChanged

    @property
    def isFullscreen(self):
        return not BigWorld.isVideoWindowed()

    @property
    def maxParams(self):
        maxWidth = maxHeight = 0
        for monitorModes in self.__suitableVideoModes:
            for mode in monitorModes:
                maxWidth = max(maxWidth, mode.width)
                maxHeight = max(maxHeight, mode.height)

        return (maxWidth, maxHeight)


g_monitorSettings = MonitorSettings()
