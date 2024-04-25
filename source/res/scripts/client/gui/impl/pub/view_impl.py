# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/view_impl.py
import typing
from frameworks.wulf import View, ViewEvent, ViewModel, Window, WindowLayer
from gui.impl.gen.resources import R
from gui.impl.pub.context_menu_window import ContextMenuContent, ContextMenuWindow
from gui.impl.pub.pop_over_window import PopOverWindow
from gui.impl.pub.tooltip_window import AdvancedToolTipWindow, SimpleToolTipWindow, ToolTipWindow
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
TViewModel = typing.TypeVar('TViewModel', bound=ViewModel)

class ViewImpl(View, EventsHandler, typing.Generic[TViewModel]):
    __slots__ = ()
    gui = dependency.descriptor(IGuiLoader)

    def _onLoading(self, *args, **kwargs):
        super(ViewImpl, self)._onLoading(*args, **kwargs)
        self._subscribe()

    def _finalize(self):
        self._unsubscribe()
        super(ViewImpl, self)._finalize()

    def createToolTipContent(self, event, contentID):
        return None

    def createPopOverContent(self, event):
        return None

    def createContextMenuContent(self, event):
        return None

    def createToolTip(self, event):
        window = None
        if event.contentID == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent() or event.contentID == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipHtmlContent():
            window = SimpleToolTipWindow(event, self.getParentWindow())
        elif event.contentID == R.views.common.tooltip_window.advanced_tooltip_content.AdvandcedTooltipContent():
            normalContent = int(event.getArgument('normalContent'))
            advancedContent = int(event.getArgument('advancedContent'))
            window = AdvancedToolTipWindow(event, self.getParentWindow(), self.createToolTipContent(event, normalContent), self.createToolTipContent(event, advancedContent))
        else:
            content = self.createToolTipContent(event, event.contentID)
            if content is not None:
                window = ToolTipWindow(event, content, self.getParentWindow())
        if window is not None:
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
        return window

    def createPopOver(self, event):
        content = self.createPopOverContent(event)
        window = None
        if content is not None:
            if not isinstance(content, PopOverViewImpl):
                raise SoftException('PopOver content should be derived from PopOverViewImpl.')
            layer = WindowLayer.UNDEFINED
            if self.getParentWindow() and self.getParentWindow().layer >= 0:
                layer = self.getParentWindow().layer
            window = PopOverWindow(event, content, self.getParentWindow(), layer)
            window.load()
        return window

    def getParentWindow(self):
        return super(ViewImpl, self).getParentWindow() or self.getInitialParentWindow()

    def createContextMenu(self, event):
        content = self.createContextMenuContent(event)
        window = None
        if content is not None:
            if not isinstance(content, ContextMenuContent):
                raise SoftException('Context menu content should be derived from ContextMenuContent.')
            window = ContextMenuWindow(event, content, self.getParentWindow())
            window.load()
            window.move(event.mouse.positionX, event.mouse.positionY)
        return window


class PopOverViewImpl(ViewImpl):
    __slots__ = ()

    @property
    def isCloseBtnVisible(self):
        return True
