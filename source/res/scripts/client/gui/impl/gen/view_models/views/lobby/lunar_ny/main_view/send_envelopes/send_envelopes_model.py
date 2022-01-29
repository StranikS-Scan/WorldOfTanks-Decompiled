# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/main_view/send_envelopes/send_envelopes_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.lunar_ny.progression_model import ProgressionModel

class SendEnvelopesModel(ViewModel):
    __slots__ = ('onQuestsClick', 'onBuyClick', 'onSendClick', 'onBuyInAdditionClick')

    def __init__(self, properties=4, commands=4):
        super(SendEnvelopesModel, self).__init__(properties=properties, commands=commands)

    @property
    def envelopesProgression(self):
        return self._getViewModel(0)

    def getFreeCount(self):
        return self._getNumber(1)

    def setFreeCount(self, value):
        self._setNumber(1, value)

    def getPaidCount(self):
        return self._getNumber(2)

    def setPaidCount(self, value):
        self._setNumber(2, value)

    def getPremiumCount(self):
        return self._getNumber(3)

    def setPremiumCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(SendEnvelopesModel, self)._initialize()
        self._addViewModelProperty('envelopesProgression', ProgressionModel())
        self._addNumberProperty('freeCount', 0)
        self._addNumberProperty('paidCount', 0)
        self._addNumberProperty('premiumCount', 0)
        self.onQuestsClick = self._addCommand('onQuestsClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onSendClick = self._addCommand('onSendClick')
        self.onBuyInAdditionClick = self._addCommand('onBuyInAdditionClick')
