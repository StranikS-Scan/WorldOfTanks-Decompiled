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

    def tick(self):
        raise NotImplementedError('Method not implemented')

    def allowedToSwitch(self):
        return True

    def setInput(self, _):
        pass

    def unlock(self, targetID):
        pass


class TutorialStateLoading(_TutorialState):

    def tick(self):
        self._gui.clear()


class TutorialStateWaitScene(_TutorialState):

    def __init__(self):
        super(TutorialStateWaitScene, self).__init__()
        self._isAllowedToSwitch = False

    def tick(self):
        nextScene, isInScene = self._tutorial.getNextScene(self._gui.getSceneID())
        if isInScene:
            self._tutorial.setFunctionalScene(nextScene)
            postEffects = nextScene.getPostEffects()
            postEffects = filter(lambda item: functional.FunctionalConditions(item.getConditions()).allConditionsOk(), postEffects)
            self._isAllowedToSwitch = True
            if postEffects:
                self._tutorial.storeEffectsInQueue(postEffects)
            else:
                self._tutorial.evaluateState()

    def allowedToSwitch(self):
        return self._isAllowedToSwitch


class TutorialStateNextScene(_TutorialState):

    def tick(self):
        sceneID = self._gui.getSceneID()
        if sceneID is not None:
            nextScene, isInScene = self._tutorial.getNextScene(sceneID)
            if not isInScene:
                self._gui.goToScene(nextScene.getID())
            self._tutorial.setState(STATE_WAIT_SCENE)
        return


class TutorialStateLearning(_TutorialState):

    def tick(self):
        scene = self._tutorial.getFunctionalScene()
        if scene is not None:
            scene.update()
        return

    def setInput(self, event):
        scene = self._tutorial.getFunctionalScene()
        action = scene.getAction(event)
        if action is not None:
            self._tutorial.storeEffectsInQueue(action.getEffects())
        return


class TutorialStateRunEffects(_TutorialState):

    def __init__(self):
        super(TutorialStateRunEffects, self).__init__()
        self._current = None
        return

    def tick(self):
        if self._current is None or not self._current.isStillRunning():
            self._current = None
            stop = False
            while not stop:
                currentEffect = self._tutorial.getFirstElementOfTop()
                if currentEffect is None:
                    stop = True
                    self._tutorial.evaluateState()
                if currentEffect.isAllConditionsOK():
                    LOG_DEBUG('Trigger effect', currentEffect.getEffect())
                    currentEffect.triggerEffect()
                    targetID = currentEffect.getTargetID()
                    if targetID is not None:
                        self._tutorial.setEffectTriggered(targetID)
                    stop = not currentEffect.isInstantaneous()
                    if stop:
                        self._current = currentEffect

        return

    def allowedToSwitch(self):
        return False

    def setInput(self, event):
        if self._current is not None and self._current.isStillRunning():
            target = self._current.getTarget()
            if target is not None:
                action = target.getAction(event)
                if action is not None:
                    self._tutorial.storeEffectsInQueue(action.getEffects(), benefit=True)
                    self.__clearCurrent()
        else:
            scene = self._tutorial.getFunctionalScene()
            action = scene.getAction(event)
            if action is not None:
                self._tutorial.storeEffectsInQueue(action.getEffects())
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
