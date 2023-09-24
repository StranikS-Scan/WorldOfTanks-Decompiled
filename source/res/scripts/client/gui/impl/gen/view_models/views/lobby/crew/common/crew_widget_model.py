# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.buttons_bar_model import ButtonsBarModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_slot_model import CrewWidgetSlotModel

class CrewWidgetModel(ViewModel):
    __slots__ = ('onSlotClick', 'onChangeCrewClick', 'onDogMoreInfoClick')

    def __init__(self, properties=11, commands=3):
        super(CrewWidgetModel, self).__init__(properties=properties, commands=commands)

    @property
    def buttonsBar(self):
        return self._getViewModel(0)

    @staticmethod
    def getButtonsBarType():
        return ButtonsBarModel

    def getVehicleName(self):
        return self._getString(1)

    def setVehicleName(self, value):
        self._setString(1, value)

    def getVehicleType(self):
        return self._getString(2)

    def setVehicleType(self, value):
        self._setString(2, value)

    def getNation(self):
        return self._getString(3)

    def setNation(self, value):
        self._setString(3, value)

    def getSelectedSlotIdx(self):
        return self._getNumber(4)

    def setSelectedSlotIdx(self, value):
        self._setNumber(4, value)

    def getSlots(self):
        return self._getArray(5)

    def setSlots(self, value):
        self._setArray(5, value)

    @staticmethod
    def getSlotsType():
        return CrewWidgetSlotModel

    def getIsDisabled(self):
        return self._getBool(6)

    def setIsDisabled(self, value):
        self._setBool(6, value)

    def getHasDog(self):
        return self._getBool(7)

    def setHasDog(self, value):
        self._setBool(7, value)

    def getCurrentLayoutID(self):
        return self._getNumber(8)

    def setCurrentLayoutID(self, value):
        self._setNumber(8, value)

    def getPreviousLayoutID(self):
        return self._getNumber(9)

    def setPreviousLayoutID(self, value):
        self._setNumber(9, value)

    def getIsCrewLocked(self):
        return self._getBool(10)

    def setIsCrewLocked(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(CrewWidgetModel, self)._initialize()
        self._addViewModelProperty('buttonsBar', ButtonsBarModel())
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('selectedSlotIdx', 0)
        self._addArrayProperty('slots', Array())
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('hasDog', False)
        self._addNumberProperty('currentLayoutID', 0)
        self._addNumberProperty('previousLayoutID', 0)
        self._addBoolProperty('isCrewLocked', False)
        self.onSlotClick = self._addCommand('onSlotClick')
        self.onChangeCrewClick = self._addCommand('onChangeCrewClick')
        self.onDogMoreInfoClick = self._addCommand('onDogMoreInfoClick')
