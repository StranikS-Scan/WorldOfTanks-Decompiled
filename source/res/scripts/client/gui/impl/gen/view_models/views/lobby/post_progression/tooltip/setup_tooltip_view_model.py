# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/post_progression/tooltip/setup_tooltip_view_model.py
from enum import Enum
from gui.impl.gen.view_models.views.lobby.post_progression.tooltip.feature_tooltip_view_model import FeatureTooltipViewModel

class SetupFeatureType(Enum):
    SHELLSCONSUMABLESSWITCH = 'shells_consumables_switch'
    OPTDEVBOOSTERSSWITCH = 'opt_dev_boosters_switch'


class SetupTooltipViewModel(FeatureTooltipViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(SetupTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getType(self):
        return SetupFeatureType(self._getString(4))

    def setType(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(SetupTooltipViewModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addStringProperty('type')
