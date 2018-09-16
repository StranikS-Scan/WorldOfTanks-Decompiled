# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/View.py
import WWISE
from collections import namedtuple
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
import SoundGroups
from gui.Scaleform.framework.entities.abstract.AbstractViewMeta import AbstractViewMeta
from gui.doc_loaders import hints_layout
from gui.shared.events import FocusEvent
_ViewKey = namedtuple('_ViewKey', ['alias', 'name'])

class ViewKey(_ViewKey):
    """
    Represents View unique key. Consists of view alias and view name. Allows to distinguish views of the same type
    (with the same alias)
    """

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
    """
    View key matcher based on alias only. Used for matching keys
    with dynamically generated names (like dialogs).
    """

    def __eq__(self, other):
        return self.alias == other.alias if isinstance(other, ViewKey) else False


class _ViewSoundsManager(object):
    """
    Represents sound manager that tracks all sounds emitted through it and stops them when the view is destroyed.
    Currently allows to play 2D sounds.
    """

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

    @staticmethod
    def playInstantSound(eventName):
        """ Plays sound immediately, without checking is it already playing or not. Can cause overlapping of sounds.
        Is intended to be used for short sounds like control clicks
        """
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
        """
        Check priorities for given eventName.
        Stop all currently playing inferior sounds.
        If given eventName is blocked by superior playing sounds, return False, otherwise True
        """
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
    """
    Base class for all visual modules. Introduces config fields used to identify and construct view both in
    Python and Flash
    """
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
        """
        Gets view settings.
        :return: an instance of GroupedViewSettings or a derived from it class.
        """
        return self.__settings

    @property
    def key(self):
        """
        Gets view key.
        :return: ViewKey instance
        """
        return self.__key

    @property
    def alias(self):
        """
        Gets view alias.
        :return: string
        """
        return self.__key.alias

    @property
    def uniqueName(self):
        """
        Gets view name.
        :return: string
        """
        return self.__key.name

    @property
    def soundManager(self):
        """
        Gets reference to view's sound manager, that allows to play 2D sounds and to track them. For details please
        see _ViewSoundsManager class description.
        :return: _ViewSoundsManager instance
        """
        return self.__commonSoundManagers.get(self._COMMON_SOUND_SPACE.name) if self._COMMON_SOUND_SPACE else self.__soundsManager

    def isViewModal(self):
        """
        Returns True if view is opened in the model state; otherwise returns False.
        :return: bool
        """
        return self.__settings.isModal

    def getUniqueName(self):
        """
        Gets view name.
        :return: string
        """
        return self.__key.name

    def getSubContainersSettings(self):
        """
        Called by container manager to create and register supported sub containers at runtime.
        
        :return: Tuples of ContainerSettings or an empty tuple if the view has no sub containers.
        """
        return self.settings.containers or ()

    def getCurrentScope(self):
        """
        Returns view scope. See ScopeTemplates
        :return:  an instance of SimpleScope or a derived from it class.
        """
        return self.__scope

    def setCurrentScope(self, scope):
        """
        Sets current view scope if the view supports run-time scope change (see ScopeTemplates.DYNAMIC_SCOPE).
        
        :param scope: an instance of SimpleScope or a derived from it class.
        """
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
        """
        Allays new view settings.
        
        :param settings: new settings (see GroupedViewSettings and derived classes).
        """
        from gui.Scaleform.framework import ScopeTemplates
        if settings is not None:
            self.__settings = settings.toImmutableSettings()
            if self.__settings.scope != ScopeTemplates.DYNAMIC_SCOPE:
                self.__scope = self.__settings.scope
            self.__key = ViewKey(self.__settings.alias, self.uniqueName)
        else:
            LOG_DEBUG('View settings cannot be set to None', self)
        return

    def setUniqueName(self, name):
        """
        Sets view name.
        :param name: string, cannot be None.
        """
        if name is not None:
            self.__key = ViewKey(self.alias, name)
        else:
            LOG_DEBUG('Unique name cannot be set to None', self)
        return

    def setupContextHints(self, hintID):
        """
        Sets up on FE side a context hint with the given ID.
        :param hintID: hint id, represented by string.
        """
        if hintID is not None:
            hintsData = dict(hints_layout.getLayout(hintID))
            if hintsData is not None:
                builder = hintsData.pop('builderLnk', '')
                self.as_setupContextHintBuilderS(builder, hintsData)
            else:
                LOG_ERROR('Hint layout is nor defined', hintID)
        return

    def onFocusIn(self, alias):
        """
        Sends FocusEvent when the view receives focus. Triggered from FE side.
        :param alias: view alias represented by string.
        """
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED))

    def delaySwitchTo(self, viewAlias, freezeCbk, unfreezeCbk):
        return False

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
