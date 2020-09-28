# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/event/status_notifications/sn_items.py
import BigWorld
from constants import LootAction, LOOT_TYPE
from gui.Scaleform.daapi.view.battle.battle_royale.status_notifications.sn_items import TimerSN
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from gui.impl import backport
from gui.impl.gen import R

class EventLootPickUpSN(TimerSN):

    def __init__(self, updateCallback):
        super(EventLootPickUpSN, self).__init__(updateCallback)
        self.__loots = {}

    def destroy(self):
        self.__loots = None
        super(EventLootPickUpSN, self).destroy()
        return

    def getItemID(self):
        return VEHICLE_VIEW_STATE.LOOT

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.LOOT_PICKUP

    def _update(self, value):
        lootID, lootType, action, serverTime = value
        if action == LootAction.PICKUP_STARTED:
            self.__showLootTimer(lootID, lootType, serverTime)
        else:
            self.__hideLootTimer(lootID)

    def __showLootTimer(self, lootID, lootTypeID, pickupTime):
        time = BigWorld.serverTime()
        if not self.__loots:
            self._isVisible = True
        self.__loots[lootID] = (lootTypeID, time + pickupTime)
        timeLeft = max((loot_time for _, loot_time in self.__loots.values()))
        timeLeft -= time
        self.__updateText()
        self._updateTimeParams(timeLeft, 0)
        self._sendUpdate()

    def __hideLootTimer(self, lootID):
        if lootID in self.__loots:
            del self.__loots[lootID]
            self.__updateText()
            self._sendUpdate()
        if not self.__loots:
            self._setVisible(False)

    def __updateText(self):
        self._vo['title'] = self.__getLootType()

    def __getLootType(self):
        count = len(self.__loots)
        if count > 1:
            return backport.text(R.strings.battle_royale.loot.multiple(), count=count)
        if count > 0:
            lootType, _ = self.__loots.values()[0]
            if lootType == LOOT_TYPE.BASIC:
                return backport.text(R.strings.battle_royale.loot.basic())
            if lootType == LOOT_TYPE.ADVANCED:
                return backport.text(R.strings.battle_royale.loot.advanced())
            if lootType == LOOT_TYPE.AIRDROP:
                return backport.text(R.strings.battle_royale.loot.airdrop())
            if lootType == LOOT_TYPE.CORPSE:
                return backport.text(R.strings.battle_royale.loot.corpse())
            if lootType == LOOT_TYPE.GROUPDROP:
                return backport.text(R.strings.wt_event.loot.groupdrop())


class EventStunSN(TimerSN):

    def __init__(self, updateCallback):
        super(EventStunSN, self).__init__(updateCallback)
        self._vo['title'] = backport.text(R.strings.wt_event.event_stun.indicator())
        self._subscribeOnVehControlling()

    def getItemID(self):
        return VEHICLE_VIEW_STATE.STUN

    def getViewTypeID(self):
        return BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN

    def _update(self, value):
        if value.duration > 0.0:
            self._updateTimeParams(value.totalTime, value.endTime)
            self._isVisible = True
            self._sendUpdate()
        else:
            self._setVisible(False)
