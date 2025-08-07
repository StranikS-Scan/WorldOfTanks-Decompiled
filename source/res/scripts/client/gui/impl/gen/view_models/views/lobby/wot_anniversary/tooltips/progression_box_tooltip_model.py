# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/tooltips/progression_box_tooltip_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.wot_anniversary_bonus_model import WotAnniversaryBonusModel

class State(Enum):
    ACTIVE = 'active'
    RECEIVED = 'received'
    LOCKED = 'locked'


class ProgressionBoxTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ProgressionBoxTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(0)

    def setBonuses(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBonusesType():
        return WotAnniversaryBonusModel

    def getState(self):
        return State(self._getString(1))

    def setState(self, value):
        self._setString(1, value.value)

    def getEnvelopesLeft(self):
        return self._getNumber(2)

    def setEnvelopesLeft(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ProgressionBoxTooltipModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self._addStringProperty('state', State.ACTIVE.value)
        self._addNumberProperty('envelopesLeft', 0)
