# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/account_dashboard/features/excluded_maps_feature.py
from typing import TYPE_CHECKING
from constants import PremiumConfigs, RENEWABLE_SUBSCRIPTION_CONFIG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel, SlotTypeEnum
from gui.impl.lobby.account_dashboard.features.base import FeatureItem
from gui.impl.lobby.account_dashboard.tooltips.excluded_maps_reward_slots_tooltip_view import ExcludedMapsRewardSlotsTooltipView
from gui.impl.lobby.premacc.views_helpers import deferPreferredMapsUiRefresh, getPreferredMapsUiRefreshDelay, getRewardSlotTooltipState, isPreferredMapsClientDiff, iterResolvedSlots, populateDashboardMapModel, shouldSchedulePreferredMapsUiRefresh
from PlayerEvents import g_playerEvents
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared.event_dispatcher import showMapsBlacklistView
from helpers import dependency, time_utils
from preferred_maps import SlotTypeId
from shared_utils import findFirst
from skeletons.gui.game_control import IGameSessionController, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.wot_plus.loggers import WotPlusAccountDashboardWidgetLogger
from uilogging.wot_plus.logging_constants import AccountDashboardFeature
if TYPE_CHECKING:
    from typing import Dict, Optional
    from frameworks.wulf import View, ViewEvent
    from gui.impl.gen.view_models.views.lobby.account_dashboard.excluded_maps_model import ExcludedMapsModel
_SLOT_TYPE_ID_TO_ENUM = {SlotTypeId.DEFAULT: SlotTypeEnum.DEFAULT,
 SlotTypeId.PREMIUM: SlotTypeEnum.PREMIUM,
 SlotTypeId.SUBSCRB: SlotTypeEnum.SUBSCRB,
 SlotTypeId.REWARDS: SlotTypeEnum.REWARDS}

class ExcludedMapsFeature(FeatureItem):
    __slots__ = ('__notifier',)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __gameSession = dependency.descriptor(IGameSessionController)
    __wotPlus = dependency.descriptor(IWotPlusController)

    def __init__(self, viewModel):
        super(ExcludedMapsFeature, self).__init__(viewModel)
        self.__notifier = Notifiable()
        self.__notifier.addNotificator(SimpleNotifier(self.__getCooldownNotificationDelta, self.__update))

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.account_dashboard.tooltips.ExcludedMapsRewardSlotsTooltipView():
            rewardsSlot = findFirst(lambda s: s.getType() == SlotTypeEnum.REWARDS, (slot for slot in self._viewModel.excludedMaps.getExcludedMaps()))
            if rewardsSlot:
                cooldownEndTimeInSecs = rewardsSlot.getCooldownEndTimeInSecs()
                return ExcludedMapsRewardSlotsTooltipView(getRewardSlotTooltipState(rewardsSlot.getSlotState(), cooldownEndTimeInSecs), cooldownEndTimeInSecs, rewardsSlot.getExpirationTime())
        return super(ExcludedMapsFeature, self).createToolTipContent(event=event, contentID=contentID)

    def initialize(self, *args, **kwargs):
        super(ExcludedMapsFeature, self).initialize(*args, **kwargs)
        self._viewModel.excludedMaps.onClick += self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated += self.__onClientUpdated
        self.__gameSession.onPremiumNotify += self.__onPremiumNotify
        self.__wotPlus.onDataChanged += self.__onWotPlusChanged
        g_clientUpdateManager.addCallbacks({'preferredMaps': self.__onPreferredMapsChanged})

    def finalize(self):
        self._viewModel.excludedMaps.onClick -= self.__onClick
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_playerEvents.onClientUpdated -= self.__onClientUpdated
        self.__gameSession.onPremiumNotify -= self.__onPremiumNotify
        self.__wotPlus.onDataChanged -= self.__onWotPlusChanged
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__notifier.clearNotification()
        super(ExcludedMapsFeature, self).finalize()

    def _fillModel(self, model):
        self.__update(model=model)

    def __onServerSettingsChanged(self, diff):
        if PremiumConfigs.IS_PREFERRED_MAPS_ENABLED in diff or RENEWABLE_SUBSCRIPTION_CONFIG in diff or PremiumConfigs.PREFERRED_MAPS in diff:
            self.__update()

    def __onClientUpdated(self, diff, _):
        if not isPreferredMapsClientDiff(diff):
            return
        deferPreferredMapsUiRefresh(self.__update)

    def __onPreferredMapsChanged(self, _):
        self.__update()

    def __onPremiumNotify(self, *_):
        self.__update()

    def __onWotPlusChanged(self, data):
        if 'isEnabled' in data:
            self.__update()

    def __getCooldownNotificationDelta(self):
        config = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        return getPreferredMapsUiRefreshDelay(config, self.__itemsCache)

    @replaceNoneKwargsModel
    def __update(self, model=None):
        submodel = model.excludedMaps
        serverSettings = self.__lobbyContext.getServerSettings()
        enabled = serverSettings.isPreferredMapsEnabled()
        submodel.setIsEnabled(enabled)
        submodel.setIsWotPlusEnabled(self.__wotPlus.isWotPlusEnabled())
        if not enabled:
            self.__notifier.stopNotification()
            return
        config = serverSettings.getPreferredMapsConfig()
        slotCooldown = config['slotCooldown']
        serverUTCTime = time_utils.getServerUTCTime()
        exclMaps = submodel.getExcludedMaps()
        exclMaps.clear()
        for slot in iterResolvedSlots(config, self.__itemsCache):
            slotModel = MapModel()
            if populateDashboardMapModel(slotModel, slot, slotCooldown, serverUTCTime, _SLOT_TYPE_ID_TO_ENUM[slot.type]):
                exclMaps.addViewModel(slotModel)

        exclMaps.invalidate()
        if shouldSchedulePreferredMapsUiRefresh(config, self.__itemsCache, serverUTCTime):
            self.__notifier.startNotification()
        else:
            self.__notifier.stopNotification()

    @staticmethod
    def __onClick():
        WotPlusAccountDashboardWidgetLogger().logWidgetClickEvent(AccountDashboardFeature.EXCLUDED_MAPS_WIDGET)
        showMapsBlacklistView()
