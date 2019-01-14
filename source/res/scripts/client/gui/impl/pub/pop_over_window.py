# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/pop_over_window.py
from frameworks.wulf import Window, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.pop_over_window_model import PopOverWindowModel
from gui.impl.pub.window_view import WindowView

class PopOverWindow(Window):
    __slots__ = ()

    def __init__(self, event, content, parent):
        super(PopOverWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, decorator=WindowView(layoutID=R.views.popOverWindow(), viewModelClazz=PopOverWindowModel), content=content, parent=parent)
        self.popOverModel.setBoundX(event.bbox.positionX)
        self.popOverModel.setBoundY(event.bbox.positionY)
        self.popOverModel.setBoundWidth(event.bbox.width)
        self.popOverModel.setBoundHeight(event.bbox.height)
        self.popOverModel.setDirectionType(event.direction)
        self.popOverModel.setIsCloseBtnVisible(content.isCloseBtnVisible)
        self.popOverModel.onCloseBtnClicked += self.__onCloseBtnClicked

    @property
    def popOverModel(self):
        return super(PopOverWindow, self)._getDecoratorViewModel()

    def _finalize(self):
        self.popOverModel.onCloseBtnClicked -= self.__onCloseBtnClicked

    def __onCloseBtnClicked(self):
        self.destroy()
