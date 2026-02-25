# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/__init__.py
from __future__ import absolute_import
import typing
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.login.login_modes.wgc_mode import WgcMode
from gui.Scaleform.daapi.view.login.login_modes.steam_mode import SteamMode
from gui.Scaleform.daapi.view.login.login_modes.credentials_mode import CredentialsMode
from gui.Scaleform.daapi.view.login.login_modes.social_mode import SocialMode
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager
if typing.TYPE_CHECKING:
    from gui.Scaleform.daapi.view.login.login_modes.base_mode import BaseMode

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
