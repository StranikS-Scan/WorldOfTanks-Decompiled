# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/game_control/halloween_anomalies_controller.py
from __future__ import absolute_import
from collections import namedtuple, OrderedDict
import random
import typing
import BattleReplay
import BigWorld
from Event import Event
from gui.ClientUpdateManager import g_clientUpdateManager
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween_common.configs.halloween_anomalies import anomaliesConfigSchema
from halloween_common.halloween_constants import HALLOWEEN_ANOMALIES_PARAMS_KEY, ANOMALIES_SYSTEM_UNLOCKED, ALL_LOOT_ANOMALY_TYPES, AnomalySettings
from shared_utils import nextTick
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from visual_script_client.arena_blocks import dependency
if typing.TYPE_CHECKING:
    from typing import Optional, List
    from halloween_common.configs.halloween_anomalies import AnomaliesConfigModel
    from gui.shared.events import GUICommonEvent
AnomalyData = namedtuple('AnomalyData', ['id', 'type'])
RecipeData = namedtuple('RecipeData', ['id', 'ingredients'])

class HalloweenAnomaliesController(IHalloweenAnomaliesController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __hwCtrl = dependency.descriptor(IHalloweenController)
    __slots__ = ('__anomalies', '__lootAnomalies', '__recipes', '_lastSkinId')

    def __init__(self):
        self.onRefreshData = Event()
        self.onChangeSystemAnomaliesUnlock = Event()
        self.__anomalies = OrderedDict()
        self.__lootAnomalies = []
        self.__recipes = OrderedDict()
        self._lastSkinId = None
        return

    def fini(self):
        self.__clear()
        super(HalloweenAnomaliesController, self).fini()

    def onLobbyInited(self, event):
        self.__refreshData()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_clientUpdateManager.addCallbacks({'tokens': self.__handleTokensUpdate})
        super(HalloweenAnomaliesController, self).onLobbyInited(event)

    def onAvatarBecomePlayer(self):
        if BattleReplay.g_replayCtrl.isPlaying and not BigWorld.player().userSeesWorld():
            nextTick(self.onAvatarBecomePlayer)()
        else:
            self.__clear()
            self.__refreshData()

    def onDisconnected(self):
        self.__clear()
        super(HalloweenAnomaliesController, self).onDisconnected()

    @property
    def anomalies(self):
        return self.__anomalies

    @property
    def lootAnomalies(self):
        return self.__lootAnomalies

    @property
    def recipes(self):
        return self.__recipes

    def getAnomalyByID(self, anomalyID):
        return self.anomalies.get(anomalyID)

    def _getConfig(self):
        return self.__lobbyContext.getServerSettings().getConfigModel(anomaliesConfigSchema)

    def __clear(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.onRefreshData.clear()
        self.__anomalies.clear()
        self.__lootAnomalies = []
        self.__recipes.clear()

    def __handleTokensUpdate(self, diff):
        if ANOMALIES_SYSTEM_UNLOCKED in diff:
            self.onChangeSystemAnomaliesUnlock()
        if any((token.startswith(AnomalySettings.TOKEN_PREFIX) for token in diff)):
            self.__refreshData()

    def __refreshData(self):
        self.__anomalies.clear()
        self.__lootAnomalies = []
        for anomaly in self._getConfig().anomalies.anomaly:
            anomalyID, anomalyType = anomaly.id, anomaly.type
            anomalyData = AnomalyData(anomalyID, anomalyType)
            self.__anomalies[anomalyID] = anomalyData
            if anomalyType in ALL_LOOT_ANOMALY_TYPES:
                self.__lootAnomalies.append(anomalyData)

        self.__recipes.clear()
        for recipe in self._getConfig().recipes.recipe:
            recipeID = recipe.id
            ingredients = OrderedDict(((i, self.__anomalies[i]) for i in recipe.ingredients))
            self.__recipes[recipeID] = RecipeData(recipeID, ingredients)

        self.onRefreshData()

    def __onServerSettingsChanged(self, diff):
        if self.__hwCtrl.isEnabled() and HALLOWEEN_ANOMALIES_PARAMS_KEY in diff:
            self.__refreshData()

    def getNextSkinId(self, maxSkinId):
        if maxSkinId <= 1:
            return 1
        newSkinId = random.randint(1, maxSkinId)
        while newSkinId == self._lastSkinId:
            newSkinId = random.randint(1, maxSkinId)

        self._lastSkinId = newSkinId
        return newSkinId
