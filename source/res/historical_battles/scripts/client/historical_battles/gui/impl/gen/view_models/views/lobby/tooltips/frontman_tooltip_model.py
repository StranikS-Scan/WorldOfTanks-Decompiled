# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/frontman_tooltip_model.py
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.tooltips.frontman_tooltip_ability_model import FrontmanTooltipAbilityModel

class FrontmanTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FrontmanTooltipModel, self).__init__(properties=properties, commands=commands)

    @property
    def roleAbility(self):
        return self._getViewModel(0)

    @staticmethod
    def getRoleAbilityType():
        return FrontmanTooltipAbilityModel

    def getFrontmanID(self):
        return self._getNumber(1)

    def setFrontmanID(self, value):
        self._setNumber(1, value)

    def getRole(self):
        return self._getString(2)

    def setRole(self, value):
        self._setString(2, value)

    def getShowRoleAbility(self):
        return self._getBool(3)

    def setShowRoleAbility(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(FrontmanTooltipModel, self)._initialize()
        self._addViewModelProperty('roleAbility', FrontmanTooltipAbilityModel())
        self._addNumberProperty('frontmanID', 0)
        self._addStringProperty('role', '')
        self._addBoolProperty('showRoleAbility', False)
