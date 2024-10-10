# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/vehicle_node_data.py
from gui.impl.gen.view_models.common.price_model import PriceModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.techtree.item_unlock import ItemUnlock

class VehicleNodeData(VehicleInfoModel):
    __slots__ = ()

    def __init__(self, properties=14, commands=0):
        super(VehicleNodeData, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(10)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def unlock(self):
        return self._getViewModel(11)

    @staticmethod
    def getUnlockType():
        return ItemUnlock

    def getNodeId(self):
        return self._getNumber(12)

    def setNodeId(self, value):
        self._setNumber(12, value)

    def getCanAddToCompare(self):
        return self._getBool(13)

    def setCanAddToCompare(self, value):
        self._setBool(13, value)

    def _initialize(self):
        super(VehicleNodeData, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('unlock', ItemUnlock())
        self._addNumberProperty('nodeId', 0)
        self._addBoolProperty('canAddToCompare', False)
