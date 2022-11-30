# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/glade/ny_max_level_rewards_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_with_roman_numbers_model import NyWithRomanNumbersModel

class NyMaxLevelRewardsModel(NyWithRomanNumbersModel):
    __slots__ = ('onAccept',)

    def __init__(self, properties=6, commands=1):
        super(NyMaxLevelRewardsModel, self).__init__(properties=properties, commands=commands)

    def getObjectType(self):
        return self._getString(1)

    def setObjectType(self, value):
        self._setString(1, value)

    def getLevel(self):
        return self._getNumber(2)

    def setLevel(self, value):
        self._setNumber(2, value)

    def getToysCount(self):
        return self._getNumber(3)

    def setToysCount(self, value):
        self._setNumber(3, value)

    def getDecorationID(self):
        return self._getString(4)

    def setDecorationID(self, value):
        self._setString(4, value)

    def getIsVisible(self):
        return self._getBool(5)

    def setIsVisible(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(NyMaxLevelRewardsModel, self)._initialize()
        self._addStringProperty('objectType', '')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('toysCount', 0)
        self._addStringProperty('decorationID', '')
        self._addBoolProperty('isVisible', False)
        self.onAccept = self._addCommand('onAccept')
