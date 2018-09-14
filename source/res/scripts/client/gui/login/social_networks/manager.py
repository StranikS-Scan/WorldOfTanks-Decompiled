# Embedded file name: scripts/client/gui/login/social_networks/Manager.py
import BigWorld
from gui import GUI_SETTINGS
from ConnectionManager import CONNECTION_METHOD
from gui.login.Manager import Manager as CredentialsLoginManager
from WebBridge import WebBridge

class SOCIAL_NETWORKS:
    FACEBOOK = 'facebook'
    GOOGLE = 'google'
    WGNI = 'wgni'
    VKONTAKTE = 'vkontakte'
    YAHOO = 'yahoo'
    NAVER = 'naver'
    TWITTER = 'twitter'
    ODNOKLASSNIKI = 'odnoklassniki'


class Manager(CredentialsLoginManager):

    def __init__(self):
        CredentialsLoginManager.__init__(self)
        self.__webBridge = None
        return

    def init(self):
        CredentialsLoginManager.init(self)
        self.__webBridge = WebBridge(self._preferences)

    def fini(self):
        CredentialsLoginManager.fini(self)
        self.__webBridge.fini()
        self.__webBridge = None
        return

    def initiateSocialLogin(self, socialNetworkName, serverName, rememberUser, isRegistration):
        self._preferences['session'] = BigWorld.wg_cpsalt(self._preferences['session'])
        self._preferences['remember_user'] = rememberUser
        self._preferences['login_type'] = socialNetworkName
        self._preferences['server_name'] = serverName
        loginParams = {'login': self._preferences['login'],
         'session': self._preferences['session'],
         'temporary': str(int(not rememberUser)),
         'auth_method': CONNECTION_METHOD.TOKEN,
         'requested_for': 'wot',
         'ip': '127.0.0.1'}
        return self.__webBridge.initiateLogin(loginParams, socialNetworkName != SOCIAL_NETWORKS.WGNI, isRegistration)

    @staticmethod
    def getAvailableSocialNetworks():
        socialNetworks = []
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.VKONTAKTE]:
            socialNetworks.append(SOCIAL_NETWORKS.VKONTAKTE)
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.FACEBOOK]:
            socialNetworks.append(SOCIAL_NETWORKS.FACEBOOK)
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.GOOGLE]:
            socialNetworks.append(SOCIAL_NETWORKS.GOOGLE)
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.WGNI]:
            socialNetworks.append(SOCIAL_NETWORKS.WGNI)
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.YAHOO]:
            socialNetworks.append(SOCIAL_NETWORKS.YAHOO)
        if GUI_SETTINGS.socialNetworkLogin[SOCIAL_NETWORKS.NAVER]:
            socialNetworks.append(SOCIAL_NETWORKS.NAVER)
        return socialNetworks
