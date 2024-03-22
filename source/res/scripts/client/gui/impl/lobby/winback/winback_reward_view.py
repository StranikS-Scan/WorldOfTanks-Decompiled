# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/winback/winback_reward_view.py
import logging
import typing
from PlayerEvents import g_playerEvents
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.battle_pass.sounds import BattlePassSounds, SOUNDS
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport.backport_tooltip import TooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import RewardName
from gui.impl.gen.view_models.views.lobby.winback.winback_reward_view_model import WinbackRewardViewModel, RewardWindowType
from gui.impl.lobby.missions.daily_quests_view import DailyTabs
from gui.impl.lobby.winback.tooltips.selectable_reward_tooltip import SelectableRewardTooltip
from gui.impl.lobby.winback.winback_bonus_packer import getWinbackBonusPacker, getWinbackBonuses
from gui.impl.lobby.winback.winback_bonuses import WinbackVehicleBonus
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.events_dispatcher import showDailyQuests
from gui.shared.event_dispatcher import selectVehicleInHangar, showHangar, showWinbackSelectRewardView
from gui.shared.missions.packers.bonus import packMissionsBonusModelAndTooltipData
from helpers import dependency
from shared_utils import findFirst, first
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.shared import IItemsCache
from sound_gui_manager import CommonSoundSpaceSettings
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
    __slots__ = ('__selectedRewards', '__tooltipData', '__bonuses', '__questIDs', '__isOnlyDaily', '__isLastWindow')
    _itemsCache = dependency.descriptor(IItemsCache)
    _winbackController = dependency.descriptor(IWinbackController)
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name=SOUNDS.ACTIVATE_CHAPTER_STATE, entranceStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_ON}, exitStates={SOUNDS.ACTIVATE_CHAPTER_STATE: SOUNDS.ACTIVATE_CHAPTER_STATE_OFF}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=BattlePassSounds.REWARD_SCREEN, exitEvent='')

    def __init__(self, ctx=None):
        super(WinbackRewardView, self).__init__(ViewSettings(layoutID=R.views.lobby.winback.WinbackRewardView(), flags=ViewFlags.VIEW, model=WinbackRewardViewModel(), args=ctx))
        self.__questIDs = ctx.get('quests', [])
        self.__tooltipData = {}
        self.__selectedRewards = ctx.get('selectedRewards', False)
        self.__isOnlyDaily = ctx.get('isOnlyDaily', False)
        self.__isLastWindow = ctx.get('isLastWindow', False)
        self.__bonuses = getWinbackBonuses(ctx.get('bonuses', {}), received=True)
        self.__bonuses.sort(key=self.__sortBonusesByKey)
        _selectablesSort(self.__bonuses)

    @property
    def viewModel(self):
        return super(WinbackRewardView, self).getViewModel()

    def createToolTip(self, event):
        tooltipId = event.getArgument('tooltipId')
        window = None
        if tooltipId is not None:
            tooltipData = self.__tooltipData.get(tooltipId)
            if tooltipData and isinstance(tooltipData, TooltipData):
                window = BackportTooltipWindow(tooltipData, self.getParentWindow(), event)
                window.load()
            else:
                window = super(WinbackRewardView, self).createToolTip(event)
        return window

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.winback.tooltips.SelectableRewardTooltip():
            tooltipId = event.getArgument('tooltipId')
            tooltipData = self.__tooltipData.get(tooltipId)
            if tooltipData:
                return SelectableRewardTooltip(**tooltipData)
        return super(WinbackRewardView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(WinbackRewardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as tx:
            tx.setState(self.__getState())
            tx.setIsFirstProgressionStep(bool([ qID for qID in self.__questIDs if self._winbackController.isWinbackQuest(qID) and self._winbackController.getQuestIdx(qID) == 1 ]))
            tx.setIsSelectableAwardAvailable(self._winbackController.hasWinbackOfferToken())
            self.__packRewards(self.__bonuses, tx)

    def _getEvents(self):
        return ((self.viewModel.onClose, self._onClose),
         (self.viewModel.onSelectReward, self._onSelectReward),
         (self.viewModel.showInHangar, self._showInHangar),
         (self.viewModel.showQuests, self._showQuests),
         (g_playerEvents.onDisconnected, self.destroyWindow))

    def _onClose(self):
        self.destroyWindow()

    @staticmethod
    def _onSelectReward():
        showWinbackSelectRewardView()

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
        self.destroyWindow()
        showDailyQuests(subTab=DailyTabs.QUESTS)

    @staticmethod
    def __sortBonusesByKey(bonus):
        bonusName = bonus.getName()
        return _AWARDS_ORDER.index(bonusName) if bonusName in _AWARDS_ORDER else len(_AWARDS_ORDER) + 1

    def __packRewards(self, bonuses, model):
        rewardsModel = model.getRewards()
        rewardsModel.clear()
        packMissionsBonusModelAndTooltipData(bonuses, getWinbackBonusPacker(), model.getRewards(), self.__tooltipData)
        rewardsModel.invalidate()

    def __getState(self):
        result = RewardWindowType.PROGRESSION_STEP
        if self.__isOnlyDaily:
            result = RewardWindowType.REGULAR_PROGRESSION_COMPLETED
        elif self.__selectedRewards:
            result = RewardWindowType.SELECTED_REWARDS
        elif len(self.__questIDs) == 1 and self._winbackController.getQuestIdx(self.__questIDs[0]) < 1:
            result = RewardWindowType.WELCOME
        elif self.__isLastWindow and self._winbackController.isFinished():
            result = RewardWindowType.WINBACK_PROGRESSION_COMPLETED
        return result


class WinbackRewardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, parent=None, ctx=None):
        super(WinbackRewardWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=WinbackRewardView(ctx), parent=parent)
