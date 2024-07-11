# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/lobby/mode_selector/races_mode_selector_item.py
from helpers import dependency
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.formatters import time_formatters
from skeletons.gui.game_control import IRacesBattleController

class RacesModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.RACES
    __racesCtrl = dependency.descriptor(IRacesBattleController)

    def _onInitializing(self):
        super(RacesModeSelectorItem, self)._onInitializing()
        self.viewModel.setName(backport.text(R.strings.mode_selector.mode.races.title()))
        self._addReward(ModeSelectorRewardID.POINTS)
        self.__racesCtrl.onPrimeTimeStatusUpdated += self.__onUpdate
        self.__racesCtrl.onStatusTick += self.__onUpdate
        self.__racesCtrl.onRacesConfigChanged += self.__onUpdate
        self.__onUpdate()

    def _onDisposing(self):
        self.__racesCtrl.onPrimeTimeStatusUpdated -= self.__onUpdate
        self.__racesCtrl.onStatusTick -= self.__onUpdate
        self.__racesCtrl.onRacesConfigChanged -= self.__onUpdate
        super(RacesModeSelectorItem, self)._onDisposing()

    def __onUpdate(self, *_):
        isAvailable = self.__racesCtrl.isAvailable()
        with self.viewModel.transaction() as vm:
            if isAvailable:
                periodInfo = self.__racesCtrl.getPeriodInfo()
                timeLeft = self.__racesCtrl.getEventEndTimestamp() - periodInfo.now
                timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
                vm.setTimeLeft(timeLeftStr)

    def _isNewLabelVisible(self):
        isInBootcamp = self._bootcamp.isInBootcamp()
        return self._getIsNew() and not isInBootcamp
