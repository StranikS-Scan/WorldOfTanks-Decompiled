# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/abstract.py
from gui.sounds.sound_constants import SoundSystems, SPEAKERS_CONFIG

class SoundSystemAbstract(object):

    def getID(self):
        raise NotImplementedError

    def init(self):
        pass

    def fini(self):
        pass

    def isMSR(self):
        return False

    def enableDynamicPreset(self):
        pass

    def disableDynamicPreset(self):
        pass

    def setSoundSystem(self, value):
        pass

    def setBassBoost(self, isEnabled):
        pass

    def getSystemSpeakersPresetID(self):
        return SPEAKERS_CONFIG.AUTO_DETECTION

    def getUserSpeakersPresetID(self):
        return SPEAKERS_CONFIG.AUTO_DETECTION

    def setUserSpeakersPresetID(self, presetID):
        pass

    def sendGlobalEvent(self, eventName, **params):
        pass

    def onEnvStart(self, environment):
        pass

    def onEnvStop(self, environment):
        pass

    def __repr__(self):
        return 'SoundSystem(%s)' % SoundSystems.getUserName(self.getID())
