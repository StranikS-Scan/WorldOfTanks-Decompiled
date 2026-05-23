# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/summer_sale/summer_sale_intro_page_view.py
from account_helpers import AccountSettings
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.summer_sale.summer_sale_intro_page_view_model import SummerSaleIntroPageViewModel
from gui.impl.pub import ViewImpl
from gui.shared.event_dispatcher import showSummerSaleInfoPage
from account_helpers.AccountSettings import SHOWN_SUMMER_SALE_INTRO

class SummerSaleIntroPageView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = SummerSaleIntroPageViewModel()
        super(SummerSaleIntroPageView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SummerSaleIntroPageView, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(SummerSaleIntroPageView, self)._initialize(*args, **kwargs)
        AccountSettings.setSettings(SHOWN_SUMMER_SALE_INTRO, True)

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseView), (self.viewModel.onGoToFeature, self.__onGoToFeature))

    def __onCloseView(self):
        self.destroyWindow()

    def __onGoToFeature(self):
        showSummerSaleInfoPage()
        self.destroyWindow()
