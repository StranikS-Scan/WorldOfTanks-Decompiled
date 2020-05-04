# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/framework/entities/view_sound.py
from collections import namedtuple
from gui.Scaleform.framework.entities.view_sound_manager import ViewSoundsManager
CommonSoundSpaceSettings = namedtuple('CommonSoundSpaceSettings', ('name', 'entranceStates', 'exitStates', 'persistentSounds', 'stoppableSounds', 'priorities', 'autoStart', 'enterEvent', 'exitEvent', 'parentSpace'))
CommonSoundSpaceSettings.__new__.func_defaults = (None,) * len(CommonSoundSpaceSettings._fields)

class ViewSoundMixin(object):
    _COMMON_SOUND_SPACE = None
    __commonSoundManagers = {}

    @property
    def soundManager(self):
        return self.__commonSoundManagers.get(self._COMMON_SOUND_SPACE.name) if self._COMMON_SOUND_SPACE else self.__soundsManager

    def _initSoundManager(self):
        if self._COMMON_SOUND_SPACE:
            soundSpaceName = self._COMMON_SOUND_SPACE.name
            if soundSpaceName not in self.__commonSoundManagers:
                self.__commonSoundManagers[soundSpaceName] = ViewSoundsManager()
        else:
            self.__soundsManager = ViewSoundsManager()
        self.soundManager.register(id(self), self._COMMON_SOUND_SPACE)
        if self._COMMON_SOUND_SPACE and self._COMMON_SOUND_SPACE.parentSpace:
            self.__parentManager = self.__commonSoundManagers.get(self._COMMON_SOUND_SPACE.parentSpace)
            if self.__parentManager is not None:
                self.__parentManager.register(id(self), CommonSoundSpaceSettings(autoStart=True))
        else:
            self.__parentManager = None
        return

    def _deinitSoundManager(self):
        self.soundManager.unregister(id(self))
        self.soundManager.clear(requester=id(self))
        if not self.soundManager.isUsed:
            if self._COMMON_SOUND_SPACE and not self._COMMON_SOUND_SPACE.persistentSounds:
                self.__commonSoundManagers.pop(self._COMMON_SOUND_SPACE.name)
        self.__soundsManager = None
        if self.__parentManager is not None:
            self.__parentManager.unregister(id(self))
            self.__parentManager.clear(requester=id(self))
            if not self.__parentManager.isUsed:
                self.__commonSoundManagers.pop(self._COMMON_SOUND_SPACE.parentSpace)
            self.__parentManager = None
        return

    def _startSoundManager(self):
        self.soundManager.startSpace(self._COMMON_SOUND_SPACE)
