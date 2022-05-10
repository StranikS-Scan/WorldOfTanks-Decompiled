# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_answers_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class MapBoxAnswersModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(MapBoxAnswersModel, self).__init__(properties=properties, commands=commands)

    def getIsMultipleChoice(self):
        return self._getBool(0)

    def setIsMultipleChoice(self, value):
        self._setBool(0, value)

    def getVariants(self):
        return self._getArray(1)

    def setVariants(self, value):
        self._setArray(1, value)

    def getSelectedVariants(self):
        return self._getArray(2)

    def setSelectedVariants(self, value):
        self._setArray(2, value)

    def _initialize(self):
        super(MapBoxAnswersModel, self)._initialize()
        self._addBoolProperty('isMultipleChoice', False)
        self._addArrayProperty('variants', Array())
        self._addArrayProperty('selectedVariants', Array())
