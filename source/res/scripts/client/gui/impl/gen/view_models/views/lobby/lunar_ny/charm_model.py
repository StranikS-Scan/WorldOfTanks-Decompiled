# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/charm_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.bonuses_model import BonusesModel

class CharmType(IntEnum):
    RARE = 0
    COMMON = 1


class CharmModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(CharmModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonuses(self):
        return self._getViewModel(0)

    def getCharmID(self):
        return self._getNumber(1)

    def setCharmID(self, value):
        self._setNumber(1, value)

    def getCharmType(self):
        return CharmType(self._getNumber(2))

    def setCharmType(self, value):
        self._setNumber(2, value.value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def getIsNew(self):
        return self._getBool(4)

    def setIsNew(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(CharmModel, self)._initialize()
        self._addViewModelProperty('bonuses', BonusesModel())
        self._addNumberProperty('charmID', 0)
        self._addNumberProperty('charmType')
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isNew', False)
