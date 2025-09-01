# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/tooltips/pm3_banner_tooltip.py
from gui.impl.pub import ViewImpl
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.missions.widget.pm3_banner_tooltip_view_model import Pm3BannerTooltipViewModel

class PM3BannerTooltipView(ViewImpl):
    __slots__ = ('__type',)

    def __init__(self, bannerType, layoutID=R.views.mono.user_missions.tooltips.pm3_banner_tooltip()):
        settings = ViewSettings(layoutID)
        settings.model = Pm3BannerTooltipViewModel()
        self.__type = bannerType
        super(PM3BannerTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PM3BannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PM3BannerTooltipView, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            model.setType(self.__type)
