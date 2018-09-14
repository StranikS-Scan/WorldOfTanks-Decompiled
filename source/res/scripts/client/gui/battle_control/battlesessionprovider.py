# Embedded file name: scripts/client/gui/battle_control/BattleSessionProvider.py
import weakref
import Event
from gui.battle_control import consumables
from gui.battle_control.BattleContext import BattleContext
from gui.battle_control.ChatCommandsController import ChatCommandsController
from gui.battle_control.ArenaLoadController import ArenaLoadController
from gui.battle_control.DRRScaleController import DRRScaleController
from gui.battle_control.arena_info.ArenaDataProvider import ArenaDataProvider
from gui.battle_control.arena_info.listeners import ListenersCollection

class BattleSessionProvider(object):
    __slots__ = ('__eManager', 'onPostMortemSwitched', 'onVehicleStateUpdated', '__ammoCtrl', '__equipmentsCtrl', '__optDevicesCtrl', '__chatCommands', '__drrScaleCtrl', '__ctx', '__arenaDP', '__arenaListeners', '__arenaLoadCtrl', '__isBattleUILoaded')

    def __init__(self):
        super(BattleSessionProvider, self).__init__()
        self.__eManager = Event.EventManager()
        self.onPostMortemSwitched = Event.Event(self.__eManager)
        self.onVehicleStateUpdated = Event.Event(self.__eManager)
        self.__ctx = BattleContext()
        self.__ammoCtrl = None
        self.__equipmentsCtrl = None
        self.__optDevicesCtrl = None
        self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__arenaDP = None
        self.__arenaLoadCtrl = None
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

    def getChatCommands(self):
        return self.__chatCommands

    def getDrrScaleCtrl(self):
        return self.__drrScaleCtrl

    def setPlayerVehicle(self, vDesc):
        self.__ammoCtrl.setGunSettings(vDesc.gun)

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
        isReplayRecording = replayCtrl.isRecording
        isReplayPlaying = replayCtrl.isPlaying
        self.__arenaDP = ArenaDataProvider()
        self.__ctx.start(self.__arenaDP)
        self.__ammoCtrl = consumables.createAmmoCtrl(isReplayPlaying, isReplayRecording)
        self.__equipmentsCtrl = consumables.createEquipmentCtrl(isReplayPlaying)
        self.__optDevicesCtrl = consumables.createOptDevicesCtrl()
        self.__chatCommands = ChatCommandsController()
        self.__arenaLoadCtrl = ArenaLoadController()
        self.__drrScaleCtrl = DRRScaleController()
        self.__arenaListeners = ListenersCollection()
        self.__arenaListeners.addController(weakref.proxy(self.__ctx), self.__arenaLoadCtrl)
        self.__arenaListeners.start(arenaDP=self.__arenaDP)

    def stop(self):
        if self.__ammoCtrl:
            self.__ammoCtrl.clear()
            self.__ammoCtrl = None
        if self.__equipmentsCtrl:
            self.__equipmentsCtrl.clear()
            self.__equipmentsCtrl = None
        if self.__optDevicesCtrl:
            self.__optDevicesCtrl.clear()
            self.__optDevicesCtrl = None
        if self.__arenaListeners is not None:
            self.__arenaListeners.stop()
            self.__arenaListeners = None
        if self.__arenaDP is not None:
            self.__arenaDP.clear()
            self.__arenaDP = None
        self.__chatCommands = None
        self.__drrScaleCtrl = None
        self.__arenaLoadCtrl = None
        self.__ctx.stop()
        self.__eManager.clear()
        return

    def setBattleUI(self, battleUI):
        self.__isBattleUILoaded = True
        self.__chatCommands.start(battleUI, self.__arenaDP)
        self.__drrScaleCtrl.start(battleUI)

    def clearBattleUI(self):
        self.__isBattleUILoaded = False
        self.__chatCommands.stop()
        self.__drrScaleCtrl.stop()

    def switchToPostmortem(self):
        self.__ammoCtrl.clear()
        self.__equipmentsCtrl.clear()
        self.__optDevicesCtrl.clear()
        from gui.WindowsManager import g_windowsManager
        g_windowsManager.showPostMortem()
        self.onPostMortemSwitched()

    def invalidateVehicleState(self, state, value):
        self.onVehicleStateUpdated(state, value)
