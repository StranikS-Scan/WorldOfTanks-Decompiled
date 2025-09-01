# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/widgets/hangar_carousel_view_model.py
from frameworks.wulf import Array, ViewModel
from white_tiger.gui.impl.gen.view_models.views.lobby.widgets.carousel_tank_model import CarouselTankModel

class HangarCarouselViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(HangarCarouselViewModel, self).__init__(properties=properties, commands=commands)

    def getIsDisableAll(self):
        return self._getBool(0)

    def setIsDisableAll(self, value):
        self._setBool(0, value)

    def getTanks(self):
        return self._getArray(1)

    def setTanks(self, value):
        self._setArray(1, value)

    @staticmethod
    def getTanksType():
        return CarouselTankModel

    def _initialize(self):
        super(HangarCarouselViewModel, self)._initialize()
        self._addBoolProperty('isDisableAll', False)
        self._addArrayProperty('tanks', Array())
        self.onClick = self._addCommand('onClick')
