# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/SoundManager.py
import logging
from Vibroeffects import VibroManager
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.entities.abstract.SoundManagerMeta import SoundManagerMeta
from gui.doc_loaders.GuiSoundsLoader import GuiSoundsLoader
import SoundGroups
_logger = logging.getLogger(__name__)

class SoundManager(SoundManagerMeta):

    def __init__(self):
        super(SoundManager, self).__init__()
        self.sounds = GuiSoundsLoader()
        self.__soundObjects = {}

    def _populate(self):
        super(SoundManager, self)._populate()
        try:
            self.sounds.load()
        except Exception:
            LOG_ERROR('There is error while loading sounds xml data')
            LOG_CURRENT_EXCEPTION()

    def soundEventHandler(self, soundsTypeSection, state, eventType, eventID):
        self.playControlSound(state, eventType, eventID)

    def playControlSound(self, state, eventType, eventID):
        sound = self.sounds.getControlSound(eventType, state, eventID)
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
            if state == 'press':
                VibroManager.g_instance.playButtonClickEffect(eventType)
        return

    def playEffectSound(self, effectName):
        sound = self.sounds.getEffectSound(effectName)
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
        else:
            _logger.warning('Sound effect "%s" not found', effectName)
        return

    def playSound2D(self, soundID):
        sound = SoundGroups.g_instance.getSound2D(soundID)
        if sound:
            self.__soundObjects[soundID] = sound
            sound.play()
        else:
            _logger.warning('Could not find 2D sound "%s".', soundID)

    def stopSound2D(self, soundID):
        sound = self.__soundObjects.get(soundID)
        if sound and sound.isPlaying:
            sound.stop()
