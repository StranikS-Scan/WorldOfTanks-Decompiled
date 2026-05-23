# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/tooltips/fun_random_base_quest_tooltip_view_model.py
from frameworks.wulf import ViewModel

class FunRandomBaseQuestTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(FunRandomBaseQuestTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getAssetsPointer(self):
        return self._getString(0)

    def setAssetsPointer(self, value):
        self._setString(0, value)

    def getStatusTimer(self):
        return self._getNumber(1)

    def setStatusTimer(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(FunRandomBaseQuestTooltipViewModel, self)._initialize()
        self._addStringProperty('assetsPointer', 'undefined')
        self._addNumberProperty('statusTimer', -1)
