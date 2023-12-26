# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_guest_d_customization_model.py
from enum import Enum, IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_toy_slots_bar_model import NyToySlotsBarModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.ny_sacks_model import NySacksModel

class ViewState(IntEnum):
    EMPTY = 0
    ACTIVE = 1


class WidgetState(Enum):
    UNAVAILABLE = 'unavailable'
    ALLPURCHASED = 'allPurchased'
    LEVEL2 = 'level2'
    LEVEL3 = 'level3'
    LEVEL4 = 'level4'


class NewYearGuestDCustomizationModel(ViewModel):
    __slots__ = ('onGoToGladeView', 'onOpenBuySacksScreen')

    def __init__(self, properties=5, commands=2):
        super(NewYearGuestDCustomizationModel, self).__init__(properties=properties, commands=commands)

    @property
    def toySlotsBar(self):
        return self._getViewModel(0)

    @staticmethod
    def getToySlotsBarType():
        return NyToySlotsBarModel

    @property
    def sacksModel(self):
        return self._getViewModel(1)

    @staticmethod
    def getSacksModelType():
        return NySacksModel

    def getState(self):
        return ViewState(self._getNumber(2))

    def setState(self, value):
        self._setNumber(2, value.value)

    def getWidgetState(self):
        return WidgetState(self._getString(3))

    def setWidgetState(self, value):
        self._setString(3, value.value)

    def getHasWidgetMarker(self):
        return self._getBool(4)

    def setHasWidgetMarker(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(NewYearGuestDCustomizationModel, self)._initialize()
        self._addViewModelProperty('toySlotsBar', NyToySlotsBarModel())
        self._addViewModelProperty('sacksModel', NySacksModel())
        self._addNumberProperty('state')
        self._addStringProperty('widgetState')
        self._addBoolProperty('hasWidgetMarker', False)
        self.onGoToGladeView = self._addCommand('onGoToGladeView')
        self.onOpenBuySacksScreen = self._addCommand('onOpenBuySacksScreen')
