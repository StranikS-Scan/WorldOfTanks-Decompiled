# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/prestige/prestige_level_grades_tooltip_view.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.prestige.prestige_emblem_model import PrestigeEmblemModel
from gui.impl.gen.view_models.views.lobby.prestige.tooltips.elite_level_grades_tooltip_model import EliteLevelGradesTooltipModel
from gui.prestige.prestige_helpers import getVehiclePrestige, fillPrestigeEmblemModel, getSortedGrades
from gui.impl.pub import ViewImpl

class PrestigeLevelGradesTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.prestige.tooltips.EliteLevelGradesTooltip(), model=EliteLevelGradesTooltipModel(), args=args, kwargs=kwargs)
        super(PrestigeLevelGradesTooltipView, self).__init__(settings, *args, **kwargs)

    @property
    def viewModel(self):
        return super(PrestigeLevelGradesTooltipView, self).getViewModel()

    def _onLoading(self, vehIntCD, *args, **kwargs):
        currentLevel, _ = getVehiclePrestige(vehIntCD)
        with self.viewModel.transaction() as tx:
            tx.setCurrentLevel(currentLevel)
            emblems = tx.getEmblems()
            emblems.clear()
            for grade in getSortedGrades(vehIntCD, onlyMain=True):
                emblem = PrestigeEmblemModel()
                fillPrestigeEmblemModel(emblem, grade.level, vehIntCD)
                emblems.addViewModel(emblem)
