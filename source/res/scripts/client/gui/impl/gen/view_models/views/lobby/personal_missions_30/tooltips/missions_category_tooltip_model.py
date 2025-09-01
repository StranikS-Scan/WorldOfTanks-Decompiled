# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/personal_missions_30/tooltips/missions_category_tooltip_model.py
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import MissionCategory
from frameworks.wulf import ViewModel

class MissionsCategoryTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(MissionsCategoryTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCategory(self):
        return MissionCategory(self._getString(0))

    def setCategory(self, value):
        self._setString(0, value.value)

    def getOperationName(self):
        return self._getString(1)

    def setOperationName(self, value):
        self._setString(1, value)

    def getMinLevel(self):
        return self._getNumber(2)

    def setMinLevel(self, value):
        self._setNumber(2, value)

    def getMaxLevel(self):
        return self._getNumber(3)

    def setMaxLevel(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(MissionsCategoryTooltipModel, self)._initialize()
        self._addStringProperty('category')
        self._addStringProperty('operationName', '')
        self._addNumberProperty('minLevel', 0)
        self._addNumberProperty('maxLevel', 0)
