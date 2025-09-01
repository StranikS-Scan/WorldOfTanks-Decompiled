# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/mode_selector/items/comp7_mode_selector_item.py
import typing
from comp7.gui.impl.lobby.comp7_helpers import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from comp7_core.gui.impl.lobby.comp7_core_helpers.comp7_core_model_helpers import getSeasonNameEnum
from comp7.gui.impl.gen.view_models.views.lobby.enums import SeasonName
from comp7.gui.impl.lobby.tooltips.progression_tooltip import ProgressionTooltip
from comp7.gui.impl.lobby.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from gui.impl import backport
from gui.impl.gen import R
from comp7.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_model import ModeSelectorComp7Model
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.formatters import time_formatters
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from comp7.gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_widget_model import ModeSelectorComp7WidgetModel

class Comp7ModeSelectorItem(ModeSelectorLegacyItem):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ('__currentSeason',)
    _VIEW_MODEL = ModeSelectorComp7Model

    def __init__(self, oldSelectorItem):
        super(Comp7ModeSelectorItem, self).__init__(oldSelectorItem)
        self.__currentSeason = None
        return

    @property
    def viewModel(self):
        return super(Comp7ModeSelectorItem, self).viewModel

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.comp7.mono.lobby.tooltips.rank_inactivity_tooltip():
            return RankInactivityTooltip()
        return ProgressionTooltip() if contentID == R.views.comp7.mono.lobby.tooltips.progression_tooltip() else super(Comp7ModeSelectorItem, self).createToolTipContent(event, contentID)

    def _onInitializing(self):
        super(Comp7ModeSelectorItem, self)._onInitializing()
        self.__updateComp7Data()
        setBattlePassState(self.viewModel)
        self.__comp7Controller.onStatusTick += self.__onDataChange
        self.__comp7Controller.onRankUpdated += self.__onDataChange
        self.__comp7Controller.onComp7RanksConfigChanged += self.__onDataChange
        self.__comp7Controller.onOfflineStatusUpdated += self.__onDataChange
        self.__comp7Controller.onQualificationBattlesUpdated += self.__onDataChange
        self.__comp7Controller.onQualificationStateUpdated += self.__onDataChange
        self.__comp7Controller.onEntitlementsUpdated += self.__onDataChange
        self.__comp7Controller.onModeConfigChanged += self.__onDataChange

    def _onDisposing(self):
        self.__comp7Controller.onStatusTick -= self.__onDataChange
        self.__comp7Controller.onRankUpdated -= self.__onDataChange
        self.__comp7Controller.onComp7RanksConfigChanged -= self.__onDataChange
        self.__comp7Controller.onOfflineStatusUpdated -= self.__onDataChange
        self.__comp7Controller.onQualificationBattlesUpdated -= self.__onDataChange
        self.__comp7Controller.onQualificationStateUpdated -= self.__onDataChange
        self.__comp7Controller.onEntitlementsUpdated -= self.__onDataChange
        self.__comp7Controller.onModeConfigChanged -= self.__onDataChange
        super(Comp7ModeSelectorItem, self)._onDisposing()

    def __onDataChange(self, *_, **__):
        self.__updateComp7Data()
        self.onCardChange()

    def __updateComp7Data(self):
        self.__currentSeason = self.__comp7Controller.getCurrentSeason()
        self.__fillViewModel()
        self.__fillWidgetData()

    def __fillViewModel(self):
        isStarted = self.__comp7Controller.hasActiveSeason()
        nextSeason = self.__comp7Controller.getNextSeason()
        prevSeason = self.__comp7Controller.getPreviousSeason()
        isInPreannounce = self.__comp7Controller.isInPreannounceState()
        isBeforeSeasons = not prevSeason and nextSeason
        isAfterLastSeason = not nextSeason and prevSeason
        with self.viewModel.transaction() as vm:
            if isStarted:
                vm.setTimeLeft(self.__getSeasonTimeLeft())
                self._addReward(ModeSelectorRewardID.PROGRESSION_STYLE)
                self._addReward(ModeSelectorRewardID.BONES)
            elif isInPreannounce:
                preannouncedSeason = self.__comp7Controller.getPreannouncedSeason()
                season = getSeasonNameEnum(self.__comp7Controller, SeasonName)
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.seasonStart.dyn(season.value)(), date=backport.getShortDateFormat(preannouncedSeason.getStartDate())))
            elif isBeforeSeasons:
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.seasonStart(), date=backport.getShortDateFormat(nextSeason.getStartDate())))
            elif isAfterLastSeason:
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.yearEnd()))
            else:
                season = getSeasonNameEnum(self.__comp7Controller, SeasonName)
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.seasonEnd.dyn(season.value)()))
            vm.setExternalPath(R.views.comp7.lobby.Comp7BattleCard())

    def __getSeasonTimeLeft(self):
        return time_formatters.getTillTimeByResource(max(0, self.__currentSeason.getEndDate() - time_utils.getServerUTCTime()), R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True) if self.__currentSeason is not None else ''

    def __fillWidgetData(self):
        division = comp7_shared.getPlayerDivision()
        rank = comp7_shared.getRankEnumValue(division)
        with self.viewModel.widget.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum(self.__comp7Controller, SeasonName))
            vm.setRank(rank)
            vm.setCurrentScore(self.__comp7Controller.rating)
            vm.setIsEnabled(self.__comp7Controller.isAvailable() and not self.__comp7Controller.isOffline)
            comp7_model_helpers.setDivisionInfo(model=vm.divisionInfo, division=division)
            vm.setHasRankInactivity(comp7_shared.hasRankInactivity(rank))
            vm.setRankInactivityCount(self.__comp7Controller.activityPoints)
            comp7_model_helpers.setElitePercentage(vm)
            comp7_qualification_helpers.setQualificationInfo(vm.qualificationModel)
