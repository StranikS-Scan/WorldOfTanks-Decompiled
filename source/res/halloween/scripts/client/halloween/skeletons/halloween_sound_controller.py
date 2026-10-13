# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/halloween_sound_controller.py
from __future__ import absolute_import
from skeletons.gui.game_control import IGameController

class IHalloweenSoundController(IGameController):

    def playSoundEvent(self, audioEvent):
        raise NotImplementedError
