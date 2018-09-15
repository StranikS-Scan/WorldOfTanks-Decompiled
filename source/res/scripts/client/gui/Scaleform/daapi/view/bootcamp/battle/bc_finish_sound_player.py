# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/bootcamp/battle/bc_finish_sound_player.py
import SoundGroups
from PlayerEvents import g_playerEvents
from gui.Scaleform.daapi.view.battle.shared.finish_sound_player import FinishSoundPlayer
from gui.battle_control.view_components import IViewComponentsCtrlListener

class BCFinishSoundPlayer(FinishSoundPlayer, IViewComponentsCtrlListener):
    """ This is functionality that moved from BootcampFinishSoundController
    """

    def __init__(self):
        super(BCFinishSoundPlayer, self).__init__()
        self.__soundID = None
        g_playerEvents.onBootcampRoundFinished += self.__onBcRoundFinished
        return

    def detachedFromCtrl(self, ctrlID):
        g_playerEvents.onBootcampRoundFinished -= self.__onBcRoundFinished

    def _playSound(self, soundID):
        self.__soundID = soundID

    def __onBcRoundFinished(self):
        if self.__soundID:
            SoundGroups.g_instance.playSound2D(self.__soundID)
