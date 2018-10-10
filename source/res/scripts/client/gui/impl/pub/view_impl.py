# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/view_impl.py
from frameworks.wulf import View, ViewEvent, Window
from gui.impl.gen.resources import R
from gui.impl.pub import ContextMenuWindow, ContextMenuContent, PopOverWindow
from gui.impl.pub import SimpleToolTipWindow, ToolTipWindow
from gui.impl.pub.tooltip_window import AdvancedToolTipWindow
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException

class ViewImpl(View):
    __slots__ = ()
    gui = dependency.descriptor(IGuiLoader)

    def createToolTipContent(self, event, contentID):
        return None

    def createPopOverContent(self, event):
        return None

    def createContextMenuContent(self, event):
        return None

    def createToolTip(self, event):
        window = None
        if event.contentID == R.views.simpleTooltipContent:
            window = SimpleToolTipWindow(event, self.getParentWindow())
        elif event.contentID == R.views.advandcedTooltipContent:
            normalContent = event.getArgument('normalContent')
            advancedContent = event.getArgument('advancedContent')
            window = AdvancedToolTipWindow(event, self.getParentWindow(), self.createToolTipContent(event, normalContent), self.createToolTipContent(event, advancedContent))
        else:
            content = self.createToolTipContent(event, 0)
            if content is not None:
                window = ToolTipWindow(event, content, self.getParentWindow())
        if window is not None:
            window.load()
        return window

    def createPopOver(self, event):
        content = self.createPopOverContent(event)
        window = None
        if content is not None:
            if not isinstance(content, PopOverViewImpl):
                raise SoftException('PopOver content should be derived from PopOverViewImpl.')
            window = PopOverWindow(event, content, self.getParentWindow())
            window.load()
        return window

    def createContextMenu(self, event):
        content = self.createContextMenuContent(event)
        window = None
        if content is not None:
            if not isinstance(content, ContextMenuContent):
                raise SoftException('Context menu content should be derived from ContextMenuContent.')
            window = ContextMenuWindow(event, content, self.getParentWindow())
            window.load()
        return window


class PopOverViewImpl(ViewImpl):
    __slots__ = ()

    @property
    def isCloseBtnVisible(self):
        return True
