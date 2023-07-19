# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/excluded_maps_feature.py
import logging
import typing
import ArenaType
from constants import PremiumConfigs, PREMIUM_TYPE, EMPTY_GEOMETRY_ID, RENEWABLE_SUBSCRIPTION_CONFIG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel, SlotStateEnum
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showMapsBlacklistView
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Dict
    from gui.impl.gen.view_models.views.lobby.account_dashboard.excluded_maps_model import ExcludedMapsModel
_logger = logging.getLogger(__name__)

class ExcludedMapsFeature(FeatureItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlus = dependency.descriptor(IWotPlusController)

    def initialize(self, *args, **kwargs):
        super(ExcludedMapsFeature, self).initialize(*args, **kwargs)
        self._viewModel.excludedMaps.onClick += self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__onPremiumNotify
        self.__wotPlus.onDataChanged += self.__onWotPlusChanged
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__onPreferredMapsChanged})

    def finalize(self):
        self._viewModel.excludedMaps.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__onPremiumNotify
        self.__wotPlus.onDataChanged -= self.__onWotPlusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExcludedMapsFeature, self).finalize()

    def _fillModel(self, model):
        self.__update(model=model)

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff or PremiumConfigs.PREFERRED_MAPS in diff or RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__update()

    def __onPreferredMapsChanged(self, _):
        self.__update()

    def __onPremiumNotify(self, *_):
        self.__update()

    def __onWotPlusChanged(self, data):
        if 'isEnabled' in data:
            self.__update()

    @replaceNoneKwargsModel
    def __update(self, model=None):
        submodel = model.excludedMaps
        serverSettings = self.__lobbyContext.getServerSettings()
        enabled = serverSettings.isPreferredMapsEnabled()
        submodel.setIsEnabled(enabled)
        if not enabled:
            return
        exclMaps = submodel.getExcludedMaps()
        exclMaps.clear()
        mapsConfig = serverSettings.getPreferredMapsConfig()
        slotCooldown = mapsConfig['slotCooldown']
        defaultSlots = mapsConfig['defaultSlots']
        premiumSlots = mapsConfig['premiumSlots']
        wotPlusSlots = mapsConfig['wotPlusSlots'] if serverSettings.isWotPlusExcludedMapEnabled() else 0
        totalSlots = defaultSlots + premiumSlots + wotPlusSlots
        maps = [ (mapId, selectedTime) for mapId, selectedTime in self.__itemsCache.items.stats.getMapsBlackList() if mapId > 0 ]
        mapsLen = len(maps)
        isPremiumAcc = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        isWotPlusAcc = self.__wotPlus.isEnabled()
        availableSlots = defaultSlots
        if isPremiumAcc:
            availableSlots += premiumSlots
        if isWotPlusAcc:
            availableSlots += wotPlusSlots
        serverUTCTime = time_utils.getServerUTCTime()

        def _getEmptyState(isSpecialSlot):
            return SlotStateEnum.EMPTY if isSpecialSlot else SlotStateEnum.DISABLED

        for i in range(totalSlots):
            slotModel = MapModel()
            if mapsLen > i:
                geometryID, selectedTime = maps[i]
                if geometryID == EMPTY_GEOMETRY_ID:
                    slotModel.setSlotState(_getEmptyState(i < availableSlots))
                    exclMaps.addViewModel(slotModel)
                    continue
                if geometryID not in ArenaType.g_geometryCache:
                    _logger.error('Server sent already selected map, but client does not have it! GeometryID: %d', geometryID)
                    continue
                slotModel.setSlotState(SlotStateEnum.SELECTED)
                slotModel.setMapId(ArenaType.g_geometryCache[geometryID].geometryName)
                dTime = serverUTCTime - selectedTime
                slotTime = 0
                if slotCooldown > dTime:
                    slotTime = slotCooldown + selectedTime
                slotModel.setCooldownEndTimeInSecs(slotTime)
            else:
                slotModel.setSlotState(_getEmptyState(i < availableSlots))
            exclMaps.addViewModel(slotModel)

        exclMaps.invalidate()

    @staticmethod
    def __onClick():
        showMapsBlacklistView()
