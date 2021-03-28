# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gui_loader.py
import typing
from frameworks.wulf import GuiApplication
from skeletons.gui.impl import IGuiLoader
if typing.TYPE_CHECKING:
    from frameworks.wulf import ViewModel
    from frameworks.wulf.tutorial import Tutorial
    from frameworks.wulf.ui_logger import UILogger

class GuiLoader(IGuiLoader):
    __slots__ = ('__gui',)

    def __init__(self):
        super(GuiLoader, self).__init__()
        self.__gui = GuiApplication()

    @property
    def resourceManager(self):
        return self.__gui.resourceManager

    @property
    def windowsManager(self):
        return self.__gui.windowsManager

    @property
    def systemLocale(self):
        return self.__gui.systemLocale

    @property
    def tutorial(self):
        return self.__gui.tutorial

    @property
    def uiLogger(self):
        return self.__gui.uiLogger

    def init(self, tutorialModel, uiLoggerModel):
        self.__gui.init(tutorialModel, uiLoggerModel)

    def fini(self):
        self.__gui.destroy()
