# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/hangar_carousel_filter_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class FilterKeys(Enum):
    ISFAVORITE = 'isFavorite'
    ISPREMIUM = 'isPremium'
    ISRENT = 'isRent'
    ISELITE = 'isElite'
    VEHICLETYPE = 'vehicleType'
    NATION = 'nation'
    SEARCHNAME = 'searchName'


class HangarCarouselFilterViewModel(ViewModel):
    __slots__ = ('onFiltered', 'onReset')

    def __init__(self, properties=7, commands=2):
        super(HangarCarouselFilterViewModel, self).__init__(properties=properties, commands=commands)

    def getIsPremium(self):
        return self._getBool(0)

    def setIsPremium(self, value):
        self._setBool(0, value)

    def getIsFavorite(self):
        return self._getBool(1)

    def setIsFavorite(self, value):
        self._setBool(1, value)

    def getIsRent(self):
        return self._getBool(2)

    def setIsRent(self, value):
        self._setBool(2, value)

    def getIsElite(self):
        return self._getBool(3)

    def setIsElite(self, value):
        self._setBool(3, value)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def getNations(self):
        return self._getString(5)

    def setNations(self, value):
        self._setString(5, value)

    def getTypes(self):
        return self._getString(6)

    def setTypes(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(HangarCarouselFilterViewModel, self)._initialize()
        self._addBoolProperty('isPremium', False)
        self._addBoolProperty('isFavorite', False)
        self._addBoolProperty('isRent', False)
        self._addBoolProperty('isElite', False)
        self._addStringProperty('name', '')
        self._addStringProperty('nations', '')
        self._addStringProperty('types', '')
        self.onFiltered = self._addCommand('onFiltered')
        self.onReset = self._addCommand('onReset')
