# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/info_tip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class TipType(Enum):
    INFO = 'info'
    ERROR = 'error'


class InfoTipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(InfoTipModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getText(self):
        return self._getString(1)

    def setText(self, value):
        self._setString(1, value)

    def getType(self):
        return TipType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(InfoTipModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('text', '')
        self._addStringProperty('type')
