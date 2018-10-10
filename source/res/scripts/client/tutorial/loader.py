# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/loader.py
import weakref
import BigWorld
import account_helpers
from constants import IS_TUTORIAL_ENABLED
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from tutorial import core
from tutorial import settings as _settings
from tutorial import cache as _cache
from tutorial.control.context import GLOBAL_FLAG, GlobalStorage
from tutorial.control.listener import AppLoaderListener
from tutorial.doc_loader import loadDescriptorData
from tutorial.hints_manager import HintsManager
from debug_utils import LOG_ERROR, LOG_DEBUG
from skeletons.gui.game_control import IBootcampController
from soft_exception import SoftException
_SETTINGS = _settings.TUTORIAL_SETTINGS
_LOBBY_DISPATCHER = _settings.TUTORIAL_LOBBY_DISPATCHER
_BATTLE_DISPATCHER = _settings.TUTORIAL_BATTLE_DISPATCHER

class RunCtx(object):
    __slots__ = ('cache', 'isFirstStart', 'databaseID', 'isAfterBattle', 'restart', 'bonusCompleted', 'battlesCount', 'newbieBattlesCount', 'initialChapter', 'globalFlags', 'canResolveChapterOnStart', 'byRequest')

    def __init__(self, cache, **kwargs):
        super(RunCtx, self).__init__()
        self.cache = cache
        self.databaseID = kwargs.get('databaseID', 0L)
        self.restart = kwargs.get('restart', False)
        self.isFirstStart = kwargs.get('isFirstStart', False)
        self.isAfterBattle = kwargs.get('isAfterBattle', False)
        self.bonusCompleted = kwargs.get('bonusCompleted', 0)
        self.battlesCount = kwargs.get('battlesCount', 0)
        self.newbieBattlesCount = kwargs.get('newbieBattlesCount', 0)
        self.initialChapter = kwargs.get('initialChapter', None)
        self.globalFlags = kwargs.get('globalFlags', {})
        self.globalFlags[GLOBAL_FLAG.IN_QUEUE] = kwargs.get('isInTutorialQueue', False)
        self.canResolveChapterOnStart = kwargs.get('canResolveChapterOnStart', True)
        self.byRequest = kwargs.get('byRequest', False)
        return

    def __repr__(self):
        return 'RunCtx(databaseID={}, restart={}, first={}, battle={}, bonuses={}, battles={}, newbie={}, chapter={}, flags={} cache={})'.format(self.databaseID, self.restart, self.isFirstStart, self.isAfterBattle, self.bonusCompleted, self.battlesCount, self.newbieBattlesCount, self.initialChapter, self.globalFlags, self.cache)


class TutorialLoader(object):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(TutorialLoader, self).__init__()
        self.__loggedDBIDs = set()
        self.__afterBattle = False
        self.__tutorial = None
        self.__dispatcher = None
        self.__restoreID = None
        self.__settings = _settings.createSettingsCollection()
        self.__hintsManager = None
        self.__listener = None
        return

    def init(self):
        self.__listener = AppLoaderListener()
        self.__listener.start(weakref.proxy(self))

    def fini(self):
        if self.__listener is not None:
            self.__listener.stop()
        if self.__hintsManager is not None:
            self.__hintsManager.stop()
        if self.__dispatcher is not None:
            self.__dispatcher.stop()
        if self.__tutorial is not None:
            self.__tutorial.onStopped -= self.__onTutorialStopped
            self.__tutorial.stop()
        self.__loggedDBIDs.clear()
        self.__settings.clear()
        return

    @property
    def tutorial(self):
        return self.__tutorial

    @property
    def tutorialID(self):
        result = ''
        if self.__tutorial is not None:
            result = self.__tutorial.getID()
        return result

    @property
    def isRunning(self):
        result = False
        if self.__tutorial is not None:
            result = not self.__tutorial.isStopped()
        return result

    def isTutorialStopped(self):
        result = True
        if self.__tutorial is not None:
            result = self.__tutorial.isStopped()
        return result

    def run(self, settingsID, state=None):
        settings = self.__settings.getSettings(settingsID)
        if settings is None:
            LOG_ERROR('Can not find settings', settingsID)
            return False
        else:
            if state is None:
                state = {}
            reloadIfRun = state.pop('reloadIfRun', False)
            restoreIfRun = state.pop('restoreIfRun', False)
            isStopForced = state.pop('isStopForced', False)
            if self.__tutorial is not None and not self.__tutorial.isStopped():
                isCurrent = self.__tutorial.getID() == settings.id
                if reloadIfRun and isCurrent:
                    if isStopForced:
                        self.__doStop()
                    else:
                        GlobalStorage.setFlags(state.get('globalFlags', {}))
                        LOG_DEBUG('invalidateFlags from TutorialLoader.run')
                        self.__tutorial.invalidateFlags()
                        return True
                elif restoreIfRun and not isCurrent:
                    self.__restoreID = self.__tutorial.getID()
                    self.__doStop()
                else:
                    LOG_ERROR('Tutorial already is running', self.__tutorial.getID())
                    return False
            state.setdefault('isAfterBattle', self.__afterBattle)
            state.setdefault('restart', True)
            state['byRequest'] = True
            result = self.__doRun(settings, state)
            if not result:
                self.__restoreID = None
            return result

    def stop(self, restore=True):
        self.__doStop()
        self.__doStopHints()
        if restore:
            self.__doRestore()
        else:
            self.__restoreID = None
        return

    def refuse(self):
        if self.__tutorial is not None:
            self.__tutorial.refuse()
        return

    def goToLobby(self):
        databaseID = account_helpers.getAccountDatabaseID()
        if not databaseID:
            raise SoftException('Acoount database ID is not defined')
        isFirstStart = databaseID not in self.__loggedDBIDs
        self.__loggedDBIDs.add(databaseID)
        state = {'isFirstStart': isFirstStart,
         'isAfterBattle': self.__afterBattle}
        self.__setDispatcher(_LOBBY_DISPATCHER)
        self.__restoreID = _SETTINGS.QUESTS.id
        bootcampController = dependency.instance(IBootcampController)
        isInBootcampAccount = bootcampController.isInBootcampAccount()
        if isInBootcampAccount:
            selectedSettings = self.__doAutoRun((_SETTINGS.OFFBATTLE, _SETTINGS.QUESTS, _SETTINGS.BOOTCAMP_LOBBY), state)
        else:
            selectedSettings = None
        if selectedSettings is None or selectedSettings.hintsEnabled:
            self.__hintsManager = HintsManager()
            self.__hintsManager.start()
        return

    def stopOnceOnlyHint(self, itemID):
        if self.__hintsManager is not None:
            self.__hintsManager.stopOnceOnlyHint(itemID)
        return

    def leaveLobby(self):
        self.stop(restore=False)

    def goToBattleLoading(self):
        self.__afterBattle = True
        self.__doClear()
        self.__doAutoRun((_SETTINGS.BATTLE_V2, _SETTINGS.BATTLE_QUESTS), {'canResolveChapterOnStart': False})

    def goToBattle(self):
        if self.__tutorial is not None:
            self.__tutorial.startBattle()
        return

    def leaveBattle(self):
        self.stop(restore=False)

    def goToLogin(self):
        self.__afterBattle = False
        self.__doClear()

    def __doAutoRun(self, seq, state):
        for settings in seq:
            if self.__doRun(settings, state):
                return settings

        return None

    def __doRun(self, settings, state):
        if not settings.enabled:
            return False
        else:
            reqs = _settings.createTutorialElement(settings.reqs)
            if not reqs.isEnabled():
                return False
            descriptor = loadDescriptorData(settings, settings.exParsers)
            if descriptor is None:
                LOG_ERROR('Descriptor is not valid. Tutorial is not available', settings)
                return False
            cache = _cache.TutorialCache(BigWorld.player().name)
            cache.read()
            cache.setSpace(settings.space, ioEnabled=settings.cacheEnabled)
            if state.get('byRequest', False):
                cache.setRefused(False)
            runCtx = RunCtx(cache, **state)
            reqs.prepare(runCtx)
            if not reqs.process(descriptor, runCtx):
                return False
            self.__doStop()
            if self.__dispatcher is None:
                self.__setDispatcher(settings.dispatcher)
            self.__tutorial = core.Tutorial(settings, descriptor)
            self.__tutorial.onStopped += self.__onTutorialStopped
            result = self.__tutorial.run(weakref.proxy(self.__dispatcher), runCtx)
            if not result:
                self.__tutorial.onStopped -= self.__onTutorialStopped
                self.__tutorial = None
            return result

    def __doStop(self):
        if self.__tutorial is not None:
            self.__tutorial.onStopped -= self.__onTutorialStopped
            self.__tutorial.stop()
            self.__tutorial = None
        return

    def __doStopHints(self):
        if self.__hintsManager is not None:
            self.__hintsManager.stop()
            self.__hintsManager = None
        return

    def __doClear(self):
        self.__restoreID = None
        self.__doStop()
        self.__doStopHints()
        if self.__dispatcher is not None:
            self.__dispatcher.stop()
            self.__dispatcher = None
        return

    def __doRestore(self):
        if self.__restoreID is not None:
            settingsID, self.__restoreID = self.__restoreID, None
            LOG_DEBUG('Restore tutorial', settingsID)
            self.run(settingsID)
        return

    def __setDispatcher(self, settings):
        if self.__dispatcher is not None:
            self.__dispatcher.stop()
            self.__dispatcher = None
        self.__dispatcher = _settings.createTutorialElement(settings)
        self.__dispatcher.start(weakref.proxy(self))
        return

    def __onTutorialStopped(self):
        self.__doRestore()


g_loader = None

def init():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        g_loader = TutorialLoader()
        LOG_DEBUG('g_loader init')
        g_loader.init()


def fini():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        if g_loader is not None:
            g_loader.fini()
            g_loader = None
            LOG_DEBUG('g_loader deinit')
    return


def isTutorialRunning(tutorialID):
    isRunning = False
    if IS_TUTORIAL_ENABLED:
        if g_loader is not None:
            isRunning = g_loader.isRunning and g_loader.tutorialID == tutorialID
    return isRunning
