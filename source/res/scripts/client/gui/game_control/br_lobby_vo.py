# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/br_lobby_vo.py
import random
import SoundGroups
import Settings
from Math import Vector3

class BRLobbyVO(object):
    __VO_TOTAL = 26
    __VO_FIRST_ENTRANCE = 'br_vo_story_hello_first'
    __VO_FIRST_ENTRANCE_IN_SESSION = 'br_vo_story_hello'
    __VO_COMMON_PREFIX = 'br_vo_story_'
    __BR_SOUNDS_KEY = 'br_lobby_sounds'
    __BR_INDEX_KEY = 'index'
    __BR_VO_SEQUENCE_KEY = 'vo_sequence'
    __SOUND_POS = Vector3(-25.244, 0.711, 8.99)

    def __init__(self):
        super(BRLobbyVO, self).__init__()
        self.__voSequence = []
        self.__currentIndex = 0
        self.__firstEntrance = not self.__readSettings()
        self.__firstEntranceInSession = True
        self.__sound = None
        if self.__firstEntrance:
            self.__voSequence = [ str(i + 1).zfill(2) for i in range(self.__VO_TOTAL) ]
            random.shuffle(self.__voSequence)
            self.__saveSequence()
        return

    def destroy(self):
        self.destroyVOSound()
        self.__voSequence = None
        return

    def setSwitch(self, group, value):
        if self.__sound is not None:
            self.__sound.setSwitch(group, value)
        return

    def createVOSound(self, wasInBR, soundPos):
        if soundPos is None:
            return
        elif self.__sound is not None:
            return
        else:
            if self.__firstEntrance:
                soundName = self.__VO_FIRST_ENTRANCE
                self.__firstEntrance = False
                self.__firstEntranceInSession = False
            elif self.__firstEntranceInSession:
                soundName = self.__VO_FIRST_ENTRANCE_IN_SESSION
                self.__firstEntranceInSession = False
            elif wasInBR:
                soundName = self.__VO_COMMON_PREFIX + self.__voSequence[self.__currentIndex]
                self.__currentIndex = (self.__currentIndex + 1) % self.__VO_TOTAL
                self.__saveIndex()
            else:
                soundName = None
            if soundName is not None:
                self.__sound = SoundGroups.g_instance.WWgetSoundPos(soundName, 'br_lobby_vo', soundPos)
                if self.__sound is not None:
                    self.__sound.play()
            return

    def restore(self):
        self.__firstEntranceInSession = True

    def destroyVOSound(self):
        if self.__sound is not None:
            if self.__sound.isPlaying:
                self.__sound.stop()
            self.__sound = None
        return

    def __readSettings(self):
        soundPref = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        brSection = soundPref[self.__BR_SOUNDS_KEY]
        if brSection is None:
            return False
        else:
            seqString = brSection.readString(self.__BR_VO_SEQUENCE_KEY)
            if not seqString:
                return False
            self.__voSequence = seqString.split(' ')
            self.__currentIndex = brSection.readInt(self.__BR_INDEX_KEY, 0)
            return True

    def __saveSequence(self):
        soundPref = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES]
        brSection = soundPref[self.__BR_SOUNDS_KEY]
        if brSection is None:
            brSection = soundPref.createSection(self.__BR_SOUNDS_KEY)
        seqString = ' '.join(self.__voSequence)
        brSection.writeString(self.__BR_VO_SEQUENCE_KEY, seqString)
        return

    def __saveIndex(self):
        brSection = Settings.g_instance.userPrefs[Settings.KEY_SOUND_PREFERENCES][self.__BR_SOUNDS_KEY]
        brSection.writeInt(self.__BR_INDEX_KEY, self.__currentIndex)
