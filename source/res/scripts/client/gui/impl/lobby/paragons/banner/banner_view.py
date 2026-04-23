# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/banner/banner_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.paragons.banner.banner_view_model import BannerViewModel
from gui.impl.gen.view_models.views.lobby.paragons.navigation_view_model import TabId
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.paragons.paragons_window_events import showParagonsNavigationView
from gui.impl.gen import R

class ParagonsBannerView(ViewImpl):
    __slots__ = ()

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.paragons.banner.BannerView())
        settings.flags = flags
        settings.model = BannerViewModel()
        super(ParagonsBannerView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ParagonsBannerView, self).getViewModel()

    @staticmethod
    def __onClick():
        showParagonsNavigationView(tabId=TabId.CHAPTERS)

    def _getEvents(self):
        return ((self.viewModel.onClick, self.__onClick),)

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ParagonsBannerView, self).createToolTip(event)
