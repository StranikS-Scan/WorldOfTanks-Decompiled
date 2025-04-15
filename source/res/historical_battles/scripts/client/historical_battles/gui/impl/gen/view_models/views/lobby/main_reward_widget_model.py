# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/main_reward_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.stage_model import StageModel

class MainRewardWidgetModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=2, commands=1):
        super(MainRewardWidgetModel, self).__init__(properties=properties, commands=commands)

    def getCurrentFrontType(self):
        return self._getString(0)

    def setCurrentFrontType(self, value):
        self._setString(0, value)

    def getStages(self):
        return self._getArray(1)

    def setStages(self, value):
        self._setArray(1, value)

    @staticmethod
    def getStagesType():
        return StageModel

    def _initialize(self):
        super(MainRewardWidgetModel, self)._initialize()
        self._addStringProperty('currentFrontType', '')
        self._addArrayProperty('stages', Array())
        self.onClick = self._addCommand('onClick')
