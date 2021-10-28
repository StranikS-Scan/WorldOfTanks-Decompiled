# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/mode_selector/items/event_battle_mode_selector_item.py
from gui.battle_pass.battle_pass_helpers import getFormattedTimeLeft
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_event_model import ModeSelectorEventModel
from gui.impl.lobby.mode_selector.items.items_constants import ModeSelectorRewardID
from gui.impl.lobby.mode_selector.items.base_item import ModeSelectorLegacyItem
from gui.impl.gen.view_models.views.lobby.mode_selector.mode_selector_card_types import ModeSelectorCardTypes
from gui.shared.tooltips.event import EventInterrogationTooltipData, InterrogationCtx
from helpers import dependency, time_utils
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache

class EventModeSelectorItem(ModeSelectorLegacyItem):
    __slots__ = ()
    _VIEW_MODEL = ModeSelectorEventModel
    _CARD_VISUAL_TYPE = ModeSelectorCardTypes.EVENT_BATTLES
    _gameEventController = dependency.descriptor(IGameEventController)
    _eventsCache = dependency.descriptor(IEventsCache)
    _itemsCache = dependency.descriptor(IItemsCache)

    @property
    def calendarTooltipText(self):
        return backport.text(R.strings.event.selector.tooltip.body(), day=self.__getEndDate())

    def createProgressionTooltipArgs(self):
        eventRewards = self._gameEventController.getEventRewardController()
        tokenID = eventRewards.rewardBoxesIDsInOrder[-1]
        currentProgress = eventRewards.getCurrentRewardProgress()
        maxProgress = eventRewards.getMaxRewardProgress()
        return [tokenID, InterrogationCtx(status=EventInterrogationTooltipData.LAST, numberMemories=min(currentProgress, maxProgress), totalMemories=maxProgress)]

    def _onInitializing(self):
        super(EventModeSelectorItem, self)._onInitializing()
        self.__fillModel()
        shop = self._gameEventController.getShop()
        shop.onBundleUnlocked += self.__onBundleUpdate
        self._gameEventController.onRewardBoxUpdated += self.__fillModel
        self._gameEventController.onIngameEventsUpdated += self.__fillModel
        self.viewModel.setName(backport.text(R.strings.mode_selector.mode.eventBattle.name()))
        self._addReward(ModeSelectorRewardID.CREDITS)
        name = ''
        vehicle = self.__getFinalRewardVehicle()
        if vehicle is not None:
            name = vehicle.shortUserName
        self._addReward(ModeSelectorRewardID.VEHICLE, locParams={'name': name})
        return

    def _onDisposing(self):
        shop = self._gameEventController.getShop()
        shop.onBundleUnlocked -= self.__onBundleUpdate
        self._gameEventController.onRewardBoxUpdated -= self.__fillModel
        self._gameEventController.onIngameEventsUpdated -= self.__fillModel

    def __onBundleUpdate(self, _):
        self.__fillModel()

    def __fillModel(self):
        eventRewardController = self._gameEventController.getEventRewardController()
        shop = self._gameEventController.getShop()
        currentProgress = eventRewardController.getCurrentRewardProgress()
        maxProgress = eventRewardController.getMaxRewardProgress()
        with self.viewModel.transaction() as vm:
            vm.setTimeLeft(self.__getEndDate())
            vm.widget.setIsEnabled(eventRewardController.isEnabled())
            vm.widget.setCurrentProgress(min(currentProgress, maxProgress))
            vm.widget.setMaximumProgress(maxProgress)
            vm.widget.setKeysCount(shop.getKeys())

    def __getFinalRewardVehicle(self):
        eventRewards = self._gameEventController.getEventRewardController()
        if not eventRewards.rewardBoxesIDsInOrder:
            return
        else:
            finalBoxID = eventRewards.rewardBoxesIDsInOrder[-1]
            bonusVehicles = eventRewards.rewardBoxesConfig[finalBoxID].bonusVehicles
            if bonusVehicles is not None:
                for bonus in bonusVehicles:
                    for veh, _ in bonus.getVehicles():
                        vehicle = self._itemsCache.items.getItemByCD(veh.intCD)
                        return vehicle

            return

    def __getEndDate(self):
        return getFormattedTimeLeft(max(0, self._eventsCache.getEventFinishTime() - time_utils.getServerUTCTime()))
