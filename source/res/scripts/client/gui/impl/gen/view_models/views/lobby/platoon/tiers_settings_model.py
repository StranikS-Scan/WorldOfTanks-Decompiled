# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/tiers_settings_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.platoon.tier_button_model import TierButtonModel

class TiersSettingsModel(ViewModel):
    __slots__ = ('onSwitchTier',)

    def __init__(self, properties=1, commands=1):
        super(TiersSettingsModel, self).__init__(properties=properties, commands=commands)

    def getTierButtons(self):
        return self._getArray(0)

    def setTierButtons(self, value):
        self._setArray(0, value)

    @staticmethod
    def getTierButtonsType():
        return TierButtonModel

    def _initialize(self):
        super(TiersSettingsModel, self)._initialize()
        self._addArrayProperty('tierButtons', Array())
        self.onSwitchTier = self._addCommand('onSwitchTier')
