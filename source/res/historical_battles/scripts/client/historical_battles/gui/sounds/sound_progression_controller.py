# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_progression_controller.py
import HBAccountSettings
import SoundGroups
from datetime import date
from helpers import dependency
from Event import Event
from historical_battles.gui.sounds.sound_constants import HBHangarProgressionEvents
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.sound_controller import IHBSoundController
from historical_battles_common.hb_constants import AccountSettingsKeys

class HBSoundProgressionController(IHBSoundController):
    __hbProgression = dependency.descriptor(IHBProgressionOnTokensController)

    def __init__(self):
        self.onHBProgressionViewLoaded = Event()
        self.onHBProgressionLeave = Event()

    def init(self):
        self.onHBProgressionViewLoaded += self.__onProgressionViewLoaded
        self.onHBProgressionLeave += self.__onHBProgressionLeave

    def fini(self):
        self.onHBProgressionViewLoaded -= self.__onProgressionViewLoaded
        self.onHBProgressionLeave -= self.__onHBProgressionLeave

    def __onProgressionViewLoaded(self):
        self.__playMusicOnProgressionViewLoaded()
        self.__playVoiceOnProgressionViewLoaded()

    def __onHBProgressionLeave(self):
        SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_EXIT)

    def __playMusicOnProgressionViewLoaded(self):
        if not self.__hbProgression.isFinished:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_START)
        else:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_COMPLETE)

    def __playVoiceOnProgressionViewLoaded(self):
        currentDay = date.today().day
        introDatestamp = HBAccountSettings.getSettings(AccountSettingsKeys.PROGRESSION_MUSIC_INTRO_DATESTAMP)
        outroDatestamp = HBAccountSettings.getSettings(AccountSettingsKeys.PROGRESSION_MUSIC_OUTRO_DATESTAMP)
        introWasPlayedOnAccount = HBAccountSettings.getSettings(AccountSettingsKeys.PROGRESSION_INTRO_PLAYED_ON_ACCOUNT)
        if self.__hbProgression.isFirstStage and introDatestamp != currentDay:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_START_VOICE_OVER)
            HBAccountSettings.setSettings(AccountSettingsKeys.PROGRESSION_MUSIC_INTRO_DATESTAMP, currentDay)
            HBAccountSettings.setSettings(AccountSettingsKeys.PROGRESSION_INTRO_PLAYED_ON_ACCOUNT, True)
        elif self.__hbProgression.isFinished and outroDatestamp != currentDay:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_COMPLETE_VOICE_OVER)
            HBAccountSettings.setSettings(AccountSettingsKeys.PROGRESSION_MUSIC_OUTRO_DATESTAMP, currentDay)
        elif not introWasPlayedOnAccount and not self.__hbProgression.isFinished:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_START_VOICE_OVER)
            HBAccountSettings.setSettings(AccountSettingsKeys.PROGRESSION_INTRO_PLAYED_ON_ACCOUNT, True)
