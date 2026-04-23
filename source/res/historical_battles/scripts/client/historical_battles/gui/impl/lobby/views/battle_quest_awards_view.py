# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/views/battle_quest_awards_view.py
import logging
import typing
from collections import defaultdict
from copy import deepcopy
from frameworks.wulf import ViewSettings, WindowFlags
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.prb_control.entities.base.listener import IPrbListener
from gui.server_events.bonuses import getNonQuestBonuses, VehiclesBonus
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from historical_battles_common.hb_constants import AccountSettingsKeys, HBTokens
import HBAccountSettings
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_quest_awards_model import BattleQuestAwardsModel, BattleStatus, AwardsViewType
from historical_battles.gui.bonuses.bonus_packer import getBonusPacker
from historical_battles.gui.bonuses.bonuses_helpers import isVehicleTokenBonus, repackTokenToVehicle
from historical_battles.gui.shared.event_dispatcher import showShopView
from historical_battles.gui.sounds.sound_constants import GENERAL_SOUND_SPACE
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from historical_battles.gui.impl.lobby.tooltips.hb_compensation_reward_tooltip import HbCompensationRewardTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_main_discount_tooltip_view import HbMainDiscountTooltipView
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.lobby.hb_helpers.hangar_helpers import closeEvent
if typing.TYPE_CHECKING:
    from typing import List, Optional, Dict
    from frameworks.wulf import Array
    from gui.server_events.bonuses import SimpleBonus
    from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel
_logger = logging.getLogger(__name__)
_MAIN_BONUSES = 'mainBonuses'
_REGULAR_BONUSES = 'regularBonuses'

def awardsFactory(bonusesData, ctx=None):
    resultBonuses = defaultdict(list)
    for key, value in bonusesData.iteritems():
        bonuses = getNonQuestBonuses(key, value, ctx)
        for bonus in bonuses:
            if bonus.getName() == 'battleToken' and isVehicleTokenBonus(bonus):
                bonus = repackTokenToVehicle(bonus)
            bonusKey = _REGULAR_BONUSES
            if bonus.getName() == VehiclesBonus.VEHICLES_BONUS:
                bonusKey = _MAIN_BONUSES
            resultBonuses[bonusKey].append(bonus)

    return resultBonuses


class BattleQuestAwardsView(ViewImpl, IPrbListener):
    _COMMON_SOUND_SPACE = GENERAL_SOUND_SPACE
    __gameEventController = dependency.descriptor(IGameEventController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__tooltipData', '_stage', '__closeCallback')

    def __init__(self, stage, closeCallback):
        settings = ViewSettings(R.views.historical_battles.lobby.BattleQuestAwardsView())
        settings.model = BattleQuestAwardsModel()
        self.__tooltipData = {}
        self._stage = deepcopy(stage)
        self.__closeCallback = closeCallback
        super(BattleQuestAwardsView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(BattleQuestAwardsView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(BattleQuestAwardsView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            return OrderTooltip(showStatus=True, **self.getTooltipData(event).specialArgs)
        if contentID == R.views.historical_battles.lobby.tooltips.HbMainDiscountTooltipView():
            return HbMainDiscountTooltipView()
        return HbCompensationRewardTooltip(contentID, **self.getTooltipData(event).specialArgs) if contentID == R.views.historical_battles.lobby.tooltips.HbCompensationRewardTooltip() else None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def updateModel(self):
        frontId = self._stage.get('frontId', 0)
        rewardsData = self._stage.get('detailedRewards', {})
        hasVehicleInRewards = self.__convertDiscountRewards(rewardsData)
        hasVehicleInInventory = self.__gameEventController.heroTank.hasHeroVehicle()
        bonuses = awardsFactory(rewardsData)
        viewType = self._stage.get('viewType', AwardsViewType.PROGRESSION)
        lastFrontId = HBAccountSettings.getSettings(AccountSettingsKeys.LAST_FRONT_ID_IN_AWARDS)
        if lastFrontId != frontId:
            HBAccountSettings.setSettings(AccountSettingsKeys.LAST_FRONT_ID_IN_AWARDS, frontId)
        with self.viewModel.transaction() as model:
            model.setFrontName(self.__gameEventController.frontController.getFront(frontId).getName())
            model.setBattleStatus(BattleStatus.INPROGRESS if not self._stage.get('finishStage', False) else BattleStatus.COMPLETED)
            model.setAwardsViewType(viewType)
            model.setLevel(self._stage.get('stage', 0))
            model.setHasVehicleInRewards(hasVehicleInRewards)
            model.setHasVehicleInInventory(hasVehicleInInventory)
            model.setIsSpecial(self._stage.get('isSpecial', False))
            self.__updateModelRewards(model.getRewards(), bonuses[_REGULAR_BONUSES])
            self.__updateModelRewards(model.getMainRewards(), bonuses[_MAIN_BONUSES])

    def _onLoading(self, *args, **kwargs):
        super(BattleQuestAwardsView, self)._onLoading(args, kwargs)
        self.updateModel()
        self.__addListeners()

    def _finalize(self):
        self.__executeCloseCallback()
        self.__removeListeners()
        super(BattleQuestAwardsView, self)._finalize()

    def __updateModelRewards(self, rewardsArray, bonuses):
        packBonusModelAndTooltipData(bonuses, rewardsArray, self.__tooltipData, getBonusPacker())

    def __addListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose += self.__onClose
            model.onApprove += self.__onApprove
            model.onShopClick += self.__onShopClick
            model.onHangarClick += self.__onHangarClick
        self.__gameEventController.onCloseAllAwardsWindow += self.__onClose

    def __removeListeners(self):
        with self.viewModel.transaction() as model:
            model.onClose -= self.__onClose
            model.onApprove -= self.__onApprove
            model.onShopClick -= self.__onShopClick
            model.onHangarClick -= self.__onHangarClick
        self.__gameEventController.onCloseAllAwardsWindow -= self.__onClose

    def __convertDiscountRewards(self, rewardsData):
        mainDiscountConf = self.__gameEventController.getMainDiscount()
        mainDiscountToken = mainDiscountConf['tokenName']
        rewardTokens = rewardsData.get('tokens', {})
        if mainDiscountToken in rewardTokens:
            if self.__itemsCache.items.tokens.getTokenCount(HBTokens.MAIN_VEHICLE_BOUGHT) > 0:
                del rewardTokens[mainDiscountToken]
            else:
                tokenCount = self.__itemsCache.items.tokens.getTokenCount(mainDiscountConf['tokenName'])
                if tokenCount == mainDiscountConf['maxTokenCount']:
                    del rewardTokens[mainDiscountToken]
                    vehicleCD = self.__gameEventController.heroTank.getVehicleCD()
                    rewardTokens['vehicle:{}:100'.format(vehicleCD)] = {'count': 1}
                    return True
        return HBTokens.MAIN_VEHICLE_DISCOUNT_COMPENSATION in rewardTokens

    def __onClose(self):
        self.__executeCloseCallback()
        self.destroyWindow()

    def __onApprove(self):
        self.__onClose()

    def __onShopClick(self):
        showShopView()
        self.__onClose()

    def __onHangarClick(self):
        vehicleCD = self.__gameEventController.heroTank.getVehicleCD()
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        if vehicle and vehicle.isInInventory:
            self.__gameEventController.onCloseAllAwardsWindow()
            event_dispatcher.selectVehicleInHangar(vehicleCD)
            closeEvent()

    def __executeCloseCallback(self):
        if self.__closeCallback is not None:
            callback = self.__closeCallback
            self.__closeCallback = None
            callback()
        return


class BattleQuestAwardsViewWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, stage, closeCallback=None, parent=None):
        super(BattleQuestAwardsViewWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=BattleQuestAwardsView(stage, closeCallback), parent=parent)
