# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/consumable_slot_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel

class ConsumableSlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(ConsumableSlotModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(15)

    def setDescription(self, value):
        self._setString(15, value)

    def getIsBuiltIn(self):
        return self._getBool(16)

    def setIsBuiltIn(self, value):
        self._setBool(16, value)

    def getItemName(self):
        return self._getString(17)

    def setItemName(self, value):
        self._setString(17, value)

    def getIsBuyMoreDisabled(self):
        return self._getBool(18)

    def setIsBuyMoreDisabled(self, value):
        self._setBool(18, value)

    def _initialize(self):
        super(ConsumableSlotModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addBoolProperty('isBuiltIn', False)
        self._addStringProperty('itemName', '')
        self._addBoolProperty('isBuyMoreDisabled', False)
