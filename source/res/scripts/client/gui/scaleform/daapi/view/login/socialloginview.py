# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/SocialLoginView.py
import BigWorld
from gui import makeHtmlString
from gui.login import g_loginManager, SOCIAL_NETWORKS
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

    def __init__(self, ctx = None):
        LoginView.__init__(self, ctx=ctx)
        self.__userName = g_loginManager.getPreference('name')
        self.__lastLoginType = g_loginManager.getPreference('login_type')

    def changeAccount(self):
        logOutAccount = g_loginManager.getPreference('login_type')
        g_loginManager.clearPreferences()
        g_loginManager.writePreferences()
        self.__lastLoginType = g_loginManager.getPreference('login_type')
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

    def _dispose(self):
        LoginView._dispose(self)

    def _showForm(self):
        socialList = g_loginManager.getAvailableSocialNetworks()
        if self.__lastLoginType in socialList and self._rememberUser:
            self.as_showSocialFormS(len(g_loginManager.getPreference('token2')) != 0, self.__userName, makeHtmlString('html_templates:socialNetworkLogin', 'transparentLogo', {'socialNetwork': self.__lastLoginType}), self.__lastLoginType)
        else:
            self.as_showSimpleFormS(True, self.__setSocialDataList(socialList))

    def __initiateSocialLogin(self, socialNetworkName, serverName, isRegistration):
        self.__lastLoginType = socialNetworkName
        self._autoSearchVisited = serverName == AUTO_LOGIN_QUERY_URL
        if g_loginManager.initiateSocialLogin(socialNetworkName, serverName, self._rememberUser, isRegistration=isRegistration):
            initLoginError = ''
        else:
            initLoginError = _ms('#menu:login/social/status/SYSTEM_ERROR')
        self.as_setErrorMessageS(initLoginError, INVALID_FIELDS.ALL_VALID)

    def __setSocialDataList(self, socialList):
        socialDataList = []
        for socialId in socialList:
            socialDataList.append({'socialId': socialId,
             'tpHeader': self.__getTooltipHeader(socialId),
             'tpBody': self.__getTooltipBody(socialId)})

        return socialDataList

    @staticmethod
    def __getLogoutWarning(socialNetworkName):
        localizationString = '#menu:login/social/warning/SOCIAL_NETWORK_LOGOUT'
        formatter = {'userName': g_loginManager.getPreference('name'),
         'socialNetworkLink': makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': socialNetworkName,
                               'socialNetworkOfficialName': _ms('#tooltips:login/social/' + socialNetworkName)})}
        if socialNetworkName != SOCIAL_NETWORKS.WGNI:
            localizationString += '_BOTH'
            formatter['wargamingNetLink'] = makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': SOCIAL_NETWORKS.WGNI,
             'socialNetworkOfficialName': _ms('#tooltips:login/social/' + SOCIAL_NETWORKS.WGNI)})
        return makeHtmlString('html_templates:socialNetworkLogin', 'logoutWarning', {'warningMessage': _ms(localizationString) % formatter})

    @staticmethod
    def __getTooltipHeader(socialNetworkName):
        if socialNetworkName == SOCIAL_NETWORKS.WGNI:
            return _ms('#tooltips:login/bySocial/' + SOCIAL_NETWORKS.WGNI + '/header')
        else:
            return _ms('#tooltips:login/bySocial/header')

    @staticmethod
    def __getTooltipBody(socialNetworkName):
        if socialNetworkName == SOCIAL_NETWORKS.WGNI:
            return _ms('#tooltips:login/bySocial/' + SOCIAL_NETWORKS.WGNI + '/body')
        else:
            return _ms('#tooltips:login/bySocial/body') % {'social': _ms('#tooltips:login/social/' + socialNetworkName)}
