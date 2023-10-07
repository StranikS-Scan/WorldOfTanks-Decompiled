# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/reward_screen_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.crew_list_model import CrewListModel
from halloween.gui.impl.gen.view_models.views.lobby.common.reward_model import RewardModel

class RewardScreenViewModel(ViewModel):
    __slots__ = ('onClose', 'onRecruitBtnClick', 'onSoundBtnClick')
    TYPE_ONE_MARK = 'oneMark'
    TYPE_ALL_MARKS = 'allMarks'
    TYPE_ONE_WITCH = 'oneWitch'
    TYPE_SHOW_CREW = 'showCrew'
    TYPE_ALL_WITCHES = 'allWitches'
    TYPE_ALL_REWARDS = 'allRewards'
    TYPE_XP_ACHIEVEMENT = 'xpAchievement'

    def __init__(self, properties=5, commands=3):
        super(RewardScreenViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def crewListBlock(self):
        return self._getViewModel(0)

    @staticmethod
    def getCrewListBlockType():
        return CrewListModel

    def getCrewGroup(self):
        return self._getString(1)

    def setCrewGroup(self, value):
        self._setString(1, value)

    def getScreenType(self):
        return self._getString(2)

    def setScreenType(self, value):
        self._setString(2, value)

    def getCondition(self):
        return self._getNumber(3)

    def setCondition(self, value):
        self._setNumber(3, value)

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return RewardModel

    def _initialize(self):
        super(RewardScreenViewModel, self)._initialize()
        self._addViewModelProperty('crewListBlock', CrewListModel())
        self._addStringProperty('crewGroup', '')
        self._addStringProperty('screenType', '')
        self._addNumberProperty('condition', 0)
        self._addArrayProperty('rewards', Array())
        self.onClose = self._addCommand('onClose')
        self.onRecruitBtnClick = self._addCommand('onRecruitBtnClick')
        self.onSoundBtnClick = self._addCommand('onSoundBtnClick')
