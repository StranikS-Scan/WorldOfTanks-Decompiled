# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/GraphicsResolutions.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_ERROR

class GraphicsResolutions(object):
    MIN_HEIGHT = 768
    MIN_WIDTH = 1024
    MIN_COLOR_DEPTH = 23
    ASPECT_RATIO = ((4, 3),
     (16, 9),
     (16, 10),
     (19, 10))

    def __init__(self):
        self.__allVideoModes = []
        for monitorModes in BigWorld.listVideoModesAllMonitors():
            modes = []
            for mode in monitorModes:
                if self.__isVideoModeSuitable(mode):
                    modes.append(mode)

            self.__allVideoModes.append(modes)

        self.__multisamplingTypes = BigWorld.getSupportedMultisamplingTypes()
        self.__multisamplingTypes.insert(0, 0)
        self.__customAAModes = BigWorld.getSupportedCustomAAModes()
        self.__monitors = BigWorld.wg_getMonitorNames()
        self.__curentMonitorIndex = BigWorld.wg_getActiveMonitorIndex()
        self.__monitorChanged = False
        self.__lastFullscreenSize = None
        self.__lastWindowedSize = None
        BigWorld.wg_setSavePreferencesCallback(self.onSavePreferencesXml)
        return

    @property
    def __windowSizes(self):
        __windowSizes = []
        for monitorModes in self.__allVideoModes:
            maxWindow = BigWorld.wg_getMaxWindowedResolution(len(__windowSizes))
            modes = []
            for m in monitorModes:
                if m[1] > maxWindow[0] or m[2] > maxWindow[1]:
                    continue
                modes.append((m[1], m[2]))

            if maxWindow not in modes:
                modes.append(maxWindow)
            __windowSizes.append(modes)

        return __windowSizes

    @property
    def __videoModes(self):
        return [ (m[0], m[1], m[2]) for m in self.__allVideoModes[self.monitorIndex] ]

    @property
    def __aspectRatios(self):
        return GraphicsResolutions.ASPECT_RATIO

    @property
    def __videoMode(self):
        return BigWorld.videoModeIndex()

    @property
    def __windowSize(self):
        return tuple(map(int, BigWorld.wg_getCurrentResolution(True)))

    @property
    def __aspectRatio(self):
        return round(BigWorld.getFullScreenAspectRatio(), 6)

    @property
    def __multisamplingType(self):
        return BigWorld.getMultisamplingType()

    @property
    def __customAAMode(self):
        return BigWorld.getCustomAAMode()

    @property
    def isVideoWindowed(self):
        return BigWorld.isVideoWindowed()

    @property
    def isVideoVSync(self):
        return BigWorld.isVideoVSync()

    @property
    def isTripleBuffered(self):
        return BigWorld.isTripleBuffered()

    @property
    def videoModeIndex(self):
        for index, videoModeInfo in enumerate(self.__videoModes):
            if videoModeInfo[0] == self.__videoMode:
                return index

    @property
    def monitorIndex(self):
        return BigWorld.wg_getActiveMonitorIndex()

    @property
    def realMonitorIndex(self):
        return self.__curentMonitorIndex

    @property
    def windowSizeIndex(self):
        for index, size in enumerate(self.__windowSizes[self.__curentMonitorIndex]):
            if size == self.__windowSize:
                return index

        return len(self.__windowSizes[self.__curentMonitorIndex])

    @property
    def aspectRatioIndex(self):
        for index, size in enumerate(self.__aspectRatios):
            if round(float(size[0]) / size[1], 6) == self.__aspectRatio:
                return index

        return len(self.__aspectRatios)

    @property
    def multisamplingTypeIndex(self):
        if self.__multisamplingType in self.__multisamplingTypes:
            return self.__multisamplingTypes.index(self.__multisamplingType)

    @property
    def customAAModeIndex(self):
        if self.__customAAMode in self.__customAAModes:
            return self.__customAAModes.index(self.__customAAMode)

    @property
    def videoModesList(self):
        allModes = []
        for monitorModes in self.__allVideoModes:
            modes = []
            for m in monitorModes:
                modes.append('%dx%d' % (m[1], m[2]))

            allModes.append(modes)

        return allModes

    @property
    def monitorsList(self):
        return self.__monitors

    @property
    def windowSizesList(self):
        allModes = []
        for monitorModes in self.__windowSizes:
            modes = []
            for m in monitorModes:
                modes.append('%dx%d' % m)

            current = '%dx%d' % self.__windowSize
            if current not in modes:
                modes.append(current + '*')
            allModes.append(modes)

        return allModes

    @property
    def aspectRatiosList(self):
        aspectRatios = [ '%d:%d' % m for m in self.__aspectRatios ]
        if self.aspectRatioIndex == len(self.__aspectRatios):
            aspectRatios.append('%s:1*' % BigWorld.wg_getNiceNumberFormat(self.__aspectRatio))
        return aspectRatios

    @property
    def multisamplingTypesList(self):
        return [ '#settings:multisamplingType/type%s' % i for i in self.__multisamplingTypes ]

    @property
    def customAAModesList(self):
        return [ '#settings:customAAMode/mode%s' % i for i in self.__customAAModes ]

    def __isVideoModeSuitable(self, videoMode):
        return videoMode[1] >= GraphicsResolutions.MIN_WIDTH and videoMode[2] >= GraphicsResolutions.MIN_HEIGHT and videoMode[3] >= GraphicsResolutions.MIN_COLOR_DEPTH

    def getVideoModeByIndex(self, index):
        if len(self.__videoModes) > index > -1:
            return self.__videoModes[int(index)][0]
        else:
            return None

    def getWindowSizeByIndex(self, index):
        if len(self.__windowSizes[self.__curentMonitorIndex]) > index > -1:
            return self.__windowSizes[self.__curentMonitorIndex][int(index)]
        return self.__windowSize

    def getAspectRatioByIndex(self, index):
        if len(self.__aspectRatios) > index > -1:
            ars = self.__aspectRatios[int(index)]
            return round(float(ars[0]) / ars[1], 6)
        else:
            return None

    def getMultisamplingTypeByIndex(self, index):
        if len(self.__multisamplingTypes) > index > -1:
            return self.__multisamplingTypes[int(index)]
        else:
            return None

    def getCustomAAModeByIndex(self, index):
        if len(self.__customAAModes) > index > -1:
            return self.__customAAModes[int(index)]
        else:
            return None

    @property
    def gamma(self):
        return BigWorld.getGammaCorrection()

    def applyChanges(self, isFullScreen, isVideoVSync, isTripleBuffered, sizeIndex, aspectRatioIndex, multisamplingIndex, customAAIndex, gamma, monitorIndex):
        if self.__curentMonitorIndex != monitorIndex:
            self.__monitorChanged = True
        self.__curentMonitorIndex = monitorIndex
        BigWorld.wg_setActiveMonitorIndex(monitorIndex)
        if self.isVideoVSync != isVideoVSync:
            BigWorld.setVideoVSync(isVideoVSync)
        if self.isTripleBuffered != isTripleBuffered:
            BigWorld.setTripleBuffering(isTripleBuffered)
        if self.gamma != gamma:
            gamma = max(gamma, 0.5)
            gamma = min(gamma, 2.0)
            BigWorld.setGammaCorrection(gamma)
        aspectRatio = self.getAspectRatioByIndex(aspectRatioIndex)
        if aspectRatio is not None and aspectRatio != self.__aspectRatio:
            BigWorld.changeFullScreenAspectRatio(aspectRatio)
        multisamplingType = self.getMultisamplingTypeByIndex(multisamplingIndex)
        if self.__multisamplingType != multisamplingType:
            BigWorld.setMultisamplingType(multisamplingType)
        customAAMode = self.getCustomAAModeByIndex(customAAIndex)
        if self.__customAAMode != customAAMode:
            BigWorld.setCustomAAMode(customAAMode)
        if isFullScreen:
            videoMode = self.getVideoModeByIndex(sizeIndex)
            if not self.__monitorChanged and (videoMode != self.__videoMode or self.isVideoWindowed):
                BigWorld.changeVideoMode(videoMode, False)
            windowSize = self.getWindowSizeByIndex(sizeIndex)
            self.__lastIsWindowed = False
            self.__lastFullscreenSize = (windowSize[0], windowSize[1])
        else:
            if not self.__monitorChanged and not self.isVideoWindowed:
                BigWorld.changeVideoMode(self.getVideoModeByIndex(sizeIndex), True)
            windowSize = self.getWindowSizeByIndex(sizeIndex)
            oldResolution = BigWorld.wg_getCurrentResolution(True)
            if windowSize is not None and (oldResolution[0] != windowSize[0] or oldResolution[1] != windowSize[1]):
                BigWorld.resizeWindow(windowSize[0], windowSize[1])
            self.__lastIsWindowed = True
            self.__lastWindowedSize = (windowSize[0], windowSize[1])
        return

    def onSavePreferencesXml(self, root):
        if not self.__monitorChanged:
            return
        else:
            devPref = root['devicePreferences']
            devPref.writeBool('windowed', self.__lastIsWindowed)
            if self.__lastFullscreenSize is not None:
                devPref.writeInt('fullscreenWidth', self.__lastFullscreenSize[0])
                devPref.writeInt('fullscreenHeight', self.__lastFullscreenSize[1])
            if self.__lastWindowedSize is not None:
                devPref.writeInt('windowedWidth', self.__lastWindowedSize[0])
                devPref.writeInt('windowedHeight', self.__lastWindowedSize[1])
            return


g_graficsResolutions = GraphicsResolutions()
