# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/pet_reward_view_model.py
from frameworks.wulf import ViewModel

class PetRewardViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=6, commands=1):
        super(PetRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getOpenedLetters(self):
        return self._getNumber(0)

    def setOpenedLetters(self, value):
        self._setNumber(0, value)

    def getStartVideo(self):
        return self._getBool(1)

    def setStartVideo(self, value):
        self._setBool(1, value)

    def getTankmanName(self):
        return self._getString(2)

    def setTankmanName(self, value):
        self._setString(2, value)

    def getTankmanIcon(self):
        return self._getString(3)

    def setTankmanIcon(self, value):
        self._setString(3, value)

    def getNumberOfTokens(self):
        return self._getNumber(4)

    def setNumberOfTokens(self, value):
        self._setNumber(4, value)

    def getTextNumber(self):
        return self._getNumber(5)

    def setTextNumber(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(PetRewardViewModel, self)._initialize()
        self._addNumberProperty('openedLetters', 0)
        self._addBoolProperty('startVideo', False)
        self._addStringProperty('tankmanName', '')
        self._addStringProperty('tankmanIcon', '')
        self._addNumberProperty('numberOfTokens', 0)
        self._addNumberProperty('textNumber', 0)
        self.onClose = self._addCommand('onClose')
