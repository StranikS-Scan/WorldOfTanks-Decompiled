# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/battle/minimap/loot_detector.py
import math
import BigWorld
import Event
import Math
from constants import VISIBILITY
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers import time_utils, dependency
from skeletons.gui.battle_session import IBattleSessionProvider

def pointSectorIntersection(p0, v0, r, a, p1):
    p0p1 = p1 - p0
    if p0p1.length <= r:
        p0p1.normalise()
        dotProduct = p0p1.dot(v0)
        if dotProduct > 0 and math.acos(dotProduct) <= a / 2:
            return True
    return False


class LootDetector(Notifiable):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(LootDetector, self).__init__()
        self.__sectorRadius = 0
        self.__sectorAngle = 0
        self.__viewDirection = None
        self.__observationPoint = None
        self.__arenaVisitor = None
        self.__lootsDetectedInSector = set()
        self.__em = Event.EventManager()
        self.__active = False
        self.onLootsDetected = Event.Event(self.__em)
        self.onLootsLost = Event.Event(self.__em)
        self.addNotificator(SimpleNotifier(lambda : time_utils.ONE_SECOND, self.__detectLoots))
        return

    def init(self, arenaVisitor=None):
        self.__arenaVisitor = arenaVisitor

    def fini(self):
        self.__em.clear()
        self.clearNotification()
        self.__lootsDetectedInSector = None
        self.__viewDirection = None
        self.__observationPoint = None
        self.__arenaVisitor = None
        return

    def start(self):
        self.startNotification()
        self.__active = True

    def stop(self):
        self.onLootsLost(self.__lootsDetectedInSector)
        self.__lootsDetectedInSector.clear()
        self.stopNotification()
        self.__active = False

    @property
    def active(self):
        return self.__active

    def __updateParams(self):
        vehicle = BigWorld.player().vehicle
        if not vehicle:
            return False
        if not vehicle.isAlive():
            return False
        coneVisibilityComponent = vehicle.dynamicComponents.get('coneVisibility')
        if not coneVisibilityComponent:
            return False
        self.__sectorAngle = coneVisibilityComponent.circularVisionAngle
        if not self.__arenaVisitor:
            return False
        self.__sectorRadius = self.__calcCircularVisionRadius()
        self.__viewDirection = self.__getGunDirectionXZ(vehicle)
        self.__observationPoint = Math.Vector2(vehicle.position.x, vehicle.position.z)
        return True

    def __detectLoots(self):
        loots = {e for e in BigWorld.entities.valuesOfType('Loot') if pointSectorIntersection(self.__observationPoint, self.__viewDirection, self.__sectorRadius, self.__sectorAngle, Math.Vector2(e.position.x, e.position.z))} if self.__updateParams() else set()
        self.onLootsLost(self.__lootsDetectedInSector - loots)
        self.onLootsDetected(loots - self.__lootsDetectedInSector)
        self.__lootsDetectedInSector = loots

    def __calcCircularVisionRadius(self):
        visibilityMinRadius = self.__arenaVisitor.getVisibilityMinRadius()
        vehAttrs = self.__sessionProvider.shared.feedback.getVehicleAttrs()
        return min(vehAttrs.get('circularVisionRadius', visibilityMinRadius), VISIBILITY.MAX_RADIUS)

    @staticmethod
    def __getGunDirectionXZ(vehicle):
        turretYaw, _ = vehicle.getServerGunAngles()
        gunYaw = vehicle.yaw + turretYaw
        return Math.Vector2(math.sin(gunYaw), math.cos(gunYaw))
