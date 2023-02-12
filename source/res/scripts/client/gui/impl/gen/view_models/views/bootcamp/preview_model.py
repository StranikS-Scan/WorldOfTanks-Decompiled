# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/preview_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PreviewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PreviewModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getResource(1)

    def setDescription(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(PreviewModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addResourceProperty('description', R.invalid())
