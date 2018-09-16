# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_external_cache.py


class IWebExternalCache(object):

    class IStorage(object):

        def get(self, url):
            raise NotImplementedError
