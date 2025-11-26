# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/shared/event_dispatcher.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen import R
from gui.impl.pub.notification_commands import WindowNotificationCommand
from gui.shared.event_dispatcher import showBrowserOverlayView, showModeSelectorWindow
from helpers import dependency
from skeletons.gui.impl import IGuiLoader, INotificationWindowController

def showFunRandomPrimeTimeWindow(subModeID):
    from fun_random.gui.Scaleform.daapi.view.lobby.states import FunRandomPrimeTimeState
    FunRandomPrimeTimeState.goTo(ctx={'subModeID': subModeID})


def showFunRandomProgressionWindow():
    from fun_random.gui.impl.lobby.feature.states import FunRandomProgressionState
    FunRandomProgressionState.goTo()


def showFunRandomTierList(parent=None):
    from fun_random.gui.impl.lobby.feature.states import FunRandomTierListState
    FunRandomTierListState.goTo(parent=parent)


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showFunRandomBattleResults(arenaUniqueID, subModeImpl, uiLoader=None):
    from fun_random.gui.impl.lobby.feature.states import FunPostBattleResultsState
    from fun_random.gui.impl.lobby.feature.fun_random_battle_results_view import FunRandomBattleResultsView
    views = uiLoader.windowsManager.findViews(lambda v: isinstance(v, FunRandomBattleResultsView))
    if views and all((view.arenaUniqueID == arenaUniqueID for view in views)):
        return
    FunPostBattleResultsState.goTo(arenaUniqueID=arenaUniqueID, subModeImpl=subModeImpl)


def showFunRandomInfoPage(infoPageUrl):
    showBrowserOverlayView(infoPageUrl, VIEW_ALIAS.WEB_VIEW_TRANSPARENT, hiddenLayers=(WindowLayer.MARKER, WindowLayer.VIEW, WindowLayer.WINDOW))


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showFunRandomModeSubSelectorWindow(uiLoader=None):
    contentResId = R.views.lobby.mode_selector.ModeSelectorView()
    if uiLoader.windowsManager.getViewByLayoutID(contentResId) is None:
        showModeSelectorWindow(subSelectorCallback=showFunRandomSubSelector)
    else:
        showFunRandomSubSelector()
    return


@dependency.replace_none_kwargs(uiLoader=IGuiLoader)
def showFunRandomSubSelector(parent=None, uiLoader=None):
    from fun_random.gui.impl.lobby.mode_selector.states import FunRandomSubSelectorState
    contentResId = R.views.lobby.mode_selector.ModeSelectorView()
    parent = parent or uiLoader.windowsManager.getViewByLayoutID(contentResId).getParentWindow()
    FunRandomSubSelectorState.goTo(parent=parent)


@dependency.replace_none_kwargs(notificationMgr=INotificationWindowController)
def showFunRandomLootBoxAwardWindow(data, notificationMgr=None):
    from fun_random.gui.impl.lobby.feature.fun_random_rewards_view import FunRandomLootBoxAwardWindow
    notificationMgr.append(WindowNotificationCommand(FunRandomLootBoxAwardWindow(data)))
