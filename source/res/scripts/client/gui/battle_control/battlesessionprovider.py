# Embedded file name: scripts/client/gui/battle_control/BattleSessionProvider.py
import weakref
from adisp import async
from gui.battle_control import consumables, vehicle_state_ctrl
from gui.battle_control.BattleContext import BattleContext
from gui.battle_control.RespawnsController import RespawnsController
from gui.battle_control.NotificationsController import NotificationsController
from gui.battle_control.battle_feedback import createFeedbackAdaptor
from gui.battle_control.ChatCommandsController import ChatCommandsController
from gui.battle_control.ArenaLoadController import ArenaLoadController
from gui.battle_control.DRRScaleController import DRRScaleController
from gui.battle_control.RepairController import RepairController
from gui.battle_control.arena_info.ArenaDataProvider import ArenaDataProvider
from gui.battle_control.arena_info.listeners import ListenersCollection
from gui.battle_control.arena_info import isEventBattle
from gui.battle_control.requests import AvatarRequestsController

class BattleSessionProvider(object):
    __slots__ = ('__ammoCtrl', '__equipmentsCtrl', '__optDevicesCtrl', '__vehicleStateCtrl', '__chatCommands', '__drrScaleCtrl', '__feedback', '__ctx', '__arenaDP', '__arenaListeners', '__arenaLoadCtrl', '__respawnsCtrl', '__notificationsCtrl', '__repairCtrl', '__isBattleUILoaded', '__requestsCtrl')

    def __init__(self):
        super(BattleSessionProvider, self).__init__()
        self.__ctx = BattleContext()
        self.__ammoCtrl = None
        self.__equipmentsCtrl = None
        self.__optDevicesCtrl = None
        self.__vehicleStateCtrl = None
        self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__feedback = None
        self.__requestsCtrl = None
        self.__arenaDP = None
        self.__arenaLoadCtrl = None
        self.__respawnsCtrl = None
        self.__notificationsCtrl = None
        self.__repairCtrl = None
        self.__arenaListeners = None
        self.__isBattleUILoaded = False
        return

    def isBattleUILoaded(self):
        return self.__isBattleUILoaded

    def getCtx(self):
        return self.__ctx

    def getAmmoCtrl(self):
        return self.__ammoCtrl

    def getEquipmentsCtrl(self):
        return self.__equipmentsCtrl

    def getOptDevicesCtrl(self):
        return self.__optDevicesCtrl

    def getVehicleStateCtrl(self):
        return self.__vehicleStateCtrl

    def getChatCommands(self):
        return self.__chatCommands

    def getDrrScaleCtrl(self):
        return self.__drrScaleCtrl

    def getRespawnsCtrl(self):
        return self.__respawnsCtrl

    def getNotificationsCtrl(self):
        return self.__notificationsCtrl

    def getRepairCtrl(self):
        return self.__repairCtrl

    def getFeedback(self):
        return self.__feedback

    @async
    def sendRequest(self, ctx, callback, allowDelay = None):
        self.__requestsCtrl.request(ctx, callback=callback, allowDelay=allowDelay)

    def setPlayerVehicle(self, vID, vDesc):
        self.__ammoCtrl.setGunSettings(vDesc.gun)
        self.__vehicleStateCtrl.setPlayerVehicle(vID)
        self.__feedback.setPlayerVehicle(vID)

    def setAimPositionUpdated(self, mode, x, y):
        self.__feedback.setAimPositionUpdated(mode, x, y)

    def getArenaDP(self):
        return self.__arenaDP

    def addArenaCtrl(self, controller):
        if self.__arenaListeners:
            self.__arenaListeners.addController(weakref.proxy(self.__ctx), controller)

    def removeArenaCtrl(self, controller):
        if self.__arenaListeners:
            self.__arenaListeners.removeController(controller)

    def start(self):
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if isEventBattle():
            replayCtrl.enableAutoRecordingBattles(0)
        isReplayRecording = replayCtrl.isRecording
        isReplayPlaying = replayCtrl.isPlaying
        self.__arenaDP = ArenaDataProvider()
        self.__ctx.start(self.__arenaDP)
        self.__ammoCtrl = consumables.createAmmoCtrl(isReplayPlaying, isReplayRecording)
        self.__equipmentsCtrl = consumables.createEquipmentCtrl(isReplayPlaying)
        self.__optDevicesCtrl = consumables.createOptDevicesCtrl()
        self.__vehicleStateCtrl = vehicle_state_ctrl.createCtrl(isReplayRecording)
        self.__chatCommands = ChatCommandsController()
        self.__arenaLoadCtrl = ArenaLoadController()
        self.__drrScaleCtrl = DRRScaleController()
        self.__respawnsCtrl = RespawnsController()
        self.__notificationsCtrl = NotificationsController()
        self.__repairCtrl = RepairController()
        self.__arenaListeners = ListenersCollection()
        self.__arenaListeners.addController(weakref.proxy(self.__ctx), self.__arenaLoadCtrl)
        self.__arenaListeners.addController(weakref.proxy(self.__ctx), self.__respawnsCtrl)
        self.__arenaListeners.start(arenaDP=self.__arenaDP)
        self.__feedback = createFeedbackAdaptor(isReplayPlaying)
        self.__feedback.start(self.__arenaDP)
        self.__requestsCtrl = AvatarRequestsController()

    def stop(self):
        if self.__requestsCtrl:
            self.__requestsCtrl.fini()
            self.__requestsCtrl = None
        if self.__ammoCtrl:
            self.__ammoCtrl.clear()
            self.__ammoCtrl = None
        if self.__equipmentsCtrl:
            self.__equipmentsCtrl.clear()
            self.__equipmentsCtrl = None
        if self.__optDevicesCtrl:
            self.__optDevicesCtrl.clear()
            self.__optDevicesCtrl = None
        if self.__vehicleStateCtrl:
            self.__vehicleStateCtrl.clear()
            self.__vehicleStateCtrl = None
        if self.__arenaListeners is not None:
            self.__arenaListeners.stop()
            self.__arenaListeners = None
        if self.__feedback is not None:
            self.__feedback.stop()
            self.__feedback = None
        if self.__arenaDP is not None:
            self.__arenaDP.clear()
            self.__arenaDP = None
        self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__arenaLoadCtrl = None
        self.__respawnsCtrl = None
        self.__notificationsCtrl = None
        self.__repairCtrl = None
        import BattleReplay
        replayCtrl = BattleReplay.g_replayCtrl
        if isEventBattle():
            from account_helpers.settings_core.SettingsCore import g_settingsCore
            replayCtrl.enableAutoRecordingBattles(g_settingsCore.getSetting('replayEnabled'))
        self.__ctx.stop()
        return

    def setBattleUI(self, battleUI):
        self.__isBattleUILoaded = True
        self.__chatCommands.start(battleUI, self.__arenaDP)
        self.__drrScaleCtrl.start(battleUI)
        self.__repairCtrl.start(battleUI)

    def clearBattleUI(self):
        self.__isBattleUILoaded = False
        self.__chatCommands.stop()
        self.__drrScaleCtrl.stop()
        self.__repairCtrl.stop()

    def switchToPostmortem(self):
        self.__ammoCtrl.clear()
        self.__equipmentsCtrl.clear()
        self.__optDevicesCtrl.clear()
        self.__feedback.setPlayerVehicle(0L)
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showPostMortem()
        self.__vehicleStateCtrl.switchToPostmortem()

    def movingToRespawnBase(self):
        self.__ammoCtrl.clear(False)
        self.__equipmentsCtrl.clear(False)
        self.__optDevicesCtrl.clear(False)
        self.__vehicleStateCtrl.onRespawnBaseMoving()

    def invalidateVehicleState(self, state, value):
        self.__vehicleStateCtrl.invalidate(state, value)

    def repairPointAction(self, repairPointIndex, action, nextActionTime):
        self.__repairCtrl.action(repairPointIndex, action, nextActionTime)
