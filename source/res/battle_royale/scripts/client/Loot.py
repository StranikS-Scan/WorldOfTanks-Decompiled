# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/Loot.py
import BigWorld
from battleground.loot_object import loadLootById
from constants import NULL_ENTITY_ID

class Loot(BigWorld.Entity):

    def __init__(self, *args, **kwargs):
        super(Loot, self).__init__(*args, **kwargs)
        self.__effect = None
        return

    def onEnterWorld(self, *args):
        self.__effect = loadLootById(self.typeID, self.position)
        if self.__effect:
            self.__showEffect()

    def onLeaveWorld(self):
        if self.__effect:
            self.__effect.clear()
        self.__effect = None
        return

    def set_pickedUpBy(self, prev=None):
        self.__effect.clear()
        self.__showEffect()

    def __showEffect(self):
        self.__effect.show(self.pickedUpBy != NULL_ENTITY_ID)
