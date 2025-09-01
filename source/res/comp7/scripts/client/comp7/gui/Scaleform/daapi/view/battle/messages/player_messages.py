# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/battle/messages/player_messages.py
from comp7_core.gui.Scaleform.daapi.view.battle.messages.player_messages import Comp7CorePlayerMessages
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7PlayerMessages(Comp7CorePlayerMessages):
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def _modeController(self):
        return self.__comp7Controller
