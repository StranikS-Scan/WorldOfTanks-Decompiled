# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/shell_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ShellInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShellInfoModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getType(self):
        return self._getString(1)

    def setType(self, value):
        self._setString(1, value)

    def getImageSource(self):
        return self._getResource(2)

    def setImageSource(self, value):
        self._setResource(2, value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ShellInfoModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addResourceProperty('imageSource', R.invalid())
        self._addNumberProperty('count', 0)
