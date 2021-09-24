# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tooltips/tankman_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_model import TankmanTooltipViewModel
from gui.impl.gen.view_models.views.lobby.tooltips.tankman_tooltip_view_icon_model import TankmanTooltipViewIconModel
from gui.impl.pub import ViewImpl

class TankmanTooltipView(ViewImpl):
    __slots__ = ('__tankmanInfo',)

    def __init__(self, tankmanInfo):
        settings = ViewSettings(R.views.lobby.tooltips.TankmanTooltipView())
        settings.model = TankmanTooltipViewModel()
        self.__tankmanInfo = tankmanInfo
        super(TankmanTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return self.getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(TankmanTooltipView, self)._onLoading()
        with self.viewModel.transaction() as model:
            model.setTitle(self.__tankmanInfo.getFullUserName())
            model.setSubtitle(self.__tankmanInfo.getLabel())
            model.setMainIcon(self.__tankmanInfo.getTankmanIcon())
            model.setDescription(self.__tankmanInfo.getDescription())
            model.setIconsTitle(self.__tankmanInfo.getSkillsLabel())
            skillsModel = model.icons
            skillsModel.clearItems()
            for skill in self.__tankmanInfo.getSkills():
                skillModel = TankmanTooltipViewIconModel()
                skillModel.setIcon(skill)
                skillsModel.addViewModel(skillModel)

            skillsModel.invalidate()
