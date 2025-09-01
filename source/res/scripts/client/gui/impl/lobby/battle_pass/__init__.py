# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_pass/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getStateMachineRegistrators():
    from gui.impl.lobby.battle_pass.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.impl.lobby.battle_pass.main_view import BattlePassWindow
    from gui.impl.lobby.battle_pass.battle_pass_browser_view import BattlePassBrowserView
    from gui.impl.lobby.battle_pass.battle_pass_video_browser_view import BattlePassVideoBrowserView
    return (ViewSettings(VIEW_ALIAS.BATTLE_PASS, BattlePassWindow, '', WindowLayer.SUB_VIEW, VIEW_ALIAS.BATTLE_PASS, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(VIEW_ALIAS.BATTLE_PASS_BROWSER, BattlePassBrowserView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.BATTLE_PASS_BROWSER, ScopeTemplates.LOBBY_TOP_SUB_SCOPE), ViewSettings(VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER, BattlePassVideoBrowserView, 'browserScreen.swf', WindowLayer.FULLSCREEN_WINDOW, VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER, ScopeTemplates.LOBBY_TOP_SUB_SCOPE))


def getBusinessHandlers():
    return (BattlePassPackageBusinessHandler(),)


class BattlePassPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.BATTLE_PASS, self.loadViewByCtxEvent), (VIEW_ALIAS.BATTLE_PASS_BROWSER, self.loadViewByCtxEvent), (VIEW_ALIAS.BATTLE_PASS_VIDEO_BROWSER, self.loadViewByCtxEvent))
        super(BattlePassPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
