# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/finish_sound_ctrl.py
import SoundGroups
from gui.battle_control.arena_info import vos_collections
from gui.battle_control.arena_info.interfaces import ITeamsBasesController, IArenaVehiclesController
from gui.battle_control.arena_info.settings import ARENA_LISTENER_SCOPE as _SCOPE
from gui.battle_control.battle_constants import BATTLE_CTRL_ID

class _SOUND_EVENTS(object):
    LAST_KILL = 'end_battle_last_kill'
    BASE_CAPTURED = 'end_battle_capture_base'


class FinishSoundController(IArenaVehiclesController, ITeamsBasesController):
    """ Controller responsible for finish battle sound.
    
    It handles two cases:
        - last vehicle in either team was killed;
        - team base was captured.
    """

    def __init__(self):
        super(FinishSoundController, self).__init__()
        self.__battleCtx = None
        self.__arenaVisitor = None
        self.__canPlaySound = True
        self.__deadAllies = set()
        self.__deadEnemies = set()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.FINISH_SOUND

    def getCtrlScope(self):
        return _SCOPE.VEHICLES | _SCOPE.LOAD | _SCOPE.TEAMS_BASES

    def startControl(self, battleCtx, arenaVisitor):
        self.__battleCtx = battleCtx
        self.__arenaVisitor = arenaVisitor

    def stopControl(self):
        self.__battleCtx = None
        self.__arenaVisitor = None
        self.__canPlaySound = True
        self.__deadAllies.clear()
        self.__deadEnemies.clear()
        return

    def invalidateArenaInfo(self):
        arenaDP = self.__battleCtx.getArenaDP()
        self.invalidateVehiclesInfo(arenaDP)

    def invalidateVehiclesInfo(self, arenaDP):
        collection = vos_collections.VehiclesInfoCollection()
        self.__deadAllies.clear()
        self.__deadEnemies.clear()
        for vInfoVO in collection.iterator(arenaDP):
            if not vInfoVO.isAlive():
                self.__registerDeadVehicle(vInfoVO, arenaDP)

        self.__checkHasAlive(arenaDP)

    def invalidateVehicleStatus(self, flags, vInfoVO, arenaDP):
        if not vInfoVO.isAlive():
            self.__registerDeadVehicle(vInfoVO, arenaDP)
            self.__checkHasAlive(arenaDP)

    def invalidateTeamBaseCaptured(self, baseTeam, baseID):
        self.__onRoundFinished(_SOUND_EVENTS.BASE_CAPTURED)

    def _playSound(self, soundID):
        """ Play sound (protected for testing purposes)
        """
        SoundGroups.g_instance.playSound2D(soundID)

    def __registerDeadVehicle(self, vInfoVO, arenaDP):
        """ Store dead vehicle's id in its team registry.
        """
        if arenaDP.isEnemyTeam(vInfoVO.team):
            self.__deadEnemies.add(vInfoVO.vehicleID)
        else:
            self.__deadAllies.add(vInfoVO.vehicleID)

    def __checkHasAlive(self, arenaDP):
        """ Check if there are alive vehicle in either team, play finish sound if there is none.
        """
        allies = set(vos_collections.AllyItemsCollection().ids(arenaDP))
        enemies = set(vos_collections.EnemyItemsCollection().ids(arenaDP))
        if allies and self.__deadAllies == allies or enemies and self.__deadEnemies == enemies:
            self.__onRoundFinished(_SOUND_EVENTS.LAST_KILL)

    def __onRoundFinished(self, soundID):
        """ Play finish sound if it hasn't already been played.
        """
        if self.__canPlaySound and not self.__arenaVisitor._arena.hasFogOfWarHiddenVehicles:
            self._playSound(soundID)
            self.__canPlaySound = False
