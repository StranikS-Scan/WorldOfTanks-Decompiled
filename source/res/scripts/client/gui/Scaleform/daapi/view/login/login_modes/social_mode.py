# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/social_mode.py
from base_mode import BaseMode, INVALID_FIELDS
from connection_mgr import LOGIN_STATUS
from gui import makeHtmlString
from gui.Scaleform.Waiting import Waiting
from gui.login.social_networks import SOCIAL_NETWORKS
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.connection_mgr import IConnectionManager
SOCIAL_NETWORK_TO_DOMAIN_MAPPING = {SOCIAL_NETWORKS.FACEBOOK: 'https://fb.com',
 SOCIAL_NETWORKS.GOOGLE: 'https://plus.google.com',
 SOCIAL_NETWORKS.WGNI: 'https://wargaming.net',
 SOCIAL_NETWORKS.VKONTAKTE: 'https://vk.com',
 SOCIAL_NETWORKS.YAHOO: 'https://yahoo.com',
 SOCIAL_NETWORKS.NAVER: 'http://naver.com',
 SOCIAL_NETWORKS.TWITTER: 'https://twitter.com',
 SOCIAL_NETWORKS.ODNOKLASSNIKI: 'https://ok.ru'}

class SocialMode(BaseMode):
    _connectionMgr = dependency.descriptor(IConnectionManager)

    @property
    def login(self):
        return self._fallbackMode.login

    @property
    def rememberUser(self):
        return self._fallbackMode.rememberUser

    @property
    def password(self):
        return self._fallbackMode.password

    @property
    def rememberPassVisible(self):
        return self._fallbackMode.rememberPassVisible

    def init(self):
        self._connectionMgr.onRejected += self.__onLoginRejected
        self._fallbackMode.init()

    def destroy(self):
        self._connectionMgr.onRejected -= self.__onLoginRejected
        self._fallbackMode.destroy()
        super(SocialMode, self).destroy()

    def isToken2(self):
        return self._fallbackMode.isToken2()

    def resetToken(self):
        self._fallbackMode.resetToken()

    def setRememberPassword(self, *args):
        self._fallbackMode.setRememberPassword(*args)

    def doLogin(self, *args):
        self._fallbackMode.doLogin(*args)

    def doSocialLogin(self, socialNetworkName, serverName, isRegistration):
        if self._loginManager.initiateSocialLogin(socialNetworkName, serverName, self.rememberUser, isRegistration=isRegistration):
            initLoginError = ''
        else:
            initLoginError = _ms('#menu:login/social/status/SYSTEM_ERROR')
        self._view.as_setErrorMessageS(initLoginError, INVALID_FIELDS.ALL_VALID)

    def updateForm(self):
        socialList = self._loginManager.getAvailableSocialNetworks()
        lastLoginType = self._loginManager.getPreference('login_type')
        if lastLoginType in socialList and self.rememberUser:
            self._view.as_showFilledLoginFormS({'haveToken': self.isToken2(),
             'userName': self._loginManager.getPreference('name'),
             'icoPath': makeHtmlString('html_templates:socialNetworkLogin', 'transparentLogo', {'socialNetwork': lastLoginType}),
             'socialId': lastLoginType})
        else:
            self._view.as_showSimpleFormS(True, self.__setSocialDataList(socialList))

    def changeAccount(self):
        logOutAccount = self._loginManager.getPreference('login_type')
        self._loginManager.clearPreferences()
        self._loginManager.writePreferences()
        self._view.as_setErrorMessageS(self.__getLogoutWarning(logOutAccount), INVALID_FIELDS.ALL_VALID)
        self._view.update()

    def __onLoginRejected(self, loginStatus, _):
        socialList = self._loginManager.getAvailableSocialNetworks()
        lastLoginType = self._loginManager.getPreference('login_type')
        if lastLoginType in socialList and (loginStatus == LOGIN_STATUS.SESSION_END or loginStatus == LOGIN_STATUS.LOGIN_REJECTED_INVALID_PASSWORD):
            Waiting.hide('login')
            self._loginManager.clearToken2Preference()
            self._view.update()
            self._view.as_setErrorMessageS(_ms('#menu:login/status/SOCIAL_SESSION_END'), INVALID_FIELDS.PWD_INVALID)

    def __setSocialDataList(self, socialList):
        socialDataList = []
        for socialId in socialList:
            socialDataList.append({'socialId': socialId,
             'tpHeader': self.__getTooltipHeader(socialId),
             'tpBody': self.__getTooltipBody(socialId)})

        return socialDataList

    def __getLogoutWarning(self, socialNetworkName):
        localizationString = '#menu:login/social/warning/SOCIAL_NETWORK_LOGOUT'
        formatter = {'userName': self._loginManager.getPreference('name'),
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
