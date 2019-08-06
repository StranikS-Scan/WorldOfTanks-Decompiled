# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/festival_congrats_model.py
from frameworks.wulf import ViewModel

class FestivalCongratsModel(ViewModel):
    __slots__ = ()

    def getElementsCount(self):
        return self._getNumber(0)

    def setElementsCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(FestivalCongratsModel, self)._initialize()
        self._addNumberProperty('elementsCount', 0)
