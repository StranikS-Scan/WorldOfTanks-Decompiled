# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/event_control_point.py
from Event import Event
from helpers import dependency
from constants import ECP_HUD_INDEXES, ECP_HUD_TOGGLES
from arena_component_system.client_arena_component_system import ClientArenaComponent
from gui.battle_control import event_dispatcher as gui_event_dispatcher
from skeletons.gui.battle_session import IBattleSessionProvider

class EventControlPointComponent(ClientArenaComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__gameEventStorage = None
        self.__ecpEntities = {}
        self.__ecpHUDEvents = {}
        for i in ECP_HUD_INDEXES.all():
            self.__ecpHUDEvents[i] = {ECP_HUD_TOGGLES.on: Event(),
             ECP_HUD_TOGGLES.off: Event()}

        return

    def toggleHUDElement(self, ecp, hudElement, toggle):
        if ecp.id in self.__ecpEntities:
            if toggle == ECP_HUD_TOGGLES.on:
                self.__ecpHUDEvents[hudElement][ECP_HUD_TOGGLES.off](ecp)
        else:
            self.__ecpEntities[ecp.id] = ecp
        self.__ecpHUDEvents[hudElement][toggle](ecp)

    def getECPEntities(self):
        return self.__ecpEntities

    def getECPByID(self, ecpID):
        return self.__ecpEntities[ecpID] if ecpID in self.__ecpEntities else None

    def ecpStateByID(self, ecpID):
        return self.gameEventComponent.ecpState.getStateByID(ecpID)

    def fadeOut(self, faderSettings):
        if gui_event_dispatcher is not None:
            gui_event_dispatcher.toggleFadeOut(faderSettings)
        return

    def deactivate(self):
        self.__ecpEntities = {}
        self.__gameEventStorage = None
        super(EventControlPointComponent, self).deactivate()
        return

    @property
    def ecpHUDEvents(self):
        return self.__ecpHUDEvents

    @property
    def gameEventComponent(self):
        component = self.__gameEventStorage
        if not component:
            componentSystem = self.sessionProvider.arenaVisitor.getComponentSystem()
            self.__gameEventStorage = component = getattr(componentSystem, 'gameEventComponent', None)
        return component
