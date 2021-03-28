# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/__init__.py
import typing
from gui import GUI_SETTINGS
from skeletons.gui.login_manager import ILoginManager
from helpers import dependency
from wgc_mode import WgcMode
from steam_mode import SteamMode
from credentials_mode import CredentialsMode
from social_mode import SocialMode
if typing.TYPE_CHECKING:
    from base_mode import BaseMode

@dependency.replace_none_kwargs(loginManager=ILoginManager)
def createLoginMode(view, loginManager=None):
    if loginManager.isWgcSteam:
        return SteamMode(view)
    mode = CredentialsMode(view)
    if GUI_SETTINGS.socialNetworkLogin['enabled']:
        mode = SocialMode(view, mode)
    if loginManager.wgcAvailable:
        mode = WgcMode(view, mode)
    return mode
