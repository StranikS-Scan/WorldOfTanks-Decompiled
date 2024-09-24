# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/impl/gen/view_models/views/lobby/intro_view_model.py
from frameworks.wulf import ViewModel

class IntroViewModel(ViewModel):
    __slots__ = ('onShowVideo', 'onContinue', 'onOpenInfoPage')

    def __init__(self, properties=1, commands=3):
        super(IntroViewModel, self).__init__(properties=properties, commands=commands)

    def getTimeOffer(self):
        return self._getNumber(0)

    def setTimeOffer(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(IntroViewModel, self)._initialize()
        self._addNumberProperty('timeOffer', 0)
        self.onShowVideo = self._addCommand('onShowVideo')
        self.onContinue = self._addCommand('onContinue')
        self.onOpenInfoPage = self._addCommand('onOpenInfoPage')
