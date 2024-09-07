# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/shared/event_dispatcher.py
from helpers import dependency
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.impl.gen import R
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import getParentWindow
from skeletons.gui.impl import IGuiLoader

@dependency.replace_none_kwargs(guiLoader=IGuiLoader)
def _getWinbackProgressionViewIfHas(guiLoader=None):
    return guiLoader.windowsManager.getViewByLayoutID(R.views.winback.ProgressionMainView())


def showProgressionView(activeTab=None):
    from winback.gui.impl.lobby.views.progression_main_view import ProgressionMainView
    from winback.gui.impl.gen.view_models.views.lobby.views.progression_main_view_model import MainViews
    if _getWinbackProgressionViewIfHas() is not None:
        return
    else:
        viewRes = R.views.winback.ProgressionMainView()
        view = ProgressionMainView
        if not activeTab:
            activeTab = MainViews.PROGRESSION
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(viewRes, view, scope=ScopeTemplates.LOBBY_SUB_SCOPE), ctx={'menuName': activeTab}), scope=EVENT_BUS_SCOPE.LOBBY)
        return


def showAwardsView(ctx):
    from winback.gui.impl.lobby.views.winback_reward_view import WinbackRewardWindow
    WinbackRewardWindow(ctx=ctx).load()
    progressionView = _getWinbackProgressionViewIfHas()
    if progressionView:
        progressionView.currentPresenter.setDeferredUpdate()


def showWinbackIntroView(parent=None):
    from winback.gui.impl.lobby.views.winback_intro_view import WinbackIntroViewWindow
    window = WinbackIntroViewWindow(parent=parent if parent is not None else getParentWindow())
    window.load()
    return


def showWinbackSelectRewardView(selectableBonusTokens=None):
    from winback.gui.impl.lobby.views.winback_selectable_reward_view import WinbackSelectableRewardWindow
    WinbackSelectableRewardWindow(selectableBonusTokens).load()
