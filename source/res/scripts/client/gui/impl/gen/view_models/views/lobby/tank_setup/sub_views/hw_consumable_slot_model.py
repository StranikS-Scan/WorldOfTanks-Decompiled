# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/hw_consumable_slot_model.py
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.consumable_slot_model import ConsumableSlotModel

class HwConsumableSlotModel(ConsumableSlotModel):
    __slots__ = ()

    def __init__(self, properties=26, commands=0):
        super(HwConsumableSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsBuyMoreHidden(self):
        return self._getBool(25)

    def setIsBuyMoreHidden(self, value):
        self._setBool(25, value)

    def _initialize(self):
        super(HwConsumableSlotModel, self)._initialize()
        self._addBoolProperty('isBuyMoreHidden', True)
