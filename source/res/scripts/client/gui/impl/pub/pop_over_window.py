# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/pop_over_window.py
import typing
from frameworks.wulf import WindowFlags, ViewFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.gen.view_models.windows.pop_over_window_model import PopOverWindowModel
from gui.impl.pub.window_impl import WindowImpl
from gui.impl.pub.window_view import WindowView

class PopOverWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, event, content, parent, layer=WindowLayer.UNDEFINED):
        super(PopOverWindow, self).__init__(wndFlags=WindowFlags.POP_OVER, decorator=WindowView(layoutID=event.decoratorID, flags=ViewFlags.POP_OVER_DECORATOR, viewModelClazz=PopOverWindowModel), content=content, parent=parent, areaID=R.areas.pop_over(), layer=layer)
        with self.popOverModel.transaction() as tx:
            tx.setBoundX(event.bbox.positionX)
            tx.setBoundY(event.bbox.positionY)
            tx.setBoundWidth(event.bbox.width)
            tx.setBoundHeight(event.bbox.height)
            tx.setDirectionType(event.direction)
            tx.setIsCloseBtnVisible(content.isCloseBtnVisible)

    @property
    def popOverModel(self):
        return super(PopOverWindow, self)._getDecoratorViewModel()
