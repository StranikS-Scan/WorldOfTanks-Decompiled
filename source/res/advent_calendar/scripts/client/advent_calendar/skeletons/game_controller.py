# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: advent_calendar/scripts/client/advent_calendar/skeletons/game_controller.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.server_events.event_items import Quest
    from Event import Event
    from advent_calendar.helpers.server_settings import AdventCalendarConfig

class IAdventCalendarController(IGameController):
    onConfigChanged = None
    onDoorsStateChanged = None
    onDoorOpened = None
    onLootBoxInfoUpdated = None

    @property
    def isActive(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isNYEntryPointStarted(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isInActivePhase(self):
        raise NotImplementedError

    def isAvailableAndActivePhase(self):
        raise NotImplementedError

    def isAvailableAndPostActivePhase(self):
        raise NotImplementedError

    def isInPostActivePhase(self):
        raise NotImplementedError

    def awaitDoorOpenQuestCompletion(self, dayID):
        raise NotImplementedError

    def progressionQuestMayBeCompleted(self, openedDoorsAmount=None):
        raise NotImplementedError

    @property
    def config(self):
        raise NotImplementedError

    @property
    def startDate(self):
        raise NotImplementedError

    @property
    def postEventStartDate(self):
        raise NotImplementedError

    @property
    def postEventEndDate(self):
        raise NotImplementedError

    def getDoorOpenQuestName(self, day):
        raise NotImplementedError

    def getDoorOpenTokenName(self, day):
        raise NotImplementedError

    def getDoorOpenTimeUI(self, doorId):
        raise NotImplementedError

    def getCurrentDayNumber(self):
        raise NotImplementedError

    @property
    def getCurrentTime(self):
        raise NotImplementedError

    def getQuestByDayId(self, dayId):
        raise NotImplementedError

    def isDoorOpened(self, doorID):
        raise NotImplementedError

    @property
    def progressionRewardQuestsOrdered(self):
        raise NotImplementedError

    @property
    def completedAwardsQuests(self):
        raise NotImplementedError

    def getLootBoxInfo(self):
        raise NotImplementedError

    def getAdventCalendarGroupedQuestsRewards(self):
        raise NotImplementedError
