# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/Scaleform/daapi/view/battle/ribbons_panel.py
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.BATTLE_EFFICIENCY_TYPES import BATTLE_EFFICIENCY_TYPES
from gui.Scaleform.daapi.view.battle.shared.ribbons_panel import BattleRibbonsPanel
from grinch.gui.Scaleform.daapi.view.battle import ribbons_aggregator
from grinch.gui.Scaleform.genConsts.GRINCH_BATTLE_EFFICIENCY_TYPES import GRINCH_BATTLE_EFFICIENCY_TYPES

class GrinchRibbonsPanel(BattleRibbonsPanel):
    _SHOW_GRICH_RIBBON_BLEED_SOUND_NOTIFICATION = 'grinch_show_ribbon_bleed'
    _SHOW_GRICH_RIBBON_HEAL_SOUND_NOTIFICATION = 'grinch_show_ribbon_heal'
    _SHOW_GRICH_RIBBON_SNOWSTORM_SOUND_NOTIFICATION = 'grinch_show_ribbon_snowstorm_damage'
    _SOUND_NOTIFICATIONS = {GRINCH_BATTLE_EFFICIENCY_TYPES.RAGE: _SHOW_GRICH_RIBBON_BLEED_SOUND_NOTIFICATION,
     BATTLE_EFFICIENCY_TYPES.VEHICLE_HEALTH_ADDED: _SHOW_GRICH_RIBBON_HEAL_SOUND_NOTIFICATION,
     GRINCH_BATTLE_EFFICIENCY_TYPES.DAMAGED_BY_SNOWSTORM: _SHOW_GRICH_RIBBON_SNOWSTORM_SOUND_NOTIFICATION}

    def __init__(self):
        super(GrinchRibbonsPanel, self).__init__(ribbonsAggregator=ribbons_aggregator.createRibbonsAggregator())

    def _getRibbonsConfig(self):
        config = super(GrinchRibbonsPanel, self)._getRibbonsConfig()
        config.extend([[GRINCH_BATTLE_EFFICIENCY_TYPES.TURRET_DEALT_DAMAGE, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.turretDealtDamage())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.BASE_DEFENDER_BONUS, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.baseDefenderBonus())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_FLARE, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.abilityAssistFlare())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_BUFF, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.abilityAssistBuff())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.ABILITY_ASSIST_BLIZZARD, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.abilityAssistBlizzard())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.PRESENTS_DELIVERY, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.presentsDelivery())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.TURRET_DESTROYED, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.turretDestroyed())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.BLIZZARD_CAUSED_DAMAGE, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.blizzardCausedDamage())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.DAMAGED_BY_BLIZZARD, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.damagedByBlizzard())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.DAMAGED_BY_SNOWSTORM, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.damagedBySnowstorm())],
         [GRINCH_BATTLE_EFFICIENCY_TYPES.RAGE, backport.text(R.strings.grinch.ribbon.efficiencyRibbons.rageDamage())]])
        return config

    def onShow(self, ribbonID):
        super(GrinchRibbonsPanel, self).onShow(ribbonID)
        self.__playNotification(ribbonID)

    def onChange(self, ribbonID):
        super(GrinchRibbonsPanel, self).onChange(ribbonID)
        self.__playNotification(ribbonID)

    def __playNotification(self, ribbonID):
        ribbon = self._ribbonsAggregator.getRibbon(ribbonID)
        notification = self._SOUND_NOTIFICATIONS.get(ribbon.getType())
        if notification:
            self._playSound(notification)
