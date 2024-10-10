# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/wt_carousel_tank_status_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WtCarouselTankStatusModel(ViewModel):
    __slots__ = ('onOpenTasks', 'onBuyTicket')

    def __init__(self, properties=5, commands=2):
        super(WtCarouselTankStatusModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getIsHunter(self):
        return self._getBool(2)

    def setIsHunter(self, value):
        self._setBool(2, value)

    def getIsSpecial(self):
        return self._getBool(3)

    def setIsSpecial(self, value):
        self._setBool(3, value)

    def getQuantity(self):
        return self._getNumber(4)

    def setQuantity(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(WtCarouselTankStatusModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addResourceProperty('icon', R.invalid())
        self._addBoolProperty('isHunter', False)
        self._addBoolProperty('isSpecial', False)
        self._addNumberProperty('quantity', -1)
        self.onOpenTasks = self._addCommand('onOpenTasks')
        self.onBuyTicket = self._addCommand('onBuyTicket')
