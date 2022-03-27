# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/order_vector.py
import logging
from DebugDrawer import DebugDrawer
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from RTSShared import RTSOrder
_logger = logging.getLogger(__name__)

class _IVectorTarget(object):

    @property
    def position(self):
        raise NotImplementedError


class _VehicleTarget(_IVectorTarget):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, vehicle):
        self._vehicle = vehicle

    @property
    def position(self):
        return None if self._vehicle is None or not self._vehicle.initialized else self._vehicle.position


class _PositionTarget(_IVectorTarget):

    def __init__(self, position):
        self._position = position

    @property
    def position(self):
        return self._position


class OrderVector(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DASH_DISTANCE = 1.3
    _COLOUR = 4291282887L
    _WIDTH = 0.0

    def __init__(self, vehicle):
        self._fromTarget = _VehicleTarget(vehicle)
        self._toTarget = None
        self.__cbID = None
        return

    def reset(self):
        self._toTarget = None
        return

    def update(self, order=None, position=None, target=None, **extra):
        if order in (RTSOrder.GO_TO_POSITION,
         RTSOrder.FORCE_GO_TO_POSITION,
         RTSOrder.DEFEND_THE_BASE,
         RTSOrder.STOP,
         RTSOrder.CAPTURE_THE_BASE,
         RTSOrder.RETREAT) or extra and extra.get('isPursuit'):
            self._toTarget = _PositionTarget(position)
        elif order in (RTSOrder.ATTACK_ENEMY, RTSOrder.FORCE_ATTACK_ENEMY) and target is not None:
            vehicle = self.__sessionProvider.dynamic.rtsCommander.vehicles.get(target)
            if vehicle:
                self._toTarget = _VehicleTarget(vehicle)
            else:
                _logger.warning('Target vehicle is not available as commander vehicle')
        else:
            self._toTarget = None
        return

    def drawVector(self):
        if self._toTarget is None or self._toTarget.position is None:
            return
        else:
            w = self._WIDTH
            dashDist = self._DASH_DISTANCE
            color = self._COLOUR
            dd = DebugDrawer()
            dd.line().colour(color).dashDistance(dashDist).width(w).zTest(False).point(self._fromTarget.position).point(self._toTarget.position)
            return
