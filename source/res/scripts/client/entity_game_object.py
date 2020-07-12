# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/entity_game_object.py
import BigWorld

class EntityGameObject(BigWorld.Entity):

    def __init__(self):
        self.gameObject = None
        return

    def onEnterWorld(self, *args):
        self.gameObject = self._loadGameObject()

    def onLeaveWorld(self):
        if self.gameObject is not None:
            self.gameObject.deactivate()
            self.gameObject.destroy()
            self.gameObject.stopLoading = True
            self.gameObject = None
        return

    def _loadGameObject(self):
        raise NotImplementedError

    def _registerGameObject(self, gameObject):
        self.gameObject = gameObject
        self.gameObject.setMotor(self.matrix)
        self.gameObject.activate()
