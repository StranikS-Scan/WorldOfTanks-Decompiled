# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/__init__.py
from __future__ import absolute_import
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics import decorative_crosshairs, mechanic_widgets, panels

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.rechargeable_nitro_widget import RechargeableNitroMechanicWidget
    from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.rocket_accelerator_widget import RocketAcceleratorMechanicIndicator
    return (ComponentSettings(BATTLE_VIEW_ALIASES.WIDGETS_PANEL, panels.MechanicWidgetsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, RocketAcceleratorMechanicIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RECHARGEABLE_NITRO_WIDGET, RechargeableNitroMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONCENTRATION_WIDGET, mechanic_widgets.ConcentrationMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CHARGE_SHOT_WIDGET, mechanic_widgets.ChargeShotMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SUPPORT_WEAPON, mechanic_widgets.SupportWeaponMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PILLBOX_SIEGE_WIDGET, mechanic_widgets.PillboxSiegeMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CHARGEABLE_BURST_WIDGET, mechanic_widgets.ChargeableBurstMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POWER_WIDGET, mechanic_widgets.PowerModeMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STANCE_DANCE_WIDGET_FIGHT, mechanic_widgets.StanceDanceFightMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STANCE_DANCE_WIDGET_TURBO, mechanic_widgets.StanceDanceTurboMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TARGET_DESIGNATOR_WIDGET, mechanic_widgets.TargetDesignatorMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATIONARY_RELOAD_WIDGET, mechanic_widgets.StationaryReloadingMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEMPERATURE_GUN_OVERHEAT_WIDGET, mechanic_widgets.TemperatureOverheatGunWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEMPERATURE_GUN_HEAT_ZONES_WIDGET, mechanic_widgets.TemperatureHeatingZonesGunWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STAGED_JET_BOOSTERS_WIDGET, mechanic_widgets.StagedJetBoostersMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DECORATIVE_CROSSHAIR_PANEL, panels.DecorativeCrosshairPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONCENTRATION_DECORATIVE_CROSSHAIR, decorative_crosshairs.ConcentrationDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ACCURACY_DECORATIVE_CROSSHAIR, decorative_crosshairs.AccuracyDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PILLBOX_SIEGE_DECORATIVE_CROSSHAIR, decorative_crosshairs.PillboxSiegeDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.OVERHEAT_DECORATIVE_CROSSHAIR, decorative_crosshairs.OverheatDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FURY_DECORATIVE_CROSSHAIR, decorative_crosshairs.FuryDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TEMPERATURE_GUN_OVERHEAT_DECORATIVE_CROSSHAIR, decorative_crosshairs.TemperatureGunOverheatDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
