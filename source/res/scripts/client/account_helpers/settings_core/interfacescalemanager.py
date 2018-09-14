# Embedded file name: scripts/client/account_helpers/settings_core/InterfaceScaleManager.py
import weakref
import Event
import BigWorld
from gui.shared.utils import graphics
from gui import g_guiResetters
from account_helpers.settings_core import settings_constants
from ConnectionManager import connectionManager
from gui.shared.utils.graphics import g_monitorSettings

class InterfaceScaleManager(object):
    onScaleChanged = Event.Event()

    def __init__(self, settingsCore):
        self.proxy = weakref.proxy(settingsCore)
        self.__index = None
        self.__scaleValue = None
        return

    def init(self):
        g_guiResetters.add(self.scaleChanged)
        connectionManager.onConnected += self.scaleChanged
        connectionManager.onDisconnected += self.scaleChanged
        self.proxy.onSettingsChanged += self.onSettingsChanged
        self.scaleChanged()

    def fini(self):
        connectionManager.onDisconnected -= self.scaleChanged
        connectionManager.onConnected -= self.scaleChanged
        self.proxy.onSettingsChanged -= self.onSettingsChanged
        g_guiResetters.discard(self.scaleChanged)

    def get(self):
        return self.__scaleValue

    def getIndex(self):
        return self.__index

    def onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.INTERFACE_SCALE in diff:
            self.__index = diff[settings_constants.GRAPHICS.INTERFACE_SCALE]
            self.__scaleValue = self.getScaleByIndex(self.__index)
            self.onScaleChanged(self.__scaleValue)

    def scaleChanged(self):
        self.__index = self.proxy.getSetting(settings_constants.GRAPHICS.INTERFACE_SCALE)
        self.__scaleValue = self.getScaleByIndex(self.__index)
        self.onScaleChanged(self.__scaleValue)

    def getScaleOptions(self):
        options = self._getOptions()
        currMonitor = g_monitorSettings.activeMonitor
        if self.proxy.getSetting(settings_constants.GRAPHICS.FULLSCREEN):
            resolutionInd = self.proxy.getSetting(settings_constants.GRAPHICS.RESOLUTION)
            return options[1][currMonitor][resolutionInd]
        else:
            return options[0][currMonitor][self.proxy.getSetting(settings_constants.GRAPHICS.WINDOW_SIZE)]

    def getScaleByIndex(self, ind, powerOfTwo = True):
        scaleLength = len(self.getScaleOptions())
        if powerOfTwo:
            if ind == 0:
                return 2.0 ** (scaleLength - 2)
            else:
                return 2.0 ** (ind - 1)
        else:
            if ind == 0:
                return scaleLength - 1
            return ind

    def _getOptions(self):
        return [self.__getScales(graphics.getSuitableWindowSizes(), BigWorld.wg_getCurrentResolution(True)), self.__getScales(graphics.getSuitableVideoModes())]

    def __getScales(self, modesVariety, additionalSize = None):
        result = []
        for i in xrange(len(modesVariety)):
            modes = sorted(set([ (mode.width, mode.height) for mode in modesVariety[i] ]))
            if additionalSize is not None:
                modes.append(additionalSize[0:2])
            result.append(map(graphics.getInterfaceScalesList, modes))

        return result
