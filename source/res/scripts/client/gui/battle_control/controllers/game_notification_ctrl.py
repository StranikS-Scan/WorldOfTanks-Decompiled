# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/game_notification_ctrl.py
from collections import defaultdict
import Event
import SoundGroups
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui.sounds.epic_sound_constants import EPIC_SOUND, EPIC_OVERTIME_SOUND_NOTIFICATIONS
from gui.sounds.epic_sound_constants import BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS
from gui.battle_control.view_components import IViewComponentsController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from epic_constants import EPIC_BATTLE_TEAM_ID
from gui.Scaleform.genConsts.GAME_MESSAGES_CONSTS import GAME_MESSAGES_CONSTS
from gui.battle_control import avatar_getter
from shared_utils import CONST_CONTAINER
from arena_component_system.sector_base_arena_component import ID_TO_BASENAME
import TriggersManager
from PlayerEvents import g_playerEvents

class GameNotificationsController(IViewComponentsController, TriggersManager.ITriggerListener):
    __slots__ = ('_notificationMap', 'onGameNotificationRecieved', '__eManager', '__ui', '_sessionProvider')

    def __init__(self, setup):
        super(GameNotificationsController, self).__init__()
        self._sessionProvider = setup.sessionProvider
        self._notificationMap = defaultdict(lambda : -1)
        self._setupNotificationMap()
        self.__ui = None
        self.__eManager = Event.EventManager()
        self.__soundNotificationOnlyOneLeft = False
        self.onGameNotificationRecieved = Event.Event(self.__eManager)
        return

    def onMessagePlaybackEnded(self, notificationID, data):
        pass

    def onMessagePlaybackStarted(self, notificationID, data):
        pass

    def onMessagePlaybackPhaseStarted(self, notificationID, data):
        pass

    def onMessagePlaybackHide(self, notificationID, data):
        pass

    def _setupNotificationMap(self):
        pass

    def setViewComponents(self, *components):
        self.__ui = components[0]
        self.__start()

    def clearViewComponents(self):
        self.__ui = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.GAME_NOTIFICATIONS

    def getUI(self):
        return self.__ui

    def startControl(self):
        pass

    def __start(self):
        LOG_DEBUG('GameNotificationsController started')

    def stopControl(self):
        self.__eManager.clear()
        self.__eManager = None
        return

    def onTriggerDeactivated(self, params):
        pass

    def translateMsgId(self, msgId):
        return self._notificationMap[msgId]


class EPIC_NOTIFICATION(CONST_CONTAINER):
    END_GAME = 1
    SPECIFIC_TIME = 2
    OVERTIME = 3
    ZONE_CAPTURED = 4
    ZONE_CONTESTED = 5
    RANK_CHANGE = 6
    HQ_DESTROYED = 7
    HQ_ACTIVE = 8
    BASE_ACTIVE = 9
    RETREAT = 10
    HQ_UNDER_ATTACK = 11
    GENERAL_APPEARED = 12
    HQ_BATTLE_START = 13
    RETREAT_SUCCESSFUL = 14


OVERTIME_DURATION_WARNINGS = [30]

class EpicGameNotificationsController(GameNotificationsController):

    def __init__(self, setup):
        super(EpicGameNotificationsController, self).__init__(setup)
        self.__playMsgOvertimeTriggered = False
        self.__shutDownSoundNotifications = False
        EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED = True
        g_playerEvents.onRoundFinished += self.__onEpicRoundFinished

    def _setupNotificationMap(self):
        self._notificationMap[GAME_MESSAGES_CONSTS.WIN] = EPIC_NOTIFICATION.END_GAME
        self._notificationMap[GAME_MESSAGES_CONSTS.DEFEAT] = EPIC_NOTIFICATION.END_GAME
        self._notificationMap[GAME_MESSAGES_CONSTS.DRAW] = EPIC_NOTIFICATION.END_GAME
        self._notificationMap[GAME_MESSAGES_CONSTS.TIME_REMAINING_POSITIVE] = EPIC_NOTIFICATION.SPECIFIC_TIME
        self._notificationMap[GAME_MESSAGES_CONSTS.TIME_REMAINING] = EPIC_NOTIFICATION.SPECIFIC_TIME
        self._notificationMap[GAME_MESSAGES_CONSTS.OVERTIME] = EPIC_NOTIFICATION.OVERTIME
        self._notificationMap[GAME_MESSAGES_CONSTS.BASE_CAPTURED_POSITIVE] = EPIC_NOTIFICATION.ZONE_CAPTURED
        self._notificationMap[GAME_MESSAGES_CONSTS.BASE_CAPTURED] = EPIC_NOTIFICATION.ZONE_CAPTURED
        self._notificationMap[GAME_MESSAGES_CONSTS.BASE_CONTESTED_POSITIVE] = EPIC_NOTIFICATION.ZONE_CONTESTED
        self._notificationMap[GAME_MESSAGES_CONSTS.BASE_CONTESTED] = EPIC_NOTIFICATION.ZONE_CONTESTED
        self._notificationMap[GAME_MESSAGES_CONSTS.RANK_UP] = EPIC_NOTIFICATION.RANK_CHANGE
        self._notificationMap[GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED_POSITIVE] = EPIC_NOTIFICATION.HQ_DESTROYED
        self._notificationMap[GAME_MESSAGES_CONSTS.OBJECTIVE_DESTROYED] = EPIC_NOTIFICATION.HQ_DESTROYED
        self._notificationMap[GAME_MESSAGES_CONSTS.RETREAT] = EPIC_NOTIFICATION.RETREAT
        self._notificationMap[GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK_POSITIVE] = EPIC_NOTIFICATION.HQ_UNDER_ATTACK
        self._notificationMap[GAME_MESSAGES_CONSTS.OBJECTIVE_UNDER_ATTACK] = EPIC_NOTIFICATION.HQ_UNDER_ATTACK
        self._notificationMap[GAME_MESSAGES_CONSTS.GENERAL_RANK_REACHED] = EPIC_NOTIFICATION.GENERAL_APPEARED
        self._notificationMap[GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED] = EPIC_NOTIFICATION.HQ_BATTLE_START
        self._notificationMap[GAME_MESSAGES_CONSTS.HQ_BATTLE_STARTED_POSITIVE] = EPIC_NOTIFICATION.HQ_BATTLE_START
        self._notificationMap[GAME_MESSAGES_CONSTS.RETREAT_SUCCESSFUL] = EPIC_NOTIFICATION.RETREAT_SUCCESSFUL
        self._notificationMap[GAME_MESSAGES_CONSTS.DESTROY_OBJECTIVE] = EPIC_NOTIFICATION.HQ_ACTIVE
        self._notificationMap[GAME_MESSAGES_CONSTS.DEFEND_OBJECTIVE] = EPIC_NOTIFICATION.HQ_ACTIVE
        self._notificationMap[GAME_MESSAGES_CONSTS.CAPTURE_BASE] = EPIC_NOTIFICATION.BASE_ACTIVE
        self._notificationMap[GAME_MESSAGES_CONSTS.DEFEND_BASE] = EPIC_NOTIFICATION.BASE_ACTIVE

    def startControl(self):
        super(EpicGameNotificationsController, self).startControl()
        TriggersManager.g_manager.addListener(self)

    def stopControl(self):
        super(EpicGameNotificationsController, self).stopControl()
        TriggersManager.g_manager.delListener(self)
        g_playerEvents.onRoundFinished -= self.__onEpicRoundFinished

    def __onEpicRoundFinished(self, winnerTeam, reason):
        EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED = False

    def notify(self, messageID, data):
        notificationID = self.translateMsgId(messageID)
        if notificationID != -1:
            self.onGameNotificationRecieved(self._notificationMap[messageID], data)
        bfVoMessage = EPIC_SOUND.BF_EB_VO_MESSAGES.get(messageID, None)
        if notificationID == EPIC_NOTIFICATION.HQ_BATTLE_START:
            componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
            sectorBaseComponent = getattr(componentSystem, 'sectorBaseComponent', None)
            if sectorBaseComponent is None:
                LOG_ERROR('Expected SectorBaseComponent not present!')
                return
            playerDataComponent = getattr(componentSystem, 'playerDataComponent', None)
            if playerDataComponent is None:
                LOG_ERROR('Expected PlayerDataComponent not present!')
                return
            isPlayerLane = sectorBaseComponent.getNumNonCapturedBasesByLane(componentSystem.playerDataComponent.physicalLane) == 0
            bfVoMessage = bfVoMessage[isPlayerLane]
        if bfVoMessage is not None:
            self.__playSound(bfVoMessage)
        return

    def onMessagePlaybackEnded(self, messageID, data):
        notificationID = self._notificationMap[messageID]
        if notificationID != -1:
            self.onGameNotificationRecieved(notificationID, data)

    def onMessagePlaybackPhaseStarted(self, messageID, data):
        notificationID = self._notificationMap[messageID]
        modificator = data['modificator']
        if notificationID == EPIC_NOTIFICATION.ZONE_CAPTURED and modificator == GAME_MESSAGES_CONSTS.WITH_ADD_TIME:
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_ADD_TIME_EMERGENCE)
        elif notificationID == EPIC_NOTIFICATION.HQ_DESTROYED:
            if modificator == GAME_MESSAGES_CONSTS.WITH_EVENT:
                SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_CANNON_DESTRUCTION_CROSS)
            elif modificator == GAME_MESSAGES_CONSTS.WITH_HIDE:
                SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_CANNON_DESTRUCTION_DISAPPEARANCE)

    def onMessagePlaybackStarted(self, messageID, data):
        componentSystem = self._sessionProvider.arenaVisitor.getComponentSystem()
        notificationID = self._notificationMap[messageID]
        isAttacker = avatar_getter.getPlayerTeam() == EPIC_BATTLE_TEAM_ID.TEAM_ATTACKER
        if notificationID == EPIC_NOTIFICATION.HQ_DESTROYED:
            SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_UI_CANNON_DESTRUCTION_EMERGENCE)
            bfVoMessage = self.__selectSoundNotifObjDestroy(componentSystem, messageID, data['id'])
            adType = EPIC_SOUND.BF_EB_HQ_DESTROYED_ATK_OR_DEF.get(messageID, None)
            if adType is None:
                return
            if self.__soundNotificationOnlyOneLeft:
                objectiveId = '_' + str(data['id'])
                soundNotification = BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS.ONE_DESTROYED + objectiveId + adType
                if soundNotification is not None:
                    self.__playSound(soundNotification)
            bfVoMessage += adType
            self.__playSound(bfVoMessage)
            return
        else:
            bfVoMessage = EPIC_SOUND.BF_EB_VO_MESSAGES.get(messageID, None)
            if bfVoMessage is None:
                return
            if notificationID == EPIC_NOTIFICATION.HQ_UNDER_ATTACK:
                sectorBaseId = data['id']
                bfVoMessage = bfVoMessage.get(sectorBaseId, None)
            elif notificationID == EPIC_NOTIFICATION.ZONE_CONTESTED:
                sectorBaseName = self._getBaseNameByBaseId(data['id'])
                bfVoMessage = bfVoMessage.get(sectorBaseName, None)
            elif notificationID == EPIC_NOTIFICATION.ZONE_CAPTURED:
                isPlayerLane = self._isPlayerLaneByBaseId(componentSystem, data['id'])
                bfVoMessage = bfVoMessage.get(isPlayerLane, None)
                sectorBaseName = self._getBaseNameByBaseId(data['id'])
                bfVoMessage += '_' + sectorBaseName
                if data['modificator'] == GAME_MESSAGES_CONSTS.WITH_UNLOCK:
                    SoundGroups.g_instance.playSound2D(EPIC_SOUND.EB_TANKS_UNLOCKED)
            elif notificationID == EPIC_NOTIFICATION.OVERTIME:
                if self.__playMsgOvertimeTriggered:
                    return
                self.__playSound(EPIC_OVERTIME_SOUND_NOTIFICATIONS.BF_EB_OVERTIME_START)
                self.__playMsgOvertimeTriggered = True
                bfVoMessage = bfVoMessage.get(isAttacker, None)
            elif notificationID == EPIC_NOTIFICATION.RANK_CHANGE:
                bfVoMessage = bfVoMessage.get('show', None)
            if messageID == GAME_MESSAGES_CONSTS.OVERTIME:
                if data['id'] in OVERTIME_DURATION_WARNINGS:
                    return
            self.__playSound(bfVoMessage)
            return

    def onMessagePlaybackHide(self, messageID, data):
        notificationID = self._notificationMap[messageID]
        if notificationID == EPIC_NOTIFICATION.RANK_CHANGE:
            bfVoMessage = EPIC_SOUND.BF_EB_VO_MESSAGES.get(messageID, None)
            if bfVoMessage is None:
                return
            bfVoMessage = bfVoMessage.get('hide', None)
            self.__playSound(bfVoMessage)
        return

    def overtimeSoundTriggered(self, val):
        self.__playMsgOvertimeTriggered = val

    def _isPlayerLaneByBaseId(self, componentSystem, sectorBaseId):
        sector = componentSystem.sectorBaseComponent.getSectorForSectorBase(sectorBaseId)
        if sector is None:
            return False
        else:
            return True if sector.playerGroup == componentSystem.playerDataComponent.physicalLane else False

    def _getBaseNameByBaseId(self, sectorBaseId):
        return ID_TO_BASENAME[sectorBaseId]

    def __selectSoundNotifObjDestroy(self, componentSystem, type_, objectiveId):
        objectiveName = '_' + str(objectiveId)
        bfVoMessage = BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS.ONE_DESTROYED + objectiveName
        self.__soundNotificationOnlyOneLeft = False
        entitiesToDestroy = BigWorld.player().arena.arenaType.numDestructiblesToDestroyForWin
        if componentSystem is not None:
            destructibleEntityComponent = getattr(componentSystem, 'destructibleEntityComponent', None)
            if destructibleEntityComponent is not None:
                destroyedEntities = destructibleEntityComponent.getNumDestroyedEntities()
                leftEntitiesToDestroy = entitiesToDestroy - destroyedEntities
                if leftEntitiesToDestroy == 1:
                    bfVoMessage = BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS.ONLY_ONE_LEFT
                    self.__soundNotificationOnlyOneLeft = True
                elif leftEntitiesToDestroy == 0:
                    bfVoMessage = BF_EB_MAIN_OBJECTIVES_SOUND_NOTIFICATIONS.ALL_DOWN
                    SoundGroups.g_instance.playSound2D(EPIC_SOUND.BF_EB_STOP_TICKING)
                    self.__shutDownSoundNotifications = True
            else:
                LOG_ERROR('Expected DestructibleEntityComponent not present!')
        return bfVoMessage

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED or eventName is None:
            return
        else:
            soundNotifications = avatar_getter.getSoundNotifications()
            if soundNotifications and hasattr(soundNotifications, 'play'):
                soundNotifications.play(eventName)
                if self.__shutDownSoundNotifications:
                    EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED = False
            return
