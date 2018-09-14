# Embedded file name: scripts/client/tutorial/cache.py
from helpers.local_cache import FileLocalCache
from tutorial.settings import TUTORIAL_VERSION, PLAYER_XP_LEVEL
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

    def setSpace(self, space, init = None):
        self.__space = space
        self.__cache.setdefault(space, {'finished': False,
         'refused': False,
         'afterBattle': False,
         'flags': {},
         'currentChapter': None,
         'localCtx': None,
         'playerXPLevel': PLAYER_XP_LEVEL.NEWBIE,
         'startOnNextLogin': True})
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

    def setAfterBattle(self, flag):
        self.__current()['afterBattle'] = flag
        return self

    def isAfterBattle(self):
        return self.__current()['afterBattle']

    def currentChapter(self):
        return self.__current()['currentChapter']

    def flags(self):
        return self.__current()['flags']

    def getLocalCtx(self):
        return self.__current()['localCtx']

    def setLocalCtx(self, ctx, flush = True):
        self.__current()['localCtx'] = ctx
        if flush:
            self.write()

    def setPlayerXPLevel(self, level):
        self.__current()['playerXPLevel'] = level
        return self

    def getPlayerXPLevel(self):
        return self.__current()['playerXPLevel']

    def setStartOnNextLogin(self, value):
        self.__current()['startOnNextLogin'] = value
        return self

    def doStartOnNextLogin(self):
        return self.__current()['startOnNextLogin']

    def clearChapterData(self):
        cache = self.__current()
        cache['flags'] = {}
        cache['afterBattle'] = False
        return self

    def clear(self):
        cache = self.__current()
        cache['currentChapter'] = None
        cache['flags'] = {}
        cache['afterBattle'] = False
        self.write()
        super(TutorialCache, self).clear()
        return

    def isEmpty(self):
        cache = self.__current()
        return cache['currentChapter'] is None or not len(cache['flags'])

    def _getCache(self):
        return (TUTORIAL_VERSION, self.__cache.copy())

    def _setCache(self, data):
        version, cache = data
        if version != TUTORIAL_VERSION:
            self.__wasReset = True
        else:
            self.__cache = cache

    def __current(self):
        raise self.__space is not None or AssertionError('Space must be set')
        return self.__cache[self.__space]
