# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gui_loader.py
from frameworks.wulf import GuiApplication
from skeletons.gui.impl import IGuiLoader

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

    def init(self):
        self.__gui.init()

    def fini(self):
        self.__gui.destroy()
