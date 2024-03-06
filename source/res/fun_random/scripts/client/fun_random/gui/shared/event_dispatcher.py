# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/event_dispatcher.py
from frameworks.wulf import WindowLayer
from gui.impl.gen import R
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams, GuiImplViewLoadParams
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.shared import events, g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView, showModeSelectorWindow
from helpers import dependency
from skeletons.gui.impl import IGuiLoader

def showFunRandomPrimeTimeWindow(subModeID):
    ctx = {'subModeID': subModeID}
    event = events.LoadViewEvent(SFViewLoadParams(FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME), ctx=ctx)
    g_eventBus.handleEvent(event, EVENT_BUS_SCOPE.LOBBY)


def showFunRandomInfoPage(infoPageUrl):
    showBrowserOverlayView(infoPageUrl, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


def showFunRandomSubSelector(parent=None):
    from fun_random.gui.impl.lobby.mode_selector.fun_sub_selector_view import FunModeSubSelectorView
    guiLoader = dependency.instance(IGuiLoader)
    layoutID = R.views.fun_random.lobby.feature.FunRandomModeSubSelector()
    if guiLoader.windowsManager.getViewByLayoutID(layoutID) is not None:
        return
    else:
        if parent is None:
            modeSelectorView = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.mode_selector.ModeSelectorView())
            parent = modeSelectorView.getParentWindow()
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID, FunModeSubSelectorView, ScopeTemplates.LOBBY_TOP_SUB_SCOPE, parent=parent)), scope=EVENT_BUS_SCOPE.LOBBY)
        return


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showFunRandomProgressionWindow(uiLoader=None):
    contentResId = R.views.fun_random.lobby.feature.FunRandomProgression()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        from fun_random.gui.impl.lobby.feature.fun_random_progression_view import FunRandomProgressionView
        params = GuiImplViewLoadParams(contentResId, FunRandomProgressionView, ScopeTemplates.LOBBY_SUB_SCOPE)
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(params), scope=EVENT_BUS_SCOPE.LOBBY)
    return


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showFunRandomModeSubSelectorWindow(uiLoader=None):
    contentResId = R.views.lobby.mode_selector.ModeSelectorView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        showModeSelectorWindow(subSelectorCallback=showFunRandomSubSelector)
    else:
        showFunRandomSubSelector()
    return
