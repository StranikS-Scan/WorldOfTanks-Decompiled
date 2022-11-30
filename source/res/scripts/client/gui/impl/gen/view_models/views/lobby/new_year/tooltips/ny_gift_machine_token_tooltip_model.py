# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_gift_machine_token_tooltip_model.py
from frameworks.wulf import ViewModel

class NyGiftMachineTokenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NyGiftMachineTokenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTokenCount(self):
        return self._getNumber(0)

    def setTokenCount(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(NyGiftMachineTokenTooltipModel, self)._initialize()
        self._addNumberProperty('tokenCount', 0)
