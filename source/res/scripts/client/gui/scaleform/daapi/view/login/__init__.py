# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/__init__.py
from gui import GUI_SETTINGS
from gui.app_loader.settings import APP_NAME_SPACE
from gui.shared import EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, GroupedViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared.events import LoginEventEx, LoginCreateEvent

def getViewSettings():
    from gui.Scaleform.daapi.view.login.EULA import EULADlg
    from gui.Scaleform.daapi.view.login.IntroPage import IntroPage
    from gui.Scaleform.daapi.view.login.LegalInfoWindow import LegalInfoWindow
    from gui.Scaleform.daapi.view.login.LoginQueue import LoginQueue
    from gui.Scaleform.daapi.view.login.RssNewsFeed import RssNewsFeed
    if GUI_SETTINGS.socialNetworkLogin['enabled']:
        from SocialLoginView import SocialLoginView as LoginView
    else:
        from LoginView import LoginView
    return (ViewSettings(VIEW_ALIAS.INTRO_VIDEO, IntroPage, 'introPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.LOGIN, LoginView, 'login.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EULA, EULADlg, 'EULADlg.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.EULA_FULL, EULADlg, 'EULAFullDlg.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.LOGIN_QUEUE, LoginQueue, 'LoginQueueWindow.swf', ViewTypes.TOP_WINDOW, '', None, ScopeTemplates.DEFAULT_SCOPE),
     GroupedViewSettings(VIEW_ALIAS.LEGAL_INFO_WINDOW, LegalInfoWindow, 'legalInfoWindow.swf', ViewTypes.WINDOW, 'legalInfoWindow', None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(VIEW_ALIAS.RSS_NEWS_FEED, RssNewsFeed, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (LoginPackageBusinessHandler(),)


class LoginPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((VIEW_ALIAS.EULA, self.loadViewByCtxEvent),
         (VIEW_ALIAS.EULA_FULL, self.loadViewByCtxEvent),
         (VIEW_ALIAS.INTRO_VIDEO, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LEGAL_INFO_WINDOW, self.loadViewByCtxEvent),
         (VIEW_ALIAS.LOGIN, self.loadViewByCtxEvent),
         (LoginEventEx.SET_LOGIN_QUEUE, self.__showLoginQueue),
         (LoginEventEx.SET_AUTO_LOGIN, self.__showLoginQueue),
         (LoginCreateEvent.CREATE_ACC, self.__createAccount))
        super(LoginPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)

    def __showLoginQueue(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.LOGIN_QUEUE, event.waitingOpen, event.msg, event.waitingClose, event.showAutoLoginBtn)

    def __createAccount(self, event):
        self.loadViewWithGenName(VIEW_ALIAS.LOGIN_CREATE_AN_ACC, event.title, event.message, event.submit)
