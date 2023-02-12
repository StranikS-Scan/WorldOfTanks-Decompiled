# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/cache.py
from helpers.local_cache import FileLocalCache
from tutorial.settings import TUTORIAL_VERSION
import constants

class TutorialCache(FileLocalCache):

    def __init__(self, accountName):
        super(TutorialCache, self).__init__('tutorial_cache', (constants.AUTH_REALM, accountName))
        self.__space = None
        self.__wasReset = False
        self.__cache = {}
        return

    def __repr__(self):
        return 'TutorialCache({0:s}): {1!r:s}'.format(hex(id(self)), self.__cache.get(self.__space, {}))

    def getSpace(self):
        return self.__space

    def setSpace(self, space, init=None, ioEnabled=True):
        if self.__space is not None and not self._ioEnabled:
            del self.__cache[self.__space]
        self.__space = space
        self._ioEnabled = ioEnabled
        defaultValues = {'finished': False,
         'refused': False,
         'flags': {},
         'currentChapter': None,
         'localCtx': None}
        if self._ioEnabled:
            self.__cache.setdefault(space, defaultValues)
        else:
            self.__cache[space] = defaultValues
        if init is not None:
            cache = self.__current()
            for flag, value in init.iteritems():
                if flag in cache:
                    cache[flag] = value

        return

    def update(self, currentChapter, flags):
        cache = self.__current()
        if currentChapter is not None:
            cache['currentChapter'] = currentChapter
        if flags is not None:
            cache['flags'] = flags
        self.write()
        return

    def wasReset(self):
        return self.__wasReset

    def setFinished(self, flag):
        self.__current()['finished'] = flag
        return self

    def isFinished(self):
        return self.__current()['finished']

    def setRefused(self, flag):
        self.__current()['refused'] = flag
        return self

    def isRefused(self):
        return self.__current()['refused']

    def currentChapter(self):
        return self.__current()['currentChapter']

    def flags(self):
        return self.__current()['flags']

    def getLocalCtx(self):
        return self.__current()['localCtx']

    def setLocalCtx(self, ctx, flush=True):
        self.__current()['localCtx'] = ctx
        if flush:
            self.write()

    def clearChapterData(self):
        cache = self.__current()
        cache['flags'] = {}
        return self

    def clear(self):
        cache = self.__current()
        cache['currentChapter'] = None
        cache['flags'] = {}
        self.write()
        super(TutorialCache, self).clear()
        return

    def isEmpty(self):
        cache = self.__current()
        return cache['currentChapter'] is None or not cache['flags']

    def _getCache(self):
        return (TUTORIAL_VERSION, self.__cache.copy())

    def _setCache(self, data):
        version, cache = data
        if version != TUTORIAL_VERSION:
            self.__wasReset = True
        else:
            self.__cache = cache

    def __current(self):
        return self.__cache[self.__space]
