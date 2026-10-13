# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/wulf/gui_application.py
from __future__ import absolute_import
import typing
from helpers import time_utils
from .formatters import Formatters
from .py_object_wrappers import PyGuiApplication
from .resource_manager import ResourceManager
from .tutorial import Tutorial
from .ui_logger import UILogger
from .view.layout_manager import LayoutManager
from .windows_system.windows_manager import WindowsManager
if typing.TYPE_CHECKING:
    from typing import Callable

class GuiApplication(object):
    __instance = None

    def __init__(self):
        super(GuiApplication, self).__init__()
        self.__impl = None
        self.__windowsManager = None
        self.__layoutManager = None
        self.__resourceManager = None
        self.__formatters = None
        self.__tutorial = None
        self.__uiLogger = None
        return

    @classmethod
    def getInstance(cls):
        if cls.__instance is None:
            cls.__instance = cls()
            cls.__instance.init()
        return cls.__instance

    @property
    def windowsManager(self):
        return self.__windowsManager

    @property
    def layoutManager(self):
        return self.__layoutManager

    @property
    def resourceManager(self):
        return self.__resourceManager

    @property
    def systemLocale(self):
        return self.__formatters

    @property
    def formatters(self):
        return self.__formatters

    @property
    def tutorial(self):
        if self.__tutorial is None:
            from gui.impl.gen.view_models.common.tutorial.tutorial_model import TutorialModel
            self.__tutorial = Tutorial.create(self.__impl.tutorial, TutorialModel())
        return self.__tutorial

    @property
    def uiLogger(self):
        if self.__uiLogger is None:
            from gui.impl.gen.view_models.common.ui_logger_model import UiLoggerModel
            self.__uiLogger = UILogger.create(self.__impl.uiLogger, UiLoggerModel())
        return self.__uiLogger

    @property
    def scale(self):
        return self.__impl.scale

    def init(self):
        if self.__impl is not None:
            return
        else:
            self.__impl = PyGuiApplication()
            self.__impl.initialize()
            self.__resourceManager = ResourceManager.create(self.__impl.resourceManager)
            self.__windowsManager = WindowsManager.create(self.__impl.windowsManager)
            self.__layoutManager = LayoutManager.create(self.__impl.layoutManager)
            self.__formatters = Formatters.create(self.__impl.formatters)
            self._setServerTimeCallback(time_utils.getServerUTCTime)
            return

    def destroy(self):
        if self.__resourceManager is not None:
            self.__resourceManager.destroy()
            self.__resourceManager = None
        if self.__windowsManager is not None:
            self.__windowsManager.destroy()
            self.__windowsManager = None
        if self.__layoutManager is not None:
            self.__layoutManager.destroy()
            self.__layoutManager = None
        if self.__formatters is not None:
            self.__formatters.destroy()
            self.__formatters = None
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

    def _setServerTimeCallback(self, callback):
        self.__impl.setServerTimeCallback(callback)
