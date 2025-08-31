# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/settings_core/InterfaceScaleManager.py
import weakref
import typing
import Event
import BigWorld
from account_helpers.settings_core.options import InterfaceScaleSetting
from gui.shared.utils import graphics
from gui import g_guiResetters
from account_helpers.settings_core import settings_constants
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
if typing.TYPE_CHECKING:
    from typing import Tuple

class InterfaceScaleManager(object):
    connectionMgr = dependency.descriptor(IConnectionManager)
    onScaleChanged = Event.Event()
    onScaleExactlyChanged = Event.Event()

    def __init__(self, settingsCore):
        self.proxy = weakref.proxy(settingsCore)
        self.__scaleValue = 0.0

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

    def onSettingsChanged(self, diff):
        if settings_constants.GRAPHICS.INTERFACE_SCALE in diff:
            index = int(diff[settings_constants.GRAPHICS.INTERFACE_SCALE])
            options = self.getScaleOptions()
            if index == InterfaceScaleSetting.AUTO_SCALE or index >= len(options):
                index = -1
            self.changeScale(options[index])

    def scaleChanged(self):
        scale = self.proxy.getSetting(settings_constants.GRAPHICS.INTERFACE_SCALE)
        self.changeScale(scale)

    def changeScale(self, scale):
        prevScaleValue = self.__scaleValue
        self.__scaleValue = scale
        self.onScaleChanged(self.__scaleValue)
        graphics.onInterfaceScaleChanged(self.__scaleValue)
        if prevScaleValue != self.__scaleValue:
            self.onScaleExactlyChanged(self.__scaleValue)

    @staticmethod
    def getScaleOptions():
        return graphics.getInterfaceScalesList(BigWorld.screenSize())
