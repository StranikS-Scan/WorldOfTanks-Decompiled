# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/voiceover_mixin.py
import SoundGroups
from helpers.dependency import descriptor
from skeletons.gui.detachment import IDetachmentCache
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ISpecialSoundCtrl
from account_helpers.settings_core.options import AltVoicesSetting

class VoiceoverMixin(object):
    __detachmentCache = descriptor(IDetachmentCache)
    __appLoader = descriptor(IAppLoader)
    __specialSounds = descriptor(ISpecialSoundCtrl)

    def __init__(self):
        super(VoiceoverMixin, self).__init__()
        self.__previewSound = None
        self.__currentSoundMode = None
        return

    def _playInstructorVoice(self, instructorInvID):
        if self.__currentSoundMode is None:
            self.__currentSoundMode = SoundGroups.g_instance.soundModes.currentMode
        if self._setInstructorSoundMode(instructorInvID):
            self.__previewSound = SoundGroups.g_instance.getSound2D(self.__appLoader.getApp().soundManager.sounds.getEffectSound(next(AltVoicesSetting.ALT_VOICES_PREVIEW)))
            if self.__previewSound is not None:
                self.__previewSound.play()
        return

    def _setInstructorSoundMode(self, instructorInvID):
        instructorItem = self.__detachmentCache.getInstructor(instructorInvID)
        soundMode = self.__specialSounds.getSoundModeBySpecialVoice(instructorItem.voiceOverID)
        if soundMode is not None:
            SoundGroups.g_instance.soundModes.setMode(soundMode.languageMode)
            return True
        else:
            return False

    def _stopInstructorVoice(self):
        if self.__previewSound is not None:
            self.__previewSound.stop()
        return

    def _restoreSoundMode(self):
        if self.__currentSoundMode is not None:
            SoundGroups.g_instance.soundModes.setMode(self.__currentSoundMode)
        else:
            SoundGroups.g_instance.soundModes.setMode(SoundGroups.SoundModes.DEFAULT_MODE_NAME)
        return
