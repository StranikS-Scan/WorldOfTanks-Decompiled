# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/wot_anniversary_award_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class WotAnniversaryAwardViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(WotAnniversaryAwardViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainRewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getMainRewardsType():
        return BonusModel

    def getQuestsCount(self):
        return self._getNumber(1)

    def setQuestsCount(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(WotAnniversaryAwardViewModel, self)._initialize()
        self._addViewModelProperty('mainRewards', UserListModel())
        self._addNumberProperty('questsCount', 0)
        self.onClose = self._addCommand('onClose')
