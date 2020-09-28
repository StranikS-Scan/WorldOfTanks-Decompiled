# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/wt_event_exchange_to_re_roll_view_model.py
from gui.impl.gen.view_models.views.lobby.common.dialog_with_exchange import DialogWithExchange
from gui.impl.gen.view_models.views.lobby.common.multiple_items_content_model import MultipleItemsContentModel

class WtEventExchangeToReRollViewModel(DialogWithExchange):
    __slots__ = ()

    def __init__(self, properties=16, commands=3):
        super(WtEventExchangeToReRollViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def mainContent(self):
        return self._getViewModel(14)

    def getBoxType(self):
        return self._getString(15)

    def setBoxType(self, value):
        self._setString(15, value)

    def _initialize(self):
        super(WtEventExchangeToReRollViewModel, self)._initialize()
        self._addViewModelProperty('mainContent', MultipleItemsContentModel())
        self._addStringProperty('boxType', 'special')
