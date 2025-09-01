# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/trajectory_drawer.py
import BigWorld
import CGF
from constants import IS_DEVELOPMENT
from debug_utils import LOG_CURRENT_EXCEPTION

class TrajectoryDrawer(object):
    __slots__ = ('__impl',)

    def __init__(self, spaceID):
        self.__impl = _TrajectoryDrawerImpl(spaceID) if IS_DEVELOPMENT else None
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
    __slots__ = ('__spaceID', '__isEnabled', '__gameObject', '__drawer')

    def __init__(self, spaceID):
        self.__spaceID = spaceID
        self.__isEnabled = False
        self.__gameObject = None
        self.__drawer = None
        BigWorld.addWatcher('Debug/Ballistics/Debug draw', self.__getEnabled, self.__setEnabled)
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

    def addProjectile(self, shotID, attackerID, startPoint, velocity, gravity, maxDistance, isOwnShot):
        if self.__isEnabled and self.__drawer is not None:
            self.__drawer.addProjectile(shotID, attackerID, startPoint, velocity, gravity, maxDistance, isOwnShot)
        return

    def removeProjectile(self, shotID):
        if self.__drawer is not None:
            self.__drawer.removeProjectile(shotID if shotID > 0 else -shotID)
        return

    @staticmethod
    def __castBool(value):
        return value.lower() not in ('false', '0')

    def __getEnabled(self):
        return self.__isEnabled

    def __setEnabled(self, value):
        self.__isEnabled = self.__castBool(value)
        if self.__isEnabled:
            if self.__gameObject is None:
                self.__gameObject = CGF.GameObject(self.__spaceID, 'TrajectoryDrawer')
            if self.__drawer is None:
                self.__drawer = self.__gameObject.createComponent(BigWorld.TrajectoryDrawer)
            self.__gameObject.activate()
        else:
            self.__gameObject.deactivate()
        return
