# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/battle/fl_progression_model.py
from frameworks.wulf import ViewModel

class FlProgressionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FlProgressionModel, self).__init__(properties=properties, commands=commands)

    def getCurrent(self):
        return self._getNumber(0)

    def setCurrent(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(FlProgressionModel, self)._initialize()
        self._addNumberProperty('current', 0)
        self._addStringProperty('name', '')
