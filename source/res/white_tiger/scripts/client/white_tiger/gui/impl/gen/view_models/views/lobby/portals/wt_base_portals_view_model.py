# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_base_portals_view_model.py
from frameworks.wulf import ViewModel

class WtBasePortalsViewModel(ViewModel):
    __slots__ = ('onBuyLootBoxes', 'onClose')

    def __init__(self, properties=1, commands=2):
        super(WtBasePortalsViewModel, self).__init__(properties=properties, commands=commands)

    def getIsBoxesEnabled(self):
        return self._getBool(0)

    def setIsBoxesEnabled(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(WtBasePortalsViewModel, self)._initialize()
        self._addBoolProperty('isBoxesEnabled', True)
        self.onBuyLootBoxes = self._addCommand('onBuyLootBoxes')
        self.onClose = self._addCommand('onClose')
