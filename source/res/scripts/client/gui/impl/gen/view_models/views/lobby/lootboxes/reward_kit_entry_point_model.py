# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/reward_kit_entry_point_model.py
from frameworks.wulf import ViewModel

class RewardKitEntryPointModel(ViewModel):
    __slots__ = ('onOpenKit',)

    def __init__(self, properties=5, commands=1):
        super(RewardKitEntryPointModel, self).__init__(properties=properties, commands=commands)

    def getKitsCount(self):
        return self._getNumber(0)

    def setKitsCount(self, value):
        self._setNumber(0, value)

    def getHasNew(self):
        return self._getBool(1)

    def setHasNew(self, value):
        self._setBool(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def getIsExternal(self):
        return self._getBool(3)

    def setIsExternal(self, value):
        self._setBool(3, value)

    def getRealm(self):
        return self._getString(4)

    def setRealm(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RewardKitEntryPointModel, self)._initialize()
        self._addNumberProperty('kitsCount', 0)
        self._addBoolProperty('hasNew', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isExternal', False)
        self._addStringProperty('realm', '')
        self.onOpenKit = self._addCommand('onOpenKit')
