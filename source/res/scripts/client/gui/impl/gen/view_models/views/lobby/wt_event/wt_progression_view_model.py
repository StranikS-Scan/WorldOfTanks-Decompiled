# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_progression_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_progression_level_model import WtProgressionLevelModel
from gui.impl.gen.view_models.views.lobby.wt_event.wt_quests_model import WtQuestsModel

class WtProgressionViewModel(ViewModel):
    __slots__ = ('onClose', 'onAboutClicked', 'onCommanderPreview', 'onTakeReward')

    def __init__(self, properties=6, commands=4):
        super(WtProgressionViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getDailyQuestsType():
        return WtQuestsModel

    def getStampsCurrent(self):
        return self._getNumber(1)

    def setStampsCurrent(self, value):
        self._setNumber(1, value)

    def getStampsPrevious(self):
        return self._getNumber(2)

    def setStampsPrevious(self, value):
        self._setNumber(2, value)

    def getStampsNeededPerStage(self):
        return self._getNumber(3)

    def setStampsNeededPerStage(self, value):
        self._setNumber(3, value)

    def getCurrentStage(self):
        return self._getNumber(4)

    def setCurrentStage(self, value):
        self._setNumber(4, value)

    def getStages(self):
        return self._getArray(5)

    def setStages(self, value):
        self._setArray(5, value)

    @staticmethod
    def getStagesType():
        return WtProgressionLevelModel

    def _initialize(self):
        super(WtProgressionViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', WtQuestsModel())
        self._addNumberProperty('stampsCurrent', 0)
        self._addNumberProperty('stampsPrevious', 0)
        self._addNumberProperty('stampsNeededPerStage', 0)
        self._addNumberProperty('currentStage', 0)
        self._addArrayProperty('stages', Array())
        self.onClose = self._addCommand('onClose')
        self.onAboutClicked = self._addCommand('onAboutClicked')
        self.onCommanderPreview = self._addCommand('onCommanderPreview')
        self.onTakeReward = self._addCommand('onTakeReward')
