# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/__init__.py
import logging
from functools import wraps
from helpers import dependency
from skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)

def ifGameEventDisabled(result=None):

    def inner(function):

        @wraps(function)
        def wrapper(*args, **kwargs):
            gameEvent = dependency.instance(IGameEventController)
            if not gameEvent.isEnabled():
                _logger.debug('Event is disabled. Call %s not allowed.', function)
                return result
            return function(*args, **kwargs)

        return wrapper

    return inner
