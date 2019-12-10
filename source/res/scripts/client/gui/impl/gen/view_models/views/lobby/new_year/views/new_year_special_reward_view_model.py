# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/new_year_special_reward_view_model.py
from frameworks.wulf import ViewModel

class NewYearSpecialRewardViewModel(ViewModel):
    __slots__ = ('onRecruit', 'onClose')

    def __init__(self, properties=0, commands=2):
        super(NewYearSpecialRewardViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(NewYearSpecialRewardViewModel, self)._initialize()
        self.onRecruit = self._addCommand('onRecruit')
        self.onClose = self._addCommand('onClose')
