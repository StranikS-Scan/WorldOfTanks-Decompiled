# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_equipment_group_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.wt_equipment_slot_model import WtEquipmentSlotModel

class WtEquipmentGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(WtEquipmentGroupModel, self).__init__(properties=properties, commands=commands)

    def getSlots(self):
        return self._getArray(0)

    def setSlots(self, value):
        self._setArray(0, value)

    @staticmethod
    def getSlotsType():
        return WtEquipmentSlotModel

    def _initialize(self):
        super(WtEquipmentGroupModel, self)._initialize()
        self._addArrayProperty('slots', Array())
