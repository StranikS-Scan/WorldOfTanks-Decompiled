# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/arena_info/interfaces.py
import typing
from gui.battle_control.arena_info.interfaces import IArenaVehiclesController
if typing.TYPE_CHECKING:
    from Event import Event

class IFallTanksVehicleInfo(object):

    @property
    def isFinished(self):
        raise NotImplementedError

    @property
    def isPlayerVehicle(self):
        raise NotImplementedError

    @property
    def isPlayerVehicleInRace(self):
        raise NotImplementedError

    @property
    def checkpoint(self):
        raise NotImplementedError

    @property
    def finishTime(self):
        raise NotImplementedError

    @property
    def frags(self):
        raise NotImplementedError

    @property
    def racePosition(self):
        raise NotImplementedError


class IFallTanksBattleController(IArenaVehiclesController):
    onFallTanksAttachedInfoUpdate = None

    def getFallTanksAttachedVehicleInfo(self):
        raise NotImplementedError

    def getFallTanksPlayerVehicleInfo(self):
        raise NotImplementedError
