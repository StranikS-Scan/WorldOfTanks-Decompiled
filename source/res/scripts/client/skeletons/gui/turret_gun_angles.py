# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/turret_gun_angles.py


class ITurretAndGunAngles(object):

    def init(self):
        raise NotImplementedError

    def destroy(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def set(self, gunPitch=0.0, turretYaw=0.0):
        raise NotImplementedError

    def getGunPitch(self):
        raise NotImplementedError

    def getTurretYaw(self):
        raise NotImplementedError
