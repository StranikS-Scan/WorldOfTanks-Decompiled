# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/shell_slot_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.shell_specification_model import ShellSpecificationModel

class ShellSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(ShellSlotModel, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(13)

    def setCount(self, value):
        self._setNumber(13, value)

    def getType(self):
        return self._getString(14)

    def setType(self, value):
        self._setString(14, value)

    def getSpecifications(self):
        return self._getArray(15)

    def setSpecifications(self, value):
        self._setArray(15, value)

    def _initialize(self):
        super(ShellSlotModel, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addStringProperty('type', '')
        self._addArrayProperty('specifications', Array())
