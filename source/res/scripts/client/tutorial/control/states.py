# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/control/states.py
from tutorial.control import TutorialProxyHolder
from tutorial.control import functional
from tutorial.logger import LOG_DEBUG
STATE_LOADING = 0
STATE_WAIT_SCENE = 1
STATE_NEXT_SCENE = 2
STATE_LEARNING = 3
STATE_RUN_EFFECTS = 4

class _TutorialState(TutorialProxyHolder):

    def destroy(self):
        pass

    def tick(self):
        raise NotImplementedError('Method not implemented')

    def allowedToSwitch(self):
        return True

    def setInput(self, event):
        self._processEvent(event, self._funcChapterCtx, isGlobal=True)
        self._processEvent(event, self._funcScene, isGlobal=False)

    def unlock(self, targetID):
        pass

    def _processEvent(self, event, scope, benefit=False, isGlobal=False):
        action = scope.getAction(event)
        if action is not None:
            self._tutorial.storeEffectsInQueue(action.getEffects(), benefit=benefit, isGlobal=isGlobal)
            return True
        else:
            return False


class TutorialStateLoading(_TutorialState):

    def tick(self):
        self._gui.clear()


class TutorialStateWaitScene(_TutorialState):

    def __init__(self):
        super(TutorialStateWaitScene, self).__init__()
        self._isAllowedToSwitch = False
        self._gui.onPageReady += self.__checkScene

    def destroy(self):
        self._gui.onPageReady -= self.__checkScene

    def tick(self):
        self.__checkScene()

    def allowedToSwitch(self):
        return self._isAllowedToSwitch

    def __checkScene(self, _=None):
        nextScene, isInScene = self._tutorial.getNextScene(self._gui.getSceneID())
        if isInScene:
            self._tutorial.setFunctionalScene(nextScene)
            postEffects = nextScene.getPostEffects()
            postEffects = [ item for item in postEffects if functional.FunctionalConditions(item.getConditions()).allConditionsOk() ]
            self._isAllowedToSwitch = True
            if postEffects:
                self._tutorial.storeEffectsInQueue(postEffects)
            else:
                self._tutorial.evaluateState()


class TutorialStateNextScene(_TutorialState):

    def __init__(self):
        super(TutorialStateNextScene, self).__init__()
        self._gui.onPageReady += self.__checkScene

    def destroy(self):
        self._gui.onPageReady -= self.__checkScene

    def tick(self):
        self.__checkScene()

    def __checkScene(self, _=None):
        sceneID = self._gui.getSceneID()
        nextScene, isInScene = self._tutorial.getNextScene(sceneID)
        if sceneID is not None:
            if not isInScene:
                self._gui.goToScene(nextScene.getID())
            self._tutorial.setState(STATE_WAIT_SCENE)
        elif isInScene:
            self._tutorial.setState(STATE_WAIT_SCENE)
        return


class TutorialStateLearning(_TutorialState):

    def __init__(self):
        super(TutorialStateLearning, self).__init__()
        self._isUpdating = False

    def tick(self):
        self._isUpdating = True
        self._funcChapterCtx.updatePreScene()
        scene = self._tutorial.getFunctionalScene()
        if scene is not None:
            scene.update()
        self._funcChapterCtx.updatePostScene()
        self._isUpdating = False
        self._tutorial.evaluateState()
        return

    def allowedToSwitch(self):
        return not self._isUpdating


class TutorialStateRunEffects(_TutorialState):

    def __init__(self):
        super(TutorialStateRunEffects, self).__init__()
        self._current = None
        self._interrupt = False
        return

    def destroy(self):
        self._interrupt = True
        if self._current is not None:
            self.__clearCurrent()
        return

    def tick(self):
        if self._current is None or not self._current.isStillRunning():
            self._current = None
            stop = False
            while not stop:
                if self._interrupt:
                    break
                currentEffect = self._tutorial.getFirstElementOfTop()
                if currentEffect is None:
                    stop = True
                    self._tutorial.evaluateState()
                if currentEffect.isAllConditionsOK():
                    LOG_DEBUG('Trigger effect', '(GLOBAL)' if currentEffect.isGlobal() else '(SCENE)', currentEffect.getEffect())
                    success = currentEffect.triggerEffect()
                    if self._interrupt:
                        break
                    targetID = currentEffect.getTargetID()
                    if targetID is not None:
                        self._tutorial.setEffectTriggered(targetID)
                    stop = success and not currentEffect.isInstantaneous() and currentEffect.isStillRunning()
                    if stop:
                        self._current = currentEffect
                        self._funcChapterCtx.onStartLongEffect()

        return

    def allowedToSwitch(self):
        return False

    def setInput(self, event):
        if self._current is not None and self._current.isStillRunning():
            target = self._current.getTarget()
            if self._processEvent(event, target, benefit=True, isGlobal=False):
                self.__clearCurrent()
        else:
            super(TutorialStateRunEffects, self).setInput(event)
        return

    def unlock(self, targetID):
        if self._current is not None and self._current.isStillRunning():
            target = self._current.getTarget()
            if hasattr(target, 'getTargetID') and target.getTargetID() == targetID:
                self.__clearCurrent()
        return

    def __clearCurrent(self):
        self._current.stop()
        self._current = None
        return


_statesFactory = {STATE_LOADING: TutorialStateLoading,
 STATE_WAIT_SCENE: TutorialStateWaitScene,
 STATE_NEXT_SCENE: TutorialStateNextScene,
 STATE_LEARNING: TutorialStateLearning,
 STATE_RUN_EFFECTS: TutorialStateRunEffects}

def factory(stateIndex):
    return _statesFactory.get(stateIndex)
