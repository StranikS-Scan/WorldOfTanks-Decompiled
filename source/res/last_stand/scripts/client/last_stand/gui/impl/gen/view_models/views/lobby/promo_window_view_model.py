# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/promo_window_view_model.py
from frameworks.wulf import ViewModel

class PromoWindowViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=3, commands=1):
        super(PromoWindowViewModel, self).__init__(properties=properties, commands=commands)

    def getStartDate(self):
        return self._getNumber(0)

    def setStartDate(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getNumber(1)

    def setEndDate(self, value):
        self._setNumber(1, value)

    def getRegularArtefactsLength(self):
        return self._getNumber(2)

    def setRegularArtefactsLength(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PromoWindowViewModel, self)._initialize()
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addNumberProperty('regularArtefactsLength', 0)
        self.onClose = self._addCommand('onClose')
