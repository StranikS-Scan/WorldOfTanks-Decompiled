# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/game_control/sounds_controller.py
import enum
import typing
import SoundGroups
import WWISE
from story_mode.gui.story_mode_gui_constants import GAMEMODE_GROUP, GAMEMODE_STATE
if typing.TYPE_CHECKING:
    from story_mode_common.configs.story_mode_missions import SoundsModel
    from story_mode_common.configs.sounds_schema import SoundModel

class DefaultMusic(str, enum.Enum):
    start = 'ob_music_start'
    stop = 'ob_music_stop'


class DefaultAmbience(str, enum.Enum):
    start = 'sm_lobby_enter'
    stop = 'sm_lobby_exit'


class SoundsController(object):

    def __init__(self):
        self.__musicStarted = None
        self.__ambienceStarted = None
        return

    def startMusicAndAmbience(self, soundSchema):
        WWISE.WW_setState(GAMEMODE_GROUP, GAMEMODE_STATE)
        self._startMusic(soundSchema.music if soundSchema else DefaultMusic)
        self._startAmbience(soundSchema.ambience if soundSchema else DefaultAmbience)

    def stopMusicAndAmbience(self):
        self.stopSound(self.__musicStarted)
        self.__musicStarted = None
        self.stopSound(self.__ambienceStarted)
        self.__ambienceStarted = None
        return

    def __startSound(self, currentSound, newSound):
        if currentSound is None or currentSound.start != newSound.start:
            self.stopSound(currentSound)
            self.setStateAndPlaySound(newSound.start, getattr(newSound, 'group', None), getattr(newSound, 'state', None))
            return newSound
        else:
            return currentSound

    def _startMusic(self, music):
        self.__musicStarted = self.__startSound(currentSound=self.__musicStarted, newSound=music if music else DefaultMusic)

    def _startAmbience(self, ambience):
        self.__ambienceStarted = self.__startSound(currentSound=self.__ambienceStarted, newSound=ambience if ambience else DefaultAmbience)

    @staticmethod
    def stopSound(sound):
        if sound is not None:
            SoundGroups.g_instance.playSound2D(sound.stop)
        return

    @staticmethod
    def setStateAndPlaySound(sound, group=None, state=None):
        if state is not None and group is not None:
            WWISE.WW_setState(group, state)
        SoundGroups.g_instance.playSound2D(sound)
        return
