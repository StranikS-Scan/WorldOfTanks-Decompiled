# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/windows/popup_window.py
from frameworks.wulf import Window, WindowFlags
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.popup_window_model import PopupWindowModel
from gui.impl.windows.window_view import WindowView

class PopUpWindow(Window):
    __slots__ = ()

    def __init__(self, event, content, parent):
        super(PopUpWindow, self).__init__(wndFlags=WindowFlags.POP_UP, decorator=WindowView(layoutID=R.views.popupWindow, viewModelClazz=PopupWindowModel), content=content, parent=parent)
        self.popupModel.setBoundX(event.bbox.positionX)
        self.popupModel.setBoundY(event.bbox.positionY)
        self.popupModel.setBoundWidth(event.bbox.width)
        self.popupModel.setBoundHeight(event.bbox.height)
        self.popupModel.setFlowType(event.flow)
        self.popupModel.setIsCloseBtnVisible(content.isCloseBtnVisible)
        self.popupModel.onCloseBtnClicked += self.__onCloseBtnClicked

    @property
    def popupModel(self):
        return super(PopUpWindow, self)._getDecoratorViewModel()

    def _finalize(self):
        self.popupModel.onCloseBtnClicked -= self.__onCloseBtnClicked

    def __onCloseBtnClicked(self):
        self.destroy()
