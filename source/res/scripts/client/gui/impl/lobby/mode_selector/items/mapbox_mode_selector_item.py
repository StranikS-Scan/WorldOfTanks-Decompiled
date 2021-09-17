# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/mapbox_mode_selector_item.py
import typing
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.event_dispatcher import showMapboxIntro
from helpers import dependency, time_utils
from skeletons.gui.game_control import IMapboxController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class MapboxModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.MAPBOX
    __mapboxCtrl = dependency.descriptor(IMapboxController)

    def handleClick(self):
        if not self.isSelectable:
            showMapboxIntro()

    @property
    def calendarTooltipText(self):
        return backport.text(R.strings.mapbox.selector.tooltip.body(), day=self.__getCurrentSeasonDate())

    @property
    def isSelectable(self):
        return self.__mapboxCtrl.isActive()

    def _getIsDisabled(self):
        return False

    def _onInitializing(self):
        super(MapboxModeSelectorItem, self)._onInitializing()
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self._addReward(ModeSelectorRewardID.OTHER)
        self.__fillViewModel()

    def _onDisposing(self):
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        super(MapboxModeSelectorItem, self)._onDisposing()

    def __onPrimeTimeStatusUpdate(self, *_):
        self.__fillViewModel()

    def __getSeasonTimeLeft(self):
        currentSeason = self.__mapboxCtrl.getCurrentSeason()
        return getFormattedTimeLeft(max(0, currentSeason.getEndDate() - time_utils.getServerUTCTime())) if currentSeason else ''

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getSeasonTimeLeft())
            nextSeason = self.__mapboxCtrl.getNextSeason()
            if not self.__mapboxCtrl.isActive() and nextSeason is not None:
                vm.setStatusNotActive(backport.text(R.strings.mapbox.selector.startEvent(), day=self.__getDate(nextSeason.getStartDate())))
        return

    def __getCurrentSeasonDate(self):
        currentSeason = self.__mapboxCtrl.getCurrentSeason()
        return self.__getDate(currentSeason.getEndDate()) if currentSeason is not None else ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)
