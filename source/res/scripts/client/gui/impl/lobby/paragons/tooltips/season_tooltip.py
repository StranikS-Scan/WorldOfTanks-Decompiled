# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/paragons/tooltips/season_tooltip.py
from gui.impl.gen import R
from frameworks.wulf import ViewSettings
from gui.impl.gen.view_models.views.lobby.paragons.tooltips.season_tooltip_model import SeasonTooltipModel
from skeletons.gui.game_control import IParagonsController
from gui.impl.lobby.paragons.paragons_helpers.paragons_model_helpers import getChapterStatus
from helpers import dependency
from gui.impl.pub import ViewImpl

class SeasonTooltip(ViewImpl):
    __slots__ = ()
    __paragonsController = dependency.descriptor(IParagonsController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.paragons.tooltips.SeasonTooltip())
        settings.model = SeasonTooltipModel()
        settings.args = args
        settings.kwargs = kwargs
        super(SeasonTooltip, self).__init__(settings)

    @property
    def viewModel(self):
        return super(SeasonTooltip, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        with self.viewModel.transaction() as tx:
            chapterID = int(kwargs.get('chapterID'))
            tx.setChapterId(chapterID)
            tx.setVehicleCount(self.__paragonsController.unlockedNecessaryLevelVehiclesCount)
            tx.setNecessaryVehicleCount(self.__paragonsController.minUnlockedNecessaryLevelVehiclesCount)
            tx.setIsAllRewardsClaimed(self.__paragonsController.isChapterComplete(chapterID) and self.__paragonsController.isAllSelectablesClaimed(chapterID))
            tx.chapterStatus.setStatus(getChapterStatus(chapterID))
