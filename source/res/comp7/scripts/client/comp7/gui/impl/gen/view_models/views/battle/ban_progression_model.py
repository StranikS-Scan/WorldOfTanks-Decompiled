# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/battle/ban_progression_model.py
from comp7.gui.impl.gen.view_models.views.battle.enums import BanState
from frameworks.wulf import ViewModel

class BanProgressionModel(ViewModel):
    __slots__ = ('pollServerTime',)

    def __init__(self, properties=4, commands=1):
        super(BanProgressionModel, self).__init__(properties=properties, commands=commands)

    def getBanState(self):
        return BanState(self._getString(0))

    def setBanState(self, value):
        self._setString(0, value.value)

    def getStartTimestamp(self):
        return self._getNumber(1)

    def setStartTimestamp(self, value):
        self._setNumber(1, value)

    def getEndTimestamp(self):
        return self._getNumber(2)

    def setEndTimestamp(self, value):
        self._setNumber(2, value)

    def getServerTimestamp(self):
        return self._getNumber(3)

    def setServerTimestamp(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(BanProgressionModel, self)._initialize()
        self._addStringProperty('banState')
        self._addNumberProperty('startTimestamp', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addNumberProperty('serverTimestamp', 0)
        self.pollServerTime = self._addCommand('pollServerTime')
