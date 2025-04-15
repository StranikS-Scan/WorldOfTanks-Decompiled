# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_progression_controller.py
import SoundGroups
from helpers import dependency
from Event import Event
from historical_battles.gui.sounds.sound_constants import HBHangarProgressionEvents
from historical_battles.skeletons.game_controller import IHBProgressionOnTokensController
from historical_battles.skeletons.gui.sound_controller import IHBSoundController

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

    def __onHBProgressionLeave(self):
        SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_EXIT)

    def __playMusicOnProgressionViewLoaded(self):
        if not self.__hbProgression.isFinished:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_START)
        else:
            SoundGroups.g_instance.playSound2D(HBHangarProgressionEvents.PROGRESSION_COMPLETE)
