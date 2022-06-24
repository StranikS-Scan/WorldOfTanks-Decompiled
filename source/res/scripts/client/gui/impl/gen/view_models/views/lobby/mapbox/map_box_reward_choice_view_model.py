# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/mapbox/map_box_reward_choice_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.mapbox.crew_book_reward_option_model import CrewBookRewardOptionModel

class MapBoxRewardChoiceViewModel(ViewModel):
    __slots__ = ('onTakeClick', 'onCloseClick', 'onAnimationFinished')

    def __init__(self, properties=4, commands=3):
        super(MapBoxRewardChoiceViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def rewards(self):
        return self._getViewModel(0)

    @staticmethod
    def getRewardsType():
        return CrewBookRewardOptionModel

    def getRewardType(self):
        return self._getString(1)

    def setRewardType(self, value):
        self._setString(1, value)

    def getIsOptionsSequence(self):
        return self._getBool(2)

    def setIsOptionsSequence(self, value):
        self._setBool(2, value)

    def getSelectedGiftId(self):
        return self._getNumber(3)

    def setSelectedGiftId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MapBoxRewardChoiceViewModel, self)._initialize()
        self._addViewModelProperty('rewards', UserListModel())
        self._addStringProperty('rewardType', '')
        self._addBoolProperty('isOptionsSequence', False)
        self._addNumberProperty('selectedGiftId', -1)
        self.onTakeClick = self._addCommand('onTakeClick')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onAnimationFinished = self._addCommand('onAnimationFinished')
