# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/ViewSoundManager.py
import WWISE
import SoundGroups
from debug_utils import LOG_WARNING
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader, GuiGlobalSpaceID

class _ViewSoundsManager(object):

    def __init__(self):
        super(_ViewSoundsManager, self).__init__()
        self.__sounds = {}
        self.__exitStates = {}
        self.__soundSpaceSettings = None
        self.__started = False
        self.__consumers = {}
        self.__privateSounds = {}
        return

    @property
    def isUsed(self):
        return bool(self.__consumers or self.__sounds)

    def clear(self, stopPersistent=False, requester=None):
        if not any(self.__consumers.values()):
            self.__stopAllSounds(stopPersistent)
            self.__setStates(self.__exitStates)
            self.__started = False
        if requester in self.__privateSounds:
            self.stopSound(self.__privateSounds[requester])
            del self.__privateSounds[requester]

    def playSound(self, eventName, owner=None):
        sound = self.__sounds.get(eventName, None)
        if owner is not None:
            self.__privateSounds[owner] = eventName
        if sound is None:
            sound = SoundGroups.g_instance.getSound2D(eventName)
            if sound:
                self.__sounds[eventName] = sound
            else:
                LOG_WARNING('Could not find 2D sound {}.'.format(eventName))
        if sound and not sound.isPlaying:
            if self.__invalidatePriority(eventName):
                sound.play()
        return

    def stopSound(self, eventName):
        sound = self.__sounds.get(eventName)
        if sound and sound.isPlaying:
            sound.stop()

    def playInstantSound(self, eventName):
        SoundGroups.g_instance.playSound2D(eventName)

    @staticmethod
    def setState(name, value):
        WWISE.WW_setState(name, value)

    @staticmethod
    def setRTPC(name, value):
        WWISE.WW_setRTCPGlobal(name, value)

    def register(self, consumerID, soundSpaceSettings):
        autoStart = soundSpaceSettings.autoStart if soundSpaceSettings is not None else False
        self.__consumers[consumerID] = autoStart
        return

    def unregister(self, consumerID):
        del self.__consumers[consumerID]

    def startSpace(self, spaceSettings):
        if spaceSettings is None:
            return
        else:
            if not self.__started:
                self.__soundSpaceSettings = spaceSettings
                if spaceSettings.autoStart:
                    for soundName in spaceSettings.persistentSounds + spaceSettings.stoppableSounds:
                        self.playSound(soundName)

                    if spaceSettings.enterEvent:
                        self.playInstantSound(spaceSettings.enterEvent)
                    self.__exitStates = spaceSettings.exitStates
                    self.__started = True
            if spaceSettings.autoStart:
                self.__setStates(spaceSettings.entranceStates)
            return

    def __stopAllSounds(self, stopPersistent):
        if stopPersistent or self.__soundSpaceSettings is None:
            persistentSounds = []
        else:
            persistentSounds = self.__soundSpaceSettings.persistentSounds
        privateSounds = self.__privateSounds.values()
        soundsToDelete = []
        for eventName, sound in self.__sounds.iteritems():
            if eventName in privateSounds:
                continue
            if eventName not in persistentSounds or not sound.isPlaying:
                soundsToDelete.append(eventName)
                if eventName not in persistentSounds:
                    self.stopSound(eventName)

        for eventName in soundsToDelete:
            del self.__sounds[eventName]

        if self.__soundSpaceSettings is not None:
            appLoader = dependency.instance(IAppLoader)
            if appLoader.getSpaceID() != GuiGlobalSpaceID.LOGIN and self.__soundSpaceSettings.exitEvent:
                self.playInstantSound(self.__soundSpaceSettings.exitEvent)
        return

    def __setStates(self, states):
        for stateName, stateValue in states.iteritems():
            self.setState(stateName, stateValue)

    def __invalidatePriority(self, eventName):
        if self.__soundSpaceSettings and eventName in self.__soundSpaceSettings.priorities:
            checkingSuperior = False
            for soundName in self.__soundSpaceSettings.priorities:
                if soundName == eventName:
                    checkingSuperior = True
                if soundName in self.__sounds:
                    if not checkingSuperior:
                        self.stopSound(soundName)
                    elif self.__sounds.get(soundName).isPlaying:
                        return False

        return True
