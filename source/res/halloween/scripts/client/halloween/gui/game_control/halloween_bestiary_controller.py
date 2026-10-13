# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_bestiary_controller.py
from __future__ import absolute_import
from collections import namedtuple
import typing
from Event import Event
from halloween.gui.impl.lobby.hw_helpers.bestiary_helper import getEnemiesSeenList, isEnemyUnlocked
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween_common.configs.halloween_bestiary import bestiarySchema
from halloween_common.halloween_constants import HALLOWEEN_BESTIARY_PARAMS_KEY
from items.vehicles import makeVehicleTypeCompDescrByName
from skeletons.gui.lobby_context import ILobbyContext
from visual_script_client.arena_blocks import dependency
if typing.TYPE_CHECKING:
    from typing import Optional, Tuple
    from halloween_common.configs.halloween_bestiary import BestiaryModel, EnemyModel
    from halloween.skeletons.halloween_controller import IHalloweenController
    from gui.shared.events import GUICommonEvent
EnemyData = namedtuple('Enemy', ['intCD', 'enemy'])

class HalloweenBestiaryController(IHalloweenBestiaryController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __hwCtrl = dependency.descriptor(IHalloweenArtefactsController)

    def __init__(self):
        self.__enemies = ()
        self.__isBestiaryPostponed = False
        self.onSettingsUpdate = Event()

    def fini(self):
        self.__clear()
        super(HalloweenBestiaryController, self).fini()

    def getEnemyByIntCD(self, intCD):
        for enemyData in self.__enemies:
            if enemyData.intCD == intCD:
                return enemyData.enemy

        return None

    def getEnemyByToken(self, token):
        return next((enemyData for enemyData in self.enemies if enemyData.enemy.unlockedByToken == token), None)

    def getFirstNewEnemy(self):
        enemiesSeenList = getEnemiesSeenList()
        return next((intCD for intCD, enemy in self.enemies if isEnemyUnlocked(enemy) and intCD not in enemiesSeenList), None)

    def hasEnemy(self, token):
        return self.getEnemyByToken(token) is not None

    @property
    def hasUnlockedEnemies(self):
        return next((True for _, enemy in self.enemies if isEnemyUnlocked(enemy)), False)

    @property
    def isBestiaryPostponed(self):
        return self.__isBestiaryPostponed

    @isBestiaryPostponed.setter
    def isBestiaryPostponed(self, value):
        self.__isBestiaryPostponed = value

    def onDisconnected(self):
        self.__clear()
        super(HalloweenBestiaryController, self).onDisconnected()

    def onLobbyInited(self, event):
        self.__initEnemies()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        super(HalloweenBestiaryController, self).onLobbyInited(event)

    @property
    def enemies(self):
        return self.__enemies

    def _getConfig(self):
        return self.__lobbyContext.getServerSettings().getConfigModel(bestiarySchema)

    def __clear(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.onSettingsUpdate.clear()
        self.__enemies = ()
        self.__isBestiaryPostponed = False

    def __initEnemies(self):
        self.__enemies = tuple((EnemyData(makeVehicleTypeCompDescrByName(enemy.name), enemy) for enemy in self._getConfig().enemies.enemy))

    def __onServerSettingsChanged(self, diff):
        if self.__hwCtrl.isEnabled() and HALLOWEEN_BESTIARY_PARAMS_KEY in diff:
            self.__initEnemies()
            self.onSettingsUpdate()
