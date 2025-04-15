# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/Scaleform/daapi/view/battle/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings, getSwfExtensionUrl
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from fall_tanks.gui.Scaleform.genConsts.FALL_TANKS_BATTLE_VIEW_ALIASES import FALL_TANKS_BATTLE_VIEW_ALIASES
from fall_tanks.gui.fall_tanks_gui_constants import VIEW_ALIAS

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import situation_indicators
    from gui.Scaleform.daapi.view.battle.shared import messages
    from gui.Scaleform.daapi.view.battle.shared import postmortem_panel
    from gui.Scaleform.daapi.view.battle.classic import battle_end_warning_panel
    from fall_tanks.gui.Scaleform.daapi.view.battle.page import FallTanksPage
    from fall_tanks.gui.Scaleform.daapi.view.battle import fall_tanks_widget_inject
    from fall_tanks.gui.Scaleform.daapi.view.battle import battle_loading
    from fall_tanks.gui.Scaleform.daapi.view.battle import minimap
    from fall_tanks.gui.Scaleform.daapi.view.battle import battle_timers
    from fall_tanks.gui.Scaleform.daapi.view.battle import consumables_panel
    from fall_tanks.gui.Scaleform.daapi.view.battle import ribbons_panel
    from fall_tanks.gui.Scaleform.daapi.view.battle import hint_panel
    from fall_tanks.gui.Scaleform.daapi.view.battle import timers_panel
    from fall_tanks.gui.Scaleform.daapi.view.battle import damage_panel
    return (ViewSettings(VIEW_ALIAS.FALL_TANKS_BATTLE_PAGE, FallTanksPage, getSwfExtensionUrl('fall_tanks', 'fallTanksBattlePage.swf'), WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(FALL_TANKS_BATTLE_VIEW_ALIASES.FALL_TANKS_BATTLE_WIDGET, fall_tanks_widget_inject.FallTanksBattleWidgetInject, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, battle_loading.FallTanksBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.FallTanksMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.DAMAGE_PANEL, damage_panel.FallTanksDamagePanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.TIMERS_PANEL, timers_panel.FallTanksTimersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.FallTanksBattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, battle_end_warning_panel.BattleEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.CONSUMABLES_PANEL, consumables_panel.FallTanksConsumablesPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.SITUATION_INDICATORS, situation_indicators.SituationIndicators, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, ribbons_panel.FallTanksBattleRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, hint_panel.FallTanksBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYER_MESSAGES, messages.PlayerMessages, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, battle_timers.FallTanksPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (BattlePageBusinessHandler(VIEW_ALIAS.FALL_TANKS_BATTLE_PAGE),)
