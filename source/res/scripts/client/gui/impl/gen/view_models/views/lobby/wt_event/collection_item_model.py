# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/collection_item_model.py
from frameworks.wulf import ViewModel

class CollectionItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CollectionItemModel, self).__init__(properties=properties, commands=commands)

    def getBonusId(self):
        return self._getString(0)

    def setBonusId(self, value):
        self._setString(0, value)

    def getTooltipId(self):
        return self._getString(1)

    def setTooltipId(self, value):
        self._setString(1, value)

    def getIsReceived(self):
        return self._getBool(2)

    def setIsReceived(self, value):
        self._setBool(2, value)

    def getIsAnimated(self):
        return self._getBool(3)

    def setIsAnimated(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(CollectionItemModel, self)._initialize()
        self._addStringProperty('bonusId', '')
        self._addStringProperty('tooltipId', '')
        self._addBoolProperty('isReceived', False)
        self._addBoolProperty('isAnimated', False)
