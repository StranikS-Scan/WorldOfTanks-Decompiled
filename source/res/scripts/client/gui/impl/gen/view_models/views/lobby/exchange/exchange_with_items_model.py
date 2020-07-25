# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/exchange/exchange_with_items_model.py
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.gen.view_models.views.lobby.common.multiple_items_content_model import MultipleItemsContentModel

class ExchangeWithItemsModel(DialogWithExchange):
    __slots__ = ()

    def __init__(self, properties=15, commands=3):
        super(ExchangeWithItemsModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainContent(self):
        return self._getViewModel(14)

    def _initialize(self):
        super(ExchangeWithItemsModel, self)._initialize()
        self._addViewModelProperty('mainContent', MultipleItemsContentModel())
