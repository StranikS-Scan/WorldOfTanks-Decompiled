# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/login/login_modes/__init__.py
from gui import GUI_SETTINGS
from skeletons.gui.login_manager import ILoginManager
from helpers import dependency
from base_mode import BaseMode
from wgc_mode import WgcMode
from credentials_mode import CredentialsMode
from social_mode import SocialMode

@dependency.replace_none_kwargs(loginManager=ILoginManager)
def createLoginMode(view, loginManager=None):
    mode = CredentialsMode(view)
    if GUI_SETTINGS.socialNetworkLogin['enabled']:
        mode = SocialMode(view, mode)
    isWgcUser = loginManager.checkWgcAvailability()
    if loginManager.wgcAvailable:
        mode = WgcMode(isWgcUser, view, mode)
    return mode
