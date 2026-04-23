# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/gsw_cards/shop_card_presenter.py
from __future__ import absolute_import
from gui.impl.lobby.user_missions.hangar_widget.tooltip_positioner import TooltipPositionerMixin
from gui.impl.pub.view_component import ViewComponent
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.shop_card_view_model import ShopCardViewModel
from last_stand.gui.impl.lobby.user_missions.hangar_widget.overlap_ctrl import LastStandOverlapCtrlMixin
from last_stand.gui.shared.event_dispatcher import showLSShopAll

class ShopCardPresenter(TooltipPositionerMixin, LastStandOverlapCtrlMixin, ViewComponent[ShopCardViewModel]):

    def __init__(self):
        super(ShopCardPresenter, self).__init__(model=ShopCardViewModel)

    def _onLoading(self, *args, **kwargs):
        self.initOverlapCtrl()
        super(ShopCardPresenter, self)._onLoading(*args, **kwargs)

    def _getEvents(self):
        return super(ShopCardPresenter, self)._getEvents() + ((self.getViewModel().onClick, self.__onClick),)

    def __onClick(self):
        showLSShopAll()
