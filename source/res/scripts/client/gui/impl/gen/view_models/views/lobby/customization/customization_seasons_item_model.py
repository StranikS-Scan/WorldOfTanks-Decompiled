# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_seasons_item_model.py
from frameworks.wulf import ViewModel

class CustomizationSeasonsItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CustomizationSeasonsItemModel, self).__init__(properties=properties, commands=commands)

    def getIsFull(self):
        return self._getBool(0)

    def setIsFull(self, value):
        self._setBool(0, value)

    def getIsSelected(self):
        return self._getBool(1)

    def setIsSelected(self, value):
        self._setBool(1, value)

    def getSeason(self):
        return self._getString(2)

    def setSeason(self, value):
        self._setString(2, value)

    def getItemNotificationCount(self):
        return self._getNumber(3)

    def setItemNotificationCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CustomizationSeasonsItemModel, self)._initialize()
        self._addBoolProperty('isFull', False)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('season', '')
        self._addNumberProperty('itemNotificationCount', 0)
