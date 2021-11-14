# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/base/mixins.py
import logging
from functools import wraps
import typing
import BigWorld
from uilogging.base.logger import ifUILoggingEnabled
from uilogging.core.core_constants import LogLevels
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from uilogging.base.logger import BaseLogger
_logger = logging.getLogger(__name__)

class LogOnceMixin(object):

    def __init__(self, feature, group):
        super(LogOnceMixin, self).__init__(feature, group)
        self._logOnce = set()

    @noexcept
    def reset(self):
        super(LogOnceMixin, self).reset()
        self._logOnce.clear()

    def dLogOnce(self, action, loglevel=LogLevels.INFO, **params):

        def inner(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.logOnce(action, loglevel=loglevel, **params)
                return func(*args, **kwargs)

            return wrapper

        return inner

    @noexcept
    @ifUILoggingEnabled()
    def logOnce(self, action, loglevel=LogLevels.INFO, **params):
        if action in self._logOnce:
            _logger.debug('%s log once action: %s already logged.', self, action)
            return
        self._logOnce.add(action)
        self.log(action, loglevel=loglevel, **params)


class TimedActionMixin(object):

    def __init__(self, *args, **kwargs):
        super(TimedActionMixin, self).__init__(*args, **kwargs)
        self._timedActions = {}
        self._suspendedActions = {}

    @noexcept
    def reset(self):
        super(TimedActionMixin, self).reset()
        self._timedActions.clear()

    def dStartAction(self, action):

        def inner(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.startAction(action)
                return func(*args, **kwargs)

            return wrapper

        return inner

    def dStopAction(self, action, loglevel=LogLevels.INFO, timeLimit=0, **params):

        def inner(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.stopAction(action, loglevel=loglevel, timeLimit=timeLimit, **params)
                return func(*args, **kwargs)

            return wrapper

        return inner

    @noexcept
    @ifUILoggingEnabled()
    def startAction(self, action):
        if action in self._timedActions:
            _logger.debug('%s action: %s already started. Setting new action.', self, action)
        self._timedActions[action] = BigWorld.time()

    @noexcept
    def stopAction(self, action, loglevel=LogLevels.INFO, timeLimit=0, **params):
        if action not in self._timedActions:
            _logger.debug('%s action: %s not started.', self, action)
            return
        else:
            if action in self._suspendedActions:
                self.resume(action)
            startTime = self._timedActions.pop(action, None)
            timeSpent = BigWorld.time() - startTime
            if timeSpent > timeLimit:
                self.log(action, loglevel=loglevel, timeSpent=timeSpent, **params)
            return

    @noexcept
    def suspend(self, action):
        if action not in self._timedActions:
            return
        if action in self._suspendedActions:
            return
        self._suspendedActions[action] = BigWorld.time()

    @noexcept
    def resume(self, action):
        if action not in self._timedActions:
            return
        else:
            suspensionStartTime = self._suspendedActions.pop(action, None)
            if suspensionStartTime is None:
                return
            suspensionTime = BigWorld.time() - suspensionStartTime
            self._timedActions[action] += suspensionTime
            return
