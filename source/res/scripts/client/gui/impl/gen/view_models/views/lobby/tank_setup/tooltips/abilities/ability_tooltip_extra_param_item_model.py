# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/tooltips/abilities/ability_tooltip_extra_param_item_model.py
from frameworks.wulf import ViewModel

class AbilityTooltipExtraParamItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AbilityTooltipExtraParamItemModel, self).__init__(properties=properties, commands=commands)

    def getParamKey(self):
        return self._getString(0)

    def setParamKey(self, value):
        self._setString(0, value)

    def getValue(self):
        return self._getString(1)

    def setValue(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def _initialize(self):
        super(AbilityTooltipExtraParamItemModel, self)._initialize()
        self._addStringProperty('paramKey', '')
        self._addStringProperty('value', '')
        self._addStringProperty('description', '')
