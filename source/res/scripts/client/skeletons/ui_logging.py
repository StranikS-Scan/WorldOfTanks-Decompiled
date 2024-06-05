# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/ui_logging.py
import typing
if typing.TYPE_CHECKING:
    from uilogging.types import FeatureType, GroupType, ActionType, LogLevelType

class IUILoggingCore(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isFeatureEnabled(self, feature):
        raise NotImplementedError

    def log(self, feature, group, action, loglevel, **params):
        raise NotImplementedError

    def logImmediately(self, feature, group, action, loglevel, **params):
        raise NotImplementedError

    def ensureSession(self):
        raise NotImplementedError

    def start(self, ensureSession=False):
        raise NotImplementedError

    def send(self):
        raise NotImplementedError


class IUILoggingListener(object):

    def fini(self):
        raise NotImplementedError
