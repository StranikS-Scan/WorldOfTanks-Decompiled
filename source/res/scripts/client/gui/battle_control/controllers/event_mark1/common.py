# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/event_mark1/common.py
from gui.battle_control.controllers.interfaces import IBattleController
from gui.battle_control.view_components import IViewComponentsController
from gui.battle_control import avatar_getter

class SoundBattleController(IBattleController):

    def startControl(self, *args):
        raise NotImplementedError

    def stopControl(self):
        raise NotImplementedError

    def getControllerID(self):
        raise NotImplementedError

    def _playSound(self, state):
        soundStateMap = self._getSoundMap()
        if state in soundStateMap:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'play'):
                soundID = soundStateMap[state]
                soundNotifications.play(soundID)

    def _getSoundMap(self):
        """
        Implement this method in child classes to return a dict,
        containing {stateName: soundID, ...}
        :return: should be a dict
        """
        raise NotImplementedError


class SoundViewComponentsController(IViewComponentsController, SoundBattleController):

    def startControl(self, *args):
        raise NotImplementedError

    def stopControl(self):
        raise NotImplementedError

    def getControllerID(self):
        raise NotImplementedError

    def setViewComponents(self, *components):
        raise NotImplementedError

    def clearViewComponents(self):
        raise NotImplementedError

    def _getSoundMap(self):
        raise NotImplementedError
