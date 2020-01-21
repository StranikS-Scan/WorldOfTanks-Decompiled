# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/core.py
import weakref
import BigWorld
import Event
from tutorial import doc_loader
from tutorial.control import g_tutorialWeaver
from tutorial.control import setTutorialProxy, clearTutorialProxy
from tutorial.control import states, summary
from tutorial.control.context import GlobalStorage
from tutorial.logger import LOG_WARNING, LOG_ERROR, LOG_DEBUG
from tutorial.settings import INITIAL_FLAG
from tutorial.settings import createTutorialElement

class Tutorial(object):

    def __init__(self, settings_, descriptor):
        super(Tutorial, self).__init__()
        self._cache = None
        self.__callbackID = None
        self._currentChapter = None
        self._currentState = None
        self._settings = settings_
        self._ctrlFactory = createTutorialElement(settings_.ctrl)
        self._descriptor = descriptor
        self._data = None
        self._stopped = True
        self._nextChapter = False
        self._nextScene = None
        self._funcScene = None
        self._funcChapterCtx = None
        self._flags = None
        self._vars = None
        self._effectsQueue = []
        self._gui = None
        self._bonuses = None
        self._sound = None
        self._initialized = 0
        self._triggeredEffects = set()
        self._sceneChanging = False
        self.onStarted = Event.Event()
        self.onStopped = Event.Event()
        return

    def __del__(self):
        pass

    def isStopped(self):
        return self._stopped

    def run(self, dispatcher, ctx):
        self._cache = ctx.cache
        if self._cache is None:
            LOG_ERROR('Cache is not init.')
            return False
        else:
            self._bonuses = self._ctrlFactory.createBonuses(ctx.bonusCompleted)
            self._sound = self._ctrlFactory.createSoundPlayer()
            GlobalStorage.setFlags(ctx.globalFlags)
            if not self._stopped:
                LOG_ERROR('Tutorial is already running.')
                return False
            self._gui = createTutorialElement(self._settings.gui)
            self._gui.setDispatcher(dispatcher)
            self._gui.onGUILoaded += self.__onGUILoaded
            if not self._gui.init():
                self._gui.onGUILoaded -= self.__onGUILoaded
                self._gui.setDispatcher(None)
                LOG_ERROR('GUI can not init. Tutorial is stopping.')
                return False
            LOG_DEBUG('Start training', self.getID())
            self._stopped = False
            proxy = weakref.proxy(self)
            setTutorialProxy(proxy)
            if self.__resolveInitialChapter(ctx):
                self._gui.loadConfig(self._descriptor.getGuiFilePath())
                self._gui.onGUIInput += self.__onGUIInput
                self._gui.onPageChanging += self.__onPageChanging
                self._gui.onItemFound += self.__onItemFound
                self._gui.onItemLost += self.__onItemLost
                self._gui.onViewLoaded += self.__onViewLoaded
                self._gui.onViewDisposed += self.__onViewDisposed
                if ctx.canResolveChapterOnStart:
                    self.__tryRunFirstState(INITIAL_FLAG.CHAPTER_RESOLVED)
            self.onStarted()
            return True

    def stop(self, finished=False):
        if self._stopped:
            return
        else:
            if self._currentState:
                self._currentState.destroy()
                self._currentState = None
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if self._funcScene is not None:
                self._funcScene.leave()
            if self._funcChapterCtx is not None:
                self._funcChapterCtx.clear()
            if self._data is not None:
                self._data.clear()
            GlobalStorage.clearFlags()
            if self._sound is not None:
                self._sound.stop()
            self._sound = None
            if self._gui is not None:
                self._gui.fini()
            self._gui = None
            if finished:
                self._cache.setFinished(True).write()
            else:
                self._cache.update(self._currentChapter, self._flags.getDict() if self._flags else None)
            self._cache = None
            g_tutorialWeaver.clear()
            clearTutorialProxy()
            self.removeEffectsInQueue()
            self._nextChapter = False
            self._stopped = True
            self._initialized = 0
            self._triggeredEffects.clear()
            LOG_DEBUG('Tutorial is stopped', self.getID())
            self.onStopped()
            return

    def refuse(self):
        self._cache.setRefused(True).write()
        self.stop()

    def restart(self, dispatcher, ctx):
        if ctx.cache:
            ctx.cache.setRefused(False)
        self.run(dispatcher, ctx)

    def reload(self, afterBattle=False):
        if not self._stopped:
            self._funcScene.reload()
            self._sound.stop()
            self._cache.setAfterBattle(afterBattle).write()
            self._gui.reloadConfig(self._descriptor.getGuiFilePath())
            self._gui.clear()
            doc_loader.clearChapterData(self._data)
            self.loadCurrentChapter(initial=True)
        else:
            LOG_ERROR('Tutorial is not running.')

    def loadCurrentChapter(self, initial=False):
        afterBattle = self._cache.isAfterBattle()
        LOG_DEBUG('Chapter is loading', self._currentChapter, afterBattle)
        self._gui.showWaiting('chapter-loading', isSingle=True)
        if self._data is not None:
            self._data.clear()
        chapter_ = self._descriptor.getChapter(self._currentChapter)
        self._data = doc_loader.loadChapterData(chapter_, self._settings.chapterParser, afterBattle=afterBattle, initial=initial)
        if self._data is None:
            LOG_ERROR('Chapter documentation is not valid. Tutorial is stopping', self._currentChapter)
            self._gui.hideWaiting('chapter-loading')
            self.stop()
            return
        else:
            self._flags = summary.FlagSummary(self._data.getFlags(), initial=self._cache.flags())
            self._vars = summary.VarSummary(self._data.getVarSets())
            self._funcChapterCtx = self._ctrlFactory.createFuncChapterCtx()
            self._funcChapterCtx.invalidate()
            self._nextScene = self._data.getInitialScene()
            self._nextChapter = False
            self._gui.lock()
            self._gui.hideWaiting('chapter-loading')
            LOG_DEBUG('Initializing tutorial chapter with state TutorialStateNextScene', self._nextScene.getID())
            self.setState(states.STATE_NEXT_SCENE)
            return

    def setState(self, stateID):
        state = states.factory(stateID)
        if state is not None:
            if not isinstance(self._currentState, state):
                if self._currentState is not None:
                    self._currentState.destroy()
                    self._currentState = None
                LOG_DEBUG('Set new state', state.__name__)
                self._currentState = state()
                self._currentState.tick()
        else:
            LOG_ERROR('Can not sets current state', stateID)
        return

    def evaluateState(self):
        if self._effectsQueue:
            if not isinstance(self._currentState, states.TutorialStateRunEffects):
                self.setState(states.STATE_RUN_EFFECTS)
        elif self._sceneChanging:
            self._sceneChanging = False
            self.setState(states.STATE_WAIT_SCENE)
        else:
            self.setState(states.STATE_LEARNING)

    def getFirstElementOfTop(self):
        result = None
        if self._effectsQueue:
            top = self._effectsQueue[0]
            result = top.pop(0)
            if not top:
                self._effectsQueue.pop(0)
        return result

    def storeEffectsInQueue(self, effects, benefit=False, isGlobal=False):
        if not effects:
            LOG_ERROR('Effect list is not defined')
        else:
            funcEffects = self._ctrlFactory.createFuncEffects(effects)
            for effect in funcEffects:
                effect.setGlobal(isGlobal)

            if benefit:
                self._effectsQueue.insert(0, funcEffects)
            else:
                self._effectsQueue.append(funcEffects)
        if self._currentState is not None and self._currentState.allowedToSwitch():
            self.setState(states.STATE_RUN_EFFECTS)
        return

    def removeEffectsInQueue(self):
        self._effectsQueue = []

    def getSettings(self):
        return self._settings

    def getID(self):
        return self._settings.id

    def getDescriptor(self):
        return self._descriptor

    def getBonuses(self):
        return self._bonuses

    def getCache(self):
        return self._cache

    def getChapterData(self):
        return self._data

    def getChapterFunctionalContext(self):
        return self._funcChapterCtx

    def getSoundPlayer(self):
        return self._sound

    def getGUIProxy(self):
        return self._gui

    def getFlags(self):
        return self._flags

    def getVars(self):
        return self._vars

    def getControlsFactory(self):
        return self._ctrlFactory

    def invalidateFlags(self):
        if self._funcChapterCtx is not None:
            self._funcChapterCtx.invalidate()
        if self._funcScene is not None:
            self._funcScene.invalidate()
        return

    def goToNextChapter(self, chapterID):
        self._cache.clearChapterData().write()
        self.removeEffectsInQueue()
        self._currentChapter = chapterID
        self._nextChapter = True

    def getNextScene(self, sceneID):
        return (self._nextScene, self._data.isInScene(self._nextScene, sceneID))

    def getFunctionalScene(self):
        return self._funcScene

    def setFunctionalScene(self, scene):
        if self._funcScene is not None:
            self._funcScene.leave()
        self._funcScene = self._ctrlFactory.createFuncScene(scene)
        self._funcScene.enter()
        self._funcChapterCtx.invalidate()
        return

    def isEffectTriggered(self, effectID):
        return effectID in self._triggeredEffects

    def setEffectTriggered(self, effectID):
        self._triggeredEffects.add(effectID)

    def unlockState(self, targetID):
        self._currentState.unlock(targetID)

    def startBattle(self):
        self.__tryRunFirstState(INITIAL_FLAG.CHAPTER_RESOLVED)
        return True

    def isAllowedToFight(self):
        return self._funcChapterCtx is None or self._funcChapterCtx.isAllowedToFight()

    def __timeLoop(self):
        self.__callbackID = None
        if not self._stopped:
            self.__tick()
            self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def __tick(self):
        if not self._nextChapter:
            self._currentState.tick()
        else:
            self.loadCurrentChapter()

    def __resolveInitialChapter(self, ctx):
        self._currentChapter = None
        if ctx.initialChapter is not None:
            self._currentChapter = ctx.initialChapter
            return True
        completed = self._bonuses.getCompleted()
        fromCache = self._cache.currentChapter()
        if fromCache is not None and self._settings.findChapterInCache:
            chapter_ = self._descriptor.getChapter(fromCache)
            if self._descriptor.isChapterInitial(chapter_, completed):
                self._currentChapter = fromCache
            else:
                self._cache.clearChapterData()
                LOG_WARNING('Initial chapter not found in cache or bonuses is invalid', fromCache, chapter_.getBonusID() if chapter_ is not None else None, completed)
        if self._currentChapter is None:
            self._currentChapter = self._descriptor.getInitialChapterID(completed=completed)
        if self._currentChapter is None:
            LOG_ERROR('Initial chapter not found. Tutorial is stopping')
            self.stop()
            return False
        else:
            return True

    def __tryRunFirstState(self, nextFlag):
        self._initialized |= nextFlag
        if self._initialized == INITIAL_FLAG.INITIALIZED:
            self.setState(states.STATE_LOADING)
            self.loadCurrentChapter(initial=True)
            self.__timeLoop()

    def __onGUILoaded(self):
        self.__tryRunFirstState(INITIAL_FLAG.GUI_LOADED)

    def __onGUIInput(self, event):
        self._currentState.setInput(event)

    def __onPageChanging(self, sceneID):
        if self._data.isInScene(self._nextScene, sceneID):
            return
        else:
            scene = self._data.getScene(sceneID)
            if scene is None:
                LOG_WARNING('Scene {0:>s} not found in chapter {1:>s}'.format(sceneID, self._currentChapter))
                return
            self._nextScene = scene
            if self._currentState.allowedToSwitch():
                self._sceneChanging = False
                self.setState(states.STATE_WAIT_SCENE)
            else:
                self._sceneChanging = True
                self.evaluateState()
            return

    def __onItemFound(self, itemID):
        if self._funcScene is not None:
            self._funcScene.addItemOnScene(itemID)
        LOG_DEBUG('invalidateFlags from __onItemFound', itemID)
        self.invalidateFlags()
        return

    def __onItemLost(self, itemID):
        if self._funcScene is not None:
            self._funcScene.removeItemFromScene(itemID)
        if self._funcChapterCtx is not None:
            self._funcChapterCtx.onItemLost(itemID)
        LOG_DEBUG('invalidateFlags from __onItemLost', itemID)
        self.invalidateFlags()
        return

    def __onViewLoaded(self, _):
        LOG_DEBUG('invalidateFlags from __onViewLoaded')
        self.invalidateFlags()

    def __onViewDisposed(self, _):
        LOG_DEBUG('invalidateFlags from __onViewDisposed')
        self.invalidateFlags()
