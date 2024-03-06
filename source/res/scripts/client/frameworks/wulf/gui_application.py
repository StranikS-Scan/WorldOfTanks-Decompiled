# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/gui_application.py
import typing
from .py_object_wrappers import PyGuiApplication
from .system_locale import SystemLocale
from .resource_manager import ResourceManager
from .windows_system.windows_manager import WindowsManager
from .tutorial import Tutorial
from .ui_logger import UILogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel

class GuiApplication(object):
    __slots__ = ('__impl', '__windowsManager', '__resourceManager', '__systemLocale', '__tutorial', '__uiLogger')

    def __init__(self):
        super(GuiApplication, self).__init__()
        self.__impl = PyGuiApplication()
        self.__windowsManager = None
        self.__resourceManager = None
        self.__systemLocale = None
        self.__tutorial = None
        self.__uiLogger = None
        return

    @property
    def windowsManager(self):
        return self.__windowsManager

    @property
    def resourceManager(self):
        return self.__resourceManager

    @property
    def systemLocale(self):
        return self.__systemLocale

    @property
    def tutorial(self):
        return self.__tutorial

    @property
    def uiLogger(self):
        return self.__uiLogger

    @property
    def scale(self):
        return self.__impl.scale

    def init(self, tutorialModel, uiLoggerModel):
        self.__impl.initialize()
        self.__resourceManager = ResourceManager.create(self.__impl.resourceManager)
        self.__windowsManager = WindowsManager.create(self.__impl.windowsManager)
        self.__systemLocale = SystemLocale.create(self.__impl.systemLocale)
        self.__tutorial = Tutorial.create(self.__impl.tutorial, tutorialModel)
        self.__uiLogger = UILogger.create(self.__impl.uiLogger, uiLoggerModel)

    def destroy(self):
        if self.__resourceManager is not None:
            self.__resourceManager.destroy()
            self.__resourceManager = None
        if self.__windowsManager is not None:
            self.__windowsManager.destroy()
            self.__windowsManager = None
        if self.__systemLocale is not None:
            self.__systemLocale.destroy()
            self.__systemLocale = None
        if self.__tutorial is not None:
            self.__tutorial.destroy()
            self.__tutorial = None
        if self.__uiLogger is not None:
            self.__uiLogger.destroy()
            self.__uiLogger = None
        if self.__impl is not None:
            self.__impl.destroy()
            self.__impl = None
        return
