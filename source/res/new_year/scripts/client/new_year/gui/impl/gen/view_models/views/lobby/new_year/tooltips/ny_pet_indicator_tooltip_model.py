# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_pet_indicator_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.pet.ny_pet_indicator_model import NyPetIndicatorModel

class NyPetIndicatorTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyPetIndicatorTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIndicator(self):
        return self._getArray(0)

    def setIndicator(self, value):
        self._setArray(0, value)

    @staticmethod
    def getIndicatorType():
        return NyPetIndicatorModel

    def _initialize(self):
        super(NyPetIndicatorTooltipModel, self)._initialize()
        self._addArrayProperty('indicator', Array())
