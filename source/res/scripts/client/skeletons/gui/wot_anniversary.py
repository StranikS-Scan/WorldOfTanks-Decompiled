# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/wot_anniversary.py
from typing import TYPE_CHECKING, Dict, Optional
from skeletons.gui.game_control import IGameController
if TYPE_CHECKING:
    from Event import Event
    from gui.server_events.event_items import Quest
    from gui.shared.gui_items import Vehicle
    from helpers.server_settings import WotAnniversaryConfig

class IWotAnniversaryController(IGameController):
    onSettingsChanged = None
    onEventActivePhaseEnded = None
    onEventWillEndSoon = None
    onEventStateChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isAvailableAndActivePhase(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getUrl(self, urlName):
        raise NotImplementedError

    def getQuests(self):
        raise NotImplementedError

    def getDailyQuests(self):
        raise NotImplementedError

    def getMascotBattleQuests(self):
        raise NotImplementedError

    def getMascotRewardQuests(self):
        raise NotImplementedError

    def getLoginQuests(self):
        raise NotImplementedError

    def getRewardVehicle(self):
        raise NotImplementedError

    def isLastDayNow(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isInActivePhase(self):
        raise NotImplementedError

    def isInPostActivePhase(self):
        raise NotImplementedError

    def isEventWillEndSoonDaysNow(self):
        raise NotImplementedError

    @property
    def lastShownMascotReminderNotification(self):
        raise NotImplementedError

    @lastShownMascotReminderNotification.setter
    def lastShownMascotReminderNotification(self, questID):
        raise NotImplementedError
