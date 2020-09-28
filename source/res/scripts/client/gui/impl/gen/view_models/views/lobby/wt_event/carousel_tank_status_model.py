# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/carousel_tank_status_model.py
from frameworks.wulf import ViewModel

class CarouselTankStatusModel(ViewModel):
    __slots__ = ('onOpenTasks', 'onBuyTicket')

    def __init__(self, properties=3, commands=2):
        super(CarouselTankStatusModel, self).__init__(properties=properties, commands=commands)

    def getIsHunter(self):
        return self._getBool(0)

    def setIsHunter(self, value):
        self._setBool(0, value)

    def getIsSpecial(self):
        return self._getBool(1)

    def setIsSpecial(self, value):
        self._setBool(1, value)

    def getQuantity(self):
        return self._getNumber(2)

    def setQuantity(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(CarouselTankStatusModel, self)._initialize()
        self._addBoolProperty('isHunter', False)
        self._addBoolProperty('isSpecial', False)
        self._addNumberProperty('quantity', 0)
        self.onOpenTasks = self._addCommand('onOpenTasks')
        self.onBuyTicket = self._addCommand('onBuyTicket')
