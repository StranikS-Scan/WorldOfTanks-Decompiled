# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/tooltips/banner_tooltip.py
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.pub import ViewImpl
from helpers import dependency, time_utils
from skeletons.gui.game_control import IEpicBattleMetaGameController
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.banner_tooltip_model import BannerTooltipModel
from gui.shared.formatters.ranges import toRangeString, toRomanRangeString
from gui.shared.utils import isRomanNumberForbidden
from frontline.gui.frontline_helpers import geFrontlineState
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineState
from frontline.constants.common import STATES_MAP
from account_helpers.AccountSettings import AccountSettings, FRONTLINE_BANNER_INTRO_CLICK_TIMESTAMP

class BannerTooltipView(ViewImpl):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)
    __slots__ = ('_isForFrontlineWidget',)

    def __init__(self, layoutID=R.views.frontline.mono.lobby.tooltips.banner_tooltip(), isForFrontlineWidget=False):
        settings = ViewSettings(layoutID)
        settings.model = BannerTooltipModel()
        super(BannerTooltipView, self).__init__(settings)
        self._isForFrontlineWidget = isForFrontlineWidget

    @property
    def viewModel(self):
        return super(BannerTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(BannerTooltipView, self)._onLoading(*args, **kwargs)
        frontlineState, eventEndDate, _ = geFrontlineState(withPrimeTime=True)
        if frontlineState == FrontlineState.FROZEN:
            eventStartDate = time_utils.getCurrentLocalServerTimestamp()
        else:
            eventStartDate, eventEndDate = self.__epicController.getSeasonTimeRange()
            if frontlineState == FrontlineState.ACTIVE:
                if AccountSettings.getSettings(FRONTLINE_BANNER_INTRO_CLICK_TIMESTAMP) < eventStartDate:
                    frontlineState = FrontlineState.INTRO
        currentLevel = self.__epicController.getCurrentLevel()
        vehicleLevels = self.__epicController.getValidVehicleLevels()
        with self.getViewModel().transaction() as model:
            model.setState(STATES_MAP[frontlineState])
            model.setEventStartDate(eventStartDate)
            model.setEventEndDate(eventEndDate)
            model.setRewardsCount(self.__epicController.getNotChosenRewardCount())
            model.setCurLevel(currentLevel)
            model.setMaxLevel(self.__epicController.getMaxPlayerLevel())
            if not self._isForFrontlineWidget:
                model.setCurPoints(self.__epicController.getCurrentProgress())
                model.setMaxPoints(self.__epicController.getPointsProgressForLevel(currentLevel))
            model.setVehiclesLevel(toRangeString(vehicleLevels) if isRomanNumberForbidden() else toRomanRangeString(vehicleLevels))
