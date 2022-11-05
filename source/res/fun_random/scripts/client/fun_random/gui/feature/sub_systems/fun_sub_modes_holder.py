# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/feature/sub_systems/fun_sub_modes_holder.py
import operator
import typing
from fun_random_common.fun_constants import FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID
from fun_random.gui.feature.fun_constants import FunSubModeBroadcast
from fun_random.gui.feature.util.fun_wrappers import skipNoSubModesAction
from fun_random.gui.feature.sub_modes import createFunSubMode
from fun_random.gui.shared.events import FunSelectionEvent, FunSubModesEvent, FunEventScope, FunEventType
from gui.battle_control.arena_visitor import createByAvatar
from skeletons.gui.game_control import IFunRandomController
if typing.TYPE_CHECKING:
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from fun_random.helpers.server_settings import FunSubModeConfig, FunRandomConfig
    from skeletons.gui.battle_session import IClientArenaVisitor

class FunSubModesHolder(IFunRandomController.IFunSubModesHolder):

    def __init__(self, subscription):
        super(FunSubModesHolder, self).__init__()
        self.__desiredSubModeID = UNKNOWN_EVENT_ID
        self.__subModes = {}
        self.__subscription = subscription

    def clear(self):
        self.__destroySubModes(set(self.__subModes.keys()))
        self.__desiredSubModeID = UNKNOWN_EVENT_ID

    def fini(self):
        self.__subscription = None
        return

    def getBattleSubMode(self, arenaVisitor=None):
        return self.getSubMode(self.getBattleSubModeID(arenaVisitor))

    def getBattleSubModeID(self, arenaVisitor=None):
        arenaVisitor = arenaVisitor or createByAvatar()
        return arenaVisitor.extra.getValue(FUN_EVENT_ID_KEY, UNKNOWN_EVENT_ID)

    def getDesiredSubMode(self):
        return self.getSubMode(self.__desiredSubModeID)

    def getDesiredSubModeID(self):
        return self.__desiredSubModeID

    def getSubMode(self, subModeID):
        return self.__subModes.get(subModeID)

    def getSubModes(self, subModesIDs=None, isOrdered=False):
        allSubModesIDs = self.__subModes.keys()
        subModesIDs = subModesIDs or allSubModesIDs
        subModes = [ self.__subModes.get(subModeID) for subModeID in subModesIDs if subModeID in allSubModesIDs ]
        return sorted(subModes, key=lambda sm: sm.getPriority()) if isOrdered else subModes

    def getSubModesIDs(self):
        return self.__subModes.keys()

    def setDesiredSubModeID(self, subModeID, trustedSource=False):
        if subModeID == self.__desiredSubModeID:
            return
        if trustedSource:
            self.__setDesiredSubMode(subModeID)
        elif subModeID == UNKNOWN_EVENT_ID:
            self.__setDesiredSubMode(subModeID, isFlush=True)
        elif subModeID in self.__subModes and self.__subModes[subModeID].isAvailable():
            self.__setDesiredSubMode(subModeID)

    def startNotification(self):
        self.__invokeSubModesMethod(FunSubModeBroadcast.START_NOTIFICATION.value)

    def stopNotification(self):
        self.__invokeSubModesMethod(FunSubModeBroadcast.STOP_NOTIFICATION.value)

    def updateSettings(self, prevSettings, newSettings):
        prevSubModes, newSubModes = prevSettings.subModes, newSettings.subModes
        prevSubModesIDs, newSubModesIDs = set(prevSubModes.keys()), set(newSubModes.keys())
        destroyed = self.__destroySubModes(prevSubModesIDs - newSubModesIDs)
        updated = self.__invalidateSubModes(prevSubModesIDs & newSubModesIDs, newSubModes)
        created = self.__createSubModes(newSubModesIDs - prevSubModesIDs, newSubModes)
        self.__invokeSubModesEvent(set.union(destroyed, updated, created), FunEventType.SUB_SETTINGS)

    def __setDesiredSubMode(self, subModeID, isFlush=False):
        self.__desiredSubModeID = subModeID
        if not isFlush:
            self.__subscription.handleEvent(FunSelectionEvent(subModeID))

    def __onSubModeEvent(self, eventType, subModeID, ctx=None):
        self.__invokeSubModesEvent({subModeID}, eventType, ctx)

    @skipNoSubModesAction
    def __invokeSubModesMethod(self, method, subModes=None, *args):
        caller = operator.methodcaller(method, *args)
        subModes = self.__subModes.iterkeys() if subModes is None else subModes
        return tuple((caller(self.__subModes[subModeID]) for subModeID in subModes))

    @skipNoSubModesAction
    def __invokeSubModesEvent(self, subModes, eventType, ctx=None):
        event = FunSubModesEvent(eventType, subModes, ctx)
        self.__subscription.handleEvent(event)
        if self.__desiredSubModeID in subModes:
            self.__subscription.handleEvent(event, scope=FunEventScope.DESIRABLE)

    @skipNoSubModesAction
    def __createSubModes(self, subModesToCreate, subModesSettings):
        for subModeID in subModesToCreate:
            self.__subModes[subModeID] = subMode = createFunSubMode(subModesSettings[subModeID])
            subMode.init()
            subMode.onSubModeEvent += self.__onSubModeEvent

        return subModesToCreate

    @skipNoSubModesAction
    def __destroySubModes(self, subModesToDestroy):
        for subModeID in subModesToDestroy:
            self.__subModes[subModeID].onSubModeEvent -= self.__onSubModeEvent
            self.__subModes[subModeID].destroy()
            del self.__subModes[subModeID]

        return subModesToDestroy

    @skipNoSubModesAction
    def __invalidateSubModes(self, subModesToUpdate, subModesSettings):
        return {sID for sID in subModesToUpdate if self.__subModes[sID].updateSettings(subModesSettings[sID])}
