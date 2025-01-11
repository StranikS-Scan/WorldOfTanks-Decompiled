# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/notifications/ny_attached_3d_rewards_model.py
from gui.impl.gen.view_models.views.lobby.new_year.notifications.receiving_rewards_model import ReceivingRewardsModel

class NyAttached3DRewardsModel(ReceivingRewardsModel):
    __slots__ = ('onGoToExterior', 'onGoToGarage')

    def __init__(self, properties=7, commands=6):
        super(NyAttached3DRewardsModel, self).__init__(properties=properties, commands=commands)

    def getIsFirstAttach(self):
        return self._getBool(6)

    def setIsFirstAttach(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NyAttached3DRewardsModel, self)._initialize()
        self._addBoolProperty('isFirstAttach', False)
        self.onGoToExterior = self._addCommand('onGoToExterior')
        self.onGoToGarage = self._addCommand('onGoToGarage')
