# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/paragons/tooltips/reset_branch_tooltip_model.py
from frameworks.wulf import ViewModel

class ResetBranchTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ResetBranchTooltipModel, self).__init__(properties=properties, commands=commands)

    def getHeader(self):
        return self._getString(0)

    def setHeader(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getAdditionalDescription(self):
        return self._getString(2)

    def setAdditionalDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(ResetBranchTooltipModel, self)._initialize()
        self._addStringProperty('header', '')
        self._addStringProperty('description', '')
        self._addStringProperty('additionalDescription', '')
