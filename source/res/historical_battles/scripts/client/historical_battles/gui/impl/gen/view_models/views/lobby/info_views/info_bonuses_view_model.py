# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/info_views/info_bonuses_view_model.py
from frameworks.wulf import ViewModel

class InfoBonusesViewModel(ViewModel):
    __slots__ = ('onClose', 'onQuestButtonClick')

    def __init__(self, properties=0, commands=2):
        super(InfoBonusesViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(InfoBonusesViewModel, self)._initialize()
        self.onClose = self._addCommand('onClose')
        self.onQuestButtonClick = self._addCommand('onQuestButtonClick')
