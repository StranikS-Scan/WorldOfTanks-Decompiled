# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_completion/utils/decorators.py
from functools import wraps
from th_async import th_async, th_await, delay
from helpers import dependency
from skeletons.gui.game_control import IOverlayController
_WAITING_DELAY = 0.001

def waitShowOverlay(func):

    @wraps(func)
    @th_async
    def _wrapper(*args, **kwargs):
        overlay = dependency.instance(IOverlayController)
        yield th_await(overlay.waitShow())
        yield th_await(delay(_WAITING_DELAY))
        func(*args, **kwargs)

    return _wrapper
