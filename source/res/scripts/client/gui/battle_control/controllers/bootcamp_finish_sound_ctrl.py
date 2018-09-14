# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/bootcamp_finish_sound_ctrl.py
import SoundGroups
from finish_sound_ctrl import FinishSoundController
from PlayerEvents import g_playerEvents

class BootcampFinishSoundController(FinishSoundController):

    def __init__(self):
        super(BootcampFinishSoundController, self).__init__()
        self.__soundID = None
        return

    def startControl(self, battleCtx, arenaVisitor):
        super(BootcampFinishSoundController, self).startControl(battleCtx, arenaVisitor)
        g_playerEvents.onBootcampRoundFinished += self.__playSound

    def stopControl(self):
        super(BootcampFinishSoundController, self).stopControl()
        g_playerEvents.onBootcampRoundFinished -= self.__playSound

    def setFinishSound(self, finishSound):
        self.__soundID = finishSound

    def _playSound(self, soundID):
        self.setFinishSound(soundID)

    def __playSound(self):
        if self.__soundID:
            SoundGroups.g_instance.playSound2D(self.__soundID)
