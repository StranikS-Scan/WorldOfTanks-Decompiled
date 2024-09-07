# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/lobby/views/winback_reward_view.py
import logging
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen import R
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.shared import IItemsCache
from winback.gui.impl.gen.view_models.views.lobby.views.winback_reward_view_model import WinbackRewardViewModel, RewardWindowType, RewardName
from winback.gui.impl.lobby.tooltips.compensation_tooltip import CompensationTooltip
from winback.gui.impl.lobby.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from winback.gui.impl.lobby.views.winback_bonus_packer import packWinbackBonusModelAndTooltipData, getWinbackBonusPacker, getWinbackBonuses
from winback.gui.impl.lobby.views.winback_bonuses import WinbackVehicleBonus
from winback.gui.shared.event_dispatcher import showWinbackSelectRewardView
from winback.gui.shared.events import WinbackViewEvent
from winback.gui.sounds_constants import REWARD_SOUND_SPACE
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
_AWARDS_ORDER = ['premium_plus',
 RewardName.VEHICLE_FOR_GIFT.value,
 RewardName.SELECTABLE_VEHICLE_FOR_GIFT.value,
 RewardName.SELECTABLE_VEHICLE_DISCOUNT.value,
 RewardName.VEHICLE_DISCOUNT.value,
 RewardName.VEHICLE_FOR_RENT.value,
 'blueprints']

def _selectablesSort(bonuses):
    fromIndex = 0
    toIndex = len(bonuses)
    needShuffle = False
    for idx, bonus in enumerate(bonuses):
        if bonus.getName() == RewardName.SELECTABLE_VEHICLE_DISCOUNT.value:
            if not needShuffle:
                fromIndex = idx
                needShuffle = True
        if needShuffle:
            toIndex = idx
            break

    if needShuffle:
        bonuses[fromIndex:toIndex] = sorted(bonuses[fromIndex:toIndex], key=lambda bonus: -bonus.getLevel())


class WinbackRewardView(ViewImpl):
    __slots__ = ('__selectedRewards', '__tooltipData', '__bonuses', '__isOnlyDaily', '__isLastWindow', '__stageNumber')
    _itemsCache = dependency.descriptor(IItemsCache)
    _winbackController = dependency.descriptor(IWinbackController)
    _COMMON_SOUND_SPACE = REWARD_SOUND_SPACE

    def __init__(self, ctx=None):
        super(WinbackRewardView, self).__init__(ViewSettings(layoutID=R.views.winback.lobby.WinbackRewardView(), flags=ViewFlags.VIEW, model=WinbackRewardViewModel(), args=ctx))
        self.__tooltipData = {}
        self.__selectedRewards = ctx.get('selectedRewards', False)
        self.__isOnlyDaily = ctx.get('isOnlyDaily', False)
        self.__isLastWindow = ctx.get('isLastWindow', False)
        self.__stageNumber = ctx.get('stageNumber', 0)
        self.__bonuses = getWinbackBonuses(ctx.get('bonuses', {}), received=True)
        self.__bonuses.sort(key=self.__sortBonusesByKey)
        _selectablesSort(self.__bonuses)

    @property
    def viewModel(self):
        return super(WinbackRewardView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WinbackRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = self.getTooltipData(event)
        if tooltipData is None:
            return
        elif contentID == R.views.winback.lobby.tooltips.SelectableRewardTooltip():
            return SelectableRewardTooltip(**tooltipData.specialArgs)
        else:
            return CompensationTooltip(**tooltipData.specialArgs) if contentID == R.views.winback.lobby.tooltips.CompensationTooltip() else None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId)

    def destroyWindow(self):
        g_eventBus.handleEvent(WinbackViewEvent(WinbackViewEvent.WINBACK_REWARD_VIEW_CLOSED))
        super(WinbackRewardView, self).destroyWindow()

    def _onLoading(self, *args, **kwargs):
        super(WinbackRewardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setState(self.__getState())
            tx.setStageNumber(self.__stageNumber)
            tx.setProgressionName(self._winbackController.progressionName)
            self.__packRewards(self.__bonuses, tx)

    def _onLoaded(self, *args, **kwargs):
        super(WinbackRewardView, self)._onLoaded(*args, **kwargs)
        g_eventBus.handleEvent(WinbackViewEvent(WinbackViewEvent.WINBACK_REWARD_VIEW_LOADED))

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose),
         (self.viewModel.onSelectReward, self._onSelectReward),
         (self.viewModel.showInHangar, self._showInHangar),
         (self.viewModel.showQuests, self._showQuests),
         (g_playerEvents.onDisconnected, self.destroyWindow))

    def _onClose(self):
        self.destroyWindow()

    def _onSelectReward(self):
        showWinbackSelectRewardView()
        self._onClose()

    def _showInHangar(self):
        vehicleBonus = findFirst(lambda x: isinstance(x, WinbackVehicleBonus), self.__bonuses)
        firstVehicle = first(vehicleBonus.getVehicleCDs()) if vehicleBonus else None
        if firstVehicle:
            selectVehicleInHangar(firstVehicle)
            self.destroyWindow()
        else:
            showHangar()
            _logger.error("Can't find vehicle in bonuses")
            self.destroyWindow()
        return

    def _showQuests(self):
        self._onClose()

    @staticmethod
    def __sortBonusesByKey(bonus):
        bonusName = bonus.getName()
        return _AWARDS_ORDER.index(bonusName) if bonusName in _AWARDS_ORDER else len(_AWARDS_ORDER) + 1

    def __packRewards(self, bonuses, model):
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        packWinbackBonusModelAndTooltipData(bonuses, getWinbackBonusPacker(), rewardsModel, self.__tooltipData)
        rewardsModel.invalidate()

    def __getState(self):
        result = RewardWindowType.PROGRESSION_STEP
        if self.__selectedRewards:
            result = RewardWindowType.SELECTED_REWARDS
        elif self.__isLastWindow:
            result = RewardWindowType.PROGRESSION_COMPLETED
        return result


class WinbackRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(WinbackRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackRewardView(ctx), parent=parent, layer=WindowLayer.TOP_WINDOW)
