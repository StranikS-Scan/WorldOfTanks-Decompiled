# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/customization/customization_window_events.py
import logging
from gui.impl.gen import R
from gui.shared.event_dispatcher import getParentWindow
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from skeletons.gui.impl import IGuiLoader
from helpers import dependency
_logger = logging.getLogger(__name__)

def showCustomizationMainView(ctx=None):
    from gui.impl.lobby.customization.customization_main_view import CustomizationMainView
    uiLoader = dependency.instance(IGuiLoader)
    layoutID = R.views.lobby.customization.CustomizationMainView()
    customizationMainView = uiLoader.windowsManager.getViewByLayoutID(layoutID)
    if customizationMainView is not None:
        return
    else:
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=layoutID, viewClass=CustomizationMainView, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx=ctx), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showFilterPopoverWindow(event, carouselDP, parent=None):
    from gui.impl.lobby.customization.popovers.customization_filter_popover_view import CustomizationFilterPopoverViewWindow
    window = CustomizationFilterPopoverViewWindow(event, parent=parent or getParentWindow(), carouselDP=carouselDP)
    window.load()
    return window


def showProgressiveItemsView(itemIntCD=None, customizationView=None):
    from gui.impl.lobby.customization.progressive_items_view.progressive_items_view import ProgressiveItemsWindow
    if customizationView is None:
        uiLoader = dependency.instance(IGuiLoader)
        layoutID = R.views.lobby.customization.CustomizationMainView()
        customizationView = uiLoader.windowsManager.getViewByLayoutID(layoutID)
    if customizationView is None:
        parent = None
        _logger.error('ProgressiveItemsView shall be created only from customization')
    else:
        parent = customizationView.getParentWindow()
    window = ProgressiveItemsWindow(customizationView, itemIntCD, parent)
    window.load()
    return
