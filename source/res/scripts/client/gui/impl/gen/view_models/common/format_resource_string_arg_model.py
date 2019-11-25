# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/format_resource_string_arg_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class FormatResourceStringArgModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FormatResourceStringArgModel, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getResource(0)

    def setValue(self, value):
        self._setResource(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(FormatResourceStringArgModel, self)._initialize()
        self._addResourceProperty('value', R.invalid())
        self._addStringProperty('name', '')
