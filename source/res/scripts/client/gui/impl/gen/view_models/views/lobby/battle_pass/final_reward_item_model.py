# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/final_reward_item_model.py
from frameworks.wulf import ViewModel

class FinalRewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FinalRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getStyleID(self):
        return self._getNumber(0)

    def setStyleID(self, value):
        self._setNumber(0, value)

    def getVehicleCD(self):
        return self._getNumber(1)

    def setVehicleCD(self, value):
        self._setNumber(1, value)

    def getVehicleUserName(self):
        return self._getString(2)

    def setVehicleUserName(self, value):
        self._setString(2, value)

    def getVoicesNumber(self):
        return self._getNumber(3)

    def setVoicesNumber(self, value):
        self._setNumber(3, value)

    def getStyleName(self):
        return self._getString(4)

    def setStyleName(self, value):
        self._setString(4, value)

    def getRecruitName(self):
        return self._getString(5)

    def setRecruitName(self, value):
        self._setString(5, value)

    def getSelected(self):
        return self._getBool(6)

    def setSelected(self, value):
        self._setBool(6, value)

    def getRewards(self):
        return self._getString(7)

    def setRewards(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(FinalRewardItemModel, self)._initialize()
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('vehicleCD', 0)
        self._addStringProperty('vehicleUserName', '')
        self._addNumberProperty('voicesNumber', 0)
        self._addStringProperty('styleName', '')
        self._addStringProperty('recruitName', '')
        self._addBoolProperty('selected', False)
        self._addStringProperty('rewards', '')
