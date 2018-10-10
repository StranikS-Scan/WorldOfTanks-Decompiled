# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/factory.py
import BigWorld
from client_request_lib.requester import Requester as WebRequester
from constants import TOKEN_TYPE
from gui.shared.utils.requesters import TokenRequester, getTokenRequester
from gui.wgcg.requests import WgcgRequester, WgcgRequestsController
from helpers.server_settings import _Wgcg

def _webUrlFetcher(url, callback, headers=None, timeout=30.0, method='GET', postData=''):
    return BigWorld.fetchURL(url, callback, headers, timeout, method, postData)


class _WebFactory(object):

    def createWebRequester(self, settings, *args, **kwargs):
        raise NotImplementedError

    def createTokenRequester(self):
        raise NotImplementedError

    def createWgcgRequester(self, webRequester):
        raise NotImplementedError

    def createWgcgRequestsController(self, webCtrl, clanRequester):
        raise NotImplementedError


class WebFactory(_WebFactory):

    def createWebRequester(self, settings, *args, **kwargs):
        return WebRequester.create_requester(_webUrlFetcher, settings, *args, **kwargs)

    def createTokenRequester(self):
        return getTokenRequester(TOKEN_TYPE.WGNI)

    def createWgcgRequester(self, webRequester):
        return WgcgRequester(webRequester)

    def createWgcgRequestsController(self, webCtrl, clanRequester):
        return WgcgRequestsController(webCtrl, clanRequester)


class FakeWebFactory(_WebFactory):

    def createWebRequester(self, settings, *args, **kwargs):
        return WebRequester.create_requester(_webUrlFetcher, _Wgcg(True, None, 'fake', False), *args, **kwargs)

    def createTokenRequester(self):
        return TokenRequester(TOKEN_TYPE.WGNI, cache=False)

    def createWgcgRequester(self, webRequester):
        return WgcgRequester(webRequester)

    def createWgcgRequestsController(self, webCtrl, clanRequester):
        return WgcgRequestsController(webCtrl, clanRequester)


g_webFactory = WebFactory()
