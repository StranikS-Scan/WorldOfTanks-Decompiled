# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/quests_widget_tooltip_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.quest_model import QuestModel

class QuestsWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(QuestsWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def questTooltipModel(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestTooltipModelType():
        return QuestModel

    def getFrontName(self):
        return self._getString(1)

    def setFrontName(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(QuestsWidgetTooltipModel, self)._initialize()
        self._addViewModelProperty('questTooltipModel', QuestModel())
        self._addStringProperty('frontName', '')
