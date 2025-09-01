# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/armor_tooltip_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.armor_layer_model import ArmorLayerModel

class ArmorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ArmorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getArmorLayers(self):
        return self._getArray(0)

    def setArmorLayers(self, value):
        self._setArray(0, value)

    @staticmethod
    def getArmorLayersType():
        return ArmorLayerModel

    def _initialize(self):
        super(ArmorTooltipModel, self)._initialize()
        self._addArrayProperty('armorLayers', Array())
