# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/battle/ribbons_panel.py
import BigWorld
from account_helpers.settings_core.settings_constants import BATTLE_EVENTS
from last_stand.gui.scaleform.daapi.view.battle import ribbons_aggregator
from gui.Scaleform.daapi.view.battle.shared.ribbons_aggregator import DAMAGE_SOURCE
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from last_stand.gui.scaleform.genConsts.LS_BATTLE_EFFICIENCY_TYPES import LS_BATTLE_EFFICIENCY_TYPES
from last_stand.gui.ls_vehicle_role_helper import getVehicleRole
from gui.impl import backport
from gui.impl.gen import R
from helpers.CallbackDelayer import CallbackDelayer
_DELAYED_RIBBONS_UPDATE_PERIOD = 0.1

class LSBattleRibbonsPanel(BattleRibbonsPanel):

    def __init__(self):
        super(LSBattleRibbonsPanel, self).__init__()
        self._ribbonsAggregator = ribbons_aggregator.createRibbonsAggregator()
        battleEfficiencyTypes = [ ribbon.TYPE for ribbon in ribbons_aggregator.LSReceiveDamageRibbonsFactory.ATTACK_REASONS.itervalues() ]
        self._ribbonsUserSettings = {BATTLE_EVENTS.RECEIVED_DAMAGE: battleEfficiencyTypes}
        self._callbackDelayer = CallbackDelayer()

    def clear(self):
        self._ribbonsAggregator.clearRibbonsData()
        self.as_resetS()

    @property
    def aggregator(self):
        return self._ribbonsAggregator

    def _populate(self):
        super(LSBattleRibbonsPanel, self)._populate()
        for settingName in self._ribbonsUserSettings:
            self.__setUserSettings(settingName, bool(self.settingsCore.getSetting(settingName)))

        ctrl = self.sessionProvider.shared.vehicleState
        if ctrl is not None:
            ctrl.onPostMortemSwitched += self._onPostMortemSwitched
            ctrl.onRespawnBaseMoving += self._onRespawnBaseMoving
        self._callbackDelayer.delayCallback(_DELAYED_RIBBONS_UPDATE_PERIOD, self._delayedRibbonsUpdate)
        return

    def _dispose(self):
        super(LSBattleRibbonsPanel, self)._dispose()
        self._callbackDelayer.clearCallbacks()
        self._callbackDelayer = None
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

    def _shouldShowRibbon(self, ribbon):
        result = super(LSBattleRibbonsPanel, self)._shouldShowRibbon(ribbon)
        return False if not result else getattr(ribbon, 'shouldShow', True)

    def _getRibbonsConfig(self):
        result = super(LSBattleRibbonsPanel, self)._getRibbonsConfig()
        result.extend([[LS_BATTLE_EFFICIENCY_TYPES.LS_DMG_VAMPIRE, backport.text(R.strings.last_stand_battle.efficiencyRibbons.damageVampire())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_BURN, backport.text(R.strings.last_stand_battle.efficiencyRibbons.aoeBurn())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_DAMAGE, backport.text(R.strings.last_stand_battle.efficiencyRibbons.aoeDamage())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_DAMAGE, backport.text(R.strings.last_stand_battle.efficiencyRibbons.instantShotAoeDamage())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_DRAIN_ENEMY_HP, backport.text(R.strings.last_stand_battle.efficiencyRibbons.instantShotAoeDrainEnemyHp())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_SHOT_AOE_STUN, backport.text(R.strings.last_stand_battle.efficiencyRibbons.instantShotAoeStun())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR, backport.text(R.strings.last_stand_battle.efficiencyRibbons.repair())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR_OTHER, backport.text(R.strings.last_stand_battle.efficiencyRibbons.repairOther())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_REPAIR_BY_OTHER, backport.text(R.strings.last_stand_battle.efficiencyRibbons.repairByOther())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_MODULES_DAMAGE_BLOCKED, backport.text(R.strings.last_stand_battle.efficiencyRibbons.modulesDamageBlocked())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_PASSIVE_IGNITE, backport.text(R.strings.ingame_gui.efficiencyRibbons.burn())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_PASSIVE_VAMPIRE, backport.text(R.strings.last_stand_battle.efficiencyRibbons.passiveVampire())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_BOMBER_EXPLOSION, backport.text(R.strings.last_stand_battle.efficiencyRibbons.bomberExplosion())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_DMG_VAMPIRE_RECEIVED, backport.text(R.strings.last_stand_battle.efficiencyRibbons.damageVampire())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_AOE_DAMAGE_RECEIVED, backport.text(R.strings.last_stand_battle.efficiencyRibbons.aoeDamage())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_NITRO_ACTIVATED, backport.text(R.strings.last_stand_battle.efficiencyRibbons.nitroActivated())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_HEAL_SITUATIONAL, backport.text(R.strings.last_stand_battle.efficiencyRibbons.healSituational())],
         [LS_BATTLE_EFFICIENCY_TYPES.LS_EXTRA_DAMAGE_SITUATIONAL, backport.text(R.strings.last_stand_battle.efficiencyRibbons.extraDamageSituational())]])
        return result

    def _getRibbonFormatter(self, ribbon):
        formatter = super(LSBattleRibbonsPanel, self)._getRibbonFormatter(ribbon)

        def lsSingleVehRibbonFormatter(ribbon, arenaDP, updater):

            def lsUpdater(*args, **kwargs):
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

            formatter(ribbon, arenaDP, lsUpdater)

        return lsSingleVehRibbonFormatter

    def _onSettingsChanged(self, diff):
        super(LSBattleRibbonsPanel, self)._onSettingsChanged(diff)
        for item in diff:
            if item in self._ribbonsUserSettings:
                self.__setUserSettings(item, bool(diff[item]))

    def _canBeShown(self, ribbon):
        base = super(LSBattleRibbonsPanel, self)._canBeShown(ribbon)
        if not base:
            return False
        else:
            delayedTill = getattr(ribbon, 'delayedTill', None)
            return BigWorld.time() >= delayedTill if delayedTill is not None else True

    def _delayedRibbonsUpdate(self):
        self._processDelayedRibbons()
        return _DELAYED_RIBBONS_UPDATE_PERIOD

    def __setUserSettings(self, settingName, value):
        ribbonTypes = self._ribbonsUserSettings.get(settingName, [])
        for rType in ribbonTypes:
            self.userPreferences[rType] = value
