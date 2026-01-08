# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_rewards_view.py
from copy import deepcopy
from armory_yard.gui.impl.lobby.feature.tooltips.armory_yard_currency_tooltip_view import ArmoryYardCurrencyTooltipView
from armory_yard.gui.impl.lobby.feature.tooltips.rest_reward_tooltip_view import RestRewardTooltipView
from armory_yard.gui.shared.bonus_packers import getArmoryYardBonusPacker, getArmoryYardMainRewardBonusPacker
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import ArmoryYardRewardsViewModel, State
from armory_yard_constants import State as ArmoryYardState
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.shared.event_dispatcher import selectVehicleInHangar
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from skeletons.gui.shared import IItemsCache
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
_LOOTBOX_RES = R.views.dyn('gui_lootboxes').dyn('lobby').dyn('gui_lootboxes').dyn('tooltips').dyn('LootboxTooltip')

class ArmoryYardRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __MAX_MAIN_BONUSES = 3
    __slots__ = ('__tooltipData', '__rawBonuses', '__mainBonuses', '__vehicles', '__state', '__closeCallback', '__stages', '__bonuses', '__isFinalReward')

    def __init__(self, layoutID, bonuses, state=State.STAGE, stage=0, closeCallback=None, isFinalReward=False):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ArmoryYardRewardsViewModel()
        self.__tooltipData = {}
        self.__rawBonuses = deepcopy(bonuses)
        self.__vehicles = self.__rawBonuses.pop('vehicles', [])
        self.__mainBonuses = []
        self.__bonuses = []
        self.__stages = stage
        self.__state = state
        self.__closeCallback = closeCallback
        self.__isFinalReward = isFinalReward
        self.__splitMainBonuses()
        super(ArmoryYardRewardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(ArmoryYardRewardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(ArmoryYardRewardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.armory_yard.lobby.feature.tooltips.RestRewardTooltipView():
            inBoxCount = event.getArgument('inBoxCount')
            return RestRewardTooltipView(self.__bonuses[len(self.__bonuses) - int(inBoxCount):])
        if contentID == R.views.armory_yard.lobby.feature.tooltips.ArmoryYardCurrencyTooltipView():
            currency = event.getArgument('currency')
            if self.getTooltipData(event):
                currency = currency or self.getTooltipData(event).specialArgs[0]
            return ArmoryYardCurrencyTooltipView(currency)
        if _LOOTBOX_RES.exists() and contentID == _LOOTBOX_RES():
            from gui_lootboxes.gui.impl.lobby.gui_lootboxes.tooltips.lootbox_tooltip import LootboxTooltip
            tooltipData = self.getTooltipData(event)
            lootBoxID = tooltipData.get('lootBoxID')
            lootBox = self.__itemsCache.items.tokens.getLootBoxByID(int(lootBoxID))
            return LootboxTooltip(lootBox)
        return super(ArmoryYardRewardsView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        index = event.getArgument(ArmoryYardRewardsViewModel.ARG_REWARD_INDEX)
        return self.__tooltipData.get(index, None)

    def onClose(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)
        if self.__closeCallback is not None:
            self.__closeCallback()
        self.destroyWindow()
        return

    def onShowVehicle(self):
        selectedVehicle = None
        for vehicleDict in self.__vehicles:
            for intCD in vehicleDict:
                vehicle = self.__itemsCache.items.getItemByCD(intCD)
                if selectedVehicle is None or selectedVehicle.level < vehicle.level:
                    selectedVehicle = vehicle

        selectVehicleInHangar(selectedVehicle.intCD)
        self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardRewardsView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        with self.viewModel.transaction() as vm:
            vm.setState(self.__state)
            vm.setStages(self.__stages)
            vm.setHasAllRewards(self.__hasAllRewards())
            vm.setIsFinalReward(self.__isFinalReward)
            vm.setIsAciveState(self.__armoryYardCtrl.getState() == ArmoryYardState.ACTIVE)
            self.__fillVehiclesModel(self.__vehicles, vm.getVehicles())
            self.__bonuses = self.__fillRewardsModel(self.__bonuses, vm.getRewards(), getArmoryYardBonusPacker)
            self.__fillRewardsModel(self.__mainBonuses, vm.getMainRewards(), getArmoryYardMainRewardBonusPacker)

    def _getEvents(self):
        events = [(self.viewModel.onClose, self.onClose), (self.viewModel.onShowVehicle, self.onShowVehicle)]
        if self.__armoryYardCtrl.isActive():
            events.append((self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdated))
        return tuple(events)

    def _finalize(self):
        super(ArmoryYardRewardsView, self)._finalize()
        self.__closeCallback = None
        return

    def __splitMainBonuses(self):
        maxBonuses = self.__MAX_MAIN_BONUSES
        bonuses = []
        for bonusType, bonusValue in self.__rawBonuses.iteritems():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            bonuses.extend(bonus)

        bonuses = splitBonuses(mergeBonuses(bonuses))
        bonuses.sort(key=bonusesSortKeyFunc)
        self.__mainBonuses = bonuses[:maxBonuses]
        self.__bonuses = bonuses[maxBonuses:]

    def __fillRewardsModel(self, bonuses, rewardsList, packer):
        rewardsList.clear()
        packBonusModelAndTooltipData(bonuses, rewardsList, self.__tooltipData, packer())
        rewardsList.invalidate()
        return bonuses

    def __fillVehiclesModel(self, vehicles, vehiclesArray):
        vehiclesArray.clear()
        if vehicles:
            packBonusModelAndTooltipData(getNonQuestBonuses('vehicles', vehicles), vehiclesArray, self.__tooltipData, getArmoryYardBonusPacker())
        vehiclesArray.invalidate()

    def __onProgressUpdated(self):
        self.getViewModel().setHasAllRewards(self.__hasAllRewards())

    def __hasAllRewards(self):
        hasAllSimpleReward = self.__armoryYardCtrl.getProgressionLevel() >= self.__armoryYardCtrl.maxNumberOfSteps - 1
        hasAllToken = self.__armoryYardCtrl.getProgressionTokenCount() == self.__armoryYardCtrl.maxNumberOfSteps
        return bool(self.__armoryYardCtrl.isActive() and hasAllSimpleReward and hasAllToken)


class ArmoryYardRewardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bonuses, state=State.STAGE, stage=0, closeCallback=None, parent=None, isFinalReward=False):
        super(ArmoryYardRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ArmoryYardRewardsView(R.views.armory_yard.lobby.feature.ArmoryYardRewardsView(), bonuses=bonuses, state=state, stage=stage, closeCallback=closeCallback, isFinalReward=isFinalReward), parent=parent)
