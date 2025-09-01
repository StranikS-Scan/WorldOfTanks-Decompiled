# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/tooltips/tankman_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_model import TankmanTooltipViewModel
from gui.impl.pub import ViewImpl

class WTTankmanTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.white_tiger.mono.lobby.tooltips.crew_info_tooltip())
        settings.model = TankmanTooltipViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(WTTankmanTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(WTTankmanTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(WTTankmanTooltipView, self)._onLoading()
        tankmanInfo = kwargs.get('tankmanInfo', None)
        if tankmanInfo is None:
            return
        else:
            with self.viewModel.transaction() as model:
                model.setTitle(tankmanInfo.getFullUserName())
                model.setSubtitle(tankmanInfo.getLabel())
                model.setMainIcon(tankmanInfo.getTankmanIcon())
                model.setDescription(tankmanInfo.getDescription())
                model.setIconsTitle(tankmanInfo.getSkillsLabel())
            return
