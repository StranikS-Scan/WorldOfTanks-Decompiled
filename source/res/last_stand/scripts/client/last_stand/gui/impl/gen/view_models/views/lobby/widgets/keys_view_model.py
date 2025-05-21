# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/keys_view_model.py
from frameworks.wulf import ViewModel

class KeysViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(KeysViewModel, self).__init__(properties=properties, commands=commands)

    def getKeys(self):
        return self._getNumber(0)

    def setKeys(self, value):
        self._setNumber(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getIsDisabled(self):
        return self._getBool(2)

    def setIsDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(KeysViewModel, self)._initialize()
        self._addNumberProperty('keys', 0)
        self._addBoolProperty('isCompleted', False)
        self._addBoolProperty('isDisabled', False)
        self.onClick = self._addCommand('onClick')
