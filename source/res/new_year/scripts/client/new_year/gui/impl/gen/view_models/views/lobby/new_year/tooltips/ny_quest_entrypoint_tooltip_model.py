# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_quest_entrypoint_tooltip_model.py
from frameworks.wulf import Array
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.quests.ny_quests_model import NyQuestsModel

class NyQuestEntrypointTooltipModel(NyQuestsModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=3):
        super(NyQuestEntrypointTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBattleTypes(self):
        return self._getArray(9)

    def setBattleTypes(self, value):
        self._setArray(9, value)

    @staticmethod
    def getBattleTypesType():
        return unicode

    def getMinResetTimeLeft(self):
        return self._getNumber(10)

    def setMinResetTimeLeft(self, value):
        self._setNumber(10, value)

    def getIsLastDay(self):
        return self._getNumber(11)

    def setIsLastDay(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(NyQuestEntrypointTooltipModel, self)._initialize()
        self._addArrayProperty('battleTypes', Array())
        self._addNumberProperty('minResetTimeLeft', 0)
        self._addNumberProperty('isLastDay', 0)
