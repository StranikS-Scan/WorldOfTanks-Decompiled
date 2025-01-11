# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/sounds/voice_over_phrase_player.py
import SoundGroups
from PlayerEvents import g_playerEvents
from gui.server_events.pm3_constants import VoiceOvers
from helpers.CallbackDelayer import CallbackDelayer

class ScreenConstants(object):
    MAIN_SCREEN = 0
    FIRST_OPERATION_SCREEN = 8
    SECOND_OPERATION_SCREEN = 9
    THIRD_OPERATION_SCREEN = 10
    MAIN_SCREEN_DELAY = 300
    SUB_SCREEN_DELAY = 180
    __ALL_CONSTANTS = {MAIN_SCREEN,
     FIRST_OPERATION_SCREEN,
     SECOND_OPERATION_SCREEN,
     THIRD_OPERATION_SCREEN}
    SOUNDS_MAP = {MAIN_SCREEN: (VoiceOvers.SPLIT_SCREEN_VO, None),
     FIRST_OPERATION_SCREEN: (VoiceOvers.OPERATION_SCREEN_VO, VoiceOvers.SWITCH_OPERATION_01),
     SECOND_OPERATION_SCREEN: (VoiceOvers.OPERATION_SCREEN_VO, VoiceOvers.SWITCH_OPERATION_02),
     THIRD_OPERATION_SCREEN: (VoiceOvers.OPERATION_SCREEN_VO, VoiceOvers.SWITCH_OPERATION_03)}

    @classmethod
    def isValid(cls, screen):
        return screen in cls.__ALL_CONSTANTS


class VoiceOverPhrasePlayer(object):
    __slots__ = ['__screen', '__callbackDelayer', '__isPlaying']

    def __init__(self, screen):
        if not ScreenConstants.isValid(screen):
            raise ValueError('Invalid screen ID: {}'.format(screen))
        self.__screen = screen
        self.__callbackDelayer = CallbackDelayer()
        self.__isPlaying = False

    def start(self):
        if self.__isPlaying:
            return
        self.__isPlaying = True
        self.__playAndScheduleNext()

    def __playAndScheduleNext(self):
        if not self.__isPlaying:
            return
        self.__enableSound()
        delay = ScreenConstants.MAIN_SCREEN_DELAY if self.__screen == ScreenConstants.MAIN_SCREEN else ScreenConstants.SUB_SCREEN_DELAY
        self.__callbackDelayer.delayCallback(delay, self.__playAndScheduleNext)

    def stop(self, skipStopSound=False):
        if not self.__isPlaying:
            return
        self.__isPlaying = False
        self.__callbackDelayer.clearCallbacks()
        if not skipStopSound:
            self.__stopSound()

    def __enableSound(self):
        sound, switch = ScreenConstants.SOUNDS_MAP[self.__screen]
        if switch:
            SoundGroups.g_instance.setSwitch(VoiceOvers.OPERATION_SCREEN_GROUP, switch)
        SoundGroups.g_instance.playSound2D(sound)

    def __stopSound(self):
        SoundGroups.g_instance.playSound2D(VoiceOvers.STOP_SPLIT_SCREEN_VO if self.__screen == ScreenConstants.MAIN_SCREEN else VoiceOvers.STOP_OPERATION_VO)


class VoiceOverHandler(object):

    def __init__(self):
        self.__voPlayer = None
        return

    def createPlayer(self, screenId=ScreenConstants.MAIN_SCREEN):
        if self.__voPlayer:
            return
        g_playerEvents.onDisconnected += self.__onDisconnected
        self.__voPlayer = VoiceOverPhrasePlayer(screenId)
        self.__voPlayer.start()

    def destroyPlayer(self, skipStopSound=False):
        if not self.__voPlayer:
            return
        else:
            g_playerEvents.onDisconnected -= self.__onDisconnected
            self.__voPlayer.stop(skipStopSound=skipStopSound)
            self.__voPlayer = None
            return

    def __onDisconnected(self):
        self.destroyPlayer(skipStopSound=True)
