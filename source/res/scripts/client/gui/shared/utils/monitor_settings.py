# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/utils/monitor_settings.py
import math
import BigWorld
import GUI
from shared_utils import findFirst
from gui.shared.utils.graphics import getSuitableVideoModes, getSuitableWindowSizes, VideoMode, WindowSize, BorderlessSize

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
        return WindowSize(*map(int, BigWorld.wg_getCurrentResolution(BigWorld.WindowModeWindowed)))

    @property
    def borderlessSizes(self):
        return self.__suitableVideoModes[self.activeMonitor]

    @property
    def currentBorderlessSize(self):
        return BorderlessSize(*map(int, BigWorld.getBorderlessParameters())) if self.windowMode == BigWorld.WindowModeBorderless else VideoMode(*BigWorld.listBorderlessResolutionsAllMonitors()[self.currentMonitor][0])

    @property
    def videoModes(self):
        return self.videoModesForAdapterOutputIndex(self.activeMonitor)

    def videoModesForAdapterOutputIndex(self, adapterOutputIndex):
        return self.__suitableVideoModes[adapterOutputIndex]

    @property
    def currentVideoMode(self):
        for videoMode in self.videoModes:
            if videoMode.index == BigWorld.videoModeIndex():
                return videoMode

        return findFirst(None, self.videoModes)

    def changeMonitor(self, monitorIdx):
        if self.__currentMonitorIdx != monitorIdx:
            self.__monitorChanged = True
        self.__currentMonitorIdx = monitorIdx
        BigWorld.setActiveMonitorIndex(monitorIdx, BigWorld.WindowModeWindowed)
        BigWorld.setActiveMonitorIndex(monitorIdx, BigWorld.WindowModeBorderless)
        BigWorld.setActiveMonitorIndex(monitorIdx, BigWorld.WindowModeExclusiveFullscreen)

    def setWindowed(self):
        if self.windowMode != BigWorld.WindowModeWindowed:
            BigWorld.changeVideoMode(-1, BigWorld.WindowModeWindowed)

    def setBorderless(self):
        if self.windowMode != BigWorld.WindowModeBorderless:
            BigWorld.changeVideoMode(-1, BigWorld.WindowModeBorderless)

    def changeWindowSize(self, width, height):
        if not self.isMonitorChanged and self.windowMode != BigWorld.WindowModeWindowed:
            self.setWindowed()
        curWindowSize = self.currentWindowSize
        if curWindowSize.width != width or curWindowSize.height != height:
            BigWorld.resizeWindow(width, height)

    def changeBorderlessSize(self, width, height):
        curBorderlessSize = self.currentBorderlessSize
        if curBorderlessSize.width != width or curBorderlessSize.height != height:
            BigWorld.setBorderlessFixedSize(width, height)
        BigWorld.changeVideoMode(-1, BigWorld.WindowModeBorderless)

    def setGlyphCache(self, scale=1):
        textureSize = int(1024 * math.ceil(scale))
        GUI.wg_setGlyphCacheParams(1, textureSize, textureSize)

    @property
    def activeMonitor(self):
        return BigWorld.getActiveMonitorIndex(BigWorld.getWindowMode())

    @property
    def currentMonitor(self):
        return self.__currentMonitorIdx

    @property
    def isMonitorChanged(self):
        return self.__monitorChanged

    @property
    def windowMode(self):
        return BigWorld.getWindowMode()

    @property
    def noRestartExclusiveFullscreenMonitorIndex(self):
        return BigWorld.getExclusiveFullscreenMonitorIndex()

    def maxParams(self):
        maxWdth = 640
        maxHght = 480
        vmodes = getSuitableVideoModes()
        for monitorModes in vmodes:
            for mode in monitorModes:
                maxWdth = max(maxWdth, mode.width)
                maxHght = max(maxHght, mode.height)

        return (maxWdth, maxHght)

    def isFullscreen(self):
        return BigWorld.getWindowMode() == BigWorld.WindowModeExclusiveFullscreen

    def isWindowed(self):
        return BigWorld.getWindowMode() == BigWorld.WindowModeWindowed

    def isBorderless(self):
        return BigWorld.getWindowMode() == BigWorld.WindowModeBorderless


g_monitorSettings = MonitorSettings()
