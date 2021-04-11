# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/decorators.py
from functools import wraps
from async import async, await
from helpers import dependency
from skeletons.gui.game_control import ISteamRegistrationOverlay

def waitShowOverlay(func):

    @wraps(func)
    @async
    def _wrapper(*args, **kwargs):
        overlay = dependency.instance(ISteamRegistrationOverlay)
        yield await(overlay.waitShow())
        func(*args, **kwargs)

    return _wrapper
