# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/battle/messages/player_messages.py
from comp7_core.gui.Scaleform.daapi.view.battle.messages.player_messages import Comp7CorePlayerMessages
from helpers import dependency
from skeletons.gui.game_control import IComp7LightController

class Comp7LightPlayerMessages(Comp7CorePlayerMessages):
    __comp7LightController = dependency.descriptor(IComp7LightController)

    @property
    def _modeController(self):
        return self.__comp7LightController
