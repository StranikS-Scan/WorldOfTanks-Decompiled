# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/battle_result_stat_tooltip_model.py
from frameworks.wulf import ViewModel

class BattleResultStatTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleResultStatTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getString(0)

    def setTitle(self, value):
        self._setString(0, value)

    def getDescr(self):
        return self._getString(1)

    def setDescr(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(BattleResultStatTooltipModel, self)._initialize()
        self._addStringProperty('title', '')
        self._addStringProperty('descr', '')
