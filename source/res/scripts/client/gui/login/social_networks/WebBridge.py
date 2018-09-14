# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/login/social_networks/WebBridge.py
import base64
import socket
from urllib import urlencode, quote_plus
import BigWorld
from constants import HAS_DEV_RESOURCES
from Event import Event
from DataServer import ThreadedDataServer, EncryptingThreadedDataServer
from gui import GUI_SETTINGS
from gui.Scaleform.Waiting import Waiting
from helpers import dependency
from helpers import getLanguageCode
from skeletons.connection_mgr import IConnectionManager

class _STATUS:
    OK = 0
    HTTP_SERVER_ERROR = 1
    WEB_BROWSER_ERROR = 2


class WebBridge(object):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self, preferences):
        self.__dataServer = None
        self.__preferences = preferences
        self.__loginParams = None
        self.dataServerReceivedData = Event()
        self.connectionMgr.onConnected += self.__finiDataServer
        self.connectionMgr.onRejected += self.__finiDataServer
        self.connectionMgr.onDisconnected += self.__finiDataServer
        return

    def fini(self):
        self.__finiDataServer()
        self.connectionMgr.onConnected -= self.__finiDataServer
        self.connectionMgr.onRejected -= self.__finiDataServer
        self.connectionMgr.onDisconnected -= self.__finiDataServer
        if HAS_DEV_RESOURCES:
            from gui.development.mock.social_network_login import fini as finalizeWGNIServerMock
            finalizeWGNIServerMock()

    def initiateLogin(self, loginParams, isExternal, isRegistration):
        self.__loginParams = loginParams
        serverStatus = _STATUS.OK
        try:
            self.__initDataServer(GUI_SETTINGS.socialNetworkLogin['encryptToken'] and not isRegistration)
        except socket.error:
            self.__finiDataServer()
            serverStatus = _STATUS.HTTP_SERVER_ERROR

        if serverStatus == _STATUS.OK:
            baseUrl = self.__getWgniBaseURL(isRegistration)
            loginParams = self.__getWgniParams(isExternal, isRegistration)
            url = baseUrl + '?' + urlencode(loginParams)
            if isRegistration and GUI_SETTINGS.registrationProxyURL:
                url = GUI_SETTINGS.registrationProxyURL + '&lpurl=' + quote_plus(url)
            if not BigWorld.wg_openWebBrowser(url):
                serverStatus = _STATUS.WEB_BROWSER_ERROR
        return serverStatus == _STATUS.OK

    def __onDataServerReceivedData(self, token, spaID, socialNetwork):
        Waiting.show('login')
        BigWorld.callback(0.1, BigWorld.wg_bringWindowToForeground)
        self.__loginParams['token'] = token
        self.__loginParams['account_id'] = spaID
        from Manager import SOCIAL_NETWORKS
        self.__preferences['login_type'] = socialNetwork or SOCIAL_NETWORKS.WGNI
        self.connectionMgr.initiateConnection(self.__loginParams, '', self.__preferences['server_name'])

    def __getWgniParams(self, isExternal, isRegistration):
        params = {'game': 'wot',
         'game_port': self.__dataServer.server_port,
         'remember': int(self.__preferences['remember_user'])}
        if isExternal:
            params['external'] = self.__preferences['login_type']
        if GUI_SETTINGS.socialNetworkLogin['encryptToken'] and not isRegistration:
            params['token_secret'] = base64.urlsafe_b64encode(self.__dataServer.tokenSecret)
        return params

    @staticmethod
    def __getWgniBaseURL(isRegistration=False):
        if isRegistration:
            baseUrl = GUI_SETTINGS.registrationURL.replace('$LANGUAGE_CODE', getLanguageCode())
        else:
            baseUrl = GUI_SETTINGS.socialNetworkLogin['initialLoginURL']
        if HAS_DEV_RESOURCES:
            from gui.development.mock.social_network_login import getServer as getWGNIServerMock
            if getWGNIServerMock() is not None:
                baseUrl = 'http://127.0.0.1:{0}/'.format(getWGNIServerMock().server_port)
        return baseUrl

    def __initDataServer(self, enableEncryption):
        self.__finiDataServer()
        if enableEncryption:
            self.__dataServer = EncryptingThreadedDataServer('SocialNetworkLoginEncryptingServer')
        else:
            self.__dataServer = ThreadedDataServer('SocialNetworkLoginEncryptingServer')
        self.__dataServer.dataReceived += self.__onDataServerReceivedData
        self.__dataServer.start_listening()

    def __finiDataServer(self, *args, **kwargs):
        if self.__dataServer is not None:
            self.__dataServer.stop_listening()
            self.__dataServer.server_close()
            self.__dataServer.dataReceived -= self.__onDataServerReceivedData
            self.__dataServer = None
        return
