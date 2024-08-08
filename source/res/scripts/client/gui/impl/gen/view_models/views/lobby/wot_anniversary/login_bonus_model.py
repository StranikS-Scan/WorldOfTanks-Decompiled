# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/login_bonus_model.py
from enum import IntEnum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class State(IntEnum):
    LOCKED = 0
    AVAILABLE = 1
    COLLECTED = 2


class LoginBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(LoginBonusModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getNumber(9))

    def setState(self, value):
        self._setNumber(9, value.value)

    def _initialize(self):
        super(LoginBonusModel, self)._initialize()
        self._addNumberProperty('state')
