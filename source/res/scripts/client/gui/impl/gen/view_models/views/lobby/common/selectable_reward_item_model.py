# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/selectable_reward_item_model.py
from frameworks.wulf import ViewModel

class SelectableRewardItemModel(ViewModel):
    __slots__ = ()
    STATE_NORMAL = 'state_normal'
    STATE_LIMITED = 'state_limited'
    STATE_RECEIVED = 'state_received'

    def __init__(self, properties=5, commands=0):
        super(SelectableRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getStorageCount(self):
        return self._getNumber(2)

    def setStorageCount(self, value):
        self._setNumber(2, value)

    def getPackSize(self):
        return self._getNumber(3)

    def setPackSize(self, value):
        self._setNumber(3, value)

    def getState(self):
        return self._getString(4)

    def setState(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SelectableRewardItemModel, self)._initialize()
        self._addStringProperty('type', '')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('storageCount', 0)
        self._addNumberProperty('packSize', 1)
        self._addStringProperty('state', 'state_normal')
