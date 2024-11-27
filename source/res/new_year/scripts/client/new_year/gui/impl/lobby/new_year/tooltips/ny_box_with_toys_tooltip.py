# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/tooltips/ny_box_with_toys_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from new_year.gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_box_with_toys_tooltip_model import NyBoxWithToysTooltipModel
from new_year.gui.impl.new_year.new_year_bonus_packer import getNewYearBonusPacker
from gui.impl.pub import ViewImpl
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData

class NyBoxWithToysTooltip(ViewImpl):
    __slots__ = ('__toys',)

    def __init__(self, toys):
        settings = ViewSettings(R.views.new_year.lobby.new_year.tooltips.NyBoxWithToysTooltip())
        settings.model = NyBoxWithToysTooltipModel()
        super(NyBoxWithToysTooltip, self).__init__(settings)
        self.__toys = toys

    @property
    def viewModel(self):
        return super(NyBoxWithToysTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(NyBoxWithToysTooltip, self)._onLoading()
        with self.viewModel.transaction() as vm:
            self.__fillToys(vm)

    def __fillToys(self, model):
        toysList = model.getToys()
        packBonusModelAndTooltipData(self.__toys, toysList, packer=getNewYearBonusPacker())
        toysList.invalidate()
