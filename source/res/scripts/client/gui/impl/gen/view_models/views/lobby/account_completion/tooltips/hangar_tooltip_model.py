# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/tooltips/hangar_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class HangarTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(HangarTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEmail(self):
        return self._getString(0)

    def setEmail(self, value):
        self._setString(0, value)

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(HangarTooltipModel, self)._initialize()
        self._addStringProperty('email', '')
        self._addArrayProperty('bonuses', Array())
