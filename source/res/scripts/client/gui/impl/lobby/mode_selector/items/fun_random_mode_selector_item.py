# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/fun_random_mode_selector_item.py
import typing
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem, formatSeasonLeftTime
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.shared.formatters.ranges import toRomanRangeString
from gui.shared.event_dispatcher import showFunRandomInfoPage
from helpers import dependency, int2roman
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_normal_card_model import ModeSelectorNormalCardModel

class FunRandomSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.FUN_RANDOM
    __funRandomCtrl = dependency.descriptor(IFunRandomController)

    def handleInfoPageClick(self):
        showFunRandomInfoPage()

    def _onInitializing(self):
        super(FunRandomSelectorItem, self)._onInitializing()
        self.__addListeners()
        self._addReward(ModeSelectorRewardID.CREDITS)
        self._addReward(ModeSelectorRewardID.EXPERIENCE)
        self.__fillModel()

    def _onDisposing(self):
        self.__removeListeners()
        super(FunRandomSelectorItem, self)._onDisposing()

    def _getIsDisabled(self):
        isNotStarted = bool(self.__funRandomCtrl.getCurrentSeason() is None and self.__funRandomCtrl.getNextSeason() is not None)
        return super(FunRandomSelectorItem, self)._getIsDisabled() if isNotStarted else super(FunRandomSelectorItem, self)._getIsDisabled() or not self.__funRandomCtrl.canGoToMode()

    def _isInfoIconVisible(self):
        return True

    def _isNewLabelVisible(self):
        return super(FunRandomSelectorItem, self)._isNewLabelVisible() and self.__funRandomCtrl.canGoToMode()

    def _getDisabledTooltipText(self):
        return self.__getNotAvailableVehiclesTooltip() if not self.__funRandomCtrl.hasSuitableVehicles() and not self.__funRandomCtrl.isFrozen() else super(FunRandomSelectorItem, self)._getDisabledTooltipText()

    def __onTimeUpdated(self):
        self.__updateLeftTime()

    def __onModeStatusChanged(self, _):
        self.__fillModel()

    def __onInventoryUpdated(self, *_):
        self.onCardChange()

    def __addListeners(self):
        self.__funRandomCtrl.onGameModeStatusTick += self.__onTimeUpdated
        self.__funRandomCtrl.onGameModeStatusUpdated += self.__onModeStatusChanged
        g_clientUpdateManager.addCallbacks({'inventory.1': self.__onInventoryUpdated})

    def __removeListeners(self):
        self.__funRandomCtrl.onGameModeStatusTick -= self.__onTimeUpdated
        self.__funRandomCtrl.onGameModeStatusUpdated -= self.__onModeStatusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __fillModel(self):
        currentSeason = self.__funRandomCtrl.getCurrentSeason()
        hasSeasons = bool(currentSeason is not None or self.__funRandomCtrl.getNextSeason() is not None)
        if not hasSeasons or not self.__funRandomCtrl.isEnabled():
            self.onCardChange()
            return
        else:
            with self.viewModel.transaction() as model:
                model.setTimeLeft(formatSeasonLeftTime(currentSeason))
                model.setIsDisabled(self._isDisabled())
                model.setConditions(backport.text(R.strings.mode_selector.mode.fun_random.condition(), levels=toRomanRangeString(self.__funRandomCtrl.getModeSettings().levels)))
                self.__updateStatus(model)
            return

    def __updateStatus(self, model):
        if not self._bootcamp.isInBootcamp() and not self.__funRandomCtrl.isBattlesPossible():
            status = backport.text(R.strings.mode_selector.mode.dyn(self.modeName).notStarted())
        else:
            status = ''
        model.setStatusNotActive(status)

    def __updateLeftTime(self):
        currentSeason = self.__funRandomCtrl.getCurrentSeason()
        with self.viewModel.transaction() as model:
            model.setTimeLeft(formatSeasonLeftTime(currentSeason))

    def __getNotAvailableVehiclesTooltip(self):
        path = R.strings.tooltips.mode_selector.unavailable.notVehicles
        availableLevels = self.__funRandomCtrl.getModeSettings().levels
        minLevel, maxLevel = min(availableLevels), max(availableLevels)
        if minLevel == maxLevel:
            levels = int2roman(minLevel)
        else:
            levels = toRomanRangeString(availableLevels)
        vehicleLevels = backport.text(path.level(), levels=levels)
        return backport.text(path.text(), vehicles=vehicleLevels)
