# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Mine.py
from battleground.mines_object import loadMines
from entity_game_object import EntityGameObject

class Mine(EntityGameObject):

    def set_isDetonated(self, prev=None):
        if self.isDetonated:
            if self.gameObject is not None:
                self.gameObject.detonate()
        return

    def _loadGameObject(self):
        return loadMines(self.ownerVehicleID, self._registerGameObject)

    def _registerGameObject(self, gameObject):
        self.gameObject.setPosition(self.position)
        super(Mine, self)._registerGameObject(gameObject)
