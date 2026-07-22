# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/premacc/views_helpers.py
import logging
from typing import TYPE_CHECKING
import ArenaType
import BigWorld
from constants import PREMIUM_TYPE, PremiumConfigs
from helpers import dependency, time_utils
from preferred_maps import BlacklistWrapper, SLOT_TYPE_NAME, Slot, SlotTypeId, SlotTypeName, getConfiguredSlotLayout, getSlotTypeID
from skeletons.gui.game_control import IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Iterator, Optional
    from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import MapModel
    from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapsBlacklistSlotModel
_logger = logging.getLogger(__name__)

def isPreferredMapsClientDiff(diff):
    if not diff:
        return False
    if 'preferredMaps' in diff:
        return True
    serverSettingsDiff = diff.get('serverSettings')
    return True if isinstance(serverSettingsDiff, dict) and PremiumConfigs.PREFERRED_MAPS in serverSettingsDiff else False


def deferPreferredMapsUiRefresh(refreshCallback):
    BigWorld.callback(0.0, refreshCallback)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _isDefaultSlotAvailable(_=None, lobbyContext=None):
    return lobbyContext.getServerSettings().isPreferredMapsSlotsEnabled(SlotTypeName.DEFAULT)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, lobbyContext=ILobbyContext)
def _isPremiumSlotsAvailable(_=None, itemsCache=None, lobbyContext=None):
    return False if not lobbyContext.getServerSettings().isPreferredMapsSlotsEnabled(SlotTypeName.PREMIUM) else itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)


@dependency.replace_none_kwargs(wotPlus=IWotPlusController, lobbyContext=ILobbyContext)
def _isSubscrbSlotsAvailable(_=None, wotPlus=None, lobbyContext=None):
    serverSettings = lobbyContext.getServerSettings()
    return False if not serverSettings.isPreferredMapsSlotsEnabled(SlotTypeName.SUBSCRB) else wotPlus.isEnabled() and serverSettings.isWotPlusExcludedMapEnabled()


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _isRewardsSlotsAvailable(slot=None, lobbyContext=None):
    return False if not lobbyContext.getServerSettings().isPreferredMapsSlotsEnabled(SlotTypeName.REWARDS) else slot is not None and slot.isEnabled()


IS_BLACKLIST_SLOT_AVAILABLE = {SlotTypeId.DEFAULT: _isDefaultSlotAvailable,
 SlotTypeId.PREMIUM: _isPremiumSlotsAvailable,
 SlotTypeId.SUBSCRB: _isSubscrbSlotsAvailable,
 SlotTypeId.REWARDS: _isRewardsSlotsAvailable}

@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isSlotDisabledByKillSwitch(slot, lobbyContext=None):
    return not lobbyContext.getServerSettings().isPreferredMapsSlotsEnabled(SLOT_TYPE_NAME[slot.type])


def fetchBlacklistWrapper(itemsCache):
    return BlacklistWrapper(itemsCache.items.stats.getMapsBlackList())


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def getResolvedSlotByTypeName(slotName, itemsCache=None, lobbyContext=None):
    config = lobbyContext.getServerSettings().getPreferredMapsConfig()
    slotTypeId = SlotTypeId(getSlotTypeID(slotName))
    for slot in iterResolvedSlots(config, itemsCache):
        if slot.type == slotTypeId:
            return slot

    return None


def resolveSlotWithServerState(slot, layout, blackList):
    newSlot = blackList.get(slot.id)
    if newSlot is not None:
        slot = layout[slot.id] = newSlot
    return slot


def iterResolvedSlots(config, itemsCache):
    layout = getConfiguredSlotLayout(config)
    blackList = fetchBlacklistWrapper(itemsCache)
    for slotId in sorted(layout):
        yield resolveSlotWithServerState(layout[slotId], layout, blackList)


def getSecondsUntilNextSlotCooldownEnds(config, itemsCache, serverUTCTime=None):
    if serverUTCTime is None:
        serverUTCTime = time_utils.getServerUTCTime()
    slotCooldown = config['slotCooldown']
    minSeconds = 0
    for slot in iterResolvedSlots(config, itemsCache):
        if not slot.mapID:
            continue
        secondsLeft = _getSlotCooldownEndTimestamp(slot, slotCooldown, serverUTCTime) - serverUTCTime
        if secondsLeft > 0:
            secondsLeft = int(secondsLeft)
            if minSeconds == 0 or secondsLeft < minSeconds:
                minSeconds = secondsLeft

    return minSeconds


def getSecondsUntilNextRewardGrantExpires(config, itemsCache, serverUTCTime=None):
    if serverUTCTime is None:
        serverUTCTime = time_utils.getServerUTCTime()
    minSeconds = -1
    for slot in iterResolvedSlots(config, itemsCache):
        if slot.type != SlotTypeId.REWARDS or slot.expire >= float('inf'):
            continue
        if slot.expire <= serverUTCTime:
            continue
        secondsLeft = int(slot.expire - serverUTCTime)
        if minSeconds < 0 or secondsLeft < minSeconds:
            minSeconds = secondsLeft

    return minSeconds


def getSecondsUntilNextPreferredMapsUiEvent(config, itemsCache, serverUTCTime=None):
    if serverUTCTime is None:
        serverUTCTime = time_utils.getServerUTCTime()
    slotCooldown = config['slotCooldown']
    minSeconds = -1
    for slot in iterResolvedSlots(config, itemsCache):
        if slot.mapID and slotCooldown > serverUTCTime - slot.modified:
            secondsLeft = _getSlotCooldownEndTimestamp(slot, slotCooldown, serverUTCTime) - serverUTCTime
            if secondsLeft > 0:
                secondsLeft = int(secondsLeft)
                if minSeconds < 0 or secondsLeft < minSeconds:
                    minSeconds = secondsLeft
        if slot.type == SlotTypeId.REWARDS and slot.expire < float('inf') and slot.expire > serverUTCTime:
            secondsLeft = int(slot.expire - serverUTCTime)
            if minSeconds < 0 or secondsLeft < minSeconds:
                minSeconds = secondsLeft

    return minSeconds


def getPreferredMapsUiRefreshDelay(config, itemsCache, serverUTCTime=None):
    secondsLeft = getSecondsUntilNextPreferredMapsUiEvent(config, itemsCache, serverUTCTime)
    if secondsLeft < 0:
        return 0
    return 1 if secondsLeft == 0 else secondsLeft


def shouldSchedulePreferredMapsUiRefresh(config, itemsCache, serverUTCTime=None):
    return getSecondsUntilNextPreferredMapsUiEvent(config, itemsCache, serverUTCTime) >= 0


def _isRewardSlotExpired(slot, serverUTCTime):
    return slot.type == SlotTypeId.REWARDS and slot.expire < float('inf') and slot.expire <= serverUTCTime


def _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime):
    if slot.type != SlotTypeId.REWARDS or slot.expire >= float('inf'):
        return
    if isSlotDisabledByKillSwitch(slot) or _isRewardSlotExpired(slot, serverUTCTime) or not isSlotAvailableForUI(slot):
        slotModel.setExpirationTime(0)
    else:
        slotModel.setExpirationTime(int(slot.expire))


def _getSlotCooldownEndTimestamp(slot, slotCooldown, serverUTCTime):
    cooldownEnd = min(int(slot.modified + slotCooldown), int(serverUTCTime + slotCooldown))
    if slot.type == SlotTypeId.REWARDS and slot.expire < float('inf'):
        cooldownEnd = min(cooldownEnd, int(slot.expire))
    return cooldownEnd


def getRewardSlotTooltipState(dashboardSlotState, cooldownEndTimeInSecs, serverUTCTime=None):
    from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import SlotStateEnum
    from gui.impl.gen.view_models.views.lobby.account_dashboard.tooltips.excluded_maps_reward_slots_tooltip_view_model import MapStateEnum
    if serverUTCTime is None:
        serverUTCTime = time_utils.getServerUTCTime()
    if dashboardSlotState in (SlotStateEnum.DISABLED, SlotStateEnum.DISABLEDBYKILLSWITCH):
        return MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED
    elif dashboardSlotState == SlotStateEnum.SELECTED:
        if cooldownEndTimeInSecs > serverUTCTime:
            return MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN
        return MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE
    else:
        return MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE


def isSlotAvailableForUI(slot):
    return IS_BLACKLIST_SLOT_AVAILABLE[slot.type](slot) and slot.isEnabled()


def getMapGeometryName(mapID):
    if mapID not in ArenaType.g_geometryCache:
        _logger.error('Server sent already selected map, but client does not have it! GeometryID: %d', mapID)
        return None
    else:
        return ArenaType.g_geometryCache[mapID].geometryName


def populateMapsBlacklistSlotModel(slotModel, slot, slotCooldown, serverUTCTime, slotTypeEnum):
    from gui.impl.gen.view_models.views.lobby.premacc.maps_blacklist_slot_model import MapStateEnum
    slotModel.setType(slotTypeEnum)
    if isSlotDisabledByKillSwitch(slot):
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED_BY_KILL_SWITCH)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        return True
    elif _isRewardSlotExpired(slot, serverUTCTime) or not isSlotAvailableForUI(slot):
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_DISABLED)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        return True
    else:
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_ACTIVE)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        if not slot.mapID:
            return True
        mapName = getMapGeometryName(slot.mapID)
        if mapName is None:
            return False
        slotModel.setMapId(mapName)
        slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_CHANGE)
        slotModel.setCooldownTime(0)
        if slotCooldown > serverUTCTime - slot.modified:
            slotModel.setState(MapStateEnum.MAPS_BLACKLIST_SLOT_STATE_COOLDOWN)
            slotModel.setCooldownTime(_getSlotCooldownEndTimestamp(slot, slotCooldown, serverUTCTime))
        return True


def populateDashboardMapModel(slotModel, slot, slotCooldown, serverUTCTime, slotTypeEnum):
    from gui.impl.gen.view_models.views.lobby.account_dashboard.map_model import SlotStateEnum
    slotModel.setType(slotTypeEnum)
    if isSlotDisabledByKillSwitch(slot):
        slotModel.setSlotState(SlotStateEnum.DISABLEDBYKILLSWITCH)
        slotModel.setCooldownEndTimeInSecs(0)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        return True
    elif _isRewardSlotExpired(slot, serverUTCTime) or not isSlotAvailableForUI(slot):
        slotModel.setSlotState(SlotStateEnum.DISABLED)
        slotModel.setCooldownEndTimeInSecs(0)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        return True
    else:
        slotModel.setSlotState(SlotStateEnum.EMPTY)
        _applyRewardSlotExpirationTime(slotModel, slot, serverUTCTime)
        if not slot.mapID:
            slotModel.setCooldownEndTimeInSecs(0)
            return True
        mapName = getMapGeometryName(slot.mapID)
        if mapName is None:
            return False
        slotModel.setMapId(mapName)
        slotModel.setSlotState(SlotStateEnum.SELECTED)
        slotModel.setCooldownEndTimeInSecs(0)
        if slotCooldown > serverUTCTime - slot.modified:
            slotModel.setCooldownEndTimeInSecs(_getSlotCooldownEndTimestamp(slot, slotCooldown, serverUTCTime))
        return True
