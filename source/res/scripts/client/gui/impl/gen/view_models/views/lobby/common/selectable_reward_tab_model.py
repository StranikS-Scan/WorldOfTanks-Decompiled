# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/selectable_reward_tab_model.py
from frameworks.wulf import ViewModel

class SelectableRewardTabModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(SelectableRewardTabModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getLimit(self):
        return self._getNumber(2)

    def setLimit(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(SelectableRewardTabModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('limit', 0)
