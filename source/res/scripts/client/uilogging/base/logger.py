# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/base/logger.py
import typing
import logging
from functools import wraps
from helpers import dependency
from skeletons.ui_logging import IUILoggingCore
from uilogging.core.core_constants import LogLevels
from uilogging.core.settings import Settings
from wotdecorators import noexcept
_logger = logging.getLogger(__name__)

def ifUILoggingEnabled(result=None):

    def inner(func):

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            if self.disabled:
                _logger.debug('UI logging disabled. %s log skipped.', self)
                return result
            return func(self, *args, **kwargs)

        return wrapper

    return inner


class BaseLogger(object):
    _core = dependency.descriptor(IUILoggingCore)

    def __init__(self, feature, group):
        self._feature = feature
        self._group = group

    def __str__(self):
        return '<{}: {}, {}>'.format(self.__class__.__name__, self._feature, self._group)

    def dLog(self, action, loglevel=LogLevels.INFO, **params):

        def inner(func):

            @wraps(func)
            def wrapper(*args, **kwargs):
                self.log(action, loglevel=loglevel, **params)
                return func(*args, **kwargs)

            return wrapper

        return inner

    def reset(self):
        pass

    @property
    def settings(self):
        return self._core.getSettings(self._feature, self._group)

    @property
    def disabled(self):
        return self.settings.disabled

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, loglevel=LogLevels.INFO, **params):
        return self._core.log(feature=self._feature, group=self._group, action=action, loglevel=loglevel, **params)

    def info(self, action, **params):
        return self.log(action, loglevel=LogLevels.INFO, **params)
