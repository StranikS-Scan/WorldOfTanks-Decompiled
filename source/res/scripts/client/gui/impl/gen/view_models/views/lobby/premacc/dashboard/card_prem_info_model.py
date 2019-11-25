# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/card_prem_info_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CardPremInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CardPremInfoModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getIsCredits(self):
        return self._getBool(2)

    def setIsCredits(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CardPremInfoModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addStringProperty('value', '')
        self._addBoolProperty('isCredits', True)
