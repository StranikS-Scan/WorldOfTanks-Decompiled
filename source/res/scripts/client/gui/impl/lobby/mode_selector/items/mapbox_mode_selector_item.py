# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/mapbox_mode_selector_item.py
import typing
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items import setBattlePassState
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, formatSeasonLeftTime
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

    def _isNeedToHideCard(self):
        return self.__mapboxCtrl.getCurrentCycleID() is None

    def _onInitializing(self):
        super(MapboxModeSelectorItem, self)._onInitializing()
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self._addReward(ModeSelectorRewardID.OTHER)
        self.__fillViewModel()

    def _onDisposing(self):
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        super(MapboxModeSelectorItem, self)._onDisposing()

    def __onPrimeTimeStatusUpdate(self, *_):
        if self._isNeedToHideCard():
            self.onCardChange()
        else:
            self.__fillViewModel()

    def __fillViewModel(self):
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(formatSeasonLeftTime(self.__mapboxCtrl.getCurrentSeason()))
            vm.setStatusNotActive(self.__getNotActiveStatus())
            setBattlePassState(self.viewModel)

    def __getNotActiveStatus(self):
        nextSeason = self.__mapboxCtrl.getNextSeason()
        return backport.text(R.strings.mapbox.selector.startEvent(), day=self.__getDate(nextSeason.getStartDate())) if not self._isDisabled() and not self.__mapboxCtrl.isActive() and nextSeason is not None else ''

    def __getCurrentSeasonDate(self):
        currentSeason = self.__mapboxCtrl.getCurrentSeason()
        return self.__getDate(currentSeason.getEndDate()) if currentSeason is not None else ''

    def __getDate(self, date):
        timeStamp = time_utils.makeLocalServerTime(date)
        return backport.getShortDateFormat(timeStamp)
