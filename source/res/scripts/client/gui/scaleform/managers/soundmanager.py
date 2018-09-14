# Embedded file name: scripts/client/gui/Scaleform/managers/SoundManager.py
import ResMgr
from Vibroeffects import VibroManager
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui.Scaleform.framework.entities.abstract.SoundManagerMeta import SoundManagerMeta
from gui.doc_loaders.GuiSoundsLoader import GuiSoundsLoader
import SoundGroups

class SoundManager(SoundManagerMeta):

    def __init__(self):
        super(SoundManager, self).__init__()
        self.sounds = GuiSoundsLoader()

    def _populate(self):
        super(SoundManager, self)._populate()
        try:
            self.sounds.load()
        except Exception:
            LOG_ERROR('There is error while loading sounds xml data')
            LOG_CURRENT_EXCEPTION()

    def soundEventHandler(self, soundsTypeSection, state, type, id):
        self.playControlSound(state, type, id)

    def playControlSound(self, state, type, id):
        sound = self.sounds.getControlSound(type, state, id)
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
            if state == 'press':
                VibroManager.g_instance.playButtonClickEffect(type)
        return

    def playEffectSound(self, effectName):
        sound = self.sounds.getEffectSound(effectName)
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound)
        return
