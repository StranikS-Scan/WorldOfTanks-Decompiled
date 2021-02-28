# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_reward_choice_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.battle_pass.device_reward_option_model import DeviceRewardOptionModel

class BattlePassRewardChoiceViewModel(ViewModel):
    __slots__ = ('onTakeClick', 'onCloseClick', 'onAnimationFinished')

    def __init__(self, properties=7, commands=3):
        super(BattlePassRewardChoiceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getChapterNumber(self):
        return self._getNumber(2)

    def setChapterNumber(self, value):
        self._setNumber(2, value)

    def getChapter(self):
        return self._getString(3)

    def setChapter(self, value):
        self._setString(3, value)

    def getRewardType(self):
        return self._getString(4)

    def setRewardType(self, value):
        self._setString(4, value)

    def getIsOptionsSequence(self):
        return self._getBool(5)

    def setIsOptionsSequence(self, value):
        self._setBool(5, value)

    def getSelectedGiftId(self):
        return self._getNumber(6)

    def setSelectedGiftId(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(BattlePassRewardChoiceViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addNumberProperty('level', 0)
        self._addNumberProperty('chapterNumber', 0)
        self._addStringProperty('chapter', '')
        self._addStringProperty('rewardType', '')
        self._addBoolProperty('isOptionsSequence', False)
        self._addNumberProperty('selectedGiftId', -1)
        self.onTakeClick = self._addCommand('onTakeClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onAnimationFinished = self._addCommand('onAnimationFinished')
