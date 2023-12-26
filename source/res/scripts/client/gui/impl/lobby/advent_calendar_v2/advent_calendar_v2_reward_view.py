# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/advent_calendar_v2/advent_calendar_v2_reward_view.py
import logging
from functools import partial
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, getAdventAwardsBonuses
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.advent_calendar.advent_calendar_reward_view_model import AdventCalendarRewardViewModel, AwardDayState, OpenDoorStatus
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.advent_calendar_big_lootbox_tooltip_model import ProgressionState
from gui.impl.lobby.advent_calendar_v2.advent_calendar_v2_helper import openAndWaitAdventCalendarDoor, isAdventAnimationEnabled
from gui.impl.lobby.advent_calendar_v2.advent_calendar_view import AdventCalendarView
from gui.impl.lobby.advent_calendar_v2.tooltips.advent_calendar_big_lootbox_tooltip import AdventCalendarBigLootBoxTooltip
from gui.impl.lobby.dialogs.full_screen_dialog_view import FullScreenDialogBaseView
from gui.impl.lobby.new_year.tooltips.ny_gift_machine_token_tooltip import NyGiftMachineTokenTooltip
from gui.server_events.awards_formatters import BATTLE_BONUS_X5_TOKEN
from gui.server_events.bonuses import BattleTokensBonus, LootBoxTokensBonus
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.events import LobbySimpleEvent
from helpers import dependency
from items.components.ny_constants import NyCurrency
from skeletons.gui.game_control import IAdventCalendarV2Controller
EXCLUDET_CLASSES = (BattleTokensBonus,)
_BONUSES_ORDER = ({'getIcon': 'nyCoin'},
 {'getName': 'tmanToken'},
 {'getName': 'newYear_premium'},
 {'getName': 'premium_plus'},
 {'getName': 'customizations'},
 {'getName': 'crewSkin'},
 {'getName': 'goodies',
  'getIcon': 'booster_credits'},
 {'getName': 'goodies',
  'getIcon': 'booster_xp'},
 {'getName': 'goodies',
  'getIcon': 'booster_free_xp_and_crew_xp'},
 {'getName': 'crewBooks'},
 {'getName': 'goodies',
  'getIcon': 'recertificationForm'},
 {'getName': BATTLE_BONUS_X5_TOKEN},
 {'getName': 'items',
  'getIcon': 'modernizedExtraHealthReserveAntifragmentationLining'},
 {'getName': 'items',
  'getIcon': 'modernizedTurbochargerRotationMechanism'},
 {'getName': 'items',
  'getIcon': 'modernizedAimDrivesAimingStabilizer'},
 {'getName': 'equipCoin'},
 {'getName': 'credits'})

def _keySortOrder(bonus, _):
    for index, criteria in enumerate(_BONUSES_ORDER):
        for method, value in criteria.items():
            if not hasattr(bonus, method) or value not in getattr(bonus, method)():
                break
        else:
            return index

    return len(_BONUSES_ORDER)


_logger = logging.getLogger(__name__)

class AdventCalendarRewardView(AdventCalendarView, FullScreenDialogBaseView):
    __slots__ = ('__bonuses', '__tooltipData', '__isProgressionReward', '__currencyName')
    __adventCalendarV2Ctrl = dependency.descriptor(IAdventCalendarV2Controller)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.advent_calendar.RewardView())
        settings.model = AdventCalendarRewardViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AdventCalendarRewardView, self).__init__(settings)
        self.__isProgressionReward = False
        self.__bonuses = []
        self.__tooltipData = {}
        self.__currencyName = ''

    @property
    def viewModel(self):
        return self.getViewModel()

    def _finalize(self):
        g_eventBus.handleEvent(events.AdventCalendarV2Event(events.AdventCalendarV2Event.PROGRESSION_REWARD_VIEWED, {'isProgressionRewardCompleted': self.__isProgressionReward,
         'doorIsOpened': self.viewModel.getOpenDoorStatus() == OpenDoorStatus.OPEN_DOOR_SUCCESS}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__bonuses = None
        self.__tooltipData = {}
        super(AdventCalendarRewardView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.viewModel.onCloseBtnClick, self.__onClose),
         (self.viewModel.onGoToBoxesBtnClick, self.__onOpenBoxes),
         (self.viewModel.onSetBlur, self.__onSetBlur),
         (self.viewModel.onRewardsShown, self.__onRequestOpenDoor))

    def _getListeners(self):
        return ((LobbySimpleEvent.SHOW_LOOT_BOX_VIEW, self.__onClose, EVENT_BUS_SCOPE.LOBBY),)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.__getBackportTooltipData(event)
            window = BackportTooltipWindow(tooltipData, self.getParentWindow()) if tooltipData is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(AdventCalendarRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        isPostEvent = self.__adventCalendarV2Ctrl.isInPostActivePhase()
        if contentID == R.views.lobby.new_year.tooltips.NyGiftMachineTokenTooltip():
            return NyGiftMachineTokenTooltip(adventCalendarState=ProgressionState.REWARD_RECEIVED, doorsToOpenAmount=0, isAdventCalendarPostEvent=isPostEvent)
        if contentID == R.views.lobby.advent_calendar.tooltips.AdventCalendarBigLootBoxTooltip():
            return AdventCalendarBigLootBoxTooltip(ProgressionState.REWARD_RECEIVED, 0, isPostEvent, False)
        tooltipData = self.__getBackportTooltipData(event)
        return getRewardTooltipContent(event, tooltipData)

    def _onLoading(self, data, dayId, isProgressionReward, currencyName, *args, **kwargs):
        super(AdventCalendarRewardView, self)._onLoading(*args, **kwargs)
        self.__isProgressionReward = isProgressionReward
        self.__updateBonuses(data)
        self.__currencyName = currencyName
        self.__tooltipData = {}
        allComplDays = len(self.__adventCalendarV2Ctrl.completedAdventCalendarAwardsQuests)
        with self.viewModel.transaction() as vm:
            self.__setBonuses(vm)
            vm.setDayId(dayId)
            vm.setDoorsOpenedAm(allComplDays)
            vm.setShowBoxesButton(self.isLootBoxInBonuses(data))
            vm.setIsAnimationEnabled(isAdventAnimationEnabled())
            vm.setOpenDoorStatus(OpenDoorStatus.OPEN_DOOR_UNDEFINED)
            if self.__isProgressionReward:
                vm.setAwardDayState(AwardDayState.PROGRESSIONQUEST)
            elif self.__adventCalendarV2Ctrl.getMaxDayNumbers == dayId:
                vm.setAwardDayState(AwardDayState.LASTDOORDAY)
            else:
                vm.setAwardDayState(AwardDayState.REGULARDAY)

    def isLootBoxInBonuses(self, rewards):
        for bonus in rewards:
            if bonus.getName() == 'battleToken' and isinstance(bonus, LootBoxTokensBonus):
                return True

        return False

    def __onClose(self, *args, **kwargs):
        self.destroy()

    def __onOpenBoxes(self):
        self.destroyWindow()
        showLootBoxEntry()

    def __onSetBlur(self, event):
        param = event.get('setBlur', '')
        g_eventBus.handleEvent(events.AdventCalendarV2Event(events.AdventCalendarV2Event.CHANGE_BLUR_STATUS, {'setBlur': param}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __setBonuses(self, viewModel):
        bonusesList = viewModel.getBonuses()
        bonusesList.clear()
        for index, (bonus, tooltip) in enumerate(self.__bonuses):
            tooltipId = str(index)
            bonus.setTooltipId(tooltipId)
            bonus.setIndex(index)
            bonusesList.addViewModel(bonus)
            self.__tooltipData[tooltipId] = tooltip

        bonusesList.invalidate()

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        if tooltipId is None:
            return
        else:
            return self.__tooltipData[tooltipId] if tooltipId in self.__tooltipData else None

    def __updateBonuses(self, data):
        adventAwards = getAdventAwardsBonuses(data, excludedCls=EXCLUDET_CLASSES, sortKey=lambda b: _keySortOrder(*b))
        self.__bonuses = adventAwards or []

    def __onRequestOpenDoor(self, event):
        if self.__isProgressionReward:
            return self.viewModel.setOpenDoorStatus(OpenDoorStatus.OPEN_DOOR_SUCCESS)
        else:
            doorId = int(event.get('dayId', 0))
            if not doorId:
                _logger.error('Parametr dayId is ommited')
                return None
            return self.__requestOpenDoor(doorId=doorId, currencyName=self.__currencyName)

    def __requestOpenDoor(self, doorId, currencyName=''):
        _logger.debug('Created open request  for doorId=%d, currencyName=%s', doorId, currencyName)
        openDoorClb = partial(self.__processServerDoorOpen, dayId=doorId)
        if self.__adventCalendarV2Ctrl.isInPostActivePhase() and not currencyName:
            currencyName = NyCurrency.CRYSTAL
        openAndWaitAdventCalendarDoor(dayID=doorId, currencyName=currencyName, callback=openDoorClb)

    def __processServerDoorOpen(self, dayId, result):
        _logger.debug('Waiting for reward window finished, doorId=%d', dayId)
        status = OpenDoorStatus.OPEN_DOOR_SUCCESS if result else OpenDoorStatus.OPEN_DOOR_FAILED
        self.viewModel.setOpenDoorStatus(status)
        if not result:
            self.__onSetBlur({'setBlur': False})
            self.destroy()
