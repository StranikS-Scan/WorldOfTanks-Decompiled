# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/rts_sound_ctrl.py
import typing
from collections import defaultdict
import BigWorld
import WWISE
from constants import ARENA_PERIOD
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID, VEHICLE_VIEW_STATE
from gui.battle_control.controllers.commander.interfaces import IRTSSoundController, ICommandsGroup
from gui.sounds.r4_sound_constants import R4_SOUND, TANK_TYPE_TO_SWITCH, FIRST_SHOT_VOICE_LINES_BY_VEH_TAG, TANK_PRIORITY_BY_CLASS_TAG
from RTSShared import RTSManner, RTSOrder, MOVEMENT_ORDERS, RTSCommandResult
from PlayerEvents import g_playerEvents
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.commander.interfaces import IProxyVehicle, ICommand
    from gui import IngameSoundNotifications
MANNER_TO_VOICE_EVENT = {RTSManner.DEFENSIVE: R4_SOUND.R4_MANNER_ADAPTIVE,
 RTSManner.SCOUT: R4_SOUND.R4_MANNER_SCOUT,
 RTSManner.HOLD: R4_SOUND.R4_MANNER_HOLDER}
ORDER_TO_VOICE_EVENT = {RTSOrder.ATTACK_ENEMY: R4_SOUND.R4_ORDER_ATTACK,
 RTSOrder.FORCE_ATTACK_ENEMY: R4_SOUND.R4_ORDER_ATTACK_AGGRESSIVE,
 RTSOrder.CAPTURE_THE_BASE: R4_SOUND.R4_ORDER_CAPTURE_BASE,
 RTSOrder.RETREAT: R4_SOUND.R4_ORDER_RETREAT,
 RTSOrder.STOP: R4_SOUND.R4_ORDER_CANCEL}
ORDER_TO_UI_EVENT = {RTSOrder.GO_TO_POSITION: R4_SOUND.R4_ORDER_TERRAIN_UI,
 RTSOrder.FORCE_GO_TO_POSITION: R4_SOUND.R4_ORDER_TERRAIN_DOUBLE_UI,
 RTSOrder.ATTACK_ENEMY: R4_SOUND.R4_ORDER_ATTACK_UI,
 RTSOrder.FORCE_ATTACK_ENEMY: R4_SOUND.R4_ORDER_ATTACK_AGGRESSIVE_UI,
 RTSOrder.CAPTURE_THE_BASE: R4_SOUND.R4_ORDER_CAPTURE_BASE_UI,
 RTSOrder.DEFEND_THE_BASE: R4_SOUND.R4_ORDER_PROTECT_BASE_UI,
 RTSOrder.RETREAT: R4_SOUND.R4_ORDER_RETREAT_UI}
MANNER_TO_POSITION_ORDER_VOICE_EVENT = {RTSManner.DEFENSIVE: R4_SOUND.R4_ORDER_TERRAIN_ADAPTIVE,
 RTSManner.SCOUT: R4_SOUND.R4_ORDER_TERRAIN_SCOUT,
 RTSManner.HOLD: R4_SOUND.R4_ORDER_TERRAIN_HOLDER}
BASE_INFO_TO_BASE_CAPTURE_EVENT = {True: {True: R4_SOUND.R4_ENEMY_CAPTURE_BASE,
        False: R4_SOUND.R4_ENEMY_CAPTURE_NEUTRAL_BASE},
 False: {True: R4_SOUND.R4_ALLY_CAPTURE_BASE,
         False: R4_SOUND.R4_ALLY_CAPTURE_NEUTRAL_BASE}}
TRIGGER_GET_DESTINATION_INSIDE_ENEMY_BASE_AFTER = {R4_SOUND.R4_ALLY_CAPTURE_BASE, R4_SOUND.R4_ALLY_CAPTURE_NEUTRAL_BASE}
_BASE_CAPTURE_POINTS = 10
_MANNER_CHANGED_DELAY = 0.7

def isHeadVehicleOfGroup(commandsGroup, vehicle):
    vehPriority = TANK_PRIORITY_BY_CLASS_TAG[vehicle.vehicleClassTag]
    for command in commandsGroup.commands:
        if command.result == RTSCommandResult.ABORTED:
            continue
        commandVehPriority = TANK_PRIORITY_BY_CLASS_TAG[command.entity.vehicleClassTag]
        if commandVehPriority < vehPriority:
            return False

    return True


class RTSSoundController(IRTSSoundController, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        CallbackDelayer.__init__(self)
        self.__playedBaseCaptureEvents = {}
        self.__selectedVehicles = []
        self.__delayedHeadVehicleEvents = {}
        self.__playedCommandsGroupEvent = set()
        self.__headVehicleIDForVehicleSelection = None
        self.__vehicleManners = defaultdict(lambda : RTSManner.DEFAULT)
        self.__vehicleShots = {}
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.RTS_SOUND_CTRL

    def startControl(self, *_):
        g_playerEvents.onAvatarReady += self.__onAvatarReady
        g_playerEvents.onArenaPeriodChange += self.__onArenaPeriodChange
        self.__sessionProvider.onBattleSessionStart += self.__onBattleSessionStart
        self.__sessionProvider.onBattleSessionStop += self.__onBattleSessionStop
        self.__setRTSVoiceOverLanguage()

    def stopControl(self):
        self.__sessionProvider.onBattleSessionStop -= self.__onBattleSessionStop
        self.__sessionProvider.onBattleSessionStart -= self.__onBattleSessionStart
        g_playerEvents.onAvatarReady -= self.__onAvatarReady
        g_playerEvents.onArenaPeriodChange -= self.__onArenaPeriodChange
        CallbackDelayer.destroy(self)
        self.__delayedHeadVehicleEvents.clear()
        self.__vehicleShots.clear()

    def playEnemyDetectedSound(self, enemyID):
        player = BigWorld.player()
        enemyPosition = BigWorld.entity(enemyID).position
        allyVehicles = [ v for v in player.vehicles if v.isAlive() and v.isStarted and v.publicInfo['team'] == player.team and not v.isObserver() ]
        if not allyVehicles:
            return
        closestAlly = min(allyVehicles, key=lambda ally: ally.position.distTo(enemyPosition))
        if not avatar_getter.isCommanderCtrlMode() and player.vehicle.id == closestAlly.id:
            self.__play2D(R4_SOUND.ENEMY_SIGHTED_FOR_TEAM)
            return
        if self.__isSupply(closestAlly.id):
            self.__playOnHeadVehicle(R4_SOUND.R4_ENEMY_DETECTED)
        else:
            self.__playOnVehicle(R4_SOUND.R4_ENEMY_DETECTED, closestAlly.id)
        self.__playOnVehicle(R4_SOUND.R4_ENEMY_DETECTED_UI, enemyID)

    def controllableVehicleStateUpdated(self, state, vehicleID):
        if state == VEHICLE_VIEW_STATE.OBSERVED_BY_ENEMY:
            arenaDP = self.__sessionProvider.getArenaDP()
            if not arenaDP.isObserver(vehicleID) and not arenaDP.isSupply(vehicleID):
                self.__playOnVehicle(R4_SOUND.R4_ALLY_DETECTED, vehicleID)

    def selectionChanged(self, selectedVehiclesIDs, selectionViaPanel):
        oldSelectedVehicles = self.__selectedVehicles
        self.__updateSelectedVehicles(selectedVehiclesIDs)
        self.__updateHeadVehicleIDForVehicleSelection()
        vehicleAdded = set(self.__selectedVehicles).difference(oldSelectedVehicles)
        if self.__selectedVehicles and vehicleAdded:
            self.__playAllySelectedUISound(selectionViaPanel)
            headVehicleID = self.__headVehicleIDForVehicleSelection
            vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(headVehicleID, None)
            if vehicle and vehicle.activeCommand is None:
                self.__playOnVehicle(R4_SOUND.R4_ALLY_SELECTED, headVehicleID)
        return

    def focusedVehicleChanged(self, focusVehicleID, isInFocus):
        if self.__isSupply(focusVehicleID):
            return
        if focusVehicleID and isInFocus:
            self.__play2D(R4_SOUND.R4_FOCUS_VEHICLE)

    def triggerDeviceDamagedSoundNotification(self, vehicleID, deviceName):
        if deviceName in R4_SOUND.R4_DAMAGED_DEVICE_TO_VOICE_EVENT:
            soundNotificationName = R4_SOUND.R4_DAMAGED_DEVICE_TO_VOICE_EVENT.get(deviceName, None)
            if soundNotificationName is not None:
                self.__playOnVehicle(soundNotificationName, vehicleID)
        else:
            self.__playOnVehicle(R4_SOUND.R4_ALLY_GET_CRITICAL_DAMAGE_UI, vehicleID)
        return

    def __setRTSVoiceOverLanguage(self):
        switchName = R4_SOUND.getVoiceOverLanguageSwitch()
        self.__setWWiseSwitchGlobal(R4_SOUND.R4_VO_LANGUAGE_SWITCH_GROUP_NAME, switchName)

    def __setWWiseSwitchGlobal(self, switchGroupName, switchName):
        WWISE.WW_setSwitch(switchGroupName, switchName)

    def __setArcadeVoTankTypeSwitch(self, vID):
        vehicleClass = self.__getVehicleClassTag(vID)
        switchName = TANK_TYPE_TO_SWITCH.get(vehicleClass, None)
        self.__setWWiseSwitchGlobal(R4_SOUND.R4_VO_TANK_TYPE_SWITCH_GROUP_NAME, switchName)
        return

    def __onStartVehicleControl(self, vehicleID):
        self.__play2D(R4_SOUND.R4_MODE_ARCADE_SFX)
        self.__play2D(R4_SOUND.R4_MODE_ARCADE)
        self.__playOnVehicle(R4_SOUND.R4_ARCADE_WELCOME, vehicleID)
        self.__setArcadeVoTankTypeSwitch(vehicleID)

    def __onStopVehicleControl(self, _):
        self.__play2D(R4_SOUND.R4_MODE_STRATEGIC_SFX)
        self.__play2D(R4_SOUND.R4_MODE_STRATEGIC)

    def __isSupply(self, vID):
        arenaDP = self.__sessionProvider.getArenaDP()
        return arenaDP.isSupply(vID) if arenaDP and vID else False

    def __getVehicleClassTag(self, vID):
        vehicleProxy = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vID, None)
        return vehicleProxy.vehicleClassTag if vehicleProxy is not None else None

    def __isAlly(self, vID):
        isAlly = self.__sessionProvider.getArenaDP().isAlly(vID)
        return isAlly

    def __playAllySelectedUISound(self, selectionViaPanel):
        soundNotification = R4_SOUND.R4_ALLY_SELECTED_ARENA_UI
        if selectionViaPanel:
            soundNotification = R4_SOUND.R4_ALLY_SELECTED_INTERFACE_UI
        self.__play2D(soundNotification)

    def __vehicleSelectionHasSameManner(self):
        manner = None
        for v in self.__selectedVehicles:
            if not manner:
                manner = v.manner
            if v.manner and manner != v.manner:
                return False

        return True

    def __playCommandGoToSound(self, vIDs, order, commonManner, isOrderChanged):
        if not isOrderChanged:
            return
        else:
            soundEvent = None
            if order == RTSOrder.FORCE_GO_TO_POSITION:
                soundEvent = R4_SOUND.R4_ORDER_TERRAIN_DOUBLE
            elif order in (RTSOrder.GO_TO_POSITION, RTSOrder.FORCE_GO_TO_POSITION):
                soundEvent = R4_SOUND.R4_ORDER_TERRAIN_UNIVERSAL
                if commonManner is not None and self.__vehicleSelectionHasSameManner():
                    soundEvent = MANNER_TO_POSITION_ORDER_VOICE_EVENT[commonManner]
            if soundEvent:
                self.__playOnHeadVehicle(soundEvent, vIDs)
            return

    def __playCommandForBaseSound(self, vIDs, order, baseIsCapturing, isOrderChanged):
        if not isOrderChanged:
            return
        if order == RTSOrder.DEFEND_THE_BASE:
            if baseIsCapturing:
                self.__playOnHeadVehicle(R4_SOUND.R4_ORDER_FIGHT_OFF_BASE, vIDs)
            else:
                self.__playOnHeadVehicle(R4_SOUND.R4_ORDER_PROTECT_BASE, vIDs)
        else:
            self.__playOnHeadVehicle(R4_SOUND.R4_ORDER_CAPTURE_BASE, vIDs)

    def __playOtherCommandSound(self, vIDs, order, isOrderChanged):
        if order in ORDER_TO_VOICE_EVENT and isOrderChanged:
            self.__playOnHeadVehicle(ORDER_TO_VOICE_EVENT[order], vIDs)

    def __playBaseCaptureSound(self, points, isPlayerBase, isTeamBase, vIDs=None):
        soundEvent = BASE_INFO_TO_BASE_CAPTURE_EVENT[isPlayerBase][isTeamBase]
        if points < _BASE_CAPTURE_POINTS:
            return
        else:
            if not self.__playedBaseCaptureEvents[soundEvent]:
                self.__playOnHeadVehicle(soundEvent, vIDs if not isPlayerBase and vIDs else None)
                self.__playedBaseCaptureEvents[soundEvent] = True
            return

    def __onBattleSessionStart(self):
        sp = self.__sessionProvider
        sp.shared.feedback.onVehicleShoot += self.__onVehicleShoot
        sp.dynamic.rtsCommander.vehicles.onMannerChanged += self.__onMannerChanged
        sp.dynamic.rtsCommander.vehicles.onOrderChanged += self.__onOrderChanged
        sp.dynamic.rtsCommander.vehicles.onCommandComplete += self.__onCommandComplete
        sp.dynamic.rtsCommander.vehicles.onCommandEnqueued += self.__onCommandEnqueued
        sp.dynamic.vehicleChange.onStartVehicleControl += self.__onStartVehicleControl
        sp.dynamic.vehicleChange.onStopVehicleControl += self.__onStopVehicleControl
        sp.dynamic.rtsBWCtrl.onTeamBaseStateChanged += self.__onTeamBaseStateChanged
        sp.dynamic.rtsCommander.vehicles.onVehicleLostWhileAttacked += self.__onVehicleLostWhileAttacked
        sp.dynamic.rtsCommander.vehicles.onVehicleDeviceDamaged += self.__onVehicleDeviceDamaged
        sp.dynamic.rtsCommander.onRTSKeyEvent += self.__onRTSKeyEvent

    def __onBattleSessionStop(self):
        self.__resetWwiseParameters()
        sp = self.__sessionProvider
        sp.shared.feedback.onVehicleShoot -= self.__onVehicleShoot
        sp.dynamic.rtsBWCtrl.onTeamBaseStateChanged -= self.__onTeamBaseStateChanged
        sp.dynamic.vehicleChange.onStopVehicleControl -= self.__onStopVehicleControl
        sp.dynamic.vehicleChange.onStartVehicleControl -= self.__onStartVehicleControl
        sp.dynamic.rtsCommander.vehicles.onCommandEnqueued -= self.__onCommandEnqueued
        sp.dynamic.rtsCommander.vehicles.onCommandComplete -= self.__onCommandComplete
        sp.dynamic.rtsCommander.vehicles.onOrderChanged -= self.__onOrderChanged
        sp.dynamic.rtsCommander.vehicles.onMannerChanged -= self.__onMannerChanged
        sp.dynamic.rtsCommander.vehicles.onVehicleLostWhileAttacked -= self.__onVehicleLostWhileAttacked
        sp.dynamic.rtsCommander.vehicles.onVehicleDeviceDamaged -= self.__onVehicleDeviceDamaged
        sp.dynamic.rtsCommander.vehicles.onVehicleAboutToReload -= self.__onVehicleAboutToReload
        sp.dynamic.rtsCommander.vehicles.onVehicleFireLineBlocked -= self.__onVehicleFireLineBlocked
        sp.dynamic.rtsCommander.onRTSKeyEvent += self.__onRTSKeyEvent

    def __onRTSKeyEvent(self, isDonw, key):
        if self.__selectedVehicles and isDonw and key in R4_SOUND.KEYS_TO_MANNER_UI_SOUND:
            self.__play2D(R4_SOUND.R4_MANNER_UI)

    def __onMannerChangedDelayedCallback(self, vIDs, manner):
        self.__playOnHeadVehicle(MANNER_TO_VOICE_EVENT[manner], vIDs)

    def __onFlushHeadVehicleEvents(self):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'playOnHeadVehicle'):
            for event, vIDs in self.__delayedHeadVehicleEvents.iteritems():
                soundNotifications.playOnHeadVehicle(event, vIDs)

        self.__delayedHeadVehicleEvents.clear()

    def __playOnHeadVehicle(self, event, vIDs=None):
        delayedVehicleIDs = self.__delayedHeadVehicleEvents.setdefault(event, set())
        if vIDs:
            delayedVehicleIDs.update(vIDs)
        if not self.hasDelayedCallback(self.__onFlushHeadVehicleEvents):
            self.delayCallback(0.2, self.__onFlushHeadVehicleEvents)

    def __playOnVehicle(self, event, vID):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(event, vID)

    def __play2D(self, event):
        soundNotifications = avatar_getter.getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(event)

    def __onAvatarReady(self):
        self.__playedBaseCaptureEvents = {R4_SOUND.R4_ALLY_CAPTURE_BASE: False,
         R4_SOUND.R4_ENEMY_CAPTURE_BASE: False,
         R4_SOUND.R4_ALLY_CAPTURE_NEUTRAL_BASE: False,
         R4_SOUND.R4_ENEMY_CAPTURE_NEUTRAL_BASE: False}

    def __onVehicleShoot(self, vID):
        numPrevShots = self.__vehicleShots.get(vID, 0)
        if numPrevShots == 0 and self.__isAlly(vID):
            classTag = self.__getVehicleClassTag(vID)
            eventName = FIRST_SHOT_VOICE_LINES_BY_VEH_TAG.get(classTag, None)
            if eventName is not None:
                self.__playOnVehicle(eventName, vID)
        self.__vehicleShots[vID] = numPrevShots + 1
        return

    def __updateSelectedVehicles(self, selectedVehiclesIDs=None):
        vehiclesMgr = self.__sessionProvider.dynamic.rtsCommander.vehicles
        if selectedVehiclesIDs:
            self.__selectedVehicles = [ vehiclesMgr[vId] for vId in selectedVehiclesIDs ]
        else:
            self.__selectedVehicles = vehiclesMgr.values(lambda v: v.isSelected)

    def __onCommandEnqueued(self, command):
        if command.order not in ORDER_TO_UI_EVENT or command is None:
            return
        else:
            if self.__isHeadVehicleForVehicleSelection(command.entity.id):
                self.__play2D(ORDER_TO_UI_EVENT[command.order])
            return

    def __onOrderChanged(self, vID, order=None, manner=None, baseID=None, **kwargs):
        isOrderChanged = kwargs['isOrderChanged']
        if order == RTSOrder.STOP:
            extra = kwargs['extra']
            hadCommandsInQueue = extra.get('hadCommandsInQueue', False)
            if not hadCommandsInQueue:
                return
        if order in (RTSOrder.GO_TO_POSITION, RTSOrder.FORCE_GO_TO_POSITION):
            self.__playCommandGoToSound([vID], order, manner, isOrderChanged)
        elif order in (RTSOrder.DEFEND_THE_BASE, RTSOrder.CAPTURE_THE_BASE):
            baseIsCapturing = baseID in self.__sessionProvider.dynamic.rtsBWCtrl.capturingControlPoints
            self.__playCommandForBaseSound([vID], order, baseIsCapturing, isOrderChanged)
        else:
            self.__playOtherCommandSound([vID], order, isOrderChanged)

    def __onMannerChanged(self, vID, manner):
        if self.__isHeadVehicleForVehicleSelection(vID):
            prevManner = self.__vehicleManners.get(vID, RTSManner.DEFAULT)
            if prevManner != manner:
                self.delayCallback(_MANNER_CHANGED_DELAY, self.__onMannerChangedDelayedCallback, [vID], manner)
            self.__vehicleManners[vID] = manner

    def __updateHeadVehicleIDForVehicleSelection(self):
        if not self.__selectedVehicles:
            self.__updateSelectedVehicles()
        self.__headVehicleIDForVehicleSelection = None
        for key in TANK_TYPE_TO_SWITCH.keys():
            for v in self.__selectedVehicles:
                vehicleType = v.typeDescriptor.type.getVehicleClass()
                if vehicleType == key:
                    self.__headVehicleIDForVehicleSelection = v.id
                    return v.id

        return

    def __isHeadVehicleForVehicleSelection(self, vID=None):
        if not self.__selectedVehicles:
            return False
        headVehicleID = self.__headVehicleIDForVehicleSelection
        if headVehicleID:
            if headVehicleID == vID:
                return True
            return False

    def __areEnemiesNearBase(self, baseID, baseTeam):
        invaders, surroundingVehicles = self.__sessionProvider.dynamic.rtsBWCtrl.getTeamBaseInvaders(baseID, baseTeam)
        return invaders or surroundingVehicles

    def __getCommandCompleteNotification(self, command):
        order = command.order
        if order == RTSOrder.CAPTURE_THE_BASE:
            for soundEvent in TRIGGER_GET_DESTINATION_INSIDE_ENEMY_BASE_AFTER:
                if self.__playedBaseCaptureEvents.get(soundEvent, False):
                    return R4_SOUND.R4_GET_DESTINATION

        else:
            if order == RTSOrder.DEFEND_THE_BASE:
                baseID, baseTeam = command.controlPoint
                if self.__areEnemiesNearBase(baseID, baseTeam):
                    return R4_SOUND.R4_FIGHTING_OFF_BASE
                return R4_SOUND.R4_GET_DESTINATION
            if order in MOVEMENT_ORDERS:
                return R4_SOUND.R4_GET_DESTINATION
        return None

    def __tryPlayCommandCompleteNotification(self, command, numCommandsInQueue):
        if numCommandsInQueue > 1 or command.result != RTSCommandResult.SUCCESS:
            return
        soundNotification = self.__getCommandCompleteNotification(command)
        if not soundNotification:
            return
        vehicle = command.entity
        group = command.group
        groupID = group.id
        if groupID not in self.__playedCommandsGroupEvent and isHeadVehicleOfGroup(group, vehicle):
            self.__playOnVehicle(soundNotification, vehicle.id)
            self.__playedCommandsGroupEvent.add(groupID)

    def __onCommandComplete(self, command, numCommandsInQueue):
        self.__tryPlayCommandCompleteNotification(command, numCommandsInQueue)
        group = command.group
        groupID = group.id
        if groupID in self.__playedCommandsGroupEvent and group.isGroupComplete:
            self.__playedCommandsGroupEvent.remove(groupID)

    def __onTeamBaseStateChanged(self, team, baseID, points, invaders):
        isTeamBase = team != 0
        isPlayerBase = team == BigWorld.player().team
        self.__playBaseCaptureSound(points, isPlayerBase, isTeamBase, invaders)

    def __onVehicleLostWhileAttacked(self, enemyVehicleID, targetedMarks):
        if targetedMarks is None:
            return
        else:
            for command, order in targetedMarks.iteritems():
                vID = command.entity.id
                if order == RTSOrder.FORCE_ATTACK_ENEMY:
                    self.__playOnHeadVehicle(R4_SOUND.R4_LOST_EYE_CONTACT, [vID])

            return

    def __resetWwiseParameters(self):
        if avatar_getter.isPlayerCommander():
            WWISE.WW_eventGlobal(R4_SOUND.R4_MODE_STRATEGIC)

    def __onVehicleDeviceDamaged(self, vehicleID, deviceName):
        self.triggerDeviceDamagedSoundNotification(vehicleID, deviceName)

    def __onVehicleAboutToReload(self, vehicleID, isNonEmptyClip):
        vehicleProxy = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(vehicleID, None)
        if vehicleProxy is not None:
            gunTags = vehicleProxy.typeDescriptor.gun.tags
            if 'clip' in gunTags and 'autoreload' not in gunTags:
                event = R4_SOUND.R4_ALLY_RELOAD_NON_EMPTY_CLIP if isNonEmptyClip else R4_SOUND.R4_ALLY_RELOAD
                self.__playOnVehicle(event, vehicleID)
        return

    def __onVehicleFireLineBlocked(self, vehicleID):
        classTag = self.__getVehicleClassTag(vehicleID)
        event = R4_SOUND.R4_ALLY_FIRE_LINE_BLOCKED.get(classTag, None)
        if event is not None:
            self.__playOnVehicle(event, vehicleID)
        return

    def __registerOnVehicleAboutToReload(self, sessionProvider=None):
        if sessionProvider:
            sessionProvider.dynamic.rtsCommander.vehicles.onVehicleAboutToReload += self.__onVehicleAboutToReload

    def __onArenaPeriodChange(self, period, _, __, ___):
        if period == ARENA_PERIOD.BATTLE:
            sp = self.__sessionProvider
            self.delayCallback(3.0, self.__registerOnVehicleAboutToReload, sp)
            sp.dynamic.rtsCommander.vehicles.onVehicleFireLineBlocked += self.__onVehicleFireLineBlocked
