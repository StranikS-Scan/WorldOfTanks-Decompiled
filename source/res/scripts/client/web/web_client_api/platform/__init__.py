# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/platform/__init__.py
import typing
from web.web_client_api import w2capi
from constants import WGC_PUBLICATION
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
from soft_exception import SoftException
from web.web_client_api import w2c, W2CSchema
from web.web_client_api.platform.china360 import China360PlatformWebApi
from web.web_client_api.platform.steam import SteamPlatformWebApi
from web.web_client_api.platform.wg import WgPlatformWebApi
if typing.TYPE_CHECKING:
    from web.web_client_api.platform.base import IPlatformWebApi

@w2capi(name='platform', key='action')
class PlatformWebApi(object):
    __slots__ = ('__mapping',)
    __loginManager = dependency.descriptor(ILoginManager)

    def __init__(self):
        super(PlatformWebApi, self).__init__()
        self.__mapping = {WGC_PUBLICATION.WGC_STEAM: SteamPlatformWebApi(),
         WGC_PUBLICATION.WGC_360: China360PlatformWebApi(),
         WGC_PUBLICATION.WGC_PC: WgPlatformWebApi()}

    @w2c(W2CSchema, 'get_type')
    def getType(self, _):
        return self.__getApi().getType()

    @w2c(W2CSchema, 'is_inited')
    def isInited(self, _):
        return self.__getApi().isInited()

    @w2c(W2CSchema, 'is_connected')
    def isConnected(self, _):
        return self.__getApi().isInited()

    def __getApi(self):
        pub = self.__loginManager.getWgcPublication()
        if pub not in self.__mapping:
            raise SoftException('Unknown platform type: %r' % pub)
        return self.__mapping[pub]
