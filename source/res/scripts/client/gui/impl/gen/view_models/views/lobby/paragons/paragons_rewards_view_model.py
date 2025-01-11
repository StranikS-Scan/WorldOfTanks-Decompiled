# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/paragons_rewards_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ParagonsRewardsViewModel(ViewModel):
    __slots__ = ('onClose', 'onSelectVehicleAsReward', 'onShowVehicleInHangar')

    def __init__(self, properties=5, commands=3):
        super(ParagonsRewardsViewModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(0)

    def setDescription(self, value):
        self._setString(0, value)

    def getChapterLevel(self):
        return self._getNumber(1)

    def setChapterLevel(self, value):
        self._setNumber(1, value)

    def getSelectedVehicle(self):
        return self._getBool(2)

    def setSelectedVehicle(self, value):
        self._setBool(2, value)

    def getMainRewards(self):
        return self._getArray(3)

    def setMainRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getMainRewardsType():
        return IconBonusModel

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return IconBonusModel

    def _initialize(self):
        super(ParagonsRewardsViewModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addNumberProperty('chapterLevel', 0)
        self._addBoolProperty('selectedVehicle', False)
        self._addArrayProperty('mainRewards', Array())
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onSelectVehicleAsReward = self._addCommand('onSelectVehicleAsReward')
        self.onShowVehicleInHangar = self._addCommand('onShowVehicleInHangar')
