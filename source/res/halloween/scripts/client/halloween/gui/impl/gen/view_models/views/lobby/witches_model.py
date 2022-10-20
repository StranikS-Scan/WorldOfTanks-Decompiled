# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/witches_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.witch_item_model import WitchItemModel

class WidgetTypeEnum(Enum):
    HANGAR = 'hangar'
    META = 'meta'


class WitchesModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(WitchesModel, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return WidgetTypeEnum(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getWitches(self):
        return self._getArray(1)

    def setWitches(self, value):
        self._setArray(1, value)

    @staticmethod
    def getWitchesType():
        return WitchItemModel

    def _initialize(self):
        super(WitchesModel, self)._initialize()
        self._addStringProperty('type')
        self._addArrayProperty('witches', Array())
        self.onClick = self._addCommand('onClick')
