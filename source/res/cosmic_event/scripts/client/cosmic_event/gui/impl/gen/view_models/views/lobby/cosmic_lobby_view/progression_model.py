# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/lobby/cosmic_lobby_view/progression_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ProgressionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ProgressionModel, self).__init__(properties=properties, commands=commands)

    def getBonuses(self):
        return self._getArray(0)

    def setBonuses(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBonusesType():
        return IconBonusModel

    def getMarsPoints(self):
        return self._getNumber(1)

    def setMarsPoints(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(ProgressionModel, self)._initialize()
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('marsPoints', 0)
