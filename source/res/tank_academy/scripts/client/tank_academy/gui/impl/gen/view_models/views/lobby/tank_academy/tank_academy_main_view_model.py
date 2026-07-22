# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_main_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_group_model import QuestGroupModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_progress_model import QuestProgressModel

class TankAcademyMainViewModel(ViewModel):
    __slots__ = ('onShowView', 'onSelectDelayedReward', 'onClose', 'onShowInfoPage', 'onShowQuestTutorial', 'onShowQuestVehicle', 'onUseQuestToken', 'onViewVehicles', 'onSeenAnimation')
    BOX_TOOLTIP_ARG_SHOW_COUNT = 'showCount'
    BOX_TOOLTIP_ARG_QUEST_GROUP_INDEX = 'questGroupIndex'
    BOX_TOOLTIP_ARG_QUEST_INDEX = 'questIndex'
    ARG_SHOW_QUEST_TUTORIAL = 'questNumber'
    ARG_SHOW_QUEST_VEHICLE = 'questNumber'
    ARG_USE_QUEST_TOKEN = 'questNumber'
    ARG_QUEST_ID = 'questID'
    ARG_TOKEN_ID = 'tokenID'

    def __init__(self, properties=4, commands=9):
        super(TankAcademyMainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def questProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestProgressType():
        return QuestProgressModel

    def getIsRewardsViewOpen(self):
        return self._getBool(1)

    def setIsRewardsViewOpen(self, value):
        self._setBool(1, value)

    def getQuest_groups(self):
        return self._getArray(2)

    def setQuest_groups(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuest_groupsType():
        return QuestGroupModel

    def getUnobtainedVehiclesCount(self):
        return self._getNumber(3)

    def setUnobtainedVehiclesCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(TankAcademyMainViewModel, self)._initialize()
        self._addViewModelProperty('questProgress', QuestProgressModel())
        self._addBoolProperty('isRewardsViewOpen', False)
        self._addArrayProperty('quest_groups', Array())
        self._addNumberProperty('unobtainedVehiclesCount', 0)
        self.onShowView = self._addCommand('onShowView')
        self.onSelectDelayedReward = self._addCommand('onSelectDelayedReward')
        self.onClose = self._addCommand('onClose')
        self.onShowInfoPage = self._addCommand('onShowInfoPage')
        self.onShowQuestTutorial = self._addCommand('onShowQuestTutorial')
        self.onShowQuestVehicle = self._addCommand('onShowQuestVehicle')
        self.onUseQuestToken = self._addCommand('onUseQuestToken')
        self.onViewVehicles = self._addCommand('onViewVehicles')
        self.onSeenAnimation = self._addCommand('onSeenAnimation')
