# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tooltips/vehicle_params_tooltip_view_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_category import VehicleParamsCategory
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_item import VehicleParamsItem
from gui.impl.gen.view_models.views.lobby.crew.tooltips.vehicle_params_note import VehicleParamsNote

class VehicleParamsTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(VehicleParamsTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getUnitOfMeasurement(self):
        return self._getString(1)

    def setUnitOfMeasurement(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getHeaderNotes(self):
        return self._getArray(3)

    def setHeaderNotes(self, value):
        self._setArray(3, value)

    @staticmethod
    def getHeaderNotesType():
        return VehicleParamsNote

    def getIcon(self):
        return self._getResource(4)

    def setIcon(self, value):
        self._setResource(4, value)

    def getCategories(self):
        return self._getArray(5)

    def setCategories(self, value):
        self._setArray(5, value)

    @staticmethod
    def getCategoriesType():
        return VehicleParamsCategory

    def getPenalties(self):
        return self._getArray(6)

    def setPenalties(self, value):
        self._setArray(6, value)

    @staticmethod
    def getPenaltiesType():
        return VehicleParamsItem

    def getIsNotFullCrew(self):
        return self._getBool(7)

    def setIsNotFullCrew(self, value):
        self._setBool(7, value)

    def getFooterNotes(self):
        return self._getArray(8)

    def setFooterNotes(self, value):
        self._setArray(8, value)

    @staticmethod
    def getFooterNotesType():
        return VehicleParamsNote

    def getIsAdvanced(self):
        return self._getBool(9)

    def setIsAdvanced(self, value):
        self._setBool(9, value)

    def _initialize(self):
        super(VehicleParamsTooltipViewModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('unitOfMeasurement', '')
        self._addStringProperty('description', '')
        self._addArrayProperty('headerNotes', Array())
        self._addResourceProperty('icon', R.invalid())
        self._addArrayProperty('categories', Array())
        self._addArrayProperty('penalties', Array())
        self._addBoolProperty('isNotFullCrew', False)
        self._addArrayProperty('footerNotes', Array())
        self._addBoolProperty('isAdvanced', False)
