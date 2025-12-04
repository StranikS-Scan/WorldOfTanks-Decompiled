# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/ny_progress_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.ny_progress_view_model import NyProgressViewModel
from new_year.gui.impl.lobby.new_year.rewards_info.ny_levels_rewards_presenter import NyLevelsRewardsPresenter
from new_year.gui.shared.event_dispatcher import showVehicleDiscountOverlay
from new_year.gui.shared.ny_level_helper import NewYearAtmospherePresenter
from new_year.gui.shared.shop_helpers import getNewYearOldCollectionRewardUrl
from new_year.gui.impl.new_year.sounds import OVERLAY_HANGAR_SOUND_SPACE
from new_year.helpers.server_settings import getNewYearGeneralConfig
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.pub import ViewImpl
from gui.shop import showIngameShop

class NyProgressView(ViewImpl):
    __slots__ = ('__levelsPresenter', '__generalConfig')
    _COMMON_SOUND_SPACE = OVERLAY_HANGAR_SOUND_SPACE

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = NyProgressViewModel()
        super(NyProgressView, self).__init__(settings)
        self.__levelsPresenter = NyLevelsRewardsPresenter(self.viewModel.levelsRewards, self)
        self.__generalConfig = getNewYearGeneralConfig()

    @property
    def viewModel(self):
        return super(NyProgressView, self).getViewModel()

    def createToolTip(self, event):
        return self.__levelsPresenter.createToolTip(event) or super(NyProgressView, self).createToolTip(event)

    def createToolTipContent(self, event, ctID):
        return self.__levelsPresenter.createToolTipContent(event, ctID)

    def _onLoading(self, *args, **kwargs):
        super(NyProgressView, self)._onLoading(*args, **kwargs)
        self.__levelsPresenter.initialize(*args, **kwargs)
        self.__setLevelInfo()

    def _finalize(self):
        self.__levelsPresenter.finalize()
        self.__levelsPresenter = None
        self.__generalConfig = None
        super(NyProgressView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseClick), (self.viewModel.onGotoStore, self.__onGoToStore), (self.viewModel.onSelectVehicleDiscount, self.__onSelectVehicleDiscount))

    def __setLevelInfo(self):
        with self.viewModel.transaction() as tx:
            tx.setProgressionLevel(NewYearAtmospherePresenter.getLevel())
            tx.setProgressionPoints(NewYearAtmospherePresenter.getTotalAtmospherePoints())
            progressionLevels = tx.getProgressionLevels()
            progressionLevels.clear()
            atmosphereLimits = self.__generalConfig.getAtmosphereLevelLimits()
            for level, bound in enumerate(atmosphereLimits):
                progressionLevelModel = tx.getProgressionLevelsType()()
                progressionLevelModel.setNumber(level)
                progressionLevelModel.setMaxPoints(bound)
                progressionLevels.addViewModel(progressionLevelModel)

            progressionLevels.invalidate()

    def __onCloseClick(self):
        self.destroyWindow()

    def __onGoToStore(self):
        showIngameShop(getNewYearOldCollectionRewardUrl())

    def __onSelectVehicleDiscount(self):
        showVehicleDiscountOverlay()
