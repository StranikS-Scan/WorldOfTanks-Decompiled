# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/newbie_restrictions_tooltip_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.condition_group import ConditionGroup

class NewbieRestrictionsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewbieRestrictionsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getConditionGroups(self):
        return self._getArray(0)

    def setConditionGroups(self, value):
        self._setArray(0, value)

    @staticmethod
    def getConditionGroupsType():
        return ConditionGroup

    def getFooterTitleText(self):
        return self._getResource(1)

    def setFooterTitleText(self, value):
        self._setResource(1, value)

    def getFooterText(self):
        return self._getResource(2)

    def setFooterText(self, value):
        self._setResource(2, value)

    def _initialize(self):
        super(NewbieRestrictionsTooltipModel, self)._initialize()
        self._addArrayProperty('conditionGroups', Array())
        self._addResourceProperty('footerTitleText', R.invalid())
        self._addResourceProperty('footerText', R.invalid())
