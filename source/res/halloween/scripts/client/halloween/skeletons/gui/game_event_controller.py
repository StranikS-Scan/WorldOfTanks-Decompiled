# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/skeletons/gui/game_event_controller.py
from skeletons.gui.game_control import IGameController

class IHalloweenProgressController(IGameController):
    onQuestsUpdated = None
    onChangeActivePhase = None
    onSyncCompleted = None
    phasesHalloween = None

    def isPostPhase(self):
        raise NotImplementedError
