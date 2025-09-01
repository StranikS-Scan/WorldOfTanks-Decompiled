# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/page/prem_shop_presenter.py
from __future__ import absolute_import
from gui.impl.gen.view_models.views.lobby.page.header.premium_shop_model import PremiumShopModel
from gui.impl.pub.view_component import ViewComponent
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from skeletons.gui.login_manager import ILoginManager

class PremShopPresenter(ViewComponent[PremiumShopModel]):
    __loginManager = dependency.descriptor(ILoginManager)

    def __init__(self):
        super(PremShopPresenter, self).__init__(model=PremiumShopModel)

    @property
    def viewModel(self):
        return super(PremShopPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self.viewModel.onOpenExternalPremiumShop, self.__onOpenExternalPremiumShop),)

    def _onLoading(self, *args, **kwargs):
        super(PremShopPresenter, self)._onLoading(*args, **kwargs)
        self.__onPremShopUpdate()

    def __onPremShopUpdate(self):
        self.viewModel.setIsPremiumShop(not self.__loginManager.isWgcSteam)

    def __onOpenExternalPremiumShop(self):
        g_eventBus.handleEvent(OpenLinkEvent(OpenLinkEvent.PREM_SHOP), EVENT_BUS_SCOPE.DEFAULT)
