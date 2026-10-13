# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/battle/ribbons_panel.py
from __future__ import absolute_import
import Event
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS
from halloween.gui.scaleform.daapi.view.battle import ribbons_aggregator
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import DAMAGE_SOURCE
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from halloween.gui.scaleform.genConsts.HW_BATTLE_EFFICIENCY_TYPES import HW_BATTLE_EFFICIENCY_TYPES
from halloween.gui.hw_vehicle_role_helper import getVehicleRole
from gui.impl import backport
from gui.impl.gen import R

class HWBattleRibbonsPanel(BattleRibbonsPanel):
    onRibbonHidden = Event.Event()

    def __init__(self):
        super(HWBattleRibbonsPanel, self).__init__()
        self._ribbonsAggregator = ribbons_aggregator.createRibbonsAggregator()
        battleEfficiencyTypes = [ ribbon.TYPE for ribbon in ribbons_aggregator.HWReceiveDamageRibbonsFactory.ATTACK_REASONS.values() ]
        self._ribbonsUserSettings = {BATTLE_EVENTS.RECEIVED_DAMAGE: battleEfficiencyTypes}

    def clear(self):
        self._ribbonsAggregator.clearRibbonsData()
        self.as_resetS()

    @property
    def aggregator(self):
        return self._ribbonsAggregator

    def onHide(self, ribbonId):
        self.onRibbonHidden(self._ribbonsAggregator.getRibbon(ribbonId))
        super(HWBattleRibbonsPanel, self).onHide(ribbonId)

    def _populate(self):
        super(HWBattleRibbonsPanel, self)._populate()
        for settingName in self._ribbonsUserSettings:
            self.__setUserSettings(settingName, bool(self.settingsCore.getSetting(settingName)))

        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self._onRespawnBaseMoving
        return

    def _dispose(self):
        super(HWBattleRibbonsPanel, self)._dispose()
        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched -= self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving -= self._onRespawnBaseMoving
        return

    def _onPostMortemSwitched(self, noRespawnPossible, respawnAvailable):
        self.aggregator.suspend()
        self.clear()

    def _onRespawnBaseMoving(self):
        self.aggregator.resume()

    def _getRibbonsConfig(self):
        result = super(HWBattleRibbonsPanel, self)._getRibbonsConfig()
        result.extend([[HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DMG_VAMPIRE, backport.text(R.strings.halloween_battle.efficiencyRibbons.damageVampire())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_BURN, backport.text(R.strings.halloween_battle.efficiencyRibbons.aoeBurn())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_DAMAGE, backport.text(R.strings.halloween_battle.efficiencyRibbons.aoeDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_DAMAGE, backport.text(R.strings.halloween_battle.efficiencyRibbons.instantShotAoeDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_DRAIN_ENEMY_HP, backport.text(R.strings.halloween_battle.efficiencyRibbons.instantShotAoeDrainEnemyHp())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHOT_AOE_STUN, backport.text(R.strings.halloween_battle.efficiencyRibbons.instantShotAoeStun())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR, backport.text(R.strings.halloween_battle.efficiencyRibbons.repair())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR_OTHER, backport.text(R.strings.halloween_battle.efficiencyRibbons.repairOther())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_REPAIR_BY_OTHER, backport.text(R.strings.halloween_battle.efficiencyRibbons.repairByOther())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_MODULES_DAMAGE_BLOCKED, backport.text(R.strings.halloween_battle.efficiencyRibbons.modulesDamageBlocked())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_PASSIVE_IGNITE, backport.text(R.strings.ingame_gui.efficiencyRibbons.burn())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_PASSIVE_VAMPIRE, backport.text(R.strings.halloween_battle.efficiencyRibbons.passiveVampire())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_BOSS_BURN, backport.text(R.strings.halloween_battle.efficiencyRibbons.bossAuraDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_BOMBER_EXPLOSION, backport.text(R.strings.halloween_battle.efficiencyRibbons.bomberExplosion())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHELLS_PICKUP, backport.text(R.strings.halloween_battle.efficiencyRibbons.shellsPickup())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SHELLS_RECEIVE, backport.text(R.strings.halloween_battle.efficiencyRibbons.shellsReceived())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DMG_VAMPIRE_RECEIVED, backport.text(R.strings.halloween_battle.efficiencyRibbons.damageVampire())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_AOE_DAMAGE_RECEIVED, backport.text(R.strings.halloween_battle.efficiencyRibbons.aoeDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_IGNITE_DAMAGE_RECEIVED, backport.text(R.strings.ingame_gui.efficiencyRibbons.deathZone())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_STUN_DAMAGE_RECEIVED, backport.text(R.strings.ingame_gui.efficiencyRibbons.deathZone())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_DAMAGE_OVERTIME_RECEIVED, backport.text(R.strings.ingame_gui.efficiencyRibbons.deathZone())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_CORROSION_DAMAGE, backport.text(R.strings.halloween_battle.efficiencyRibbons.corrosionDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_STOMPING_DAMAGE, backport.text(R.strings.halloween_battle.efficiencyRibbons.stompingDamage())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_HANGAR_ITEMS_PICKUP, backport.text(R.strings.halloween_battle.efficiencyRibbons.secretReward())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_HANGAR_ITEMS_RECEIVE, backport.text(R.strings.halloween_battle.efficiencyRibbons.secretRewardReceive())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_PICKUP, backport.text(R.strings.halloween_battle.efficiencyRibbons.soulsPickup())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_RECEIVE, backport.text(R.strings.halloween_battle.efficiencyRibbons.soulsReceive())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_DRAINED, backport.text(R.strings.halloween_battle.efficiencyRibbons.soulsDrained())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_SOULS_REFUND, backport.text(R.strings.halloween_battle.efficiencyRibbons.soulsRefund())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_ANOMALY_PICKUP, backport.text(R.strings.halloween_battle.efficiencyRibbons.anomalyPickup())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_ANOMALY_RECEIVE, backport.text(R.strings.halloween_battle.efficiencyRibbons.anomalyReceive())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_BOMBER_RESIST, backport.text(R.strings.halloween_battle.efficiencyRibbons.buffBomberResist())],
         [HW_BATTLE_EFFICIENCY_TYPES.HALLOWEEN_INSTANT_KILL, backport.text(R.strings.halloween_battle.efficiencyRibbons.buffInstakill())]])
        return result

    def _getRibbonFormatter(self, ribbon):
        formatter = super(HWBattleRibbonsPanel, self)._getRibbonFormatter(ribbon)

        def hwSingleVehRibbonFormatter(ribbon, arenaDP, updater):

            def hwUpdater(*args, **kwargs):
                vehicleId = None
                if kwargs.get('vehType', DAMAGE_SOURCE.HIDE) != DAMAGE_SOURCE.HIDE:
                    if hasattr(ribbon, 'getVehicleID'):
                        vehicleId = ribbon.getVehicleID()
                    elif hasattr(ribbon, 'getVehIDs'):
                        vehicleId = ribbon.getVehIDs()[0]
                if vehicleId is not None:
                    vInfo = arenaDP.getVehicleInfo(vehicleId)
                    vehicleType = vInfo.vehicleType
                    role = getVehicleRole(vehicleType)
                    if role is not None:
                        kwargs['vehType'] = role
                    if vInfo.isEnemy():
                        kwargs['vehName'] = vInfo.getDisplayedName()
                updater(*args, **kwargs)
                return

            formatter(ribbon, arenaDP, hwUpdater)

        return hwSingleVehRibbonFormatter

    def _onSettingsChanged(self, diff):
        super(HWBattleRibbonsPanel, self)._onSettingsChanged(diff)
        for item in diff:
            if item in self._ribbonsUserSettings:
                self.__setUserSettings(item, bool(diff[item]))

    def __setUserSettings(self, settingName, value):
        ribbonTypes = self._ribbonsUserSettings.get(settingName, [])
        for rType in ribbonTypes:
            self.userPreferences[rType] = value
