# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/View.py
from collections import namedtuple
import WWISE
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
import SoundGroups
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.doc_loaders import hints_layout
from gui.shared.events import FocusEvent
_ViewKey = namedtuple('_ViewKey', ['alias', 'name'])

class ViewKey(_ViewKey):

    @staticmethod
    def __new__(cls, alias, name=None):
        if name is None:
            name = alias
        return _ViewKey.__new__(cls, alias, name)

    def __repr__(self):
        return '{}[alias={}, name={}]'.format(self.__class__.__name__, self.alias, self.name)

    def __eq__(self, other):
        return self.name == other.name and self.alias == other.alias if isinstance(other, ViewKey) else False


class ViewKeyDynamic(ViewKey):

    def __eq__(self, other):
        return self.alias == other.alias if isinstance(other, ViewKey) else False


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

                    self.__setStates(spaceSettings.entranceStates)
                    self.__exitStates = spaceSettings.exitStates
                    self.__started = True
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


CommonSoundSpaceSettings = namedtuple('CommonSoundSpaceSettings', ('name', 'entranceStates', 'exitStates', 'persistentSounds', 'stoppableSounds', 'priorities', 'autoStart'))

class View(AbstractViewMeta):
    _COMMON_SOUND_SPACE = None
    __commonSoundManagers = {}

    def __init__(self, *args, **kwargs):
        super(View, self).__init__()
        from gui.Scaleform.framework import ViewSettings
        self.__settings = ViewSettings()
        self.__key = ViewKey(None, None)
        self.__initSoundManager()
        from gui.Scaleform.framework import ScopeTemplates
        self.__scope = ScopeTemplates.DEFAULT_SCOPE
        return

    def __repr__(self):
        return '{}[{}]=[key={}, scope={}, state={}]'.format(self.__class__.__name__, hex(id(self)), self.key, self.__scope, self.getState())

    def __del__(self):
        LOG_DEBUG('View deleted:', self)

    @property
    def settings(self):
        return self.__settings

    @property
    def key(self):
        return self.__key

    @property
    def alias(self):
        return self.__key.alias

    @property
    def uniqueName(self):
        return self.__key.name

    @property
    def soundManager(self):
        return self.__commonSoundManagers.get(self._COMMON_SOUND_SPACE.name) if self._COMMON_SOUND_SPACE else self.__soundsManager

    def isViewModal(self):
        return self.__settings.isModal

    def getUniqueName(self):
        return self.__key.name

    def getSubContainersSettings(self):
        return self.settings.containers or ()

    def getCurrentScope(self):
        return self.__scope

    def setCurrentScope(self, scope):
        from gui.Scaleform.framework import ScopeTemplates
        if self.__settings is not None:
            if self.__settings.scope == ScopeTemplates.DYNAMIC_SCOPE:
                if scope != ScopeTemplates.DYNAMIC_SCOPE:
                    self.__scope = scope
                else:
                    raise Exception('View.__scope cannot be a ScopeTemplates.DYNAMIC value. This value might have only settings.scope for {} view.'.format(self.alias))
            else:
                raise Exception('You can not change a non-dynamic scope. Declare ScopeTemplates.DYNAMIC in settings for {} view'.format(self.alias))
        else:
            LOG_ERROR('Can not change a current scope, until unimplemented __settings ')
        return

    def setSettings(self, settings):
        from gui.Scaleform.framework import ScopeTemplates
        if settings is not None:
            self.__settings = settings.toImmutableSettings()
            if self.__settings.scope != ScopeTemplates.DYNAMIC_SCOPE:
                self.__scope = self.__settings.scope
            self.__key = ViewKey(self.__settings.alias, self.uniqueName)
        else:
            LOG_DEBUG('settings can`t be None!')
        return

    def setUniqueName(self, name):
        if name is not None:
            self.__key = ViewKey(self.alias, name)
        else:
            LOG_DEBUG('Unique name cannot be set to None', self)
        return

    def setupContextHints(self, hintID):
        if hintID is not None:
            hintsData = hints_layout.getLayout(hintID)
            if hintsData is not None:
                tutorialManager = self.app.tutorialManager if self.app is not None else None
                if tutorialManager is not None:
                    viewTutorialID = tutorialManager.getViewTutorialID(self.__key.name)
                    tutorialManager.setupViewContextHints(viewTutorialID, hintsData)
            else:
                LOG_ERROR('Hint layout is nor defined', hintID)
        return

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED))

    def _populate(self):
        super(View, self)._populate()
        self.soundManager.startSpace(self._COMMON_SOUND_SPACE)

    def _destroy(self):
        self.soundManager.unregister(id(self))
        self.soundManager.clear(requester=id(self))
        if not self.soundManager.isUsed:
            if self._COMMON_SOUND_SPACE and not self._COMMON_SOUND_SPACE.persistentSounds:
                self.__commonSoundManagers.pop(self._COMMON_SOUND_SPACE.name)
        super(View, self)._destroy()

    def __initSoundManager(self):
        if self._COMMON_SOUND_SPACE:
            soundSpaceName = self._COMMON_SOUND_SPACE.name
            if soundSpaceName not in self.__commonSoundManagers:
                self.__commonSoundManagers[soundSpaceName] = _ViewSoundsManager()
        else:
            self.__soundsManager = _ViewSoundsManager()
        self.soundManager.register(id(self), self._COMMON_SOUND_SPACE)
