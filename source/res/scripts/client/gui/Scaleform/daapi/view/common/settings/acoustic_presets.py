# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/common/settings/acoustic_presets.py
import weakref
from collections import namedtuple
import BigWorld
import SoundGroups
from debug_utils import LOG_WARNING, LOG_ERROR
from gui.Scaleform.genConsts.ACOUSTICS import ACOUSTICS
from shared_utils import findFirst
_SOUND_DELAY = 1.0
PresetItem = namedtuple('PresetItem', 'speakerIDs soundID')
_PRESETS = {ACOUSTICS.TYPE_HEADPHONES: (PresetItem((ACOUSTICS.SPEAKER_ID_LEFT,), 'multichanel_test_L'), PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT,), 'multichanel_test_R')),
 ACOUSTICS.TYPE_LAPTOP: (PresetItem((ACOUSTICS.SPEAKER_ID_LEFT,), 'multichanel_test_L'), PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT,), 'multichanel_test_R')),
 ACOUSTICS.TYPE_ACOUSTIC_20: (PresetItem((ACOUSTICS.SPEAKER_ID_LEFT, ACOUSTICS.SPEAKER_ID_SUB), 'multichanel_test_L'), PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT, ACOUSTICS.SPEAKER_ID_SUB), 'multichanel_test_R')),
 ACOUSTICS.TYPE_ACOUSTIC_51: (PresetItem((ACOUSTICS.SPEAKER_ID_LEFT_FRONT,), 'multichanel_test_L'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT_FRONT,), 'multichanel_test_R'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_CENTER,), 'multichanel_test_C'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_SUB,), 'multichanel_test_LFE'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_LEFT,), 'multichanel_test_SL'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT,), 'multichanel_test_SR')),
 ACOUSTICS.TYPE_ACOUSTIC_71: (PresetItem((ACOUSTICS.SPEAKER_ID_LEFT_FRONT,), 'multichanel_test_L'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT_FRONT,), 'multichanel_test_R'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_CENTER,), 'multichanel_test_C'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_SUB,), 'multichanel_test_LFE'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_LEFT_BACK,), 'multichanel_test_BL'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT_BACK,), 'multichanel_test_BR'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_LEFT,), 'multichanel_test_SL'),
                              PresetItem((ACOUSTICS.SPEAKER_ID_RIGHT,), 'multichanel_test_SR'))}

class AcousticPresetsPlayer(object):
    """Class to play sounds from specified speakers preset."""

    def __init__(self, view, items):
        super(AcousticPresetsPlayer, self).__init__()
        self.__view = weakref.proxy(view)
        self.__cursor = 0
        self.__items = items
        self.__sound = None
        self.__isPlaying = False
        self.__isPlayRound = True
        self.__callbackID = None
        return

    def clear(self):
        """Clears data."""
        self.__clearCallback()
        self.__stopSound()
        self.__view = None
        self.__cursor = 0
        self.__items = None
        return

    def setupInitState(self):
        """Selects firsts item that can be played at first."""
        self.__cursor = 0
        self.__view.setPauseEnabled(False)
        if len(self.__items):
            self.__view.setItemsSelected(self.__items[0].speakerIDs)

    def play(self):
        """Plays sounds in order that is defined in specified speakers preset."""
        if self.__isPlaying:
            LOG_WARNING('Player is already running')
            return
        self.__isPlayRound = True
        if self.__playNextSound():
            self.__isPlaying = True
            self.__lockView()

    def pause(self):
        """Set pause to play sounds."""
        if not self.__isPlaying:
            LOG_WARNING('Player is not running')
            return
        self.__clearCallback()
        self.__stopSound()
        self.__unlockView(pause=True)
        self.__isPlaying = False

    def reset(self):
        """Stops to play sounds and selects firsts item that can be played at first."""
        self.__clearCallback()
        self.__stopSound()
        self.__unlockView()
        self.__isPlaying = False
        self.__isPlayRound = True
        self.setupInitState()

    def click(self, speakerID):
        """Play single sound for speaker that is selected by player."""
        if self.__isPlaying:
            LOG_WARNING('Player is already running', speakerID)
            return
        else:
            found = findFirst(lambda item: speakerID in item.speakerIDs, self.__items)
            if found is None:
                LOG_ERROR('speakerID is not found in sequence to play', speakerID)
                return
            self.__isPlayRound = False
            self.__cursor = self.__items.index(found)
            if self.__playSound(found):
                self.__isPlaying = True
                self.__lockView()
            return

    def __lockView(self):
        self.__view.setEnabled(False)
        self.__view.setPlayEnabled(False)
        self.__view.setPauseEnabled(True)

    def __unlockView(self, pause=False):
        self.__view.setEnabled(True)
        self.__view.setItemsPlay(None)
        self.__view.setPlayEnabled(True)
        if not pause and self.__isPlayRound:
            self.setupInitState()
        else:
            self.__view.setPauseEnabled(False)
        return

    def __hasNextSound(self):
        return self.__cursor < len(self.__items)

    def __playNextSound(self):
        if self.__hasNextSound():
            if self.__playSound(self.__items[self.__cursor]):
                return True
        return False

    def __playSound(self, item):
        if self.__sound is None:
            self.__sound = SoundGroups.g_instance.getSound2D(item.soundID)
        if self.__sound is not None:
            self.__view.setItemsSelected(item.speakerIDs)
            self.__view.setItemsPlay(item.speakerIDs)
            self.__sound.setCallback(self.__onSoundStop)
            self.__sound.play()
            return True
        else:
            return False
            return

    def __stopSound(self):
        if self.__sound is not None:
            self.__sound.stop()
            self.__sound = None
        return

    def __onSoundStop(self, _):
        self.__stopSound()
        if self.__isPlayRound:
            self.__cursor += 1
        if self.__isPlayRound and self.__hasNextSound():
            self.__setCallback()
        else:
            self.__unlockView()
            self.__isPlaying = False

    def __clearCallback(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def __setCallback(self):
        self.__clearCallback()
        self.__callbackID = BigWorld.callback(_SOUND_DELAY, self.__handleCallback)

    def __handleCallback(self):
        self.__callbackID = None
        if not self.__playNextSound():
            self.__unlockView()
        return


def createPlayer(view, acousticType):
    """Create AcousticPresetsPlayer by specified type of acoustic.
    :param view: instance of view.
    :param acousticType: string containing
    :return: instance of AcousticPresetsPlayer or None.
    """
    if acousticType in _PRESETS:
        return AcousticPresetsPlayer(view, _PRESETS[acousticType])
    else:
        LOG_ERROR('Sound speakers preset is not found', acousticType)
        return None
        return None
