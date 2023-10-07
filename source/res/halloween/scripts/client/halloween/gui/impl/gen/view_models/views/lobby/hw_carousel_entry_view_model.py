# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/hw_carousel_entry_view_model.py
from frameworks.wulf import ViewModel

class HwCarouselEntryViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=0, commands=1):
        super(HwCarouselEntryViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(HwCarouselEntryViewModel, self)._initialize()
        self.onAction = self._addCommand('onAction')
