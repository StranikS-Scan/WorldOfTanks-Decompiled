# Embedded file name: scripts/client/tutorial/TutorialCache.py
import BigWorld
import base64, cPickle, os
from tutorial.logger import LOG_CURRENT_EXCEPTION, LOG_WARNING
from tutorial.settings import TUTORIAL_VERSION, PLAYER_XP_LEVEL
import constants

class TutorialCache(object):
    __internal = None

    def __init__(self, accountName, space, initRecords = None):
        p = os.path
        prefsFilePath = unicode(BigWorld.wg_getPreferencesFilePath(), 'utf-8', errors='ignore')
        self.__cacheDir = p.join(p.dirname(prefsFilePath), 'tutorial_cache')
        self.__cacheFileName = p.join(self.__cacheDir, '{0:>s}.dat'.format(base64.b32encode('{0:>s};{1:>s}'.format(constants.AUTH_REALM, accountName))))
        self.__space = space
        self.__version = TUTORIAL_VERSION
        self.__wasReset = False
        self.__cache = {space: {'finished': False,
                 'refused': False,
                 'afterBattle': False,
                 'flags': {},
                 'currentChapter': None,
                 'localCtx': None,
                 'playerXPLevel': PLAYER_XP_LEVEL.NEWBIE,
                 'startOnNextLogin': True}}
        self.__read()
        cache = self.__current()
        if initRecords is None:
            initRecords = {}
        for flag, value in initRecords.iteritems():
            if flag in cache and not cache[flag]:
                cache[flag] = value

        return

    def __repr__(self):
        return 'TutorialCache({0:s}): {1!r:s}'.format(hex(id(self)), self.__cache.get(self.__space, {}))

    def __current(self):
        return self.__cache[self.__space]

    def __read(self):
        cacheFile = None
        if TutorialCache.__internal is not None:
            LOG_WARNING('Cache retrieved from internal property. Record to file is denied.', TutorialCache.__internal)
            self.__cache.update(TutorialCache.__internal)
            return
        else:
            try:
                if not os.path.isfile(self.__cacheFileName):
                    return
                cacheFile = open(self.__cacheFileName, 'rb')
                self.__version, cache = cPickle.load(cacheFile)
                if self.__version != TUTORIAL_VERSION:
                    self.__version = TUTORIAL_VERSION
                    self.__wasReset = True
                else:
                    self.__cache.setdefault(self.__space, {})
                    self.__cache.update(cache)
            except (IOError, EOFError, cPickle.PickleError):
                LOG_CURRENT_EXCEPTION()
                if TutorialCache.__internal is not None:
                    self.__cache.update(TutorialCache.__internal)
            finally:
                if cacheFile is not None:
                    cacheFile.close()

            return

    def write(self):
        output = None
        try:
            if not os.path.isdir(self.__cacheDir):
                os.makedirs(self.__cacheDir)
            output = open(self.__cacheFileName, 'wb')
            cPickle.dump((self.__version, self.__cache), output, -1)
        except (IOError, cPickle.PickleError):
            LOG_CURRENT_EXCEPTION()
            TutorialCache.__internal = self.__cache.copy()
        finally:
            if output is not None:
                output.close()

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
        return

    def isEmpty(self):
        cache = self.__current()
        return cache['currentChapter'] is None or not len(cache['flags'])
