# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clientgw/factory.py
import BigWorld
from client_request_lib.requester import Requester as WebRequester
from constants import TOKEN_TYPE
from gui.shared.utils.requesters import TokenRequester, getTokenRequester
from gui.clientgw.requests import ClientgwRequester, ClientgwRequestsController
from helpers.server_settings import _Clientgw

def _webUrlFetcher(url, callback, headers=None, timeout=30.0, method='GET', postData=''):
    return BigWorld.fetchURL(url, callback, headers, timeout, method, postData)


class _WebFactory(object):

    def createWebRequester(self, settings, *args, **kwargs):
        raise NotImplementedError

    def createTokenRequester(self):
        raise NotImplementedError

    def createClientgwRequester(self, webRequester):
        raise NotImplementedError

    def createClientgwRequestsController(self, webCtrl, clanRequester):
        raise NotImplementedError


class WebFactory(_WebFactory):

    def createWebRequester(self, settings, *args, **kwargs):
        return WebRequester.create_requester(_webUrlFetcher, settings, *args, **kwargs)

    def createTokenRequester(self):
        return getTokenRequester(TOKEN_TYPE.WGNI_JWT)

    def createClientgwRequester(self, webRequester):
        return ClientgwRequester(webRequester)

    def createClientgwRequestsController(self, webCtrl, clanRequester):
        return ClientgwRequestsController(webCtrl, clanRequester)


class FakeWebFactory(_WebFactory):

    def createWebRequester(self, settings, *args, **kwargs):
        return WebRequester.create_requester(_webUrlFetcher, _Clientgw(True, None, 'fake', False, False), *args, **kwargs)

    def createTokenRequester(self):
        return TokenRequester(TOKEN_TYPE.WGNI, cache=False)

    def createClientgwRequester(self, webRequester):
        return ClientgwRequester(webRequester)

    def createClientgwRequestsController(self, webCtrl, clanRequester):
        return ClientgwRequestsController(webCtrl, clanRequester)


g_webFactory = WebFactory()
