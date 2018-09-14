# Embedded file name: scripts/client/tutorial/__init__.py
import weakref
import BigWorld
from tutorial import doc_loader
from tutorial.control import setTutorialProxy, clearTutorialProxy
from tutorial.control import states, summary
from tutorial.control import functional, g_tutorialWeaver
from tutorial.control.context import GlobalStorage
from tutorial.data import chapter
from tutorial.logger import LOG_WARNING, LOG_ERROR, LOG_DEBUG, LOG_MEMORY
from tutorial.settings import TUTORIAL_SETTINGS, TUTORIAL_STOP_REASON

class INITIAL_FLAG(object):
    GUI_LOADED = 1
    CHAPTER_RESOLVED = 2
    INITIALIZED = GUI_LOADED | CHAPTER_RESOLVED


class Tutorial(object):

    def __init__(self, settings):
        super(Tutorial, self).__init__()
        self._cache = None
        self.__callbackID = None
        self._currentChapter = None
        self._currentState = None
        self._settings = settings
        self._ctrlFactory = TUTORIAL_SETTINGS.factory(settings.ctrl)
        self._descriptor = doc_loader.loadDescriptorData(settings.descriptorPath, settings.exParsers)
        self._data = None
        self._tutorialStopped = True
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
        return

    def __del__(self):
        pass

    def run(self, ctx):
        self._cache = ctx.cache
        if self._cache is None:
            LOG_ERROR('Cache is not init.')
            return
        else:
            self._bonuses = self._ctrlFactory.createBonuses(ctx.bonusCompleted)
            self._sound = self._ctrlFactory.createSoundPlayer()
            if not self._tutorialStopped:
                LOG_ERROR('Tutorial is already running.')
                return
            self._gui = TUTORIAL_SETTINGS.factory(self._settings.gui)
            self._gui.onGUILoaded += self.__onGUILoaded
            if not self._gui.init():
                self._gui.onGUILoaded -= self.__onGUILoaded
                LOG_ERROR('GUI can not init. Tutorial is stopping.')
                return
            LOG_DEBUG('Start training', ctx)
            self._tutorialStopped = False
            proxy = weakref.proxy(self)
            setTutorialProxy(proxy)
            if self.__resolveInitialChapter():
                self._gui.setPlayerXPLevel(self._cache.getPlayerXPLevel())
                self._gui.setTrainingRunMode()
                self._gui.loadConfig(self._descriptor.getGuiFilePath())
                self._gui.onMouseClicked += self.__onMouseClicked
                self._gui.onPageChanging += self.__onPageChanging
                self.__tryRunFirstState(INITIAL_FLAG.CHAPTER_RESOLVED)
            return

    def stop(self, finished = False, reason = TUTORIAL_STOP_REASON.DEFAULT):
        if self._tutorialStopped:
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
                self._gui.fini(isItemsRevert=self._descriptor.isItemsRevertIfStop(reason))
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
            self._tutorialStopped = True
            self._initialized = 0
            return

    def refuse(self):
        title = self._data.getTitle()
        description = self._data.getDescription(afterBattle=self._cache.isAfterBattle())
        self._cache.setRefused(True).write()
        level = self._cache.getPlayerXPLevel()
        self.stop(reason=TUTORIAL_STOP_REASON.PLAYER_ACTION)
        dispatcher = TUTORIAL_SETTINGS.getClass(self._settings.gui).getDispatcher()
        if dispatcher is not None:
            dispatcher.setPlayerXPLevel(level)
            dispatcher.setTrainingRestartMode()
            dispatcher.setChapterInfo(title, description)
        return

    def pause(self, ctx):
        self._cache = ctx.cache
        if self._cache is None:
            LOG_ERROR('Cache is not init.')
            return
        else:
            self._bonuses = self._ctrlFactory.createBonuses(ctx.bonusCompleted)
            if self.__resolveInitialChapter():
                chapter = self._descriptor.getChapter(self._currentChapter)
                dispatcher = TUTORIAL_SETTINGS.getClass(self._settings.gui).getDispatcher()
                if dispatcher is not None:
                    dispatcher.setPlayerXPLevel(self._cache.getPlayerXPLevel())
                    dispatcher.setTrainingRestartMode()
                    dispatcher.setChapterInfo(chapter.getTitle(), chapter.getDescription(afterBattle=self._cache.isAfterBattle()))
            self._cache = None
            return

    def restart(self, ctx):
        if ctx.cache:
            ctx.cache.setRefused(False)
        self.run(ctx)

    def reload(self, afterBattle = False):
        if not self._tutorialStopped:
            self._funcScene.reload()
            self._sound.stop()
            self._cache.setAfterBattle(afterBattle).write()
            self._gui.reloadConfig(self._descriptor.getGuiFilePath())
            self._gui.clear()
            doc_loader.clearChapterData(self._data)
            self.loadCurrentChapter(initial=True)
        else:
            LOG_ERROR('Tutorial is not running.')

    def __timeLoop(self):
        self.__callbackID = None
        if not self._tutorialStopped:
            self._tick()
            self.__callbackID = BigWorld.callback(0.1, self.__timeLoop)
        return

    def _tick(self):
        if not self._nextChapter:
            self._currentState._tick()
        else:
            self.loadCurrentChapter()

    def __resolveInitialChapter(self):
        self._currentChapter = None
        bonusCompleted = self._bonuses.getCompleted()
        fromCache = self._cache.currentChapter()
        if fromCache is not None and self._settings.findChapterInCache:
            chapter = self._descriptor.getChapter(fromCache)
            if self._descriptor.isChapterInitial(chapter, bonusCompleted):
                self._currentChapter = fromCache
            else:
                self._cache.clearChapterData()
                LOG_WARNING('Initial chapter not found in cache or bonuses is invalid', fromCache, chapter.getBonusID() if chapter is not None else None, bonusCompleted)
        if self._currentChapter is None:
            self._currentChapter = self._descriptor.getInitialChapterID(completed=bonusCompleted)
        if self._currentChapter is None:
            LOG_ERROR('Initial chapter not found. Tutorial is stopping')
            self.stop(reason=TUTORIAL_STOP_REASON.CRITICAL_ERROR)
            return False
        else:
            return True

    def __tryRunFirstState(self, nextFlag):
        self._initialized |= nextFlag
        if self._initialized == INITIAL_FLAG.INITIALIZED:
            self._currentState = states.TutorialStateLoading()
            self._currentState._tick()
            self.loadCurrentChapter(initial=True)
            self.__timeLoop()

    def loadCurrentChapter(self, initial = False):
        afterBattle = self._cache.isAfterBattle()
        LOG_DEBUG('Chapter is loading', self._currentChapter, afterBattle)
        self._gui.showWaiting('chapter-loading', isSingle=True)
        if self._data is not None:
            self._data.clear()
        chapter = self._descriptor.getChapter(self._currentChapter)
        self._data = doc_loader.loadChapterData(chapter, afterBattle=afterBattle, initial=initial)
        if self._data is None:
            LOG_ERROR('Chapter documentation is not valid. Tutorial is stopping', self._currentChapter)
            self._gui.hideWaiting('chapter-loading')
            self.stop(reason=TUTORIAL_STOP_REASON.CRITICAL_ERROR)
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
        state = states.factory(stateID)
        if state is not None:
            LOG_DEBUG('Set new state', state.__name__)
            self._currentState = state()
        else:
            LOG_ERROR('Can not sets current state', stateID)
        return

    def evaluateState(self):
        if len(self._effectsQueue):
            if not isinstance(self._currentState, states.TutorialStateRunEffects):
                self.setState(states.STATE_RUN_EFFECTS)
        else:
            self.setState(states.STATE_LEARNING)

    def getFirstElementOfTop(self):
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

    def storeEffectsInQueue(self, effects, benefit = False):
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
        self._effectsQueue = []

    def getFlags(self):
        return self._flags

    def getVars(self):
        return self._vars

    def invalidateFlags(self):
        self._funcInfo.invalidate()
        if self._funcScene is not None:
            self._funcScene._sceneToBeUpdated = True
        return

    def goToNextChapter(self, chapterID):
        self._cache.clearChapterData().write()
        self.removeEffectsInQueue()
        self._currentChapter = chapterID
        self._nextChapter = True

    def getNextScene(self):
        return self._nextScene

    def getFunctionalScene(self):
        return self._funcScene

    def setFunctionalScene(self, scene):
        if self._funcScene is not None:
            self._funcScene.leave()
        self._funcScene = self._ctrlFactory.createFuncScene(scene)
        self._funcScene.enter()
        return

    def setDispatcher(self, dispatcher):
        TUTORIAL_SETTINGS.getClass(self._settings.gui).setDispatcher(dispatcher)

    def __onGUILoaded(self):
        self.__tryRunFirstState(INITIAL_FLAG.GUI_LOADED)

    def __onMouseClicked(self, event):
        self._currentState.mouseClicked(event)

    def __onPageChanging(self, sceneID):
        if self._nextScene.getID() == sceneID:
            return
        else:
            scene = self._data.getScene(sceneID)
            if scene is None:
                LOG_WARNING('Scene {0:>s} not found in chapter {1:>s}'.format(sceneID, self._currentChapter))
                return
            self._nextScene = scene
            self.setState(states.STATE_WAIT_SCENE)
            return
