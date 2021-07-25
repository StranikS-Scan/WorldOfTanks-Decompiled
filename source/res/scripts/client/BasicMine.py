# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/BasicMine.py
from battleground.mines_object import loadMines
from entity_game_object import EntityGameObject

class BasicMine(EntityGameObject):

    def set_isDetonated(self, prev=None):
        if self.isDetonated:
            if self.gameObject is not None:
                self.gameObject.detonate()
        return

    def _loadGameObject(self):
        return loadMines(self.ownerVehicleID, self._registerGameObject)

    def _registerGameObject(self, gameObject):
        self.gameObject.setPosition(self.position)
        self.gameObject.setIsEnemyMarkerEnabled(self.isMarkerEnabled)
        super(BasicMine, self)._registerGameObject(gameObject)

    def set_isMarkerEnabled(self, prev=None):
        if self.gameObject is not None:
            self.gameObject.enableEnemyIdleEffect(self.isMarkerEnabled)
        return
