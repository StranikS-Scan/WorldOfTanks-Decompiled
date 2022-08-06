# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/ui_logging.py


class IUILoggingCore(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def isFeatureEnabled(self, feature):
        raise NotImplementedError

    def log(self, feature, group, action, loglevel, **params):
        raise NotImplementedError


class IUILoggingListener(object):

    def fini(self):
        raise NotImplementedError
