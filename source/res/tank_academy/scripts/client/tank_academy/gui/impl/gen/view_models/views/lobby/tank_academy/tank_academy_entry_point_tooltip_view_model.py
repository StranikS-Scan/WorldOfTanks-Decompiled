# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tank_academy/scripts/client/tank_academy/gui/impl/gen/view_models/views/lobby/tank_academy/tank_academy_entry_point_tooltip_view_model.py
from frameworks.wulf import ViewModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_progress_model import QuestProgressModel
from tank_academy.gui.impl.gen.view_models.views.lobby.tank_academy.quest_view_model import QuestViewModel

class TankAcademyEntryPointTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(TankAcademyEntryPointTooltipViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def questProgress(self):
        return self._getViewModel(0)

    @staticmethod
    def getQuestProgressType():
        return QuestProgressModel

    @property
    def quest(self):
        return self._getViewModel(1)

    @staticmethod
    def getQuestType():
        return QuestViewModel

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getHasToken(self):
        return self._getBool(3)

    def setHasToken(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(TankAcademyEntryPointTooltipViewModel, self)._initialize()
        self._addViewModelProperty('questProgress', QuestProgressModel())
        self._addViewModelProperty('quest', QuestViewModel())
        self._addNumberProperty('endDate', 0)
        self._addBoolProperty('hasToken', False)
