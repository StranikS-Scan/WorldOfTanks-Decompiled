# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_lootboxes/scripts/client/event_lootboxes/gui/impl/gen/view_models/views/lobby/event_lootboxes/tooltips/infotype_reward_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class InfotypeRewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(InfotypeRewardModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(InfotypeRewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('count', 0)
        self._addResourceProperty('icon', R.invalid())
