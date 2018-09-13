# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/sf_settings.py
from gui.Scaleform.framework.managers.loaders import PackageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.events import ShowWindowEvent

class PRB_WINDOW_VIEW_ALIAS(object):
    SEND_INVITES_WINDOW = 'prb_windows/sendInvitesWindow'
    AUTO_INVITE_WINDOW = 'prb_windows/autoInviteWindow'
    SQUAD_WINDOW = 'prb_windows/squadWindow'
    BATTLE_SESSION_WINDOW = 'prb_windows/battleSessionWindow'
    BATTLE_SESSION_LIST = 'prb_windows/battleSessionList'
    COMPANY_WINDOW = 'prb_windows/companyWindow'
    COMPANIES_WINDOW = 'prb_windows/companiesWindow'


def getViewSettings():
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionList import BattleSessionList
    from gui.Scaleform.daapi.view.lobby.prb_windows.BattleSessionWindow import BattleSessionWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.CompaniesWindow import CompaniesWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.CompanyWindow import CompanyWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows.PrbSendInvitesWindow import PrbSendInvitesWindow
    from gui.Scaleform.daapi.view.lobby.prb_windows import invite_windows
    from gui.Scaleform.daapi.view.lobby.prb_windows.SquadWindow import SquadWindow
    return [GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.SEND_INVITES_WINDOW, PrbSendInvitesWindow, 'prbSendInvitesWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_SEND_INVITES_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.AUTO_INVITE_WINDOW, invite_windows.AutoInviteWindow, 'receivedInviteWindow.swf', ViewTypes.WINDOW, 'receivedInviteWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.SQUAD_WINDOW, SquadWindow, 'squadWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_SQUAD_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.COMPANY_WINDOW, CompanyWindow, 'companyWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_COMPANY_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.COMPANIES_WINDOW, CompaniesWindow, 'companiesListWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_COMPANIES_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.BATTLE_SESSION_WINDOW, BattleSessionWindow, 'battleSessionWindow.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_BATTLE_SESSION_WINDOW, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(PRB_WINDOW_VIEW_ALIAS.BATTLE_SESSION_LIST, BattleSessionList, 'battleSessionList.swf', ViewTypes.WINDOW, '', ShowWindowEvent.SHOW_BATTLE_SESSION_LIST, ScopeTemplates.DEFAULT_SCOPE)]


def getBusinessHandlers():
    return [PrbPackageBusinessHandler()]


class PrbPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = [(ShowWindowEvent.SHOW_SQUAD_WINDOW, self.__showSquadWindow),
         (ShowWindowEvent.SHOW_COMPANY_WINDOW, self.__showCompanyWindow),
         (ShowWindowEvent.SHOW_COMPANIES_WINDOW, self.__showCompaniesWindow),
         (ShowWindowEvent.SHOW_BATTLE_SESSION_WINDOW, self.__showBattleSessionWindow),
         (ShowWindowEvent.SHOW_BATTLE_SESSION_LIST, self.__showBattleSessionList),
         (ShowWindowEvent.SHOW_SEND_INVITES_WINDOW, self.__showSendInvitesWindow),
         (ShowWindowEvent.SHOW_AUTO_INVITE_WINDOW, self.__showAutoInviteWindow)]
        super(PrbPackageBusinessHandler, self).__init__(listeners, EVENT_BUS_SCOPE.LOBBY)

    def __showBattleSessionWindow(self, _):
        viewAlias = PRB_WINDOW_VIEW_ALIAS.BATTLE_SESSION_WINDOW
        self.app.loadView(viewAlias, viewAlias)

    def __showBattleSessionList(self, _):
        viewAlias = PRB_WINDOW_VIEW_ALIAS.BATTLE_SESSION_LIST
        self.app.loadView(viewAlias, viewAlias)

    def __showSquadWindow(self, event):
        alias = name = PRB_WINDOW_VIEW_ALIAS.SQUAD_WINDOW
        self.app.loadView(alias, name, event.ctx)

    def __showSendInvitesWindow(self, event):
        alias = name = PRB_WINDOW_VIEW_ALIAS.SEND_INVITES_WINDOW
        self.app.loadView(alias, name, event.ctx)

    def __showAutoInviteWindow(self, event):
        alias = PRB_WINDOW_VIEW_ALIAS.AUTO_INVITE_WINDOW
        name = 'autoInviteWindow_{0:n}'.format(event.ctx.get('prbID'))
        self.app.loadView(alias, name, event.ctx)

    def __showCompaniesWindow(self, _):
        alias = name = PRB_WINDOW_VIEW_ALIAS.COMPANIES_WINDOW
        self.app.loadView(alias, name)

    def __showCompanyWindow(self, event):
        alias = name = PRB_WINDOW_VIEW_ALIAS.COMPANY_WINDOW
        self.app.loadView(alias, name, event.ctx)
