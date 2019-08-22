# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/death_ctrl.py
import BigWorld
import Event
from gui.battle_control import avatar_getter
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.server_events.battle_royale_formatters import InBattleRoyaleScoreFormatter, InBattleRoyaleSummaryFormatter, SoloPlaceFinder, SquadPlaceFinder
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

    def stopControl(self):
        if self.__delayedCB is not None:
            BigWorld.cancelCallback(self.__delayedCB)
            self.__delayedCB = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.DEATH_SCREEN_CTRL

    def addVehicleInfo(self, vo, arenaDP):
        super(DeathScreenController, self).addVehicleInfo(vo, arenaDP)
        self.__showDeathScreen(vo)

    def invalidateVehicleStatus(self, flags, vo, arenaDP):
        super(DeathScreenController, self).invalidateVehicleStatus(flags, vo, arenaDP)
        self.__showDeathScreen(vo)

    def __readyToShow(self, vo):
        if self.__isShown:
            return False
        arenaDP = self.sessionProvider.getArenaDP()
        vInfoVO = arenaDP.getVehicleInfo()
        if self.__isSolo():
            if vo.vehicleID == self.__playerVehicleID() and not vo.isAlive():
                pos = SoloPlaceFinder.getPlace(vInfoVO, arenaDP)
                return pos > self._SKIP_SCREEN_FOR_TOP_POSITIONS
        elif all((not infoVo.isAlive() for infoVo, statsVo in vos_collections.AllyItemsCollection().iterator(arenaDP))):
            pos = SquadPlaceFinder.getPlace(vInfoVO, arenaDP)
            return pos > self._SKIP_SCREEN_FOR_TOP_POSITIONS
        return False

    def __showDeathScreen(self, vo):
        if not self.__readyToShow(vo):
            return
        self.onShowDeathScreen()
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
        self.__delayedCB = None
        data = {'summaryResults': self.__getBattleSummaryResultsData(),
         'scoreResults': InBattleRoyaleScoreFormatter(self.sessionProvider.getArenaDP()).getInfo()}
        event_dispatcher.showBattleRoyaleResultsView(data)
        return

    def __getBattleSummaryResultsData(self):
        efficiencyCtrl = self.sessionProvider.shared.personalEfficiencyCtrl
        arenaInfo = avatar_getter.getArenaInfo()
        return None if not arenaInfo else InBattleRoyaleSummaryFormatter(self.sessionProvider.getArenaDP(), efficiencyCtrl, arenaInfo.getBonusByQuestID()).getInfo()
