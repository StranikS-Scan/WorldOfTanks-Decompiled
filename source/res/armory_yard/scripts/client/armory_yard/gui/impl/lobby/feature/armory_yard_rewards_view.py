# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/lobby/feature/armory_yard_rewards_view.py
from copy import deepcopy
from CurrentVehicle import g_currentVehicle
from armory_yard.gui.impl.lobby.feature.tooltips.rest_reward_tooltip_view import RestRewardTooltipView
from armory_yard.gui.shared.bonus_packers import getArmoryYardBonusPacker
from armory_yard.gui.shared.bonuses_sorter import bonusesSortKeyFunc
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl.gen import R
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_rewards_view_model import ArmoryYardRewardsViewModel
from armory_yard.gui.impl.gen.view_models.views.lobby.feature.armory_yard_reward_state import ArmoryYardRewardState
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import getNonQuestBonuses, mergeBonuses, splitBonuses
from gui.shared.event_dispatcher import showHangar
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import Currency
from helpers import dependency
from skeletons.gui.game_control import IArmoryYardController
from skeletons.gui.shared import IItemsCache
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent

class ArmoryYardRewardsView(ViewImpl):
    __itemsCache = dependency.descriptor(IItemsCache)
    __armoryYardCtrl = dependency.descriptor(IArmoryYardController)
    __MAX_MAIN_BONUSES = 3
    __MAIN_BONUS_SECTIONS = ['customizations',
     'premium_plus',
     Currency.CRYSTAL,
     'freeXP']
    __slots__ = ('__tooltipData', '__rawBonuses', '__mainBonuses', '__vehicles', '__state', '__closeCallback', '__stages', '__bonuses')

    def __init__(self, layoutID, bonuses, state=None, stage=0, closeCallback=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = ArmoryYardRewardsViewModel()
        self.__tooltipData = {}
        self.__rawBonuses = deepcopy(bonuses)
        self.__vehicles = self.__rawBonuses.pop('vehicles', [])
        self.__mainBonuses = {}
        self.__bonuses = []
        self.__stages = stage
        self.__state = state or ArmoryYardRewardState.STAGE
        self.__closeCallback = closeCallback
        self.__fillMainBonuses()
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
        showHangar()
        selectedVehicle = None
        for vehicleDict in self.__vehicles:
            for intCD in vehicleDict:
                vehicle = self.__itemsCache.items.getItemByCD(intCD)
                if selectedVehicle is None or selectedVehicle.level < vehicle.level:
                    selectedVehicle = vehicle

        if selectedVehicle is not None:
            g_currentVehicle.selectVehicle(selectedVehicle.invID)
        self.destroyWindow()
        return

    def _onLoading(self, *args, **kwargs):
        super(ArmoryYardRewardsView, self)._onLoading(*args, **kwargs)
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': False}), EVENT_BUS_SCOPE.GLOBAL)
        with self.viewModel.transaction() as vm:
            vm.setState(self.__state)
            vm.setStages(self.__stages)
            vm.setHasAllRewards(self.__hasAllRewards())
            self.__fillVehiclesModel(self.__vehicles, vm.getVehicles())
            self.__bonuses = self.__fillRewardsModel(self.__rawBonuses, vm.getRewards())
            self.__fillRewardsModel(self.__mainBonuses, vm.getMainRewards())

    def _getEvents(self):
        events = [(self.viewModel.onClose, self.onClose), (self.viewModel.onShowVehicle, self.onShowVehicle)]
        if self.__armoryYardCtrl.isActive():
            events.append((self.__armoryYardCtrl.onProgressUpdated, self.__onProgressUpdated))
        return tuple(events)

    def _finalize(self):
        super(ArmoryYardRewardsView, self)._finalize()
        self.__closeCallback = None
        return

    def __fillMainBonuses(self):
        if self.__stages == 1:
            self.__mainBonuses = self.__rawBonuses
            self.__rawBonuses = {}
            return
        maxBonuses = self.__MAX_MAIN_BONUSES + 1
        if 'items' in self.__rawBonuses:
            devices = {}
            items = self.__rawBonuses['items']
            for itemCD in items.keys():
                if self.__itemsCache.items.getItemByCD(itemCD).itemTypeID == GUI_ITEM_TYPE.OPTIONALDEVICE:
                    devices[itemCD] = items.pop(itemCD)
                    if len(devices) == self.__MAX_MAIN_BONUSES:
                        break

            if devices:
                self.__mainBonuses['items'] = devices
                maxBonuses -= len(devices)
        for section in self.__MAIN_BONUS_SECTIONS:
            if len(self.__mainBonuses) == maxBonuses:
                return
            if section in self.__rawBonuses:
                self.__mainBonuses[section] = self.__rawBonuses.pop(section)

    def __fillRewardsModel(self, bonuses, rewardsList):
        rewardsList.clear()
        rewards = []
        for bonusType, bonusValue in bonuses.items():
            bonus = getNonQuestBonuses(bonusType, bonusValue)
            rewards.extend(bonus)

        rewards = splitBonuses(mergeBonuses(rewards))
        rewards.sort(key=bonusesSortKeyFunc)
        for idx, value in enumerate(rewards):
            if value.getName() == 'battleToken' and value.getValue().get('ny24_yaga') is not None:
                rewards.pop(idx)

        packBonusModelAndTooltipData(rewards, rewardsList, self.__tooltipData, getArmoryYardBonusPacker())
        rewardsList.invalidate()
        return rewards

    def __fillVehiclesModel(self, vehicles, vehiclesArray):
        vehiclesArray.clear()
        if vehicles:
            packBonusModelAndTooltipData(getNonQuestBonuses('vehicles', vehicles), vehiclesArray, self.__tooltipData, getArmoryYardBonusPacker())
        vehiclesArray.invalidate()

    def __onProgressUpdated(self):
        self.getViewModel().setHasAllRewards(self.__hasAllRewards())

    def __hasAllRewards(self):
        hasAllSimpleReward = self.__armoryYardCtrl.getProgressionLevel() >= self.__armoryYardCtrl.getTotalSteps() - 1
        hasAllToken = self.__armoryYardCtrl.getCurrencyTokenCount() == self.__armoryYardCtrl.getTotalSteps()
        return self.__armoryYardCtrl.isActive() and hasAllSimpleReward and hasAllToken


class ArmoryYardRewardsWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, bonuses, state=None, stage=0, closeCallback=None, parent=None):
        super(ArmoryYardRewardsWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=ArmoryYardRewardsView(R.views.armory_yard.lobby.feature.ArmoryYardRewardsView(), bonuses=bonuses, state=state, stage=stage, closeCallback=closeCallback), parent=parent)
