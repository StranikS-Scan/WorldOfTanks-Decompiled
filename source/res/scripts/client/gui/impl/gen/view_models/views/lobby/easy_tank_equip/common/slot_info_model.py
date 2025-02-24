# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/easy_tank_equip/common/slot_info_model.py
from gui.impl.gen.view_models.common.price_model import PriceModel

class SlotInfoModel(PriceModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(SlotInfoModel, self).__init__(properties=properties, commands=commands)

    def getIsInStorage(self):
        return self._getBool(4)

    def setIsInStorage(self, value):
        self._setBool(4, value)

    def getIsOnVehicle(self):
        return self._getBool(5)

    def setIsOnVehicle(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(SlotInfoModel, self)._initialize()
        self._addBoolProperty('isInStorage', False)
        self._addBoolProperty('isOnVehicle', False)
