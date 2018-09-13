# Embedded file name: scripts/client/tutorial/loader.py
import BigWorld
import weakref
from ConnectionManager import connectionManager
from constants import IS_TUTORIAL_ENABLED
from PlayerEvents import g_playerEvents
from tutorial import Tutorial
from tutorial import TutorialCache
from tutorial.control.context import GlobalStorage, GLOBAL_FLAG
from tutorial.gui import GUIProxy
from tutorial.logger import LOG_ERROR
from tutorial.settings import TUTORIAL_SETTINGS, TUTORIAL_STOP_REASON

class RunCtx(object):
    __slots__ = ['cache',
     'afterBattle',
     'restart',
     'isInRandomQueue',
     'isInPrebattle',
     'isInTutorialQueue',
     'settings',
     'bonusCompleted']

    def __init__(self, **kwargs):
        super(RunCtx, self).__init__()
        self.cache = None
        self.restart = kwargs.get('restart', False)
        self.isInRandomQueue = kwargs.get('isInRandomQueue', False)
        self.isInPrebattle = kwargs.get('prebattleID', 0L) > 0L
        self.isInTutorialQueue = GlobalStorage(GLOBAL_FLAG.IN_QUEUE, kwargs.get('isInTutorialQueue', False))
        self.settings = kwargs.get('settings', TUTORIAL_SETTINGS.DEFAULT_SETTINGS)
        self.bonusCompleted = kwargs.get('bonusCompleted', 0)
        return

    def __repr__(self):
        return 'RunCtx(settings = {0:>s}, bonuses = {1:n}, cache = {2!r:s},  inPrb = {3!r:s}, inQueue = {4!r:s})'.format(self.settings, self.bonusCompleted, self.cache, self.isInPrebattle, self.isInTutorialQueue.value())


class _TutorialLoader(object):

    def __init__(self):
        super(_TutorialLoader, self).__init__()
        self.__afterBattle = False
        self.__tutorial = None
        self.__dispatcher = None
        return

    def init(self):
        g_playerEvents.onAccountShowGUI += self.__pe_onAccountShowGUI
        g_playerEvents.onAvatarBecomePlayer += self.__pe_onAvatarBecomePlayer
        connectionManager.onDisconnected += self.__cm_onDisconnected
        windowsManager = GUIProxy.windowsManager()
        windowsManager.onInitBattleGUI += self.__wm_onInitBattleGUI
        windowsManager.onDestroyBattleGUI += self.__wm_onDestroyBattleGUI

    def fini(self):
        g_playerEvents.onAccountShowGUI -= self.__pe_onAccountShowGUI
        g_playerEvents.onAvatarBecomePlayer -= self.__pe_onAvatarBecomePlayer
        connectionManager.onDisconnected -= self.__cm_onDisconnected
        windowsManager = GUIProxy.windowsManager()
        windowsManager.onInitBattleGUI -= self.__wm_onInitBattleGUI
        windowsManager.onDestroyBattleGUI -= self.__wm_onDestroyBattleGUI
        if self.__tutorial is not None:
            self.__dispatcher.stop()
            self.__tutorial.stop()
        return

    def _clear(self):
        self.__tutorial = None
        return

    @property
    def tutorial(self):
        return self.__tutorial

    @property
    def isAfterBattle(self):
        return self.__afterBattle

    def tryingToRun(self, runCtx):
        settings = TUTORIAL_SETTINGS.getSettings(runCtx.settings)
        if not settings.enabled:
            return
        else:
            runCtx.cache = TutorialCache.TutorialCache(BigWorld.player().name, settings.space)
            reqs = TUTORIAL_SETTINGS.factory(settings.reqs, init=(weakref.proxy(self), runCtx))
            if reqs.isEnabled():
                if self.__tutorial is None or self.__tutorial._settings.id != settings.id:
                    self.__tutorial = Tutorial(settings)
                    if self.__tutorial._descriptor is None:
                        LOG_ERROR('Tutorial descriptor is not valid. Tutorial is not available.')
                        return
                    if self.__dispatcher is not None:
                        self.__dispatcher.stop()
                        self.__dispatcher = None
                    self.__dispatcher = TUTORIAL_SETTINGS.factory(settings.dispatcher)
                self.__dispatcher.start(runCtx)
                self.__tutorial.setDispatcher(weakref.proxy(self.__dispatcher))
                reqs.process()
            return

    def refuse(self):
        if self.__tutorial is not None:
            self.__tutorial.refuse()
        return

    def restart(self, afterBattle = False):
        self.__afterBattle = afterBattle
        self.tryingToRun(RunCtx(restart=True))

    def _doRun(self, ctx):
        if ctx.isInPrebattle:
            self.__tutorial.pause(ctx)
        else:
            self.__tutorial.run(ctx)

    def _doStop(self, reason = TUTORIAL_STOP_REASON.DEFAULT):
        if self.__tutorial is not None:
            self.__tutorial.stop(reason=reason)
        if self.__dispatcher is not None:
            self.__dispatcher.stop()
        return

    def __pe_onAccountShowGUI(self, ctx):
        self.tryingToRun(RunCtx(**ctx))

    def __pe_onAvatarBecomePlayer(self):
        self.__afterBattle = True
        self._doStop()

    def __cm_onDisconnected(self):
        self.__afterBattle = False
        self._doStop(reason=TUTORIAL_STOP_REASON.DISCONNECT)

    def __wm_onInitBattleGUI(self):
        self.tryingToRun(RunCtx(settings='BATTLE'))

    def __wm_onDestroyBattleGUI(self):
        self._doStop()


g_loader = None

def init():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        g_loader = _TutorialLoader()
        g_loader.init()


def fini():
    global g_loader
    if IS_TUTORIAL_ENABLED:
        if g_loader is not None:
            g_loader.fini()
            g_loader = None
    return
