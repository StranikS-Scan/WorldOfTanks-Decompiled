# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/game_control/battle_controller.py
from __future__ import absolute_import
import logging
import typing
import BattleReplay
import Event
import SoundGroups
from PlayerEvents import g_playerEvents
from adisp import adisp_process
from constants import IS_CHINA
from fort_rush_common.fort_rush_constants import EXT_GAME_PARAMS_KEY
from fort_rush.gui.shared.event_dispatcher import showWelcomeScreen
from fort_rush.gui.sounds.sound_constants import SoundLanguage
from gui.impl.lobby.user_missions.hangar_widget.services import IEventsService
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, PREBATTLE_RESTRICTION
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.utils.requesters import REQ_CRITERIA
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from fort_rush.account_helpers.account_settings import isStartEventNotificationShown, setStartEventNotificationShown, isEndEventNotificationShown, setEndEventNotificationShown, isPauseEventNotificationShown, setPauseEventNotificationShown, isResumeEventNotificationShown, setResumeEventNotificationShown, isWelcomeScreenSeen
from fort_rush.gui.fort_rush_gui_constants import PREBATTLE_ACTION_NAME, SCH_CLIENT_MSG_TYPE
from fort_rush.gui.game_control.perfomance_analyzer_controller import PerformanceAnalyzer
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.configs.fort_rush_battles_config import fortRushBattlesConfigGameParamsSchema, FortRushBattlesConfigModel
from fort_rush_common.fort_rush_constants import PREBATTLE_TYPE, QUEUE_TYPE, EventStates, FORT_RUSH_EXCLUDED_TAGS
from gui.prb_control import prbEntityProperty, prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency, server_settings
from helpers.time_utils import getServerUTCTime, getDateTimeInUTC, getDayTimeLeft, getServerRegionalTime, getTimestampFromUTC
from skeletons.gui.system_messages import ISystemMessages
if typing.TYPE_CHECKING:
    from gui.shared.events import GUICommonEvent
    from gui.shared.gui_items.Vehicle import Vehicle
    from typing import List, Optional
_logger = logging.getLogger(__name__)

class FortRushBattleController(IFortRushBattleController, IGlobalListener, PerformanceAnalyzer):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsService = dependency.descriptor(IEventsService)

    def __init__(self):
        super(FortRushBattleController, self).__init__()
        self.onConfigUpdated = Event.Event()

    def init(self):
        super(FortRushBattleController, self).init()
        g_playerEvents.onPrbDispatcherCreated += self.__onPrbDispatcherCreated

    def fini(self):
        self.onConfigUpdated.clear()
        g_playerEvents.onPrbDispatcherCreated -= self.__onPrbDispatcherCreated
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__clear()
        super(FortRushBattleController, self).fini()

    def onDisconnected(self):
        super(FortRushBattleController, self).onDisconnected()
        self.stopGlobalListening()
        self.__clear()
        self.__onExitPrb()

    def onAvatarBecomePlayer(self):
        super(FortRushBattleController, self).onAvatarBecomePlayer()
        if BattleReplay.g_replayCtrl.isPlaying:
            self.__setEventVoiceoverLanguage()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(FortRushBattleController, self).onAccountBecomePlayer()
        self.__setEventVoiceoverLanguage()
        g_playerEvents.onConfigModelUpdated += self.configModelUpdated

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isAvailable(self):
        return self.getConfig().isEnabled and not self.getConfig().technicalPause and self.isWithinActiveTimeframe()

    def isFrozen(self):
        return self.getConfig().technicalPause

    def isWithinActiveTimeframe(self):
        serverDatetime = getDateTimeInUTC(getServerUTCTime())
        return self.getConfig().startDatetime <= serverDatetime < self.getConfig().endDatetime

    def isInAnnouncement(self):
        serverDatetime = getDateTimeInUTC(getServerUTCTime())
        return serverDatetime < self.getConfig().startDatetime

    def getTimeLeft(self):
        if not self.isAvailable():
            return 0
        endTimestamp = getTimestampFromUTC(self.getConfig().endDatetime.timetuple())
        return max(0, int(endTimestamp - getServerUTCTime()))

    def isEventPrbActive(self):
        dispatcher = self.prbDispatcher
        if dispatcher is not None:
            state = dispatcher.getFunctionalState()
            return state.isInUnit(PREBATTLE_TYPE.FORT_RUSH) or state.isInPreQueue(QUEUE_TYPE.FORT_RUSH)
        else:
            return False

    def getConfig(self):
        return fortRushBattlesConfigGameParamsSchema.getModel()

    @prbEntityProperty
    def prbEntity(self):
        pass

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    @adisp_process
    def selectBattle(self, callback=None):
        prebattleType = PREBATTLE_ACTION_NAME.FORT_RUSH
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            return
        else:
            result = yield dispatcher.doSelectAction(PrbAction(prebattleType))
            if callback and result:
                callback()
            return

    @adisp_process
    def selectRandomBattle(self):
        dispatcher = self.prbDispatcher
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined.')
            return
        else:
            result = yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
            if not result:
                _logger.error('Could not switch to random battle.')
            return

    def isInPrb(self):
        return self.prbEntity is not None and self.prbEntity.getEntityType() == QUEUE_TYPE.FORT_RUSH and not self.prbEntity.isInQueue()

    def onPrbEntitySwitching(self):
        if self.isInPrb():
            self.__onExitPrb()

    def onPrbEntitySwitched(self):
        if self.isAvailable() and self.isEnabled() and self.isInPrb():
            if not isWelcomeScreenSeen():
                showWelcomeScreen()
            self.__onEnterPrb()

    def onLobbyInited(self, event):
        super(FortRushBattleController, self).onLobbyInited(event)
        self.__setEventVoiceoverLanguage()
        self.__showNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        if not self.isAvailable() and self.isEventPrbActive():
            self.selectRandomBattle()

    def onLobbyStarted(self, ctx):
        super(FortRushBattleController, self).onLobbyStarted(ctx)
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def configModelUpdated(self, gpKey):
        if fortRushBattlesConfigGameParamsSchema.gpKey == gpKey:
            self.__showNotification()

    def isInfoPageEnabled(self):
        return self.getConfig().isInfoPageEnabled

    def getNewDailyMissionsTimestamp(self):
        return int(getServerRegionalTime() + getDayTimeLeft())

    def getFortRushDailyQuests(self):
        quests = []
        if not self.isEnabled():
            return quests
        dailyMissionsConfig = self.getConfig().dailyMissionsConfig
        dailyTokens = self.__itemsCache.items.tokens.getTokensByPrefixAndPostfix(dailyMissionsConfig.dailyMissionTokenPrefix)
        if not dailyTokens:
            return quests
        token = dailyTokens.keys().pop()
        for prefix in (dailyMissionsConfig.dailyMissionQuestPrefix, dailyMissionsConfig.hardDailyMissionQuestPrefix):
            allQuests = self.__eventsCache.getAllQuests(lambda q, p=prefix: q.getID().startswith(p))
            quests.extend((q for q in allQuests.values() if any((t.getID() == token for t in q.accountReqs.getTokens()))))

        return quests

    def getTotalProgressionPoints(self):
        return self.__itemsCache.items.tokens.getTokenCount(self.getConfig().baseProgressionToken)

    def getCurrentStageIndex(self):
        thresholds = self.__getStageThresholds()
        total = self.getTotalProgressionPoints()
        for i, threshold in enumerate(thresholds):
            if total < threshold:
                return i + 1

        return max(1, len(thresholds))

    def isProgressionCompleted(self):
        completedToken = self.getConfig().completedProgressionToken
        return self.__itemsCache.items.tokens.getTokenCount(completedToken) > 0

    def getCurrentProgressionStageRewards(self):
        config = self.getConfig()
        stages = config.progression.stage
        stageIdx = self.getCurrentStageIndex() - 1
        if stageIdx >= len(stages):
            return ()
        else:
            questId = stages[stageIdx].quest
            quests = self.__eventsCache.getAllQuests(lambda q, qid=questId: q.getID() == qid)
            quest = quests.get(questId)
            return () if quest is None else tuple((bonus for bonus in quest.getBonuses() if bonus.isShowInGUI()))

    def getProgressionRewards(self, questId):
        quest = self.__eventsCache.getQuestByID(questId)
        if quest is None:
            return []
        else:
            return [ bonus for bonus in quest.getBonuses() if bonus.isShowInGUI() ]

    def getEligibleVehicleTiers(self):
        config = self.getConfig()
        if config is None:
            _logger.debug('[FORT_RUSH] getEligibleVehicleTiers: config unavailable')
            return []
        else:
            return sorted(config.eligibleVehicleTiers)

    def getForbiddenVehClasses(self):
        config = self.getConfig()
        if config is None:
            _logger.debug('[FORT_RUSH] getForbiddenVehClasses: config unavailable')
            return []
        else:
            return list(config.forbiddenVehClasses)

    def isSuitableVehicle(self, vehicle):
        if vehicle.tags & FORT_RUSH_EXCLUDED_TAGS:
            return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE, {'forbiddenTag': vehicle.shortUserName})
        else:
            eligibleVehicleTiers = self.getEligibleVehicleTiers()
            if vehicle.level not in eligibleVehicleTiers:
                return ValidationResult(False, PRE_QUEUE_RESTRICTION.LIMIT_LEVEL, {'levels': eligibleVehicleTiers})
            forbiddenVehClasses = self.getForbiddenVehClasses()
            return ValidationResult(False, PREBATTLE_RESTRICTION.VEHICLE_NOT_SUPPORTED, {'forbiddenClass': forbiddenVehClasses}) if vehicle.type in forbiddenVehClasses else None

    def hasSuitableVehicles(self):
        criteria = REQ_CRITERIA.INVENTORY | REQ_CRITERIA.CUSTOM(self.__isSuitableVehicleCriteria)
        return len(self.__itemsCache.items.getVehicles(criteria, limit=1)) > 0

    def __isSuitableVehicleCriteria(self, vehicle):
        return self.isSuitableVehicle(vehicle) is None

    def getLastStageThreshold(self):
        thresholds = self.__getStageThresholds()
        return thresholds[-1] if thresholds else 0

    def getCurrentStagePoints(self):
        thresholds = self.__getStageThresholds()
        if not thresholds:
            return (0, 0)
        currentProgressionPoints = self.getTotalProgressionPoints()
        prevThreshold = 0
        for threshold in thresholds:
            if currentProgressionPoints < threshold:
                return (currentProgressionPoints - prevThreshold, threshold - prevThreshold)
            prevThreshold = threshold

        lastSize = thresholds[-1] - (thresholds[-2] if len(thresholds) > 1 else 0)
        return (lastSize, lastSize)

    def __getStageThresholds(self):
        config = self.getConfig()
        progressionToken = config.baseProgressionToken
        stages = config.progression.stage
        if not stages:
            return []
        else:
            questIds = [ s.quest for s in stages ]
            quests = self.__eventsCache.getAllQuests(lambda q: q.getID() in questIds)
            thresholds = []
            for stage in stages:
                quest = quests.get(stage.quest)
                if quest is None:
                    continue
                for tokenCond in quest.accountReqs.getTokens():
                    if tokenCond.getID() == progressionToken:
                        thresholds.append(tokenCond.getNeededCount())
                        break

            return thresholds

    def __setEventVoiceoverLanguage(self):
        if IS_CHINA:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_CN)
        else:
            SoundGroups.g_instance.setSwitch(SoundLanguage.VOICEOVER_LOCALIZATION_SWITCH, SoundLanguage.VOICEOVER_EN)

    def __clear(self):
        g_playerEvents.onConfigModelUpdated -= self.configModelUpdated
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def __onPrbDispatcherCreated(self):
        self.startGlobalListening()

    def __onEnterPrb(self):
        pass

    def __onExitPrb(self):
        pass

    def __showNotification(self):
        if self.isAvailable() and not isStartEventNotificationShown():
            self.__dispatchEventStateNotification(EventStates.START)
            setStartEventNotificationShown(True)
            setEndEventNotificationShown(False)
            return
        if not self.isEnabled() and isStartEventNotificationShown() and not isEndEventNotificationShown():
            self.__dispatchEventStateNotification(EventStates.ENDED)
            setEndEventNotificationShown(True)
            setStartEventNotificationShown(False)
            return
        if self.isEnabled() and self.isFrozen() and not isPauseEventNotificationShown():
            self.__dispatchEventStateNotification(EventStates.PAUSE)
            setPauseEventNotificationShown(True)
            setResumeEventNotificationShown(False)
            return
        if self.isAvailable() and isPauseEventNotificationShown() and not isResumeEventNotificationShown():
            self.__dispatchEventStateNotification(EventStates.RESUME)
            setResumeEventNotificationShown(True)
            setPauseEventNotificationShown(False)
            return

    def __dispatchEventStateNotification(self, eventType):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventType}, SCH_CLIENT_MSG_TYPE.FORT_RUSH_MSG_TYPE)

    def __onSelectVehicleInHangar(self, event):
        if not self.isEventPrbActive():
            return
        vehicleInvID = event.ctx['vehicleInvID']
        vehicle = self.__itemsCache.items.getVehicle(vehicleInvID)
        if vehicle:
            self.selectRandomBattle()

    @server_settings.serverSettingsChangeListener(EXT_GAME_PARAMS_KEY)
    def __onServerSettingsChanged(self, diff):
        if not self.isAvailable() and self.isEventPrbActive():
            self.selectRandomBattle()
        self.onConfigUpdated()
        self.__eventsService.updateEntries()
