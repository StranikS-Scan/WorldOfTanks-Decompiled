# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/summer_sale/summer_sale_intro_page_view_model.py
from frameworks.wulf import ViewModel

class SummerSaleIntroPageViewModel(ViewModel):
    __slots__ = ('onGoToFeature', 'onClose')

    def __init__(self, properties=0, commands=2):
        super(SummerSaleIntroPageViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(SummerSaleIntroPageViewModel, self)._initialize()
        self.onGoToFeature = self._addCommand('onGoToFeature')
        self.onClose = self._addCommand('onClose')
