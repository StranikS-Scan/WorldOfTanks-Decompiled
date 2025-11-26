# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/__init__.py
from gui.Scaleform.framework import ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.charge_shot_widget import ChargeShotMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.concentration_crosshair import ConcentrationDecorativeCrosshair
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.accuracy_crosshair import AccuracyDecorativeCrosshair
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.pillbox_siege_crosshair import PillboxSiegeDecorativeCrosshair
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.concentration_widget import ConcentrationMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.chargeable_burst_widget import ChargeableBurstMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.power_mode_widget import PowerModeMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.support_weapon_widget import SupportWeaponMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.pillbox_siege_widget import PillboxSiegeMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.stationary_reloading_widget import StationaryReloadingMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels.mechanic_widgets_panel import MechanicWidgetsPanel
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.panels.decorative_crosshairs_panel import DecorativeCrosshairPanel
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.overheat_crosshair import OverheatDecorativeCrosshair
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.fury_crosshair import FuryDecorativeCrosshair
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.target_designator_widget import TargetDesignatorMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.stance_dance_turbo_widget import StanceDanceTurboMechanicWidget
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.stance_dance_fight_widget import StanceDanceFightMechanicWidget
__all__ = ('MechanicWidgetsPanel', 'ConcentrationMechanicWidget', 'ChargeShotMechanicWidget', 'ChargeableBurstMechanicWidget', 'PowerModeMechanicWidget', 'SupportWeaponMechanicWidget', 'PillboxSiegeMechanicWidget', 'StationaryReloadingMechanicWidget', 'DecorativeCrosshairPanel', 'ConcentrationDecorativeCrosshair', 'AccuracyDecorativeCrosshair', 'PillboxSiegeDecorativeCrosshair', 'OverheatDecorativeCrosshair', 'FuryDecorativeCrosshair', 'TargetDesignatorMechanicWidget', 'StanceDanceFightMechanicWidget', 'StanceDanceTurboMechanicWidget')

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.rechargeable_nitro_widget import RechargeableNitroMechanicWidget
    from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.rocket_accelerator_widget import RocketAcceleratorMechanicIndicator
    return (ComponentSettings(BATTLE_VIEW_ALIASES.WIDGETS_PANEL, MechanicWidgetsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ROCKET_ACCELERATOR_INDICATOR, RocketAcceleratorMechanicIndicator, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RECHARGEABLE_NITRO_WIDGET, RechargeableNitroMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONCENTRATION_WIDGET, ConcentrationMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CHARGE_SHOT_WIDGET, ChargeShotMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SUPPORT_WEAPON, SupportWeaponMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PILLBOX_SIEGE_WIDGET, PillboxSiegeMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CHARGEABLE_BURST_WIDGET, ChargeableBurstMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POWER_WIDGET, PowerModeMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STANCE_DANCE_WIDGET_FIGHT, StanceDanceFightMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STANCE_DANCE_WIDGET_TURBO, StanceDanceTurboMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TARGET_DESIGNATOR_WIDGET, TargetDesignatorMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATIONARY_RELOAD_WIDGET, StationaryReloadingMechanicWidget, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DECORATIVE_CROSSHAIR_PANEL, DecorativeCrosshairPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONCENTRATION_DECORATIVE_CROSSHAIR, ConcentrationDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.ACCURACY_DECORATIVE_CROSSHAIR, AccuracyDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PILLBOX_SIEGE_DECORATIVE_CROSSHAIR, PillboxSiegeDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.OVERHEAT_DECORATIVE_CROSSHAIR, OverheatDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FURY_DECORATIVE_CROSSHAIR, FuryDecorativeCrosshair, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    pass
