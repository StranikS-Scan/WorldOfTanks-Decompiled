# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/impl/gen/view_models/views/battle/cosmic_hud/tooltips/ability_tooltip_model.py
from frameworks.wulf import ViewModel

class AbilityTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AbilityTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAbility(self):
        return self._getString(0)

    def setAbility(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(AbilityTooltipModel, self)._initialize()
        self._addStringProperty('ability', 'none')
