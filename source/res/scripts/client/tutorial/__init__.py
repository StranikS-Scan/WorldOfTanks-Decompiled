# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/__init__.py
import weakref
import BigWorld
import Event
from tutorial import doc_loader
from tutorial.control import setTutorialProxy, clearTutorialProxy
from tutorial.control import states, summary
from tutorial.control import functional, g_tutorialWeaver
from tutorial.control.context import GlobalStorage
from tutorial.data import chapter
from tutorial.logger import LOG_WARNING, LOG_ERROR, LOG_DEBUG, LOG_MEMORY
from tutorial.settings import TUTORIAL_SETTINGS
from tutorial.settings import createTutorialElement

class INITIAL_FLAG(object):
    """
    Tutorial initial state flags.
    """
    GUI_LOADED = 1
    CHAPTER_RESOLVED = 2
    INITIALIZED = GUI_LOADED | CHAPTER_RESOLVED


class Tutorial(object):
    """
    Tutorial core class.
    Computation state in each moment may will be represented:
    <D, CTRL, S, IN, OUT>, where
        - D is abstract representation of training.
        - CTRL is control state of the tutorial's core: wait scene,
            play effects, leaning, ...
        - S is tutorial state. It included set of active/inactive flags, values
            of vars.
        - IN is the input stream. Action witch receives from GUI.
        - OUT is the output stream. Commands witch sends to GUI.
    """

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
        self._funcInfo = None
        self._flags = None
        self._vars = None
        self._effectsQueue = []
        self._gui = None
        self._bonuses = None
        self._sound = None
        self._initialized = 0
        self._triggeredEffects = set()
        self.onStarted = Event.Event()
        self.onStopped = Event.Event()
        return

    def __del__(self):
        pass

    def isStopped(self):
        return self._stopped

    def run(self, dispatcher, ctx):
        """
        Begins the process of training.
        :param ctx: instance of RunCtx.
        """
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
            LOG_DEBUG('Start training', ctx)
            self._stopped = False
            proxy = weakref.proxy(self)
            setTutorialProxy(proxy)
            if self.__resolveInitialChapter(ctx):
                self._gui.loadConfig(self._descriptor.getGuiFilePath())
                self._gui.onGUIInput += self.__onGUIInput
                self._gui.onPageChanging += self.__onPageChanging
                self._gui.onItemFound += self.__onItemFound
                self._gui.onItemLost += self.__onItemLost
                self.__tryRunFirstState(INITIAL_FLAG.CHAPTER_RESOLVED)
            self.onStarted()
            return True

    def stop(self, finished=False):
        """
        Stops the process of training.
        :param finished: if it equals True than training completed.
        """
        if self._stopped:
            return
        else:
            if self.__callbackID is not None:
                BigWorld.cancelCallback(self.__callbackID)
                self.__callbackID = None
            if self._funcScene is not None:
                self._funcScene.leave()
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
            self.onStopped()
            return

    def refuse(self):
        """
        Player refuses training.
        """
        self._cache.setRefused(True).write()
        self.stop()

    def restart(self, dispatcher, ctx):
        """
        Restart training if player refused training and he wants training again.
        :param dispatcher: instance of dispatcher.
        :param ctx: see Tutorial.run.
        """
        if ctx.cache:
            ctx.cache.setRefused(False)
        self.run(dispatcher, ctx)

    def reload(self, afterBattle=False):
        """
        Reloads tutorial.
        :param afterBattle: bool.
        """
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
        """
        Loads current chapter: gets chapter summary from descriptor, loads
        full chapter data, creates the flags, creates the vars, gets initial
        scene ID and waits when this scene is loaded.
        :param initial: bool.
        """
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
            self._funcInfo = self._ctrlFactory.createFuncInfo()
            self._funcInfo.invalidate()
            self._nextScene = self._data.getInitialScene()
            self._currentState = states.TutorialStateNextScene()
            LOG_DEBUG('Set new state TutorialStateNextScene', self._nextScene.getID())
            self._nextChapter = False
            self._gui.lock()
            self._gui.hideWaiting('chapter-loading')
            return

    def setState(self, stateID):
        """
        Sets tutorial state: loading, play effects, leaning, ...
        :param stateID: state ID (@see tutorial.control.states.STATE_*)
        """
        state = states.factory(stateID)
        if state is not None:
            LOG_DEBUG('Set new state', state.__name__)
            self._currentState = state()
        else:
            LOG_ERROR('Can not sets current state', stateID)
        return

    def evaluateState(self):
        """
        Evaluate current state, if queue of effects is not empty than current
        state is play effects, otherwise - leaning.
        """
        if len(self._effectsQueue):
            if not isinstance(self._currentState, states.TutorialStateRunEffects):
                self.setState(states.STATE_RUN_EFFECTS)
        else:
            self.setState(states.STATE_LEARNING)

    def getFirstElementOfTop(self):
        """
        Gets top item (list of effects) from effect queue and them removes from
        queue.
        :return: list or None.
        """
        result = None
        if len(self._effectsQueue):
            top = self._effectsQueue[0]
            if not len(top):
                self._effectsQueue.pop(0)
                if len(self._effectsQueue):
                    top = self._effectsQueue[0]
            if len(top):
                result = top.pop(0)
        return result

    def storeEffectsInQueue(self, effects, benefit=False):
        """
        Stores a series of effects in the queue, and changes the state of
            tutorial.
        :param effects: list of effects.
        :param benefit: True - effects insert to head of queue,
            otherwise - tail of queue.
        """
        if effects is None or len(effects) == 0:
            LOG_ERROR('Effect list is not defined')
        else:
            funcEffects = self._ctrlFactory.createFuncEffects(effects)
            if benefit:
                self._effectsQueue.insert(0, funcEffects)
            else:
                self._effectsQueue.append(funcEffects)
        if self._currentState.allowedToSwitch():
            self.setState(states.STATE_RUN_EFFECTS)
        return

    def removeEffectsInQueue(self):
        """
        Removes all effects from queue.
        """
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

    def getSoundPlayer(self):
        return self._sound

    def getGUIProxy(self):
        return self._gui

    def getFlags(self):
        """
        Gets tutorial flag summary.
        :return: object (@see tutorial.control.flags.FlagSummary).
        """
        return self._flags

    def getVars(self):
        """
        Gets tutorial var summary.
        :return: object (@see tutorial.control.gameVars.VarSummary).
        """
        return self._vars

    def invalidateFlags(self):
        """
        Tutorials need to update because value of flag was changed.
        """
        self._funcInfo.invalidate()
        if self._funcScene is not None:
            self._funcScene.invalidate()
        return

    def goToNextChapter(self, chapterID):
        """
        Goes to next chapter.
        :param chapterID: chapter ID (string).
        """
        self._cache.clearChapterData().write()
        self.removeEffectsInQueue()
        self._currentChapter = chapterID
        self._nextChapter = True

    def getNextScene(self, sceneID):
        """
        Gets next loading scene ID.
        :param sceneID: string containing unique scene ID.
        :return: tuple(scene ID (str), is in scene (bool)).
        """
        return (self._nextScene, self._data.isInScene(self._nextScene, sceneID))

    def getFunctionalScene(self):
        """
        Gets object controlled scene.
        :return: object of tutorial.functional.FunctionalScene.
        """
        return self._funcScene

    def setFunctionalScene(self, scene):
        """
        Sets object controlled scene.
        :param scene: object of tutorial.data.Scene.
        """
        if self._funcScene is not None:
            self._funcScene.leave()
        self._funcScene = self._ctrlFactory.createFuncScene(scene)
        self._funcScene.enter()
        return

    def isEffectTriggered(self, effectID):
        return effectID in self._triggeredEffects

    def setEffectTriggered(self, effectID):
        self._triggeredEffects.add(effectID)

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
        """
        Resolves initial chapter when tutorial is loading by following steps:
            1. Double check: received bonuses in the tutorial scenario.
                If they are in the scenario than go to step 2, otherwise
                tutorial is stopping.
            2. Gets current chapter from cache. If current chapter is exists
                in cache and valid then chapter is found, otherwise go to
                step 3.
            3. Resolves chapter by received bonuses.
            4. Double check: current chapter found. If it not found than
                tutorial is stopping.
        :param ctx: @see run.
        :return: True - if initial chapter resolved, otherwise - False.
        """
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
        """
        Starts training process when GUI is loaded and initial chapter is
            resolved.
        :param nextFlag: one of INITIAL_FLAG.*.
        """
        self._initialized |= nextFlag
        if self._initialized == INITIAL_FLAG.INITIALIZED:
            self._currentState = states.TutorialStateLoading()
            self._currentState.tick()
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
            self.setState(states.STATE_WAIT_SCENE)
            return

    def __onItemFound(self, itemID):
        if self._funcScene is not None:
            self._funcScene.addItemOnScene(itemID)
        return

    def __onItemLost(self, itemID):
        if self._funcScene is not None:
            self._funcScene.removeItemFromScene(itemID)
        return
