# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/widgets/shop_card_view_model.py
from frameworks.wulf import ViewModel

class ShopCardViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=0, commands=1):
        super(ShopCardViewModel, self).__init__(properties=properties, commands=commands)

    def _initialize(self):
        super(ShopCardViewModel, self)._initialize()
        self.onClick = self._addCommand('onClick')
