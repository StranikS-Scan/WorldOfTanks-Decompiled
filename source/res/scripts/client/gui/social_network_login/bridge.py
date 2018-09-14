# Embedded file name: scripts/client/gui/social_network_login/Bridge.py
import base64
from helpers import i18n
from urllib import urlencode
import BigWorld
from ConnectionManager import AUTH_METHODS
from DataServer import DataServer
import Settings
import constants
from gui import GUI_SETTINGS, makeHtmlString

class _SOCIAL_NETWORKS:
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    WGNI = 'wgni'
    VKONTAKTE = 'vkontakte'
    YAHOO = 'yahoo'
    NAVER = 'naver'
    TWITTER = 'twitter'
    ODNOKLASSNIKI = 'odnoklassniki'


_SOCIAL_NETWORK_TO_DOMAIN_MAPPING = {_SOCIAL_NETWORKS.FACEBOOK: ('Facebook', 'fb.com'),
 _SOCIAL_NETWORKS.GOOGLE: ('Google+', 'plus.google.com'),
 _SOCIAL_NETWORKS.WGNI: ('Wargaming.net', 'wargaming.net'),
 _SOCIAL_NETWORKS.VKONTAKTE: (u'\u0412\u041a\u043e\u043d\u0442\u0430\u043a\u0442\u0435', 'vk.com'),
 _SOCIAL_NETWORKS.YAHOO: ('Yahoo!', 'yahoo.com'),
 _SOCIAL_NETWORKS.NAVER: ('NAVER', 'naver.com'),
 _SOCIAL_NETWORKS.TWITTER: ('Twitter', 'twitter.com'),
 _SOCIAL_NETWORKS.ODNOKLASSNIKI: (u'\u041e\u0434\u043d\u043e\u043a\u043b\u0430\u0441\u0441\u043d\u0438\u043a\u0438', 'ok.ru')}

class Bridge(object):

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
        self.__server = DataServer('SocialNetworkLoginServer', serverReceivedDataCallback, self.__encryptToken)
        self.__server.start()

    def fini(self):
        if self.__server is None:
            return
        else:
            self.__server.stop()
            self.__server = None
            self.__token2 = None
            self.__userName = None
            return

    @staticmethod
    def getLoginParams():
        return {'auth_method': AUTH_METHODS.TOKEN,
         'requested_for': 'wot',
         'ip': '127.0.0.1'}

    def initializeLogin(self, socialNetworkName, rememberMe):
        baseUrl = self.__getInitialLoginBaseURL(constants.IS_DEVELOPMENT)
        params = self.__getInitialLoginParams(socialNetworkName, rememberMe)
        BigWorld.wg_openWebBrowser(baseUrl + '?' + urlencode(params))

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
    def getLogoutWarning(socialNetworkName, logoutBoth = True):
        localizationString = '#menu:login/social/warning/SOCIAL_NETWORK_LOGOUT'
        formatter = {'userName': Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('user'),
         'socialNetworkLink': makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': socialNetworkName,
                               'socialNetworkOfficialName': _SOCIAL_NETWORK_TO_DOMAIN_MAPPING[socialNetworkName][0]})}
        if logoutBoth and socialNetworkName != _SOCIAL_NETWORKS.WGNI:
            localizationString += '_BOTH'
            formatter['wargamingNetLink'] = makeHtmlString('html_templates:socialNetworkLogin', 'socialNetworkLink', {'socialNetworkName': _SOCIAL_NETWORKS.WGNI,
             'socialNetworkOfficialName': _SOCIAL_NETWORK_TO_DOMAIN_MAPPING[_SOCIAL_NETWORKS.WGNI][0]})
        return makeHtmlString('html_templates:socialNetworkLogin', 'logoutWarning', {'warningMessage': i18n.makeString(localizationString) % formatter})

    @staticmethod
    def getSocialNetworkURL(socialNetworkName):
        protocol = 'http'
        if socialNetworkName != _SOCIAL_NETWORKS.NAVER:
            protocol += 's'
        return protocol + '://' + _SOCIAL_NETWORK_TO_DOMAIN_MAPPING[socialNetworkName][1]

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

    def __getInitialLoginParams(self, socialNetworkName, rememberMe):
        params = {'game': 'wot',
         'game_port': self.__server.server_port,
         'remember': int(rememberMe)}
        if socialNetworkName != _SOCIAL_NETWORKS.WGNI:
            params['external'] = socialNetworkName
        if self.__encryptToken:
            params['token_secret'] = base64.b64encode(self.__server.tokenSecret)
        return params

    @staticmethod
    def __getInitialLoginBaseURL(isDevelopmentMode):
        baseUrl = GUI_SETTINGS.socialNetworkLogin['initialLoginURL']
        if isDevelopmentMode:
            from gui.development.mock.social_network_login import getServer as getWGNIServerMock
            if getWGNIServerMock() is not None:
                baseUrl = 'http://127.0.0.1:{0}/'.format(getWGNIServerMock().server_port)
        return baseUrl

    def __readToken2FromPreferences(self):
        token2FromPreferences = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('token2', '')
        if token2FromPreferences:
            self.__token2 = ':'.join(token2FromPreferences.split(':')[1:])

    def __readUserFromPreferences(self):
        self.__userName = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO].readString('user', 'UNKNOWN')


bridge = Bridge()
