# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/cache_providers/base_provider.py


class IBaseProvider(object):

    def start(self):
        raise NotImplementedError

    def stop(self, withClear=False):
        raise NotImplementedError
