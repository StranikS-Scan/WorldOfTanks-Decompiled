# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/paragons_window_events.py
import adisp
import th_async
from frameworks.wulf import WindowStatus
from gui.Scaleform.Waiting import Waiting
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework import ScopeTemplates
from helpers import dependency
from BWUtil import AsyncReturn
from skeletons.gui.game_control import IParagonsRewardsShopController
from skeletons.gui.impl import IGuiLoader

def showParagonsNavigationView(parent=None, tabId=TabId.PROGRESS):
    from gui.impl.lobby.paragons.navigation_view import NavigationView
    g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.lobby.paragons.NavigationView(), NavigationView, ScopeTemplates.LOBBY_SUB_SCOPE), tabId=tabId), scope=EVENT_BUS_SCOPE.LOBBY)


def showChapterRewardsView(chapterID, parent=None):
    from gui.impl.lobby.paragons.chapter_rewards_view import ChapterRewardsWindow
    window = ChapterRewardsWindow(chapterID, parent=parent)
    window.load()


def showParagonsIntroView(parent=None, onCloseCallback=None):
    from gui.impl.lobby.paragons.intro_view import IntroViewWindow
    window = IntroViewWindow(parent, onCloseCallback)
    window.load()


def showParagonsResetBranchView(parent=None, branchID=0, closeCallback=None):
    from gui.impl.lobby.paragons.reset_branch_view import ResetBranchViewWindow
    if not branchID:
        return
    window = ResetBranchViewWindow(parent, branchID, closeCallback)
    window.load()


@adisp.adisp_process
@dependency.replace_none_kwargs(selectableRewardsCtrl=IParagonsRewardsShopController)
def _getProductsProcess(selectableRewardsCtrl=None, callback=None):
    res = yield selectableRewardsCtrl.getProducts()
    callback(res)


@th_async.th_async
@dependency.replace_none_kwargs(selectableRewardsCtrl=IParagonsRewardsShopController, guiLoader=IGuiLoader)
def showParagonsSelectRewardsWindow(chapterID, levelID, entitlementID, parent=None, selectableRewardsCtrl=None, guiLoader=None):
    from gui.impl.lobby.paragons.select_rewards_view import SelectRewardsViewWindow
    try:
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.paragons.SelectRewardsView())
        if view is not None:
            raise AsyncReturn(None)
        Waiting.show('paragons/loadSelector')
        yield th_async.await_callback(_getProductsProcess)(selectableRewardsCtrl=selectableRewardsCtrl)
        selectableRewardsCtrl.entitlements.update()
        if parent is not None and parent.windowStatus in (WindowStatus.DESTROYING, WindowStatus.DESTROYED):
            raise AsyncReturn(None)
        window = SelectRewardsViewWindow(chapterID=chapterID, levelID=levelID, entitlementID=entitlementID, parent=parent)
        window.load()
    finally:
        Waiting.hide('paragons/loadSelector')

    return
