# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/SocialLoginView.py
import BigWorld
from connection_mgr import LOGIN_STATUS
from gui import makeHtmlString
from gui.login.social_networks import SOCIAL_NETWORKS
from gui.Scaleform.Waiting import Waiting
from LoginView import LoginView, INVALID_FIELDS
from helpers.i18n import makeString as _ms
from predefined_hosts import AUTO_LOGIN_QUERY_URL
_SOCIAL_NETWORK_TO_DOMAIN_MAPPING = {SOCIAL_NETWORKS.FACEBOOK: 'https://fb.com',
 SOCIAL_NETWORKS.GOOGLE: 'https://plus.google.com',
 SOCIAL_NETWORKS.WGNI: 'https://wargaming.net',
 SOCIAL_NETWORKS.VKONTAKTE: 'https://vk.com',
 SOCIAL_NETWORKS.YAHOO: 'https://yahoo.com',
 SOCIAL_NETWORKS.NAVER: 'http://naver.com',
 SOCIAL_NETWORKS.TWITTER: 'https://twitter.com',
 SOCIAL_NETWORKS.ODNOKLASSNIKI: 'https://ok.ru'}

class SocialLoginView(LoginView):

    def __init__(self, ctx=None):
        LoginView.__init__(self, ctx=ctx)
        self.__userName = self.loginManager.getPreference('name')
        self.__lastLoginType = self.loginManager.getPreference('login_type')

    def changeAccount(self):
        logOutAccount = self.loginManager.getPreference('login_type')
        self.loginManager.clearPreferences()
        self.loginManager.writePreferences()
        self.__lastLoginType = self.loginManager.getPreference('login_type')
        self._setData()
        self._showForm()
        self.as_setErrorMessageS(self.__getLogoutWarning(logOutAccount), INVALID_FIELDS.ALL_VALID)

    def onRegister(self, host):
        self.__initiateSocialLogin(SOCIAL_NETWORKS.WGNI, host, True)

    def onLoginBySocial(self, socialNetworkName, serverName):
        self.__initiateSocialLogin(socialNetworkName, serverName, False)

    def onTextLinkClick(self, socialNetworkName):
        BigWorld.wg_openWebBrowser(_SOCIAL_NETWORK_TO_DOMAIN_MAPPING[socialNetworkName])

    def _populate(self):
        LoginView._populate(self)
        self.connectionMgr.onLoggedOn += self.__onLoggedOn

    def _dispose(self):
        self.connectionMgr.onLoggedOn -= self.__onLoggedOn
        LoginView._dispose(self)

    def _showForm(self):
        socialList = self.loginManager.getAvailableSocialNetworks()
        if self.__lastLoginType in socialList and self._rememberUser:
            self.as_showSocialFormS(bool(self.loginManager.getPreference('token2')), self.__userName, makeHtmlString('html_templates:socialNetworkLogin', 'transparentLogo', {'socialNetwork': self.__lastLoginType}), self.__lastLoginType)
        else:
            self.as_showSimpleFormS(True, self.__setSocialDataList(socialList))

    def _onLoginRejected(self, loginStatus, responseData):
        socialList = self.loginManager.getAvailableSocialNetworks()
        if self.__lastLoginType in socialList and (loginStatus == LOGIN_STATUS.SESSION_END or loginStatus == LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD):
            Waiting.hide('login')
            self.loginManager.clearToken2Preference()
            self._showForm()
            self.as_setErrorMessageS(_ms('#menu:login/status/SOCIAL_SESSION_END'), INVALID_FIELDS.PWD_INVALID)
            self._dropLoginQueue(loginStatus)
        else:
            super(SocialLoginView, self)._onLoginRejected(loginStatus, responseData)

    def __initiateSocialLogin(self, socialNetworkName, serverName, isRegistration):
        self._autoSearchVisited = serverName == AUTO_LOGIN_QUERY_URL
        if self.loginManager.initiateSocialLogin(socialNetworkName, serverName, self._rememberUser, isRegistration=isRegistration):
            initLoginError = ''
        else:
            initLoginError = _ms('#menu:login/social/status/SYSTEM_ERROR')
        self.as_setErrorMessageS(initLoginError, INVALID_FIELDS.ALL_VALID)

    def __onLoggedOn(self, *args):
        """Event handler that sets an actual last login type.
        
        Last login type should be set at the very end instead of beginning in order
        to handle cases like choosing wrong social network, or misclicking on social
        network and then typing wrong password using basic login.
        """
        self.__lastLoginType = self.loginManager.getPreference('login_type')

    def __setSocialDataList(self, socialList):
        socialDataList = []
        for socialId in socialList:
            socialDataList.append({'socialId': socialId,
             'tpHeader': self.__getTooltipHeader(socialId),
             'tpBody': self.__getTooltipBody(socialId)})

        return socialDataList

    def __getLogoutWarning(self, socialNetworkName):
        localizationString = '#menu:login/social/warning/SOCIAL_NETWORK_LOGOUT'
        formatter = {'userName': self.loginManager.getPreference('name'),
         'socialNetworkLink': makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': socialNetworkName,
                               'socialNetworkOfficialName': _ms('#tooltips:login/social/' + socialNetworkName)})}
        if socialNetworkName != SOCIAL_NETWORKS.WGNI:
            localizationString += '_BOTH'
            formatter['wargamingNetLink'] = makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': SOCIAL_NETWORKS.WGNI,
             'socialNetworkOfficialName': _ms('#tooltips:login/social/' + SOCIAL_NETWORKS.WGNI)})
        return makeHtmlString('html_templates:socialNetworkLogin', 'logoutWarning', {'warningMessage': _ms(localizationString) % formatter})

    @staticmethod
    def __getTooltipHeader(socialNetworkName):
        return _ms('#tooltips:login/bySocial/' + SOCIAL_NETWORKS.WGNI + '/header') if socialNetworkName == SOCIAL_NETWORKS.WGNI else _ms('#tooltips:login/bySocial/header')

    @staticmethod
    def __getTooltipBody(socialNetworkName):
        return _ms('#tooltips:login/bySocial/' + SOCIAL_NETWORKS.WGNI + '/body') if socialNetworkName == SOCIAL_NETWORKS.WGNI else _ms('#tooltips:login/bySocial/body') % {'social': _ms('#tooltips:login/social/' + socialNetworkName)}
