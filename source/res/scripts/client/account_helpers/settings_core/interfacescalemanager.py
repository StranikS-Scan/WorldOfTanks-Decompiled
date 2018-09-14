# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/InterfaceScaleManager.py
import weakref
import Event
import BigWorld
from gui.shared.utils import graphics
from gui import g_guiResetters
from account_helpers.settings_core import settings_constants
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager

class InterfaceScaleManager(object):
    connectionMgr = dependency.descriptor(IConnectionManager)
    onScaleChanged = Event.Event()

    def __init__(self, settingsCore):
        self.proxy = weakref.proxy(settingsCore)
        self.__index = None
        self.__scaleValue = None
        return

    def init(self):
        g_guiResetters.add(self.scaleChanged)
        self.connectionMgr.onConnected += self.scaleChanged
        self.connectionMgr.onDisconnected += self.scaleChanged
        self.proxy.onSettingsChanged += self.onSettingsChanged
        self.scaleChanged()

    def fini(self):
        self.connectionMgr.onDisconnected -= self.scaleChanged
        self.connectionMgr.onConnected -= self.scaleChanged
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

    @staticmethod
    def getScaleOptions():
        """
        Return list of scales for the current resolution.
        This list does not depend on what is set in SettingsWindow.
        :return: list of scales, for example: ['auto', 'x1', ...]
        """
        return graphics.getInterfaceScalesList(BigWorld.screenSize())

    def getScaleByIndex(self, ind, powerOfTwo=True):
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
