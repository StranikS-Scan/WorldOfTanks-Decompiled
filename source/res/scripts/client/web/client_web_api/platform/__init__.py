# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/client_web_api/platform/__init__.py
import typing
from constants import WGC_PUBLICATION
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
from web.client_web_api.api import C2WHandler
from web.client_web_api.platform.steam import SteamPlatformEventHandler
if typing.TYPE_CHECKING:
    from web.client_web_api.common import WebEventSender
_MAPPING = {WGC_PUBLICATION.WGC_STEAM: SteamPlatformEventHandler}

@dependency.replace_none_kwargs(loginManager=ILoginManager)
def getPlatformEventHandler(sender, loginManager=None):
    pub = loginManager.getWgcPublication()
    return _MAPPING[pub](sender) if pub in _MAPPING else C2WHandler(sender)
