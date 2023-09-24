# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/filter_toggle_group_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.filter_toggle_button_model import FilterToggleButtonModel

class ToggleGroupType(Enum):
    DEFAULT = 'default'
    NATION = 'nation'
    LOCATION = 'location'
    TANKMANROLE = 'tankmanRole'
    TANKMANKIND = 'tankmanKind'
    VEHICLEGRADE = 'vehicleGrade'
    VEHICLETIER = 'vehicleTier'
    VEHICLETYPE = 'vehicleType'
    PERSONALDATATYPE = 'personalDataType'
    VEHICLECD = 'vehicle'


class FilterToggleGroupModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(FilterToggleGroupModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getId(self):
        return self._getString(1)

    def setId(self, value):
        self._setString(1, value)

    def getType(self):
        return ToggleGroupType(self._getString(2))

    def setType(self, value):
        self._setString(2, value.value)

    def getHasDiscount(self):
        return self._getBool(3)

    def setHasDiscount(self, value):
        self._setBool(3, value)

    def getFilters(self):
        return self._getArray(4)

    def setFilters(self, value):
        self._setArray(4, value)

    @staticmethod
    def getFiltersType():
        return FilterToggleButtonModel

    def _initialize(self):
        super(FilterToggleGroupModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addStringProperty('id', '')
        self._addStringProperty('type')
        self._addBoolProperty('hasDiscount', False)
        self._addArrayProperty('filters', Array())
