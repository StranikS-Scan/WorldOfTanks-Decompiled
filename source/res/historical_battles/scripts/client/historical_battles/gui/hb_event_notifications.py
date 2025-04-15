# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/hb_event_notifications.py
import logging
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from helpers import dependency, time_utils
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.system_messages import ISystemMessages
from historical_battles.skeletons.gui.hb_notifications_controller import IHBEventNotifications
from historical_battles.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from historical_battles.hb_constants import FrontsOpenStates
_logger = logging.getLogger(__name__)

class HBEventNotifications(IHBEventNotifications):
    __gameEventCtrl = dependency.descriptor(IGameEventController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def init(self):
        self.__wasBattlesEnabled = True
        self.__isEventStartNotificationViewed = False
        self.__isOffenceStartNotificationViewed = False
        self.__gameEventCtrl.onGameParamsChanged += self.__onGameParamsChanged
        self.__gameEventCtrl.onFrontTimeStatusUpdated += self.__onFrontTimeStatusUpdated

    def fini(self):
        self.__gameEventCtrl.onFrontTimeStatusUpdated += self.__onFrontTimeStatusUpdated
        self.__gameEventCtrl.onGameParamsChanged -= self.__onGameParamsChanged
        self.__wasBattlesEnabled = None
        self.__isEventStartNotificationViewed = None
        self.__isOffenceStartNotificationViewed = None
        return

    def pushRegularAwardMessage(self, message):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.HB_PROGRESSION_NOTIFICATIONS)

    def pushLastAwardMessage(self, message):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.HB_BOTH_PROGRESSIONS_FINISHED)

    def pushDivisionLevelUpSysMsg(self, message):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message, SCH_CLIENT_MSG_TYPE.HB_DIVISION_LEVEL_UP)

    def pushArenaPunishmentSysMsg(self, data, punishmentType):
        self.__systemMessages.proto.serviceChannel.pushClientMessage(data, punishmentType)

    def __onGameParamsChanged(self):
        frontsConfig = self.__gameEventCtrl.frontController.getFrontsConfig()
        offenceId = self.__getFrontIdByName(frontsConfig, 'offence')
        defenceId = self.__getFrontIdByName(frontsConfig, 'defence')
        isOffenceFrontSeen = self.__gameEventCtrl.frontController.isFrontSeen(offenceId)
        isDefenceFrontSeen = self.__gameEventCtrl.frontController.isFrontSeen(defenceId)
        if not self.__gameEventCtrl.isEnabled():
            if isDefenceFrontSeen or isOffenceFrontSeen:
                expiryTime = self.__gameEventCtrl.getGameEventData().get('endDate')
                if time_utils.getTimeDeltaFromNow(expiryTime) <= 1:
                    self.__pushHBEndedNotification()
                else:
                    self.__pushHBSwitchedOffNotification()
                self.__gameEventCtrl.frontController.setIsFrontSeen(defenceId, False)
                self.__gameEventCtrl.frontController.setIsFrontSeen(offenceId, False)
                self.__isEventStartNotificationViewed = False
                self.__isOffenceStartNotificationViewed = False
            return
        if not self.__isEventStartNotificationViewed and not self.__gameEventCtrl.isHistoricalBattlesMode() and not isDefenceFrontSeen and not isOffenceFrontSeen:
            self.__pushHBDefenceStartedNotification()
            self.__isEventStartNotificationViewed = True
        if not self.__isOffenceStartNotificationViewed and not isOffenceFrontSeen:
            data = frontsConfig.get(offenceId)
            frontEnabled = data.get('enabled', False)
            startDate = data.get('startDate')
            isFrontAvailable = frontEnabled and time_utils.getTimeDeltaFromNow(startDate) <= 0
            if isFrontAvailable:
                self.__pushHBOffenceStartedNotification()
                self.__isOffenceStartNotificationViewed = True
        if self.__wasBattlesEnabled != self.__gameEventCtrl.isBattlesEnabled():
            if not self.__gameEventCtrl.isBattlesEnabled():
                self.__pushHBBattlesSwitchedOffNotification()
            else:
                self.__pushHBBattlesSwitchedOnNotification()
            self.__wasBattlesEnabled = self.__gameEventCtrl.isBattlesEnabled()

    def __onFrontTimeStatusUpdated(self, frontId):
        frontsConfig = self.__gameEventCtrl.frontController.getFrontsConfig()
        data = frontsConfig.get(frontId)
        frontEnabled = data.get('enabled', False)
        if frontEnabled and frontId == self.__getFrontIdByName(frontsConfig, 'offence'):
            self.__pushHBOffenceStartedNotification()

    def __getFrontIdByName(self, config, name):
        for frontId, frontData in config.iteritems():
            if frontData.get('frontName') == name:
                return frontId

    def __pushHBEndedNotification(self):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.HB_FRONT_STATE_NOTIFICATION, auxData=FrontsOpenStates.EVENT_ENDED)

    def __pushHBSwitchedOffNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_off_event.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.ErrorSimple)

    def __pushHBDefenceStartedNotification(self):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.HB_FRONT_STATE_NOTIFICATION, auxData=FrontsOpenStates.DEFENCE_STARTED)

    def __pushHBOffenceStartedNotification(self):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.HB_FRONT_STATE_NOTIFICATION, auxData=FrontsOpenStates.OFFENCE_STARTED)

    def __pushHBBattlesSwitchedOnNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_on_battles.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.Information)

    def __pushHBBattlesSwitchedOffNotification(self):
        text = backport.text(R.strings.hb_lobby.system_messages.switched_off_battles.body())
        SystemMessages.pushMessage(text, type=SystemMessages.SM_TYPE.ErrorSimple)
