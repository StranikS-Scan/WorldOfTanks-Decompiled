# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/vehicle_hub/views/sub_models/armor_layer_model.py
from frameworks.wulf import ViewModel

class ArmorLayerModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(ArmorLayerModel, self).__init__(properties=properties, commands=commands)

    def getLayerName(self):
        return self._getString(0)

    def setLayerName(self, value):
        self._setString(0, value)

    def getNominalArmor(self):
        return self._getNumber(1)

    def setNominalArmor(self, value):
        self._setNumber(1, value)

    def getImpactAngle(self):
        return self._getNumber(2)

    def setImpactAngle(self, value):
        self._setNumber(2, value)

    def getResultArmor(self):
        return self._getNumber(3)

    def setResultArmor(self, value):
        self._setNumber(3, value)

    def getColor(self):
        return self._getString(4)

    def setColor(self, value):
        self._setString(4, value)

    def getCount(self):
        return self._getNumber(5)

    def setCount(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ArmorLayerModel, self)._initialize()
        self._addStringProperty('layerName', '')
        self._addNumberProperty('nominalArmor', 0)
        self._addNumberProperty('impactAngle', 0)
        self._addNumberProperty('resultArmor', 0)
        self._addStringProperty('color', '')
        self._addNumberProperty('count', 0)
