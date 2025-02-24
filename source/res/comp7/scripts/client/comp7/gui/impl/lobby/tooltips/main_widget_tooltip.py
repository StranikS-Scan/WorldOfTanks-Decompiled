# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/tooltips/main_widget_tooltip.py
from comp7.gui.impl.gen.view_models.views.lobby.tooltips.main_widget_tooltip_model import MainWidgetTooltipModel
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from comp7.gui.impl.lobby.comp7_helpers.comp7_model_helpers import getSeasonNameEnum
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class MainWidgetTooltip(ViewImpl):
    __slots__ = ()
    __comp7Controller = dependency.descriptor(IComp7Controller)

    def __init__(self, layoutID=R.views.comp7.lobby.tooltips.MainWidgetTooltip()):
        settings = ViewSettings(layoutID)
        settings.model = MainWidgetTooltipModel()
        super(MainWidgetTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(MainWidgetTooltip, self).getViewModel()

    def _onLoading(self):
        super(MainWidgetTooltip, self)._onLoading()
        self.__updateData()

    def __updateData(self):
        with self.viewModel.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum())
            isQualification = self.__comp7Controller.isQualificationActive()
            if isQualification:
                self.__updateQualificationdata(vm)
            else:
                self.__updateProgressionData(vm)

    def __updateQualificationdata(self, model):
        comp7_qualification_helpers.setQualificationInfo(model.qualificationModel)

    def __updateProgressionData(self, model):
        division = comp7_shared.getPlayerDivision()
        model.setRank(comp7_shared.getRankEnumValue(division))
        model.setCurrentScore(self.__comp7Controller.rating)
        comp7_model_helpers.setDivisionInfo(model=model.divisionInfo, division=division)
        comp7_model_helpers.setElitePercentage(model)
