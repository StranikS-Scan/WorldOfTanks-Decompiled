# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_reserves/reserves_conversion_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.personal_reserves.converted_booster_model import ConvertedBoosterModel

class ReservesConversionViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=4, commands=1):
        super(ReservesConversionViewModel, self).__init__(properties=properties, commands=commands)

    def getBattleXPConverted(self):
        return self._getArray(0)

    def setBattleXPConverted(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBattleXPConvertedType():
        return ConvertedBoosterModel

    def getCreditsConverted(self):
        return self._getArray(1)

    def setCreditsConverted(self, value):
        self._setArray(1, value)

    @staticmethod
    def getCreditsConvertedType():
        return ConvertedBoosterModel

    def getCrewXPConverted(self):
        return self._getArray(2)

    def setCrewXPConverted(self, value):
        self._setArray(2, value)

    @staticmethod
    def getCrewXPConvertedType():
        return ConvertedBoosterModel

    def getFreeXPConverted(self):
        return self._getArray(3)

    def setFreeXPConverted(self, value):
        self._setArray(3, value)

    @staticmethod
    def getFreeXPConvertedType():
        return ConvertedBoosterModel

    def _initialize(self):
        super(ReservesConversionViewModel, self)._initialize()
        self._addArrayProperty('battleXPConverted', Array())
        self._addArrayProperty('creditsConverted', Array())
        self._addArrayProperty('crewXPConverted', Array())
        self._addArrayProperty('freeXPConverted', Array())
        self.onClose = self._addCommand('onClose')
