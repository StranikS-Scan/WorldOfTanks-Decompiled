# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/train_slot_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class TrainSlotModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(TrainSlotModel, self).__init__(properties=properties, commands=commands)

    def getIsLocked(self):
        return self._getBool(8)

    def setIsLocked(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(TrainSlotModel, self)._initialize()
        self._addBoolProperty('isLocked', False)
