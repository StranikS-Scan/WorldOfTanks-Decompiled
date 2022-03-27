# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/rts_battles/rts_notifications.py
import logging
from constants import ARENA_BONUS_TYPE
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.game_control import IRTSBattlesController
from skeletons.gui.game_control import IRTSNotificationsController
from skeletons.gui.game_control import IRTSProgressionController
_logger = logging.getLogger(__name__)

class RTSEventNotifications(IRTSNotificationsController):
    _STR_RES = R.strings.rts_battles.notifications
    __rtsController = dependency.descriptor(IRTSBattlesController)
    __rtsProgressionController = dependency.descriptor(IRTSProgressionController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def __init__(self):
        super(RTSEventNotifications, self).__init__()
        self._curStatus = PrimeTimeStatus.NOT_SET
        self._isEnabled = False
        self._isSubmodeEnabled = {}

    def onLobbyInited(self, event):
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__rtsController.onGameModeStatusUpdated += self.__onPrimeTimeStatusUpdate
        self.__rtsProgressionController.onProgressUpdated += self.__onProgressionUpdate
        status, _, _ = self.__rtsController.getPrimeTimeStatus()
        self._curStatus = status
        self._isEnabled = self.__rtsController.isEnabled()
        self._isSubmodeEnabled = self.__getSubmodesEnabled()
        _logger.debug('RTSEventNotifications:onLobbyInited - %s', status)

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def __clear(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__rtsController.onGameModeStatusUpdated -= self.__onPrimeTimeStatusUpdate
        self.__rtsProgressionController.onProgressUpdated -= self.__onProgressionUpdate

    def __getSubmodesEnabled(self):
        submodeEnabled = {}
        for bonusType in ARENA_BONUS_TYPE.RTS_BATTLES:
            submodeEnabled[bonusType] = self.__rtsController.isSubmodeEnabled(bonusType)

        return submodeEnabled

    def __pushModeSwitchMessage(self, resId, isWarning):
        SystemMessages.pushMessage(text=backport.text(resId.body()), messageData={'header': backport.text(self._STR_RES.modeSwitch.header())}, type=SystemMessages.SM_TYPE.WarningHeader if isWarning else SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH)

    def __onServerSettingsChange(self, diff):
        _logger.debug('RTSEventNotifications:__onServerSettingsChange')
        subModeEnabled = self.__getSubmodesEnabled()
        isEnabled = self.__rtsController.isEnabled()
        if self._isEnabled != isEnabled:
            if isEnabled:
                self.__pushModeSwitchMessage(self._STR_RES.modeSwitchOn, False)
            else:
                self.__pushModeSwitchMessage(self._STR_RES.modeSwitchOff, True)
            self._isEnabled = isEnabled
        if self._isSubmodeEnabled[ARENA_BONUS_TYPE.RTS] != subModeEnabled[ARENA_BONUS_TYPE.RTS]:
            if subModeEnabled[ARENA_BONUS_TYPE.RTS]:
                self.__pushModeSwitchMessage(self._STR_RES.submode1x7SwitchOn, False)
            else:
                self.__pushModeSwitchMessage(self._STR_RES.submode1x7SwitchOff, True)
        if self._isSubmodeEnabled[ARENA_BONUS_TYPE.RTS_1x1] != subModeEnabled[ARENA_BONUS_TYPE.RTS_1x1]:
            if subModeEnabled[ARENA_BONUS_TYPE.RTS_1x1]:
                self.__pushModeSwitchMessage(self._STR_RES.submode1x1SwitchOn, False)
            else:
                self.__pushModeSwitchMessage(self._STR_RES.submode1x1SwitchOff, True)
        self._isSubmodeEnabled = subModeEnabled

    def __onProgressionUpdate(self):
        progress = self.__rtsProgressionController.getCollectionProgress()
        progression = self.__rtsProgressionController.getConfig().progression
        progressionLen = len(progression)
        _logger.debug('RTSEventNotifications:__onProgressionUpdate - %d', progress)
        for idx, stage in enumerate(progression):
            if progress == stage['itemsCount']:
                rewards = self.__getProgressionRewardsList(stage)
                if idx == progressionLen - 1:
                    SystemMessages.pushMessage(text=backport.text(self._STR_RES.progression.completed(), rewards=rewards), type=SystemMessages.SM_TYPE.RTSProgression, priority=NotificationPriorityLevel.HIGH)
                else:
                    SystemMessages.pushMessage(text=backport.text(self._STR_RES.progression.stageAchieved(), count=progress, rewards=rewards), type=SystemMessages.SM_TYPE.RTSProgression, priority=NotificationPriorityLevel.MEDIUM)

    def __onPrimeTimeStatusUpdate(self, status):
        if self._curStatus == status:
            return
        _logger.debug('RTSEventNotifications:__onPrimeTimeStatusUpdate - %s/%s', self._curStatus, status)
        if status == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOff.body()), messageData={'header': backport.text(self._STR_RES.switchOff.header())}, type=SystemMessages.SM_TYPE.WarningHeader, priority=NotificationPriorityLevel.HIGH)
        elif self._curStatus == PrimeTimeStatus.FROZEN:
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.switchOn.body()), messageData={'header': backport.text(self._STR_RES.switchOn.header())}, type=SystemMessages.SM_TYPE.InformationHeader, priority=NotificationPriorityLevel.HIGH)
        elif status == PrimeTimeStatus.AVAILABLE:
            if self.__isFirstPrimeTime():
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventStart.body()), type=SystemMessages.SM_TYPE.RTSEventStart)
            else:
                SystemMessages.pushMessage(text=backport.text(self._STR_RES.primeTime.available.body()), messageData={'title': backport.text(self._STR_RES.primeTime.available.header())}, type=SystemMessages.SM_TYPE.PeriodicBattlesNotSet)
        elif status == PrimeTimeStatus.NOT_AVAILABLE and not self.__rtsController.getNextSeason() and not self.__rtsController.getCurrentSeason():
            SystemMessages.pushMessage(text=backport.text(self._STR_RES.eventEnd.body()), type=SystemMessages.SM_TYPE.Information, priority=NotificationPriorityLevel.MEDIUM)
        self._curStatus = status

    def __isFirstPrimeTime(self):
        if not self.__rtsController.getSeasonPassed():
            curSeason = self.__rtsController.getCurrentSeason()
            if curSeason is not None and curSeason.getPassedCyclesNumber() == 0 and not self.__rtsController.hasPrimeTimesPassedForCurrentCycle():
                return True
        return False

    def __getProgressionRewardsList(self, stage):
        rewards = self.__rtsProgressionController.getQuestRewards(stage.get('quest', ''))
        formattedList = [ formatted for r in rewards for formatted in r.formattedList() ]
        return ', '.join(formattedList)
