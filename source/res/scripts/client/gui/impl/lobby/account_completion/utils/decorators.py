# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/utils/decorators.py
from functools import wraps
from async import async, await, delay
from helpers import dependency
from skeletons.gui.game_control import IOverlayController
_WAITING_DELAY = 0.001

def waitShowOverlay(func):

    @wraps(func)
    @async
    def _wrapper(*args, **kwargs):
        overlay = dependency.instance(IOverlayController)
        yield await(overlay.waitShow())
        yield await(delay(_WAITING_DELAY))
        func(*args, **kwargs)

    return _wrapper
