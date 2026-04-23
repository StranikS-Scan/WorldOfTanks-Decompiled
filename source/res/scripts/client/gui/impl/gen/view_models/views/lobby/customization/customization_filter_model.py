# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/customization/customization_filter_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class StructureBlockType(Enum):
    GROUPS = 'groups'
    AVAILABILITY = 'availability'
    ONANOTHERVEH = 'onAnotherVeh'
    SPECIAL = 'special'
    HISTORIC = 'historic'
    EDITABLE = 'editable'
    FORMFACTOR = 'formfactor'
    SORTING = 'sorting'
    PROGRESSIONDECALS = 'progressionDecals'


class CustomizationFilterModel(ViewModel):
    __slots__ = ('openPopoverView', 'clearFilter', 'changeFilter')

    def __init__(self, properties=26, commands=3):
        super(CustomizationFilterModel, self).__init__(properties=properties, commands=commands)

    def getGroups(self):
        return self._getArray(0)

    def setGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getGroupsType():
        return unicode

    def getSelectedGroup(self):
        return self._getNumber(1)

    def setSelectedGroup(self, value):
        self._setNumber(1, value)

    def getAvailability(self):
        return self._getString(2)

    def setAvailability(self, value):
        self._setString(2, value)

    def getOnAnotherVeh(self):
        return self._getBool(3)

    def setOnAnotherVeh(self, value):
        self._setBool(3, value)

    def getIsEnableOnAnotherVeh(self):
        return self._getBool(4)

    def setIsEnableOnAnotherVeh(self, value):
        self._setBool(4, value)

    def getApplied(self):
        return self._getBool(5)

    def setApplied(self, value):
        self._setBool(5, value)

    def getFavorite(self):
        return self._getBool(6)

    def setFavorite(self, value):
        self._setBool(6, value)

    def getHistoric(self):
        return self._getBool(7)

    def setHistoric(self, value):
        self._setBool(7, value)

    def getNonHistoric(self):
        return self._getBool(8)

    def setNonHistoric(self, value):
        self._setBool(8, value)

    def getFantastical(self):
        return self._getBool(9)

    def setFantastical(self, value):
        self._setBool(9, value)

    def getOnlyEditableStyles(self):
        return self._getBool(10)

    def setOnlyEditableStyles(self, value):
        self._setBool(10, value)

    def getOnlyNonEditableStyles(self):
        return self._getBool(11)

    def setOnlyNonEditableStyles(self, value):
        self._setBool(11, value)

    def getOnlyProgressionStyles(self):
        return self._getBool(12)

    def setOnlyProgressionStyles(self, value):
        self._setBool(12, value)

    def getOnlyProgressionDecals(self):
        return self._getBool(13)

    def setOnlyProgressionDecals(self, value):
        self._setBool(13, value)

    def getFormfactor_square(self):
        return self._getBool(14)

    def setFormfactor_square(self, value):
        self._setBool(14, value)

    def getFormfactor_rect1x2(self):
        return self._getBool(15)

    def setFormfactor_rect1x2(self, value):
        self._setBool(15, value)

    def getFormfactor_rect1x3(self):
        return self._getBool(16)

    def setFormfactor_rect1x3(self, value):
        self._setBool(16, value)

    def getFormfactor_rect1x4(self):
        return self._getBool(17)

    def setFormfactor_rect1x4(self, value):
        self._setBool(17, value)

    def getFormfactor_rect1x6(self):
        return self._getBool(18)

    def setFormfactor_rect1x6(self, value):
        self._setBool(18, value)

    def getDisplayGroups(self):
        return self._getArray(19)

    def setDisplayGroups(self, value):
        self._setArray(19, value)

    @staticmethod
    def getDisplayGroupsType():
        return unicode

    def getSelectedDisplayGroup(self):
        return self._getNumber(20)

    def setSelectedDisplayGroup(self, value):
        self._setNumber(20, value)

    def getAllItemsCounter(self):
        return self._getNumber(21)

    def setAllItemsCounter(self, value):
        self._setNumber(21, value)

    def getFilteredItemsCounter(self):
        return self._getNumber(22)

    def setFilteredItemsCounter(self, value):
        self._setNumber(22, value)

    def getNewHiddenItemsCounter(self):
        return self._getNumber(23)

    def setNewHiddenItemsCounter(self, value):
        self._setNumber(23, value)

    def getIsFilteringActive(self):
        return self._getBool(24)

    def setIsFilteringActive(self, value):
        self._setBool(24, value)

    def getStructure(self):
        return self._getArray(25)

    def setStructure(self, value):
        self._setArray(25, value)

    @staticmethod
    def getStructureType():
        return StructureBlockType

    def _initialize(self):
        super(CustomizationFilterModel, self)._initialize()
        self._addArrayProperty('groups', Array())
        self._addNumberProperty('selectedGroup', 0)
        self._addStringProperty('availability', '')
        self._addBoolProperty('onAnotherVeh', False)
        self._addBoolProperty('isEnableOnAnotherVeh', False)
        self._addBoolProperty('applied', False)
        self._addBoolProperty('favorite', False)
        self._addBoolProperty('historic', False)
        self._addBoolProperty('nonHistoric', False)
        self._addBoolProperty('fantastical', False)
        self._addBoolProperty('onlyEditableStyles', False)
        self._addBoolProperty('onlyNonEditableStyles', False)
        self._addBoolProperty('onlyProgressionStyles', False)
        self._addBoolProperty('onlyProgressionDecals', False)
        self._addBoolProperty('formfactor_square', False)
        self._addBoolProperty('formfactor_rect1x2', False)
        self._addBoolProperty('formfactor_rect1x3', False)
        self._addBoolProperty('formfactor_rect1x4', False)
        self._addBoolProperty('formfactor_rect1x6', False)
        self._addArrayProperty('displayGroups', Array())
        self._addNumberProperty('selectedDisplayGroup', 0)
        self._addNumberProperty('allItemsCounter', 0)
        self._addNumberProperty('filteredItemsCounter', 0)
        self._addNumberProperty('newHiddenItemsCounter', 0)
        self._addBoolProperty('isFilteringActive', False)
        self._addArrayProperty('structure', Array())
        self.openPopoverView = self._addCommand('openPopoverView')
        self.clearFilter = self._addCommand('clearFilter')
        self.changeFilter = self._addCommand('changeFilter')
