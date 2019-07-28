# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AnimatedScene.py
import random
from functools import partial
import BigWorld
import AnimationSequence
import Math

class AnimatedScene(BigWorld.Entity):

    def __init__(self):
        super(AnimatedScene, self).__init__()
        self._animators = {}
        self._callbackStart = {}
        self._callbackStop = {}

    def prerequisites(self):
        return [AnimationSequence.Loader(self.sequencePath, self.spaceID)]

    def onEnterWorld(self, prereqs):
        delay = 0.0
        for i in range(self.repeat):
            self._callbackStart[i] = BigWorld.callback(delay, partial(self._start, i))
            randomDelay = random.uniform(-self.delayDeviation, self.delayDeviation)
            delay += self.repeatDelay + randomDelay

    def onLeaveWorld(self):
        for i in self._animators:
            if self._callbackStart.get(i):
                BigWorld.cancelCallback(self._callbackStart[i])
                self._callbackStart[i] = None
            if self._callbackStop.get(i):
                BigWorld.cancelCallback(self._callbackStop[i])
                self._callbackStop[i] = None
            self._stop(i)

        return

    def _start(self, i):
        self._callbackStart[i] = None
        model = BigWorld.Model('')
        matrix = Math.Matrix(self.matrix)
        initialOffset = matrix.translation
        initialYPR = Math.Vector3(matrix.yaw, matrix.pitch, matrix.roll)
        randomYPR = [ random.uniform(-self.yprDeviation[c], self.yprDeviation[c]) for c in range(3) ]
        matrix.setRotateYPR(initialYPR + tuple(randomYPR))
        randomOffset = [ random.uniform(-self.offsetDeviation[c], self.offsetDeviation[c]) for c in range(3) ]
        matrix.translation = initialOffset + self.offset + tuple(randomOffset)
        model.addMotor(BigWorld.Servo(matrix))
        self.addModel(model)
        loader = AnimationSequence.Loader(self.sequencePath, self.spaceID)
        animator = loader.loadSync()
        animator.bindTo(AnimationSequence.ModelWrapperContainer(model, self.spaceID))
        animator.start()
        self._animators[i] = animator
        self._callbackStop[i] = BigWorld.callback(self.sequenceDuration, partial(self._stop, i))
        return

    def _stop(self, i):
        self._callbackStop[i] = None
        if self._animators[i]:
            self._animators[i].stop()
            self._animators[i] = None
        return
