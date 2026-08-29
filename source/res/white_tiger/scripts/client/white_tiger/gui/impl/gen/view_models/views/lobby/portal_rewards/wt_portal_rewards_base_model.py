# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portal_rewards/wt_portal_rewards_base_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WtPortalRewardsBaseModel(ViewModel):
    __slots__ = ('onClose', 'onBackToPortal', 'onPreview', 'onBuy')

    def __init__(self, properties=4, commands=4):
        super(WtPortalRewardsBaseModel, self).__init__(properties=properties, commands=commands)

    def getIsBoxesEnabled(self):
        return self._getBool(0)

    def setIsBoxesEnabled(self, value):
        self._setBool(0, value)

    def getFirstLaunchReward(self):
        return self._getNumber(1)

    def setFirstLaunchReward(self, value):
        self._setNumber(1, value)

    def getIsFirstLaunch(self):
        return self._getBool(2)

    def setIsFirstLaunch(self, value):
        self._setBool(2, value)

    def getRewards(self):
        return self._getArray(3)

    def setRewards(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRewardsType():
        return BonusModel

    def _initialize(self):
        super(WtPortalRewardsBaseModel, self)._initialize()
        self._addBoolProperty('isBoxesEnabled', True)
        self._addNumberProperty('firstLaunchReward', 100)
        self._addBoolProperty('isFirstLaunch', False)
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onBackToPortal = self._addCommand('onBackToPortal')
        self.onPreview = self._addCommand('onPreview')
        self.onBuy = self._addCommand('onBuy')
