# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/platform/platform_type.py
import typing
from constants import DISTRIBUTION_PLATFORM, WGC_PUBLICATION
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
from soft_exception import SoftException
from web.web_client_api import w2c, W2CSchema

class GetTypeWebApiMixin(object):
    _MAPPING = {WGC_PUBLICATION.WGC_STEAM: DISTRIBUTION_PLATFORM.STEAM,
     WGC_PUBLICATION.WGC_360: DISTRIBUTION_PLATFORM.CHINA_360,
     WGC_PUBLICATION.WGC_PC: DISTRIBUTION_PLATFORM.WG}

    @w2c(W2CSchema, 'get_type')
    @dependency.replace_none_kwargs(loginManager=ILoginManager)
    def getType(self, _, loginManager=None):
        pub = loginManager.getWgcPublication()
        if pub in self._MAPPING:
            return self._MAPPING[pub].value
        raise SoftException('Unknown platform type: %r' % pub)
