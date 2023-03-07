# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/ranked/ranked_entry_point.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.ranked.ranked_entry_point_model import RankedEntryPointModel
from gui.impl.pub import ViewImpl
from helpers import dependency
from skeletons.gui.game_control import IRankedBattlesController
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils
from gui.prb_control.settings import SELECTOR_BATTLE_TYPES
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.ranked.ranked_season_model import RankedSeasonModel
    from season_common import GameSeason
_logger = logging.getLogger(__name__)

@dependency.replace_none_kwargs(rankedController=IRankedBattlesController)
def isRankedEntryPointAvailable(rankedController=None):
    vehicleIsAvailable = rankedController.hasSuitableVehicles() or rankedController.suitableVehicleIsAvailable()
    return rankedController.isEnabled() and vehicleIsAvailable


class RankedEntryPoint(ViewImpl):
    __rankedController = dependency.descriptor(IRankedBattlesController)

    def __init__(self, flags=ViewFlags.VIEW):
        settings = ViewSettings(R.views.lobby.ranked.EntryPoint())
        settings.flags = flags
        settings.model = RankedEntryPointModel()
        super(RankedEntryPoint, self).__init__(settings)

    @property
    def viewModel(self):
        return super(RankedEntryPoint, self).getViewModel()

    def _initialize(self, *args, **kwargs):
        super(RankedEntryPoint, self)._initialize(*args, **kwargs)
        self.viewModel.onClick += self.__onClick
        self.__rankedController.onUpdated += self.__onUpdate
        self.__rankedController.onGameModeStatusUpdated += self.__onUpdate

    def _finalize(self):
        self.viewModel.onClick -= self.__onClick
        self.__rankedController.onUpdated -= self.__onUpdate
        self.__rankedController.onGameModeStatusUpdated -= self.__onUpdate
        super(RankedEntryPoint, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(RankedEntryPoint, self)._onLoading(*args, **kwargs)
        self.__updateViewModel()

    def __updateViewModel(self):
        if isRankedEntryPointAvailable():
            with self.viewModel.transaction() as tx:
                state = self.__getState()
                tx.setState(state)
                currentSeason = self.__rankedController.getCurrentSeason()
                if currentSeason:
                    self.__updateSeason(tx.currentSeason, self.__rankedController.getCurrentSeason())
                else:
                    self.__updateSeason(tx.currentSeason, self.__rankedController.getPreviousSeason())
                self.__updateSeason(tx.nextSeason, self.__rankedController.getNextSeason())
        else:
            self.destroy()

    def __updateSeason(self, tx, season):
        if season:
            tx.setIsValid(True)
            tx.setSeasonNumber(season.getNumber())
            tx.setStartDate(season.getStartDate())
            tx.setEndDate(season.getEndDate())
        else:
            self.__resetSeasonViewModel(tx)

    def __resetSeasonViewModel(self, tx):
        tx.setIsValid(False)
        tx.setStartDate(-1)
        tx.setEndDate(-1)
        tx.setSeasonNumber(-1)

    def __onUpdate(self, _=None):
        self.__updateViewModel()

    def __getState(self):
        result = RankedEntryPointModel.STATE_RANKED_DISABLED
        if self.__rankedController.isEnabled():
            currentSeason = self.__rankedController.getCurrentSeason()
            if currentSeason:
                if self.__rankedController.isFrozen():
                    result = RankedEntryPointModel.STATE_FROZEN
                else:
                    result = RankedEntryPointModel.STATE_ACTIVE_SEASON
            elif self.__rankedController.getPreviousSeason() is None:
                result = RankedEntryPointModel.STATE_BEFORE_SEASON
            elif self.__rankedController.getNextSeason():
                result = RankedEntryPointModel.STATE_WAIT_NEXT_SEASON_DATE
            else:
                result = RankedEntryPointModel.STATE_WAIT_NEXT_SEASON_WITHOUT_DATE
        return result

    def __onClick(self):
        self.__rankedController.doActionOnEntryPointClick()
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.RANKED)
