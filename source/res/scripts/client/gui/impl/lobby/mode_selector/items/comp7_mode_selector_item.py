# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/comp7_mode_selector_item.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_model import ModeSelectorComp7Model
from gui.impl.lobby.comp7 import comp7_model_helpers, comp7_shared, comp7_qualification_helpers
from gui.impl.lobby.comp7.comp7_model_helpers import getSeasonNameEnum
from gui.impl.lobby.comp7.tooltips.main_widget_tooltip import MainWidgetTooltip
from gui.impl.lobby.comp7.tooltips.rank_inactivity_tooltip import RankInactivityTooltip
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.formatters import time_formatters
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IComp7Controller
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_comp7_widget_model import ModeSelectorComp7WidgetModel

class Comp7ModeSelectorItem(ModeSelectorLegacyItem):
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __slots__ = ('__currentSeason',)
    _VIEW_MODEL = ModeSelectorComp7Model
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.COMP7

    def __init__(self, oldSelectorItem):
        super(Comp7ModeSelectorItem, self).__init__(oldSelectorItem)
        self.__currentSeason = None
        return

    @property
    def viewModel(self):
        return super(Comp7ModeSelectorItem, self).viewModel

    def createToolTipContent(self, contentID):
        return RankInactivityTooltip() if contentID == R.views.lobby.comp7.tooltips.RankInactivityTooltip() else MainWidgetTooltip()

    def _onInitializing(self):
        super(Comp7ModeSelectorItem, self)._onInitializing()
        self.__updateComp7Data()
        setBattlePassState(self.viewModel)
        self.__comp7Controller.onStatusTick += self.__onDataChange
        self.__comp7Controller.onComp7ConfigChanged += self.__onDataChange

    def _onDisposing(self):
        self.__comp7Controller.onStatusTick -= self.__onDataChange
        self.__comp7Controller.onComp7ConfigChanged -= self.__onDataChange
        super(Comp7ModeSelectorItem, self)._onDisposing()

    def __onDataChange(self):
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
        isBeforeSeasons = not prevSeason and nextSeason
        isAfterLastSeason = not nextSeason and prevSeason
        with self.viewModel.transaction() as vm:
            if isStarted:
                vm.setTimeLeft(self.__getSeasonTimeLeft())
                self._addReward(ModeSelectorRewardID.PROGRESSION_STYLE)
                self._addReward(ModeSelectorRewardID.BONES)
            elif isBeforeSeasons:
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.seasonStart(), date=backport.getShortDateFormat(nextSeason.getStartDate())))
            elif isAfterLastSeason:
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.yearEnd()))
            else:
                vm.setStatusNotActive(backport.text(R.strings.mode_selector.mode.comp7.seasonEnd.dyn(getSeasonNameEnum().value)()))

    def __getSeasonTimeLeft(self):
        return time_formatters.getTillTimeByResource(max(0, self.__currentSeason.getEndDate() - time_utils.getServerUTCTime()), R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True) if self.__currentSeason is not None else ''

    def __fillWidgetData(self):
        division = comp7_shared.getPlayerDivision()
        with self.viewModel.widget.transaction() as vm:
            vm.setSeasonName(getSeasonNameEnum())
            vm.setRank(comp7_shared.getRankEnumValue(division))
            vm.setCurrentScore(self.__comp7Controller.rating)
            vm.setIsEnabled(self.__comp7Controller.isAvailable() and not self.__comp7Controller.isOffline)
            comp7_model_helpers.setDivisionInfo(model=vm.divisionInfo, division=division)
            comp7_model_helpers.setRanksInactivityInfo(vm)
            comp7_model_helpers.setElitePercentage(vm)
            comp7_qualification_helpers.setQualificationInfo(vm.qualificationModel)
