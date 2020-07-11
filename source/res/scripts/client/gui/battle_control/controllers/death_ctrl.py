# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/death_ctrl.py
import BigWorld
import Event
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.arena_vos import BattleRoyaleKeys
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.server_events.battle_royale_formatters import IngameBattleRoyaleResultsViewDataFormatter
from gui.shared import event_dispatcher
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class DeathScreenController(IArenaVehiclesController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _TIME_BETWEEN_SCREENS = 4
    _SKIP_SCREEN_FOR_TOP_POSITIONS = 2

    def __init__(self):
        self.onShowDeathScreen = Event.Event()
        self.__delayedCB = None
        self.__isShown = False
        return

    def startControl(self, battleCtx, arenaVisitor):
        super(DeathScreenController, self).startControl(battleCtx, arenaVisitor)
        self.sessionProvider.shared.vehicleState.onPostMortemSwitched += self.__onSwitchedToPostmortem

    def stopControl(self):
        if self.__delayedCB is not None:
            BigWorld.cancelCallback(self.__delayedCB)
            self.__delayedCB = None
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self.__onSwitchedToPostmortem
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.DEATH_SCREEN_CTRL

    def addVehicleInfo(self, vo, arenaDP):
        super(DeathScreenController, self).addVehicleInfo(vo, arenaDP)
        self.__showDeathScreen(vo)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        super(DeathScreenController, self).invalidateVehicleStatus(flags, vo, arenaDP)
        self.__showDeathScreen(vo)

    def __onSwitchedToPostmortem(self, _, __):
        vehID = self.sessionProvider.shared.vehicleState.getControllingVehicleID()
        _, vo = self.sessionProvider.getArenaDP().updateVehicleStatus(vehID, self.sessionProvider.arenaVisitor.vehicles.getVehicleInfo(vehID))
        self.__showDeathScreen(vo)

    def __readyToShow(self, vo):
        if self.__isShown:
            return False
        arenaDP = self.sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo()
        pos = arenaDP.getVehicleStats(vInfoVO.vehicleID).gameModeSpecific.getValue(BattleRoyaleKeys.RANK.value)
        if self.__isSolo():
            if vo.vehicleID == self.__playerVehicleID() and not vo.isAlive():
                return pos > self._SKIP_SCREEN_FOR_TOP_POSITIONS
        elif all((not infoVo.isAlive() for infoVo, statsVo in vos_collections.AllyItemsCollection().iterator(arenaDP))):
            return pos > self._SKIP_SCREEN_FOR_TOP_POSITIONS
        return False

    def __showDeathScreen(self, vo):
        if not self.__readyToShow(vo):
            return
        self.__delayedCB = BigWorld.callback(self._TIME_BETWEEN_SCREENS, self.__showBattleResults)
        self.__isShown = True

    def __isSolo(self):
        arenaDP = self.sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo()
        return not vInfoVO.isSquadMan()

    def __playerVehicleID(self):
        arenaDP = self.sessionProvider.getArenaDP()
        return arenaDP.getPlayerVehicleID()

    def __showBattleResults(self):
        self.onShowDeathScreen()
        self.__delayedCB = None
        bonusByQuestID = None
        arenaInfo = avatar_getter.getArenaInfo()
        if arenaInfo is not None:
            bonusByQuestID = arenaInfo.getBonusByQuestID()
        data = IngameBattleRoyaleResultsViewDataFormatter(self.sessionProvider, bonusByQuestID).getInfo()
        event_dispatcher.showBattleRoyaleResultsView({'data': data}, isInBattle=True)
        return
