# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/event/event_items_for_tokens_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.event.ift_item_group_model import IftItemGroupModel

class EventItemsForTokensModel(ViewModel):
    __slots__ = ('onBack', 'onClose', 'onItemClicked')
    TOKEN_TOOLTIP_ID = 'eventShopTokenTooltipID'

    def __init__(self, properties=2, commands=3):
        super(EventItemsForTokensModel, self).__init__(properties=properties, commands=commands)

    @property
    def groups(self):
        return self._getViewModel(0)

    def getTokens(self):
        return self._getNumber(1)

    def setTokens(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(EventItemsForTokensModel, self)._initialize()
        self._addViewModelProperty('groups', ListModel())
        self._addNumberProperty('tokens', 0)
        self.onBack = self._addCommand('onBack')
        self.onClose = self._addCommand('onClose')
        self.onItemClicked = self._addCommand('onItemClicked')
