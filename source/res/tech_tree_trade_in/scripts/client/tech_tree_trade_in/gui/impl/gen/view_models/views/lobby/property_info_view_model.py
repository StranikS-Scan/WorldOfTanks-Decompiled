# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/property_info_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.subcategory_info_view_model import SubcategoryInfoViewModel

class CategoryType(Enum):
    EXPERIENCE = 'experience'
    EQUIPMENT = 'equipment'
    AMMUNITION = 'ammunition'
    DIRECTIVES = 'directives'
    CONSUMABLES = 'consumables'
    EXTERIORELEMENTS = 'exteriorElements'
    CREW = 'crew'
    FIELDMODIFICATION = 'fieldModification'
    RENTALVEHICLE = 'rentalVehicle'
    MODULES = 'modules'


class PropertyInfoViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PropertyInfoViewModel, self).__init__(properties=properties, commands=commands)

    def getCategoryType(self):
        return CategoryType(self._getString(0))

    def setCategoryType(self, value):
        self._setString(0, value.value)

    def getAmount(self):
        return self._getNumber(1)

    def setAmount(self, value):
        self._setNumber(1, value)

    def getSubcategories(self):
        return self._getArray(2)

    def setSubcategories(self, value):
        self._setArray(2, value)

    @staticmethod
    def getSubcategoriesType():
        return SubcategoryInfoViewModel

    def _initialize(self):
        super(PropertyInfoViewModel, self)._initialize()
        self._addStringProperty('categoryType')
        self._addNumberProperty('amount', 0)
        self._addArrayProperty('subcategories', Array())
