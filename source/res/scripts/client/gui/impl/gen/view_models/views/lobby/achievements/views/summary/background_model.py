# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/summary/background_model.py
from frameworks.wulf import ViewModel

class BackgroundModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BackgroundModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getImage(self):
        return self._getString(1)

    def setImage(self, value):
        self._setString(1, value)

    def getLabel(self):
        return self._getString(2)

    def setLabel(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(BackgroundModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('image', '')
        self._addStringProperty('label', '')
