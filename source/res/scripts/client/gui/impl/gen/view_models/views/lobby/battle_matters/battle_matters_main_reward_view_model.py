# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/battle_matters_main_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.battle_matters.battle_matters_vehicle_model import BattleMattersVehicleModel

class BattleMattersMainRewardViewModel(ViewModel):
    __slots__ = ('onShowView', 'onPreview', 'onBack', 'onClose')

    def __init__(self, properties=1, commands=4):
        super(BattleMattersMainRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicles(self):
        return self._getArray(0)

    def setVehicles(self, value):
        self._setArray(0, value)

    @staticmethod
    def getVehiclesType():
        return BattleMattersVehicleModel

    def _initialize(self):
        super(BattleMattersMainRewardViewModel, self)._initialize()
        self._addArrayProperty('vehicles', Array())
        self.onShowView = self._addCommand('onShowView')
        self.onPreview = self._addCommand('onPreview')
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
