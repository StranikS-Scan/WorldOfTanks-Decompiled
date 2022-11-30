# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_guest_d_customization_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_toy_slots_bar_model import NyToySlotsBarModel

class NewYearGuestDCustomizationModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearGuestDCustomizationModel, self).__init__(properties=properties, commands=commands)

    @property
    def toySlotsBar(self):
        return self._getViewModel(0)

    @staticmethod
    def getToySlotsBarType():
        return NyToySlotsBarModel

    def getHasTutorial(self):
        return self._getBool(1)

    def setHasTutorial(self, value):
        self._setBool(1, value)

    def getShowDogTooltip(self):
        return self._getBool(2)

    def setShowDogTooltip(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearGuestDCustomizationModel, self)._initialize()
        self._addViewModelProperty('toySlotsBar', NyToySlotsBarModel())
        self._addBoolProperty('hasTutorial', False)
        self._addBoolProperty('showDogTooltip', False)
