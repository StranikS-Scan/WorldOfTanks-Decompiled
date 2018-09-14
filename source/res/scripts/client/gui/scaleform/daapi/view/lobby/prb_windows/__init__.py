# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/__init__.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.CONTEXT_MENU_HANDLER_TYPE import CONTEXT_MENU_HANDLER_TYPE
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.Scaleform.managers.context_menu import ContextMenuManager
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.utils.functions import getViewName
ContextMenuManager.registerHandler(CONTEXT_MENU_HANDLER_TYPE.PREBATTLE_USER, 'gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleUserCMHandler', 'PrebattleUserCMHandler')

def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.prb_windows import invite_windows
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionList import BattleSessionList
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionWindow import BattleSessionWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.CompanyListView import CompanyListView
    from gui.Scaleform.daapi.view.lobby.prb_windows.CompanyMainWindow import CompanyMainWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.CompanyRoomView import CompanyRoomView
    from gui.Scaleform.daapi.view.lobby.SendInvitesWindow import SendInvitesWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.SquadPromoWindow import SquadPromoWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.SquadView import SquadView
    from gui.Scaleform.daapi.view.lobby.prb_windows.SquadWindow import SquadWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.SwitchPeripheryWindow import SwitchPeripheryWindow
    return (GroupedViewSettings(PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, SendInvitesWindow, 'sendInvitesWindow.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, invite_windows.AutoInviteWindow, 'receivedInviteWindow.swf', ViewTypes.WINDOW, 'receivedInviteWindow', None, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.SQUAD_WINDOW_PY, SquadWindow, 'squadWindow.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.SQUAD_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.COMPANY_WINDOW_PY, CompanyMainWindow, 'companyMainWindow.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.COMPANY_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, BattleSessionWindow, 'battleSessionWindow.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, BattleSessionList, 'battleSessionList.swf', ViewTypes.WINDOW, '', PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, ScopeTemplates.DEFAULT_SCOPE, True),
     GroupedViewSettings(VIEW_ALIAS.SQUAD_PROMO_WINDOW, SquadPromoWindow, 'squadPromoWindow.swf', ViewTypes.WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW, SwitchPeripheryWindow, 'switchPeripheryWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(PREBATTLE_ALIASES.SQUAD_VIEW_PY, SquadView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(PREBATTLE_ALIASES.COMPANY_LIST_VIEW_PY, CompanyListView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(PREBATTLE_ALIASES.COMPANY_ROOM_VIEW_PY, CompanyRoomView, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_PrbPackageBusinessHandler(),)


class _PrbPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((PREBATTLE_ALIASES.SQUAD_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.COMPANY_WINDOW_PY, self.__showCompanyMainWindow),
         (PREBATTLE_ALIASES.BATTLE_SESSION_ROOM_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.BATTLE_SESSION_LIST_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.SEND_INVITES_WINDOW_PY, self.__showPrebattleWindow),
         (PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, self.__showAutoInviteWindow),
         (VIEW_ALIAS.SQUAD_PROMO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.SWITCH_PERIPHERY_WINDOW, self.loadViewByCtxEvent))
        super(_PrbPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showPrebattleWindow(self, event):
        alias = name = event.eventType
        self.loadViewWithDefName(alias, name, event.ctx)

    def __showAutoInviteWindow(self, event):
        alias = PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY
        name = getViewName(PREBATTLE_ALIASES.AUTO_INVITE_WINDOW_PY, event.ctx.get('prbID'))
        self.loadViewWithDefName(alias, name, event.ctx)

    def __showCompanyMainWindow(self, event):
        alias = name = PREBATTLE_ALIASES.COMPANY_WINDOW_PY
        window = self.findViewByAlias(ViewTypes.WINDOW, alias)
        if window is not None:
            window.updateWindowState(event.ctx)
        else:
            self.loadViewWithDefName(alias, name, event.ctx if event else None)
        return
