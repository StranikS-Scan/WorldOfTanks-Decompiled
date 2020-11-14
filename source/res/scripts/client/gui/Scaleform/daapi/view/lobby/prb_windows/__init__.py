# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.prb_windows.squad_window import BattleRoyaleSquadWindow
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings, GroupedViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName

def getContextMenuHandlers():
    from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleUserCMHandler import PrebattleUserCMHandler
    return ((CONTEXT_MENU_HANDLER_TYPE.PREBATTLE_USER, PrebattleUserCMHandler),)


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.prb_windows import invite_windows
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionList import BattleSessionList
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionWindow import BattleSessionWindow
    from gui.Scaleform.daapi.view.lobby.SendInvitesWindow import SendInvitesWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.SquadPromoWindow import SquadPromoWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import SquadView
    from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import EventSquadView
    from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import EpicSquadView
    from gui.Scaleform.daapi.view.lobby.prb_windows.squad_view import BattleRoyaleSquadView
    from gui.Scaleform.daapi.view.lobby.prb_windows.squad_window import SquadWindow, EventSquadWindow, EpicSquadWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.SwitchPeripheryWindow import SwitchPeripheryWindow
    return (GroupedViewSettings(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, SendInvitesWindow, 'sendInvitesWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, invite_windows.AutoInviteWindow, 'receivedInviteWindow.swf', WindowLayer.WINDOW, 'receivedInviteWindow', None, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(PREBATTLE_ALIASES.SQUAD_WINDOW_PY, SquadWindow, 'squadWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.SQUAD_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.EVENT_SQUAD_WINDOW_PY, EventSquadWindow, 'EventSquadWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.EVENT_SQUAD_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.EPIC_SQUAD_WINDOW_PY, EpicSquadWindow, 'squadWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.EPIC_SQUAD_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.BATTLE_ROYALE_SQUAD_WINDOW_PY, BattleRoyaleSquadWindow, 'squadWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.BATTLE_ROYALE_SQUAD_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, BattleSessionWindow, 'battleSessionWindow.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, BattleSessionList, 'battleSessionList.swf', WindowLayer.WINDOW, '', PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True, isCentered=False),
     GroupedViewSettings(VIEW_ALIAS.SQUAD_PROMO_WINDOW, SquadPromoWindow, 'squadPromoWindow.swf', WindowLayer.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW, SwitchPeripheryWindow, 'switchPeripheryWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW_MODAL, SwitchPeripheryWindow, 'switchPeripheryWindow.swf', WindowLayer.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canDrag=False),
     ComponentSettings(PREBATTLE_ALIASES.SQUAD_VIEW_PY, SquadView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PREBATTLE_ALIASES.EVENT_SQUAD_VIEW_PY, EventSquadView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PREBATTLE_ALIASES.EPIC_SQUAD_VIEW_PY, EpicSquadView, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(PREBATTLE_ALIASES.BATTLE_ROYALE_SQUAD_VIEW_PY, BattleRoyaleSquadView, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_PrbPackageBusinessHandler(),)


class _PrbPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((PREBATTLE_ALIASES.SQUAD_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.EVENT_SQUAD_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.EPIC_SQUAD_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.BATTLE_ROYALE_SQUAD_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, self.__showAutoInviteWindow),
         (VIEW_ALIAS.SQUAD_PROMO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW, self.loadViewByCtxEvent))
        super(_PrbPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showPrebattleWindow(self, event):
        alias = name = event.alias
        self.loadViewWithDefName(alias, name, event.ctx)

    def __showAutoInviteWindow(self, event):
        alias = PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY
        name = getViewName(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, event.ctx.get('prbID'))
        self.loadViewWithDefName(alias, name, event.ctx)
