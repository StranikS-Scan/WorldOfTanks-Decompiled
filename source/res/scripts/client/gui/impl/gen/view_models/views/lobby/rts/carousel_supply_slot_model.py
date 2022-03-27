# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/carousel_supply_slot_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.roster_view.roster_supply_view_model import RosterSupplyViewModel

class CarouselSupplySlotModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CarouselSupplySlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def supply(self):
        return self._getViewModel(0)

    def getIsEmpty(self):
        return self._getBool(1)

    def setIsEmpty(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(CarouselSupplySlotModel, self)._initialize()
        self._addViewModelProperty('supply', RosterSupplyViewModel())
        self._addBoolProperty('isEmpty', True)
