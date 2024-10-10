# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/postbattle/tooltips/personal_efficiency.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.postbattle.tooltips.tooltip_efficiency_model import TooltipEfficiencyModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService

class EfficiencyTooltip(ViewImpl):
    __slots__ = ('__arenaUniqueID', '__efficiencyType')
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, arenaUniqueID, efficiencyType):
        contentResID = R.views.white_tiger.lobby.postbattle.tooltips.PersonalEfficiency()
        settings = ViewSettings(contentResID)
        settings.model = TooltipEfficiencyModel()
        super(EfficiencyTooltip, self).__init__(settings)
        self.__arenaUniqueID = arenaUniqueID
        self.__efficiencyType = efficiencyType

    def _onLoading(self, *args, **kwargs):
        super(EfficiencyTooltip, self)._onLoading(*args, **kwargs)
        with self.getViewModel().transaction() as model:
            self.__battleResults.presenter.setEfficiencyTooltipData(model, self.__arenaUniqueID, self.__efficiencyType)
