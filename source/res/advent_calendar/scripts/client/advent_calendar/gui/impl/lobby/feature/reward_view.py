# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/gui/impl/lobby/feature/reward_view.py
from __future__ import absolute_import
import logging
from functools import partial
import typing
from advent_calendar.gui.impl.gen.view_models.views.lobby.reward_view_model import RewardViewModel, OpenDoorStatus, AwardDayState
from advent_calendar.gui.impl.lobby.feature.advent_helper import openAndWaitDoor, isAdventAnimationEnabled
from advent_calendar.gui.impl.lobby.feature.bonus_grouper import RewardBonusGrouper, RewardsBonusGroups
from advent_calendar.gui.impl.lobby.feature.bonus_packers import getRewardBonusPacker
from advent_calendar.gui.shared import events
from advent_calendar.skeletons.game_controller import IAdventCalendarController
from frameworks.wulf import ViewSettings, WindowFlags, WindowLayer
from gui.impl.gen import R
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.server_events.bonuses import BattleTokensBonus, LootBoxTokensBonus
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency
if typing.TYPE_CHECKING:
    from typing import Any, List, Tuple
    from gui.impl.backport import TooltipData
    from gui.server_events.bonuses import SimpleBonus
_logger = logging.getLogger(__name__)
EXCLUDET_CLASSES = (BattleTokensBonus,)
_BONUSES_ORDER = (RewardsBonusGroups.LOOTBOX,
 RewardsBonusGroups.EXPERIMENTAL_EQUIPMENT,
 RewardsBonusGroups.MENTORING_LICENSE,
 RewardsBonusGroups.CREW_MEMBER,
 RewardsBonusGroups.STYLE_2D,
 RewardsBonusGroups.FREEXP,
 RewardsBonusGroups.PREMIUM,
 RewardsBonusGroups.COMPONENTS,
 RewardsBonusGroups.CREDITS,
 RewardsBonusGroups.RESERVE_CREDITS,
 RewardsBonusGroups.RESERVE_EXP,
 RewardsBonusGroups.CREW_BONUSES,
 RewardsBonusGroups.BATTLE_BONUS_5X,
 RewardsBonusGroups.RECERTIFICATION_FORM,
 RewardsBonusGroups.DECAL,
 RewardsBonusGroups.RESERVE_COMBINED_EXP)

def sortBonuses(groupedBonuses, excluded=(), excludedCls=()):
    sortedGroupedBonuses = sorted(groupedBonuses, key=lambda b: _BONUSES_ORDER.index(b[0]) if b[0] in _BONUSES_ORDER else len(_BONUSES_ORDER))
    bonuses = []
    for _, bonus in sortedGroupedBonuses:
        if bonus.getName() in excluded or isinstance(bonus, excludedCls):
            continue
        bonuses.append(bonus)

    return bonuses


class RewardView(ViewImpl):
    __slots__ = ('__bonuses', '__isProgressionReward', '__tooltips')
    __adventController = dependency.descriptor(IAdventCalendarController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.advent_calendar.mono.lobby.reward_view(), model=RewardViewModel(), args=args, kwargs=kwargs)
        super(RewardView, self).__init__(settings)
        self.__tooltips = {}
        self.__isProgressionReward = False

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(RewardView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _isLootBoxInBonuses(self, bonuses):
        for bonus in bonuses:
            if bonus.getName() == 'lootBox' and isinstance(bonus, LootBoxTokensBonus):
                return True

        return False

    def _onLoading(self, dayId, isProgressionReward, bonuses, *args, **kwargs):
        super(RewardView, self)._onLoading(*args, **kwargs)
        self.__isProgressionReward = isProgressionReward
        openedDoors = len(self.__adventController.completedAwardsQuests)
        openedDoors = openedDoors + 1 if not isProgressionReward else openedDoors
        with self.viewModel.transaction() as vm:
            packBonusModelAndTooltipData(sortBonuses(RewardBonusGrouper().group(bonuses), excludedCls=EXCLUDET_CLASSES), vm.getBonuses(), self.__tooltips, packer=getRewardBonusPacker())
            vm.setDayId(dayId)
            vm.setDoorsOpenedAm(openedDoors)
            vm.setShowBoxesButton(self._isLootBoxInBonuses(bonuses))
            vm.setIsAnimationEnabled(isAdventAnimationEnabled())
            vm.setOpenDoorStatus(OpenDoorStatus.OPEN_DOOR_UNDEFINED)
            if self.__isProgressionReward:
                vm.setAwardDayState(AwardDayState.PROGRESSIONQUEST)
            elif self.__adventController.config.isSpecialDay(dayId):
                vm.setAwardDayState(AwardDayState.SPECIALDAY)
            else:
                vm.setAwardDayState(AwardDayState.REGULARDAY)

    def _finalize(self):
        g_eventBus.handleEvent(events.AdventCalendarEvent(events.AdventCalendarEvent.PROGRESSION_REWARD_VIEWED, {'isProgressionRewardCompleted': self.__isProgressionReward,
         'doorIsOpened': self.viewModel.getOpenDoorStatus() == OpenDoorStatus.OPEN_DOOR_SUCCESS}), scope=EVENT_BUS_SCOPE.LOBBY)
        self.__tooltips.clear()
        super(RewardView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onCloseBtnClick, self.__onClose),
         (self.viewModel.onGoToBoxesBtnClick, self.__onOpenBoxes),
         (self.viewModel.onSetBlur, self.__onSetBlur),
         (self.viewModel.onRewardsShown, self.__onRequestOpenDoor))

    def __onClose(self, *args, **kwargs):
        self.destroyWindow()

    def __onOpenBoxes(self):
        self.destroyWindow()

    def __onSetBlur(self, event):
        param = event.get('setBlur', '')
        g_eventBus.handleEvent(events.AdventCalendarEvent(events.AdventCalendarEvent.CHANGE_BLUR_STATUS, {'setBlur': param}), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onRequestOpenDoor(self, event):
        if self.__isProgressionReward:
            return self.viewModel.setOpenDoorStatus(OpenDoorStatus.OPEN_DOOR_SUCCESS)
        doorId = int(event.get('dayId', 0))
        if not doorId:
            _logger.error('Parameter dayId is missing')
            return
        self.__requestOpenDoor(doorId=doorId)

    def __requestOpenDoor(self, doorId):
        _logger.debug('Created open request for doorId=%d', doorId)
        openDoorClb = partial(self.__processServerDoorOpen, dayId=doorId)
        openAndWaitDoor(dayID=doorId, callback=openDoorClb)

    def __processServerDoorOpen(self, dayId, result):
        _logger.debug('Waiting for reward window finished, doorId=%d', dayId)
        status = OpenDoorStatus.OPEN_DOOR_SUCCESS if result else OpenDoorStatus.OPEN_DOOR_FAILED
        self.viewModel.setOpenDoorStatus(status)
        if not result:
            self.__onSetBlur({'setBlur': False})
            self.destroyWindow()


class AdventCalendarRewardWindow(LobbyWindow):

    def __init__(self, dayId, isProgressionReward, data, parent=None):
        super(AdventCalendarRewardWindow, self).__init__(WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, layer=WindowLayer.FULLSCREEN_WINDOW, content=RewardView(dayId, isProgressionReward, data), parent=parent)
