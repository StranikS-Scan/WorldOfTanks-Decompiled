# Embedded file name: scripts/client/_FMODStubs.py
import Math

class Sound:

    def __init__(self, *args, **kwargs):
        raise TypeError, 'FMOD.Sound is abstract and cannot be directly instanced.'


class SoundParameter:

    def __init__(self, *args, **kwargs):
        raise TypeError, 'FMOD.SoundParameter is abstract and cannot be directly instanced.'


class EventCategory:

    def __init__(self, name):
        self.muted = False
        self.paused = False
        self.volume = 0.0
        self.pitch = 0.0

    def stopAllEvents(self):
        pass


class EventGroup:

    def __init__(self, name):
        self.memoryUsed = 0
        self.isPlaying = False
        self.isLoaded = False

    def loadEventData(self, arg = False):
        pass

    def freeEventData(self, arg = False):
        pass


class EventProject:

    def __init__(self, *args, **kwargs):
        self.memoryUsed = 0

    def stopAllEvents(self, arg = False):
        pass

    def release(self):
        pass


class EventReverb:

    def __init__(self, name):
        self.active = False
        self.position = Math.Vector3(0, 0, 0)
        self.minDistance = 0.0
        self.maxDistance = 0.0


class MusicSystem:

    def __init__(self):
        self.memoryUsed = 0
        self.muted = False
        self.paused = False
        self.volume = 0.0

    def promptCue(self, name):
        pass

    def setParameterValue(self, name, value):
        pass

    def getParameterValue(self, name):
        return 0.0

    def setCallback(self, fn):
        pass

    def reset(self, type, cb):
        pass

    def loadSoundData(self, blocking):
        pass


def getMusicSystem():
    return MusicSystem()


def getSound(*args, **kwargs):
    pass


def playSound(*args, **kwargs):
    pass


def getSoundBanks(*args, **kwargs):
    return []


def loadSoundBankIntoMemory(*args, **kwargs):
    pass


def unloadSoundBankFromMemory(*args, **kwargs):
    pass


def setDefaultSoundProject(*args, **kwargs):
    pass


def loadEventProject(*args, **kwargs):
    pass


def reloadEventProject(*args, **kwargs):
    pass


def unloadEventProject(*args, **kwargs):
    pass


def loadSoundGroup(*args, **kwargs):
    pass


def unloadSoundGroup(*args, **kwargs):
    pass


def setMasterVolume(*args, **kwargs):
    pass


def getFxSoundDuration(*args, **kwargs):
    return 0.0


def registerEventReverb(*args, **kwargs):
    pass


def getEventReverb(*args, **kwargs):
    pass
