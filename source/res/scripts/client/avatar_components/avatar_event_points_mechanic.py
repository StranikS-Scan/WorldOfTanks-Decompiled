# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/avatar_event_points_mechanic.py
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS as BONUS_CAPS
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class AvatarEventPointsMechanic(object):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)
    ownEventPointsCount = property(lambda self: self.__ownEventPointsCount)
    totalEventPoints = property(lambda self: self.__totalEventPoints)

    def __init__(self):
        self.__enabled = False
        self.__ownEventPointsCount = None
        self.__totalEventPoints = None
        return

    def destroy(self):
        pass

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = BONUS_CAPS.checkAny(self.arenaBonusType, BONUS_CAPS.EVENT_BATTLES)

    def initEventPoints(self, vehicleID):
        if not self.__enabled:
            return
        else:
            self.__vehicleID = vehicleID
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            eventPointsComp = getattr(componentSystem, 'eventPointsComponent', None)
            if eventPointsComp is not None:
                eventPointsComp.onCurrentEventPointsUpdated += self.__onCurrentEventPointsUpdated
                eventPointsComp.onTotalEventPointsUpdated += self.__onTotalEventPointsUpdated
                self.__onCurrentEventPointsUpdated(eventPointsComp.currentEventPoints)
                self.__onTotalEventPointsUpdated(eventPointsComp.totalEventPoints)
            return

    def onBecomeNonPlayer(self):
        if not self.__enabled:
            return
        else:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            eventPointsComp = getattr(componentSystem, 'eventPointsComponent', None)
            if eventPointsComp is not None:
                eventPointsComp.onCurrentEventPointsUpdated -= self.__onCurrentEventPointsUpdated
                eventPointsComp.onTotalEventPointsUpdated -= self.__onTotalEventPointsUpdated
            return

    def __onCurrentEventPointsUpdated(self, eventPoints):
        if not self.__enabled:
            return
        self.__ownEventPointsCount = eventPoints[self.team].get(self.__vehicleID, 0)
        self.guiSessionProvider.shared.eventPoints.setCurrentEventPointsCount(self.__ownEventPointsCount)

    def __onTotalEventPointsUpdated(self, eventPoints):
        if not self.__enabled:
            return
        self.guiSessionProvider.shared.eventPoints.setTotalEventPointsCount(eventPoints.get(self.team, 0))
        self.__totalEventPoints = eventPoints
