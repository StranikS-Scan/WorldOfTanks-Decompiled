# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/tooltips/ny_talisman_tooltip.py
from frameworks.wulf import View
from frameworks.wulf import ViewFlags
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_talisman_tooltip_model import NyTalismanTooltipModel
from helpers import dependency
from skeletons.new_year import INewYearController

class NewYearTalismanTooltipContent(View):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, level):
        settings = ViewSettings(layoutID=R.views.lobby.new_year.tooltips.ny_talisman_tooltip.NewYearTalismanTooltipContent(), flags=ViewFlags.VIEW, model=NyTalismanTooltipModel())
        settings.args = (level,)
        super(NewYearTalismanTooltipContent, self).__init__(settings)

    @property
    def viewModel(self):
        return super(NewYearTalismanTooltipContent, self).getViewModel()

    def _initialize(self, level):
        super(NewYearTalismanTooltipContent, self)._initialize()
        talismanInfo = self._nyController.getLevel(level).getTalismanInfo()
        with self.viewModel.transaction() as model:
            model.setIsAvailable(talismanInfo is not None)
            if talismanInfo is not None:
                model.setTalismanImage(talismanInfo.getBigIcon())
            else:
                model.setTalismanImage(R.images.gui.maps.icons.new_year.talismans.big.default())
        return
