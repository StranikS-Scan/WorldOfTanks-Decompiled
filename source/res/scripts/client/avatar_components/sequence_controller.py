# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/sequence_controller.py
import BigWorld
from sequence import SequenceManager

class SequenceController(SequenceManager):

    def onBecomePlayer(self):
        pass

    def onSpaceLoaded(self):
        self.init(BigWorld.player().spaceID)

    def onBecomeNonPlayer(self):
        if not self.isEnabled:
            return
        self.destroy()

    def handleKey(self, isDown, key, mods):
        pass
