# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gui_loader.py
from __future__ import absolute_import
import typing
from frameworks.wulf import GuiApplication
from gui.impl.gui_factories import GuiEntitiesFactories
from gui.impl.optimization_manager import GraphicsOptimizationManager
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from frameworks.wulf.tutorial import Tutorial
    from frameworks.wulf.ui_logger import UILogger

class GuiLoader(IGuiLoader):

    def __init__(self):
        super(GuiLoader, self).__init__()
        self.__gui = GuiApplication.getInstance()
        self.__entitiesFactory = GuiEntitiesFactories()
        self.__graphicsOptimizationManager = GraphicsOptimizationManager()

    @property
    def resourceManager(self):
        return self.__gui.resourceManager

    @property
    def windowsManager(self):
        return self.__gui.windowsManager

    @property
    def layoutManager(self):
        return self.__gui.layoutManager

    @property
    def systemLocale(self):
        return self.__gui.systemLocale

    @property
    def formatters(self):
        return self.__gui.formatters

    @property
    def tutorial(self):
        return self.__gui.tutorial

    @property
    def uiLogger(self):
        return self.__gui.uiLogger

    @property
    def scale(self):
        return self.__gui.scale

    @property
    def entitiesFactory(self):
        return self.__entitiesFactory

    def init(self):
        self.__gui.init()
        self.__graphicsOptimizationManager.init(self.__gui.windowsManager, self.__gui.scale)

    def fini(self):
        self.__gui.destroy()
        self.__graphicsOptimizationManager.fini()
