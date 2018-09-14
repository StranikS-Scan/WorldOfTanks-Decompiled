# Embedded file name: scripts/client/tutorial/loader.py
import weakref
import BigWorld
from ConnectionManager import connectionManager
from constants import IS_TUTORIAL_ENABLED
from PlayerEvents import g_playerEvents
from tutorial import Tutorial, LOG_DEBUG
from tutorial import settings as _settings
from tutorial import cache as _cache
from tutorial.control.context import GLOBAL_FLAG, GlobalStorage
from tutorial.doc_loader import loadDescriptorData
from tutorial.hints_manager import HintsManager
from tutorial.logger import LOG_ERROR
_STOP_REASON = _settings.TUTORIAL_STOP_REASON
_SETTINGS = _settings.TUTORIAL_SETTINGS
_LOBBY_DISPATCHER = _settings.TUTORIAL_LOBBY_DISPATCHER

class RunCtx(object):
    __slots__ = ('cache', 'isFirstStart', 'databaseID', 'isAfterBattle', 'restart', 'bonusCompleted', 'battlesCount', 'newbieBattlesCount', 'initialChapter', 'globalFlags')

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
        return

    def __repr__(self):
        return 'RunCtx(databaseID={}, restart={}, first={}, battle={}, bonuses={}, battles={}, newbie={}, chapter={}, flags={} cache={})'.format(self.databaseID, self.restart, self.isFirstStart, self.isAfterBattle, self.bonusCompleted, self.battlesCount, self.newbieBattlesCount, self.initialChapter, self.globalFlags, self.cache)


class TutorialLoader(object):

    def __init__(self):
        super(TutorialLoader, self).__init__()
        self.__loggedDBIDs = set()
        self.__afterBattle = False
        self.__tutorial = None
        self.__dispatcher = None
        self.__restoreID = None
        self.__settings = _settings.createSettingsCollection()
        self.__hintsManager = None
        return

    def init(self):
        g_playerEvents.onGuiCacheSyncCompleted += self.__pe_onGuiCacheSyncCompleted
        g_playerEvents.onAvatarBecomePlayer += self.__pe_onAvatarBecomePlayer
        connectionManager.onDisconnected += self.__cm_onDisconnected

    def fini(self):
        g_playerEvents.onGuiCacheSyncCompleted -= self.__pe_onGuiCacheSyncCompleted
        g_playerEvents.onAvatarBecomePlayer -= self.__pe_onAvatarBecomePlayer
        connectionManager.onDisconnected -= self.__cm_onDisconnected
        if self.__hintsManager is not None:
            self.__hintsManager.stop()
        if self.__tutorial is not None:
            self.__dispatcher.stop()
            self.__tutorial.onStopped -= self.__onTutorialStopped
            self.__tutorial.stop()
        self.__loggedDBIDs.clear()
        self.__settings.clear()
        return

    def clear(self):
        if self.__tutorial is not None:
            self.__tutorial.onStopped -= self.__onTutorialStopped
        self.__tutorial = None
        return

    @property
    def tutorial(self):
        return self.__tutorial

    @property
    def tutorialID(self):
        result = 0
        if self.__tutorial is not None:
            result = not self.__tutorial.getID()
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

    def run(self, settingsID, state = None):
        """
        Try to run tutorial.
        
        :param settingsID: string containing settings ID of required tutorial.
        :param state: dict(
                        reloadIfRun : bool - just reload tutorial if it's running,
                        afterBattle : bool - tutorial should load scenario that is played
                                when player left battle,
                        initialChapter : str - name of initial chapter,
                        restoreIfRun: bool - current tutorial will be started again
                                if required tutorial stop.
                        globalFlags : dict(GLOBAL_FLAG.* : bool,)
                )
        :return: True if tutorial has started, otherwise - False.
        """
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
                        self.__tutorial.invalidateFlags()
                        return True
                elif restoreIfRun and not isCurrent:
                    self.__restoreID = self.__tutorial.getID()
                    self.__doStop()
                else:
                    LOG_ERROR('Tutorial already is running', self.__tutorial.getID())
                    return False
            if self.__dispatcher is None:
                self.__setDispatcher(settings.dispatcher)
            cache = _cache.TutorialCache(BigWorld.player().name)
            cache.read()
            state.setdefault('isAfterBattle', self.__afterBattle)
            state.setdefault('restart', True)
            result = self.__doRun(settings, RunCtx(cache, **state), byRequest=True)
            if not result:
                self.__restoreID = None
            return result

    def areSettingsEnabled(self, settingsID):
        settings = self.__settings.getSettings(settingsID)
        if settings is None:
            LOG_ERROR('Can not find settings', settingsID)
            return False
        else:
            return _settings.createTutorialElement(settings.reqs).isEnabled()

    def stop(self, restore = True):
        self.__doStop(reason=_STOP_REASON.PLAYER_ACTION)
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

    def __doAutoRun(self, seq, runCtx):
        for settings in seq:
            if self.__doRun(settings, runCtx):
                return

    def __doRun(self, settings, runCtx, byRequest = False):
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
            runCtx.cache.setSpace(settings.space)
            if byRequest:
                runCtx.cache.setRefused(False)
            reqs.prepare(runCtx)
            if not reqs.process(descriptor, runCtx):
                return False
            self.clear()
            tutorial = Tutorial(settings, descriptor)
            result = tutorial.run(weakref.proxy(self.__dispatcher), runCtx)
            if result:
                self.__tutorial = tutorial
                self.__tutorial.onStopped += self.__onTutorialStopped
            return result

    def __doStop(self, reason = _STOP_REASON.DEFAULT):
        if self.__tutorial is not None:
            self.__tutorial.onStopped -= self.__onTutorialStopped
            self.__tutorial.stop(reason=reason)
            self.__tutorial = None
        return

    def __doStopHints(self):
        if self.__hintsManager is not None:
            self.__hintsManager.stop()
        return

    def __doClear(self, reason = _STOP_REASON.DEFAULT):
        self.__restoreID = None
        self.__doStop(reason=reason)
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

    def __pe_onGuiCacheSyncCompleted(self, ctx):
        if 'databaseID' in ctx:
            databaseID = ctx['databaseID']
            isFirstStart = databaseID not in self.__loggedDBIDs
            self.__loggedDBIDs.add(databaseID)
        else:
            isFirstStart = False
        cache = _cache.TutorialCache(BigWorld.player().name)
        cache.read()
        runCtx = RunCtx(cache, isFirstStart=isFirstStart, isAfterBattle=self.__afterBattle, **ctx)
        self.__setDispatcher(_LOBBY_DISPATCHER)
        self.__restoreID = _SETTINGS.QUESTS.id
        self.__doAutoRun((_SETTINGS.OFFBATTLE, _SETTINGS.QUESTS), runCtx)
        self.__hintsManager = HintsManager()
        self.__hintsManager.start()

    def __pe_onAvatarBecomePlayer(self):
        self.__afterBattle = True
        self.__doClear()

    def __cm_onDisconnected(self):
        self.__afterBattle = False
        self.__doClear(reason=_STOP_REASON.DISCONNECT)

    def __onTutorialStopped(self):
        self.__doRestore()


g_loader = None

def init():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        g_loader = TutorialLoader()
        g_loader.init()


def fini():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        if g_loader is not None:
            g_loader.fini()
            g_loader = None
    return
