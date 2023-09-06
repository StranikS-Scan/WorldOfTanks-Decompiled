# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/collection/page_backgrounds_model.py
from frameworks.wulf import ViewModel

class PageBackgroundsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PageBackgroundsModel, self).__init__(properties=properties, commands=commands)

    def getMain(self):
        return self._getString(0)

    def setMain(self, value):
        self._setString(0, value)

    def getLogicalCircuit(self):
        return self._getString(1)

    def setLogicalCircuit(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(PageBackgroundsModel, self)._initialize()
        self._addStringProperty('main', '')
        self._addStringProperty('logicalCircuit', '')
