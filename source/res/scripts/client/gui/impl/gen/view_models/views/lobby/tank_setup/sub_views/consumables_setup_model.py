# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/consumables_setup_model.py
from gui.impl.wrappers.user_hints_model import UserHintsModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel

class ConsumablesSetupModel(BaseSetupModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=8):
        super(ConsumablesSetupModel, self).__init__(properties=properties, commands=commands)

    @property
    def hints(self):
        return self._getViewModel(5)

    def getTempString(self):
        return self._getString(6)

    def setTempString(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(ConsumablesSetupModel, self)._initialize()
        self._addViewModelProperty('hints', UserHintsModel())
        self._addStringProperty('tempString', '')
