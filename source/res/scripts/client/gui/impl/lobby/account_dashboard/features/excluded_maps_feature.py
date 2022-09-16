# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/excluded_maps_feature.py
import logging
import typing
import ArenaType
from constants import PremiumConfigs, PREMIUM_TYPE, EMPTY_GEOMETRY_ID
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel, SlotStateEnum
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showMapsBlacklistView
from helpers import dependency, time_utils
from skeletons.gui.game_control import IGameSessionController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.views.lobby.account_dashboard.excluded_maps_model import ExcludedMapsModel
_logger = logging.getLogger(__name__)

class ExcludedMapsFeature(FeatureItem):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)

    def initialize(self, *args, **kwargs):
        super(ExcludedMapsFeature, self).initialize(*args, **kwargs)
        self._viewModel.excludedMaps.onClick += self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify += self.__updatePrem
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__onPreferredMapsChanged})

    def finalize(self):
        self._viewModel.excludedMaps.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.__gameSession.onPremiumNotify -= self.__updatePrem
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(ExcludedMapsFeature, self).finalize()

    def _fillModel(self, model):
        self.__update(model=model)

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff or PremiumConfigs.PREFERRED_MAPS in diff:
            self.__update()

    def __onPreferredMapsChanged(self, _):
        self.__update()

    def __updatePrem(self, *_):
        self.__update()

    @replaceNoneKwargsModel
    def __update(self, model=None):
        submodel = model.excludedMaps
        enabled = self.__lobbyContext.getServerSettings().isPreferredMapsEnabled()
        submodel.setIsEnabled(enabled)
        if not enabled:
            return
        exclMaps = submodel.getExcludedMaps()
        exclMaps.clear()
        mapsConfig = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        slotCooldown = mapsConfig['slotCooldown']
        defaultSlots = mapsConfig['defaultSlots']
        premiumSlots = mapsConfig['premiumSlots']
        totalSlots = defaultSlots + premiumSlots
        maps = self.__itemsCache.items.stats.getMapsBlackList()
        mapsLen = len(maps)
        isPremiumAcc = self.__itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        serverUTCTime = time_utils.getServerUTCTime()

        def _getEmptyState(isPremiumSlot):
            return SlotStateEnum.DISABLED if isPremiumSlot and not isPremiumAcc else SlotStateEnum.EMPTY

        for i in range(totalSlots):
            slotModel = MapModel()
            if mapsLen > i:
                geometryID, selectedTime = maps[i]
                if geometryID == EMPTY_GEOMETRY_ID:
                    slotModel.setSlotState(_getEmptyState(i >= defaultSlots))
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
                slotModel.setSlotState(_getEmptyState(i >= defaultSlots))
            exclMaps.addViewModel(slotModel)

        exclMaps.invalidate()

    @staticmethod
    def __onClick():
        showMapsBlacklistView()
