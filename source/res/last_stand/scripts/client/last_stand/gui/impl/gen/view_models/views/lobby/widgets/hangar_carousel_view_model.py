# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/hangar_carousel_view_model.py
from enum import Enum
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_filter_view_model import HangarCarouselFilterViewModel

class VehicleStates(Enum):
    DEFAULT = 'default'
    LOCKED = 'locked'
    INBATTLE = 'inBattle'
    INPLATOON = 'inPlatoon'
    CREWINCOMPLETE = 'crewIncomplete'
    RENTED = 'rented'
    SUSPENDED = 'suspended'
    REPAIR = 'repair'
    UNTRAINEDCREW = 'untrainedCrew'
    LOWEFFICIENCY = 'lowEfficiency'
    UNSUITABLE = 'unsuitable'


class HangarCarouselViewModel(ViewModel):
    __slots__ = ('onChangeVehicle',)
    LS_CAROUSEL_VEHICLE_TOOLTIP = 'lsCarouselVehicle'

    def __init__(self, properties=5, commands=1):
        super(HangarCarouselViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def filter(self):
        return self._getViewModel(0)

    @staticmethod
    def getFilterType():
        return HangarCarouselFilterViewModel

    def getSelectedVehicle(self):
        return self._getNumber(1)

    def setSelectedVehicle(self, value):
        self._setNumber(1, value)

    def getVehicles(self):
        return self._getString(2)

    def setVehicles(self, value):
        self._setString(2, value)

    def getVehicleDailyCompleted(self):
        return self._getString(3)

    def setVehicleDailyCompleted(self, value):
        self._setString(3, value)

    def getOrderedNations(self):
        return self._getArray(4)

    def setOrderedNations(self, value):
        self._setArray(4, value)

    @staticmethod
    def getOrderedNationsType():
        return unicode

    def _initialize(self):
        super(HangarCarouselViewModel, self)._initialize()
        self._addViewModelProperty('filter', HangarCarouselFilterViewModel())
        self._addNumberProperty('selectedVehicle', 0)
        self._addStringProperty('vehicles', '')
        self._addStringProperty('vehicleDailyCompleted', '')
        self._addArrayProperty('orderedNations', Array())
        self.onChangeVehicle = self._addCommand('onChangeVehicle')
