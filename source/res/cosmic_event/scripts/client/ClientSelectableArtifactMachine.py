# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/ClientSelectableArtifactMachine.py
from ClientSelectableObject import ClientSelectableObject
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from helpers import dependency

class ClientSelectableArtifactMachine(ClientSelectableObject):
    __cosmicController = dependency.descriptor(ICosmicEventBattleController)

    def onEnterWorld(self, prereqs):
        super(ClientSelectableArtifactMachine, self).onEnterWorld(prereqs)
        self.__cosmicController.onPrimeTimeStatusUpdated += self.__onGameModeStatusUpdate
        self.__onGameModeStatusUpdate()
        self.setEnable(True)

    def onLeaveWorld(self):
        self.__cosmicController.onPrimeTimeStatusUpdated -= self.__onGameModeStatusUpdate
        super(ClientSelectableArtifactMachine, self).onLeaveWorld()

    def onMouseClick(self):
        super(ClientSelectableArtifactMachine, self).onMouseClick()
        self.__cosmicController.switchPrb()

    def __onGameModeStatusUpdate(self, *_):
        self.setEnable(self.__cosmicController.isAvailable())
