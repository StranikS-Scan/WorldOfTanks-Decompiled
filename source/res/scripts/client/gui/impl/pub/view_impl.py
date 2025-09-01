# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/pub/view_impl.py
import logging
import typing
import json
from frameworks.wulf import View, ViewEvent, ViewModel, Window, WindowLayer, WindowStatus
from helpers import dependency
from helpers.events_handler import EventsHandler
from skeletons.gui.impl import IGuiLoader
from soft_exception import SoftException
from ..gen.resources import R
from .context_menu_window import ContextMenuContent, ContextMenuWindow
from .pop_over_window import PopOverWindow
from .tooltip_window import AdvancedToolTipWindow, SimpleToolTipWindow, ToolTipWindow
from .view_impl_helpers import createBackportContextMenuWindow, createParamTooltipWindow, createWulfTooltipWindow
TViewModel = typing.TypeVar('TViewModel', bound=ViewModel)
_logger = logging.getLogger(__name__)
_BACKPORT_POPOVER_DIRECTION_OVERRIDE = {1: 3,
 3: 0,
 0: 1}

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

    def prepareBackportTooltipArgs(self, args):
        return args

    def prepareBackportPopOverArgs(self, args):
        return args

    def createToolTip(self, event):
        window = None
        if event.contentID == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipContent() or event.contentID == R.views.common.tooltip_window.simple_tooltip_content.SimpleTooltipHtmlContent():
            window = SimpleToolTipWindow(event, self.getParentWindow())
        elif event.contentID == R.views.common.tooltip_window.advanced_tooltip_content.AdvandcedTooltipContent():
            window = self.__createAdvancedTooltipContentWindow(event, self.getParentWindow())
        elif event.contentID == R.aliases.common.tooltip.Backport():
            window = self.__createSpecialTooltipContentWindow(event, self.getParentWindow())
        elif event.contentID == R.aliases.common.tooltip.Wulf():
            window = createWulfTooltipWindow(event, self.getParentWindow())
        elif event.contentID == R.aliases.common.tooltip.Param():
            window = createParamTooltipWindow(event, self.getParentWindow())
        else:
            content = self.createToolTipContent(event, event.contentID)
            if content is not None:
                window = ToolTipWindow(event, content, self.getParentWindow())
        if window is not None and window.windowStatus == WindowStatus.CREATED:
            window.load()
        return window

    def createPopOver(self, event):
        window = None
        directionOverride = None
        if event.contentID in (R.views.common.pop_over_window.backport_pop_over.BackportPopOverContent(), R.aliases.common.popOver.Backport()):
            directionOverride = _BACKPORT_POPOVER_DIRECTION_OVERRIDE.get(event.direction, None)
        if event.contentID == R.aliases.common.popOver.Backport():
            content = self.__createBackportPopOverContent(event)
        else:
            content = self.createPopOverContent(event)
        if content is not None:
            if not isinstance(content, PopOverViewImpl):
                raise SoftException('PopOver content should be derived from PopOverViewImpl.')
            layer = self._getPopOverLayer()
            window = PopOverWindow(event, content, self.getParentWindow(), layer, directionOverride)
            window.load()
        return window

    def createContextMenu(self, event):
        if event.contentID == R.aliases.common.contextMenu.Backport():
            return createBackportContextMenuWindow(event, self.getParentWindow())
        else:
            content = self.createContextMenuContent(event)
            window = None
            if content is not None:
                if not isinstance(content, ContextMenuContent):
                    raise SoftException('Context menu content should be derived from ContextMenuContent.')
                window = ContextMenuWindow(event, content, self.getParentWindow())
                window.load()
                window.move(event.mouse.positionX, event.mouse.positionY)
            return window

    def _getPopOverLayer(self):
        layer = WindowLayer.UNDEFINED
        if self.getParentWindow() and self.getParentWindow().layer >= 0:
            layer = self.getParentWindow().layer
        return layer

    def __createSpecialTooltipContentWindow(self, event, parentWindow):
        from gui.impl.backport.backport_tooltip import createBackportTooltipContent
        tooltipId = event.getArgument('tooltipId')
        tooltipArgs = event.getArgument('tooltipArgs', None)
        if not tooltipId:
            _logger.error('SpecialTooltipContent. tooltipId is not specified')
            return
        else:
            args = json.loads(tooltipArgs)
            args = self.prepareBackportTooltipArgs(args)
            content = createBackportTooltipContent(specialAlias=tooltipId, specialArgs=args)
            if content is not None:
                window = ToolTipWindow(event, content, parentWindow)
                return window
            raise SoftException('Preparing of BackportTooltip with json args failed: backportTooltipContent is None or invalid.')
            return

    def __createAdvancedTooltipContentWindow(self, event, parentWindow):
        normalContent = int(event.getArgument('normalContent'))
        advancedContent = int(event.getArgument('advancedContent'))
        window = AdvancedToolTipWindow(event, parentWindow, self.createToolTipContent(event, normalContent), self.createToolTipContent(event, advancedContent))
        return window

    def __createBackportPopOverContent(self, event):
        from gui.impl.backport.backport_pop_over import BackportPopOverContent
        from gui.impl.backport.backport_pop_over import createPopOverData
        popoverId = event.getArgument('popoverId')
        popoverArgs = event.getArgument('popoverArgs', None)
        if not popoverId:
            _logger.error('PopOver. popoverId is not specified')
            return
        else:
            if popoverArgs:
                args = json.loads(popoverArgs)
            else:
                args = None
            args = self.prepareBackportPopOverArgs(args)
            content = BackportPopOverContent(createPopOverData(popoverId, args))
            return content


class PopOverViewImpl(ViewImpl):
    __slots__ = ()

    @property
    def isCloseBtnVisible(self):
        return True
