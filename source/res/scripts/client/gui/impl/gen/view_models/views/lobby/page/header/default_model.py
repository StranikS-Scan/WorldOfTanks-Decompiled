# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/header/default_model.py
from frameworks.wulf import ViewModel

class DefaultModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DefaultModel, self).__init__(properties=properties, commands=commands)

    def getOldStyle(self):
        return self._getBool(0)

    def setOldStyle(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(DefaultModel, self)._initialize()
        self._addBoolProperty('oldStyle', False)
