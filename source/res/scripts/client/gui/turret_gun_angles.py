# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/turret_gun_angles.py
from gui.ClientHangarSpace import hangarCFG
from skeletons.gui.turret_gun_angles import ITurretAndGunAngles

class TurretAndGunAngles(ITurretAndGunAngles):

    def __init__(self):
        self.__gunPitch = 0.0
        self.__turretYaw = 0.0

    def init(self):
        self.reset()

    def reset(self):
        cfg = hangarCFG()
        self.__gunPitch = cfg.get('vehicle_gun_pitch', 0.0)
        self.__turretYaw = cfg.get('vehicle_turret_yaw', 0.0)

    def destroy(self):
        self.__gunPitch = 0.0
        self.__turretYaw = 0.0

    def set(self, gunPitch=0.0, turretYaw=0.0):
        self.__gunPitch = gunPitch
        self.__turretYaw = turretYaw

    def getTurretYaw(self):
        return self.__turretYaw

    def getGunPitch(self):
        return self.__gunPitch
