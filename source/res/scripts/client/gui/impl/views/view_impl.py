# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/views/view_impl.py
from frameworks.wulf import View, ViewEvent, Window
from gui.impl.gen import R
from gui.impl.windows import ContextMenuWindow, ContextMenuContent, PopUpWindow
from gui.impl.windows import SimpleToolTipWindow, ToolTipWindow
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException

class ViewImpl(View):
    __slots__ = ()
    gui = dependency.descriptor(IGuiLoader)

    def createToolTipContent(self, event):
        return None

    def createPopUpContent(self, event):
        return None

    def createContextMenuContent(self, event):
        return None

    def createToolTip(self, event):
        if event.contentID == R.views.simpleTooltipContent:
            return SimpleToolTipWindow(event, self.getParentWindow())
        else:
            content = self.createToolTipContent(event)
            return ToolTipWindow(event, content, self.getParentWindow()) if content is not None else None

    def createPopUp(self, event):
        content = self.createPopUpContent(event)
        if content is not None:
            if not isinstance(content, PopupViewImpl):
                raise SoftException('PopUp content should be derived from PopupViewImpl.')
            return PopUpWindow(event, content, self.getParentWindow())
        else:
            return

    def createContextMenu(self, event):
        content = self.createContextMenuContent(event)
        if content is not None:
            if not isinstance(content, ContextMenuContent):
                raise SoftException('Context menu content should be derived from ContextMenuContent.')
            return ContextMenuWindow(event, content, self.getParentWindow())
        else:
            return


class PopupViewImpl(ViewImpl):
    __slots__ = ()

    @property
    def isCloseBtnVisible(self):
        return True
