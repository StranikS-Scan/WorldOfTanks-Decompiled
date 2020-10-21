# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/arena_components/loot.py
import BigWorld
from Event import Event
from arena_component_system.client_arena_component_system import ClientArenaComponent
from effect_controller import EffectController
from helpers.CallbackDelayer import CallbackDelayer

class SequencePlayer(object):

    def __init__(self, loot):
        self._appearanceID = loot.visualAppearanceID
        self._model = BigWorld.Model('')
        self._model.position = loot.position
        self._effectController = EffectController(self._appearanceID)

    def __del__(self):
        self.stop()

    def play(self):
        BigWorld.player().addModel(self._model)
        self._effectController.playSequence(self._model)

    def stop(self):
        if self._model is not None:
            BigWorld.player().delModel(self._model)
            self._model = None
            self._effectController.reset()
        return

    @classmethod
    def stopPlaying(cls, effectPlayer):
        effectPlayer.stop()
        del effectPlayer


class LootComponent(ClientArenaComponent):

    def __init__(self, componentSystem):
        ClientArenaComponent.__init__(self, componentSystem)
        self.__lootEntities = {}
        self.__delayer = CallbackDelayer()
        self.onLootAdded = Event()
        self.onLootRemoved = Event()

    def addLoot(self, loot):
        self.__lootEntities[loot.id] = loot
        self.onLootAdded(loot)

    def removeLoot(self, loot):
        if loot.id in self.__lootEntities:
            effectPlayer = SequencePlayer(loot)
            effectPlayer.play()
            self.__delayer.delayCallback(1, SequencePlayer.stopPlaying, effectPlayer)
            del self.__lootEntities[loot.id]
            self.onLootRemoved(loot)

    def getLootEntities(self):
        return self.__lootEntities

    def getLootByID(self, lootID):
        return self.__lootEntities[lootID] if lootID in self.__lootEntities else None

    def deactivate(self):
        self.__delayer.clearCallbacks()
        self.__lootEntities = {}
        super(LootComponent, self).deactivate()

    def destroy(self):
        self.__delayer.destroy()
        super(LootComponent, self).destroy()
