# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/shop_card_presenter.py
from gui.impl.pub.view_component import ViewComponent
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.shop_card_view_model import ShopCardViewModel
from last_stand.gui.shared.event_dispatcher import showLSShopAll

class ShopCardPresenter(ViewComponent[ShopCardViewModel]):

    def __init__(self):
        super(ShopCardPresenter, self).__init__(model=ShopCardViewModel)

    def _getEvents(self):
        return ((self.getViewModel().onClick, self.__onClick),)

    def __onClick(self):
        showLSShopAll()
