# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/tooltips/battle_pass_points_sources_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_royale.tooltips.battle_pass_quests_points import BattlePassQuestsPoints

class BattlePassPointsSourcesTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattlePassPointsSourcesTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getBattlePoints(self):
        return self._getNumber(0)

    def setBattlePoints(self, value):
        self._setNumber(0, value)

    def getQuestPoints(self):
        return self._getArray(1)

    def setQuestPoints(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(BattlePassPointsSourcesTooltipViewModel, self)._initialize()
        self._addNumberProperty('battlePoints', 0)
        self._addArrayProperty('questPoints', Array())
