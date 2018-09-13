# Embedded file name: scripts/client/Vibroeffects/VibroEffect.py
import BigWorld
from Vibroeffects.EffectsSettings import EffectsSettings

class VibroEffect:

    def __init__(self, name, handle, priority, vibrationObject, group):
        self.name = name
        self.group = group
        self.__priority = priority
        self.__vibrationObject = vibrationObject
        self.__isRunning = False
        self.handle = handle
        self.__relativeGain = 100
        self.__requiresGainChange = False
        durationInMs = None
        if self.handle is not None:
            durationInMs = self.__vibrationObject.getEffectLength(self.handle)
        if durationInMs is not None:
            self.__duration = durationInMs / 1000.0
        else:
            self.__duration = None
        self.__count = 0
        self.__startDelayId = None
        self.__stopDelayId = None
        return

    def reInit(self, vibroEffect):
        self.name = vibroEffect.name
        self.handle = vibroEffect.handle
        self.group = vibroEffect.group
        self.__vibrationObject = vibroEffect.__vibrationObject
        self.__isRunning = vibroEffect.__isRunning
        self.__duration = vibroEffect.__duration
        self.__startDelayId = None
        self.__stopDelayId = None
        self.__relativeGain = 100
        self.__requiresGainChange = False
        return

    def destroy(self):
        if self.__startDelayId is not None:
            BigWorld.cancelCallback(self.__startDelayId)
            self.__startDelayId = None
        if self.__stopDelayId is not None:
            BigWorld.cancelCallback(self.__stopDelayId)
            self.__stopDelayId = None
        if self.handle is not None:
            self.__vibrationObject.deleteEffect(self.handle)
        return

    def onStart(self, count = None):
        if self.handle is None:
            return
        else:
            self.__count = count
            if self.__startDelayId is not None:
                BigWorld.cancelCallback(self.__startDelayId)
            self.__startDelayId = BigWorld.callback(EffectsSettings.DELAY_BETWEEN_EFFECTS, self.__delayedStart)
            self.__isRunning = True
            return

    def __delayedStart(self):
        self.__startDelayId = None
        if self.__count is None:
            self.__vibrationObject.startEffect(self.handle, EffectsSettings.COUNT_INFINITY)
        else:
            self.__vibrationObject.startEffect(self.handle, self.__count)
        duration = self.getDuration()
        if duration is not None and self.__count is not None:
            self.__stopDelayId = BigWorld.callback(duration * self.__count, self.onStop)
        return

    def onStop(self):
        if self.__startDelayId is not None:
            BigWorld.cancelCallback(self.__startDelayId)
            self.__startDelayId = None
        self.__stopDelayId = None
        self.__vibrationObject.stopEffect(self.handle)
        self.__stopDelayId = BigWorld.callback(EffectsSettings.DELAY_BETWEEN_EFFECTS, self.__delayedStop)
        return

    def __delayedStop(self):
        self.__stopDelayId = None
        self.__isRunning = False
        return

    def setRelativeGain(self, gain):
        self.__relativeGain = gain
        self.__requiresGainChange = True

    def getRelativeGain(self):
        return self.__relativeGain

    def isRunning(self):
        return self.__isRunning

    def requiresGainChange(self):
        return self.__requiresGainChange

    def getPriority(self):
        return self.__priority

    def getDuration(self):
        return self.__duration
