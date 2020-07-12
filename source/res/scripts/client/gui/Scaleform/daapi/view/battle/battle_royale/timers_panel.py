# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/timers_panel.py
import weakref
import BigWorld
from constants import LootAction, LOOT_TYPE, VEHICLE_MISC_STATUS
from gui.Scaleform.daapi.view.battle.shared.destroy_times_mapping import getTimerViewTypeID, _TIMER_STATES
from gui.Scaleform.daapi.view.battle.shared.timers_panel import TimersPanel, _RegularStackTimersCollection
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_LINKAGES import BATTLE_NOTIFICATIONS_TIMER_LINKAGES
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_COLORS import BATTLE_NOTIFICATIONS_TIMER_COLORS
from gui.Scaleform.locale.BATTLE_ROYALE import BATTLE_ROYALE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R
_WARNING_TEXT_TIMER = 3
_LEAVE_ZONE_DEFENDER_DELAY = 10
_MAX_DISPLAYED_SECONDARY_STATUS_TIMERS = 4

class _BattleRoyaleStackTimersCollection(_RegularStackTimersCollection):

    def __init__(self, *args, **kwargs):
        super(_BattleRoyaleStackTimersCollection, self).__init__(*args, **kwargs)
        self._maxDisplayedSecondaryTimers = _MAX_DISPLAYED_SECONDARY_STATUS_TIMERS


class BattleRoyaleTimersPanel(TimersPanel):
    __slots__ = ('__loots', '_timers')

    def __init__(self):
        super(BattleRoyaleTimersPanel, self).__init__()
        self.__loots = {}
        self._timers = _BattleRoyaleStackTimersCollection(weakref.proxy(self))

    def _generateMainTimersData(self):
        data = super(BattleRoyaleTimersPanel, self)._generateMainTimersData()
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HALF_OVERTURNED_ICON, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_DESTROY_TIMER_UI, iconOffsetY=-10))
        return data

    def _generateSecondaryTimersData(self):
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.SECONDARY_TIMER_UI
        data = super(BattleRoyaleTimersPanel, self)._generateSecondaryTimersData()
        data.append(self._getNotificationTimerData(_TIMER_STATES.HEALING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_POINT_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, True, BATTLE_ROYALE.EQUIPMENT_HEALPOINT_HEALED))
        data.append(self._getNotificationTimerData(_TIMER_STATES.HEALING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.HEAL_POINT_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_HEALPOINT_HEALED))
        data.append(self._getNotificationTimerData(_TIMER_STATES.BERSERKER, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BERSERKER_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_BERSERK_ACTIVE))
        data.append(self._getNotificationTimerData(_TIMER_STATES.REPAIRING, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_REPAIRPOINT))
        data.append(self._getNotificationTimerData(_TIMER_STATES.REPAIRING_CD, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ZONE_ICON, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False, BATTLE_ROYALE.EQUIPMENT_REPAIRPOINT))
        link = BATTLE_NOTIFICATIONS_TIMER_LINKAGES.BATTLE_ROYALE_TIMER_UI
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.RECOVERY_ICON_CONTENT, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.GREEN, False, False))
        data.append(self._getNotificationTimerData(BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE, BATTLE_NOTIFICATIONS_TIMER_LINKAGES.ORANGE_ZONE_ICON_CONTENT, link, BATTLE_NOTIFICATIONS_TIMER_COLORS.ORANGE, False, False, countdownVisible=False, isCanBeMainType=True, priority=40000))
        return data

    def _onVehicleStateUpdated(self, state, value):
        super(BattleRoyaleTimersPanel, self)._onVehicleStateUpdated(state, value)
        if state == VEHICLE_VIEW_STATE.LOOT:
            lootID, _, action, serverTime = value
            if action == LootAction.PICKUP_STARTED:
                self.__showLootTimer(lootID, serverTime)
            else:
                self.__hideLootTimer(lootID)
        elif state == VEHICLE_VIEW_STATE.DOT_EFFECT:
            self.__updateDotEffectTimer(value)

    def _showDestroyTimer(self, value):
        if value.needToCloseAll():
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED)
            for typeID in self._mapping.getDestroyTimersTypesIDs():
                self._hideTimer(typeID)

            self._timers.removeTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.FIRE)
        elif value.needToCloseTimer():
            self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED)
            self._hideTimer(self._mapping.getTimerTypeIDByMiscCode(value.code))
        else:
            typeID = self.__getDestroyTimerTypeIDByCode(value)
            self._showTimer(typeID, value.totalTime, value.level, None, value.startTime)
            if typeID == BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED:
                description = backport.text(R.strings.battle_royale.timersPanel.halfOverturned())
                self.as_setTimerTextS(typeID, '', description)
        return

    def _getInspireSecondaryTimerText(self, isSourceVehicle=False):
        return backport.text(R.strings.battle_royale.timersPanel.inspired())

    def __getDestroyTimerTypeIDByCode(self, value):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.HALF_OVERTURNED if value.code == VEHICLE_MISC_STATUS.VEHICLE_IS_OVERTURNED and getTimerViewTypeID(value.level) == BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW else self._mapping.getTimerTypeIDByMiscCode(value.code)

    def _showDeathZoneTimer(self, value):
        self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE)
        self._hideTimer(BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE)
        if value.needToShow():
            self.__showDeathZoneWithText(value)

    def __showDeathZoneWithText(self, value):
        if getTimerViewTypeID(value.level) == BATTLE_NOTIFICATIONS_TIMER_TYPES.WARNING_VIEW:
            typeId = BATTLE_NOTIFICATIONS_TIMER_TYPES.ORANGE_ZONE
            self._showTimer(typeId, value.totalTime, getTimerViewTypeID(value.level), value.finishTime)
            self.as_setSecondaryTimerTextS(typeId, '', backport.text(R.strings.battle_royale.timersPanel.orangeZone()))
        else:
            typeId = BATTLE_NOTIFICATIONS_TIMER_TYPES.DEATH_ZONE
            self._showTimer(typeId, value.totalTime, value.level, value.finishTime)
            self.as_setTimerTextS(typeId, '', backport.text(R.strings.battle_royale.timersPanel.deathZone()))

    def __showLootTimer(self, lootID, pickupTime):
        loot = BigWorld.entity(lootID)
        if loot is not None:
            if not self.__loots:
                time = BigWorld.serverTime()
                self.as_showSecondaryTimerS(BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY, time, 0, False)
            self.__loots[lootID] = (loot.typeID, BigWorld.serverTime() + pickupTime)
            self.__updateTimer()
        return

    def __hideLootTimer(self, lootID):
        if lootID in self.__loots:
            del self.__loots[lootID]
        if not self.__loots:
            self.as_hideSecondaryTimerS(BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY)

    def __updateTimer(self):
        time = BigWorld.serverTime()
        timeLeft = max((loot_time for _, loot_time in self.__loots.values())) - time
        timeText = backport.text(R.strings.battle_royale.timersPanel.lootPickup(), lootType=self.__getLootType())
        self.as_setSecondaryTimerTextS(BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY, timeText)
        self.as_setSecondaryTimeSnapshotS(BATTLE_NOTIFICATIONS_TIMER_TYPES.RECOVERY, timeLeft, 0)

    def __getLootType(self):
        count = len(self.__loots)
        if count > 1:
            return backport.text(R.strings.battle_royale.loot.multiple(), count=count)
        lootType, _ = self.__loots.values()[0]
        if lootType == LOOT_TYPE.BASIC:
            return backport.text(R.strings.battle_royale.loot.basic())
        if lootType == LOOT_TYPE.ADVANCED:
            return backport.text(R.strings.battle_royale.loot.advanced())
        if lootType == LOOT_TYPE.AIRDROP:
            return backport.text(R.strings.battle_royale.loot.airdrop())
        return backport.text(R.strings.battle_royale.loot.corpse()) if lootType == LOOT_TYPE.CORPSE else ''

    def __updateDotEffectTimer(self, dotInfo):
        if dotInfo is not None:
            totalTime = dotInfo.endTime - BigWorld.serverTime()
            self._showTimer(_TIMER_STATES.BERSERKER, totalTime, _TIMER_STATES.WARNING_VIEW, dotInfo.endTime)
        else:
            self._hideTimer(_TIMER_STATES.BERSERKER)
        return
