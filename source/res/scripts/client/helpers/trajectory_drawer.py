# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/trajectory_drawer.py
import BigWorld
import Svarog
from debug_utils import LOG_CURRENT_EXCEPTION
try:
    import BallisticsDebug
    isDebugDrawInited = True
except ImportError:
    isDebugDrawInited = False

class TrajectoryDrawer(object):
    __slots__ = ('__impl',)

    def __init__(self, spaceID):
        self.__impl = _TrajectoryDrawerImpl(spaceID) if isDebugDrawInited else None
        return

    def destroy(self):
        if self.__impl is not None:
            self.__impl.destroy()
        return

    def addProjectile(self, shotID, attackerID, startPoint, velocity, gravity, maxDistance, isOwnShot):
        if self.__impl is not None:
            self.__impl.addProjectile(shotID, attackerID, startPoint, velocity, gravity, maxDistance, isOwnShot)
        return

    def removeProjectile(self, shotID):
        if self.__impl is not None:
            self.__impl.removeProjectile(shotID)
        return


class _TrajectoryDrawerImpl(object):
    __slots__ = ('__gameObject', '__isEnabled', '__drawer', '__spaceID')

    def __init__(self, spaceID):
        self.__spaceID = spaceID
        self.__isEnabled = False
        self.__gameObject = None
        self.__drawer = None
        BigWorld.addWatcher('Debug/Ballistics/Debug draw', self.__getEnabled, self.__setEnabled, 'Enable debug trajectory drawer')
        return

    def destroy(self):
        try:
            BigWorld.delWatcher('Debug/Ballistics/Debug draw')
        except ValueError:
            LOG_CURRENT_EXCEPTION()

        self.__drawer = None
        if self.__gameObject is not None:
            self.__gameObject.destroy()
        return

    def addProjectile(self, shotID, attackerID, refStartPoint, refVelocity, gravity, maxDistance, isOwnShot):
        if self.__isEnabled and self.__drawer is not None:
            self.__drawer.addProjectile(shotID, attackerID, refStartPoint, refVelocity, gravity, maxDistance, isOwnShot)
        return

    def removeProjectile(self, shotID):
        if self.__drawer is not None:
            self.__drawer.removeProjectile(shotID if shotID > 0 else -shotID)
        return

    def __getEnabled(self):
        return self.__isEnabled

    def __setEnabled(self, value):
        self.__isEnabled = self.__castBool(value)
        if self.__isEnabled:
            if self.__gameObject is None:
                self.__gameObject = Svarog.GameObject(self.__spaceID)
            if self.__drawer is None:
                self.__drawer = self.__gameObject.createComponent(BallisticsDebug.TrajectoryDrawer)
            self.__gameObject.activate()
        else:
            self.__gameObject.deactivate()
        return

    @staticmethod
    def __castBool(value):
        return value.lower() not in ('false', '0')
