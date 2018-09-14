# Embedded file name: scripts/client/gui/social_network_login/Bridge.py
import base64
import socket
from urllib import urlencode
import BigWorld
import Settings
import constants
from helpers import getLanguageCode
from helpers.i18n import makeString as _ms
from ConnectionManager import AUTH_METHODS
from DataServer import DataServer
from gui import GUI_SETTINGS, makeHtmlString

class _SOCIAL_NETWORKS():
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    WGNI = 'wgni'
    VKONTAKTE = 'vkontakte'
    YAHOO = 'yahoo'
    NAVER = 'naver'
    TWITTER = 'twitter'
    ODNOKLASSNIKI = 'odnoklassniki'


_SOCIAL_NETWORK_TO_DOMAIN_MAPPING = {_SOCIAL_NETWORKS.FACEBOOK: 'fb.com',
 _SOCIAL_NETWORKS.GOOGLE: 'plus.google.com',
 _SOCIAL_NETWORKS.WGNI: 'wargaming.net',
 _SOCIAL_NETWORKS.VKONTAKTE: 'vk.com',
 _SOCIAL_NETWORKS.YAHOO: 'yahoo.com',
 _SOCIAL_NETWORKS.NAVER: 'naver.com',
 _SOCIAL_NETWORKS.TWITTER: 'twitter.com',
 _SOCIAL_NETWORKS.ODNOKLASSNIKI: 'ok.ru'}

class Bridge(object):

    class __STATUS:
        OK = 0
        HTTP_SERVER_ERROR = 1
        WEB_BROWSER_ERROR = 2

    def __init__(self):
        self.__encryptToken = False
        self.__server = None
        self.__userName = None
        self.__token2 = None
        return

    def init(self, serverReceivedDataCallback, encryptToken):
        self.__readToken2FromPreferences()
        self.__readUserFromPreferences()
        self.__encryptToken = encryptToken
        self.__serverReceivedDataCallback = serverReceivedDataCallback

    def fini(self):
        self.__token2 = None
        self.__userName = None
        if self.__server is not None:
            self.__server.stop()
            self.__server.server_close()
            self.__server = None
        return

    @staticmethod
    def getLoginParams():
        return {'auth_method': AUTH_METHODS.TOKEN,
         'requested_for': 'wot',
         'ip': '127.0.0.1'}

    def initiateLogin(self, socialNetworkName, rememberMe, isRegistration = False):
        serverStatus = self.__STATUS.OK
        try:
            if self.__server is not None:
                self.__server.stop()
                self.__server.server_close()
            self.__server = DataServer('SocialNetworkLoginServer', self.__serverReceivedDataCallback, self.__encryptToken and not isRegistration)
            self.__server.start()
        except socket.error:
            if self.__server is not None:
                self.__server.stop()
                self.__server = None
            serverStatus = self.__STATUS.HTTP_SERVER_ERROR

        if serverStatus == self.__STATUS.OK:
            baseUrl = self.__getInitialLoginBaseURL(constants.IS_DEVELOPMENT, isRegistration=isRegistration)
            loginParams = self.__getInitialLoginParams(socialNetworkName, rememberMe, isRegistration=isRegistration)
            url = baseUrl + ('&' if isRegistration else '?') + urlencode(loginParams)
            if not BigWorld.wg_openWebBrowser(url):
                serverStatus = self.__STATUS.WEB_BROWSER_ERROR
        return serverStatus == self.__STATUS.OK

    @staticmethod
    def getAvailableSocialNetworks():
        socialNetworks = []
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.VKONTAKTE]:
            socialNetworks.append(_SOCIAL_NETWORKS.VKONTAKTE)
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.FACEBOOK]:
            socialNetworks.append(_SOCIAL_NETWORKS.FACEBOOK)
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.GOOGLE]:
            socialNetworks.append(_SOCIAL_NETWORKS.GOOGLE)
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.WGNI]:
            socialNetworks.append(_SOCIAL_NETWORKS.WGNI)
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.YAHOO]:
            socialNetworks.append(_SOCIAL_NETWORKS.YAHOO)
        if GUI_SETTINGS.socialNetworkLogin[_SOCIAL_NETWORKS.NAVER]:
            socialNetworks.append(_SOCIAL_NETWORKS.NAVER)
        return socialNetworks

    @staticmethod
    def getLogoutWarning(socialNetworkName):
        localizationString = '#menu:login/social/warning/SOCIAL_NETWORK_LOGOUT'
        formatter = {'userName': Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('user'),
         'socialNetworkLink': makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': socialNetworkName,
                               'socialNetworkOfficialName': _ms('#tooltips:login/social/' + socialNetworkName)})}
        if socialNetworkName != _SOCIAL_NETWORKS.WGNI:
            localizationString += '_BOTH'
            formatter['wargamingNetLink'] = makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': _SOCIAL_NETWORKS.WGNI,
             'socialNetworkOfficialName': _ms('#tooltips:login/social/' + _SOCIAL_NETWORKS.WGNI)})
        return makeHtmlString('html_templates:socialNetworkLogin', 'logoutWarning', {'warningMessage': _ms(localizationString) % formatter})

    @staticmethod
    def getTooltipHeader(socialNetworkName):
        if socialNetworkName == _SOCIAL_NETWORKS.WGNI:
            return _ms('#tooltips:login/bySocial/' + _SOCIAL_NETWORKS.WGNI + '/header')
        else:
            return _ms('#tooltips:login/bySocial/header')

    @staticmethod
    def getTooltipBody(socialNetworkName):
        if socialNetworkName == _SOCIAL_NETWORKS.WGNI:
            return _ms('#tooltips:login/bySocial/' + _SOCIAL_NETWORKS.WGNI + '/body')
        else:
            return _ms('#tooltips:login/bySocial/body') % {'social': _ms('#tooltips:login/social/' + socialNetworkName)}

    @staticmethod
    def getSocialNetworkURL(socialNetworkName):
        protocol = 'http'
        if socialNetworkName != _SOCIAL_NETWORKS.NAVER:
            protocol += 's'
        return protocol + '://' + _SOCIAL_NETWORK_TO_DOMAIN_MAPPING[socialNetworkName]

    def setCredentials(self, userName, token2):
        self.__userName = userName
        self.__token2 = token2

    def makeToken2LoginParams(self, previousLoginParams):
        if self.__token2 is None:
            return
        else:
            previousLoginParams['auth_method'] = AUTH_METHODS.TOKEN2
            previousLoginParams['login'] = self.__userName
            previousLoginParams['token2'] = self.__token2
            if 'token' in previousLoginParams:
                del previousLoginParams['token']
            if 'account_id' in previousLoginParams:
                del previousLoginParams['account_id']
            if 'ip' in previousLoginParams:
                del previousLoginParams['ip']
            if 'requested_for' in previousLoginParams:
                del previousLoginParams['requested_for']
            return

    def __getInitialLoginParams(self, socialNetworkName, rememberMe, isRegistration = False):
        params = {'game_port': self.__server.server_port,
         'remember': int(rememberMe)}
        if not isRegistration:
            params['game'] = 'wot'
        if socialNetworkName != _SOCIAL_NETWORKS.WGNI:
            params['external'] = socialNetworkName
        if self.__encryptToken and not isRegistration:
            params['token_secret'] = base64.b64encode(self.__server.tokenSecret)
        return params

    @staticmethod
    def __getInitialLoginBaseURL(isDevelopmentMode, isRegistration = False):
        if isRegistration:
            baseUrl = GUI_SETTINGS.registrationURL.replace('$LANGUAGE_CODE', getLanguageCode())
        else:
            baseUrl = GUI_SETTINGS.socialNetworkLogin['initialLoginURL']
        if isDevelopmentMode:
            from gui.development.mock.social_network_login import getServer as getWGNIServerMock
            if getWGNIServerMock() is not None:
                baseUrl = 'http://127.0.0.1:{0}/{1}'.format(getWGNIServerMock().server_port, '?dummy=1' if isRegistration else '')
        return baseUrl

    def __readToken2FromPreferences(self):
        token2FromPreferences = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('token2', '')
        if token2FromPreferences:
            self.__token2 = ':'.join(token2FromPreferences.split(':')[1:])

    def __readUserFromPreferences(self):
        self.__userName = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('user', 'UNKNOWN')


bridge = Bridge()
