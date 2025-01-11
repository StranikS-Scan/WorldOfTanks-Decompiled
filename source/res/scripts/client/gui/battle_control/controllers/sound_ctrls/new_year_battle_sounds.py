# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/sound_ctrls/new_year_battle_sounds.py
import WWISE
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayersBattleController
from helpers import dependency
from skeletons.new_year import INewYearController

class NewYearSoundController(SoundPlayersBattleController):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self):
        super(NewYearSoundController, self).__init__()
        self.__isNyEnabled = self.__nyController.isEnabled()

    def startControl(self, *args):
        if self.__isNyEnabled:
            WWISE.activateRemapping('newYear')
        super(NewYearSoundController, self).startControl(*args)

    def stopControl(self):
        if self.__isNyEnabled:
            WWISE.deactivateRemapping('newYear')
        super(NewYearSoundController, self).stopControl()

    def _initializeSoundPlayers(self):
        return []
