# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/pve_base/__init__.py
import typing
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.view.battle.shared.page import BattlePageBusinessHandler
from gui.Scaleform.framework import GroupedViewSettings, ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
if typing.TYPE_CHECKING:
    from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
    from gui.Scaleform.daapi.view.battle.pve_base.page import PveBaseBattlePage
    from gui.Scaleform.framework.package_layout import PackageBusinessHandler

class OverridableViewSettingsMapping(object):
    __slots__ = ('_settingsMap',)

    def __init__(self, settings):
        super(OverridableViewSettingsMapping, self).__init__()
        self._settingsMap = {s.alias:s for s in settings}

    def getSettings(self):
        return self._settingsMap.values()

    def extend(self, settings=None):
        if not settings:
            return
        for s in settings:
            self._settingsMap[s.alias] = s


class OverridableContextMenuHandlers(object):
    __slots__ = ('_handlers',)

    def __init__(self, handlers=None):
        self._handlers = {key:handler for key, handler in handlers} if handlers else {}

    def extend(self, handlers=None):
        if not handlers:
            return
        for key, handler in handlers:
            self._handlers[key] = handler

    def getHandlers(self):
        return self._handlers.items()


def getDefaultViewSettings(battlePageAlias, battlePageClass, swfUrl='pveBaseBattlePage.swf'):
    from gui.Scaleform.daapi.view.battle.pve_base.progress_counter.progress_counter import PveProgressCounter
    from gui.Scaleform.daapi.view.battle.pve_base.stats_exchange import PveStatisticsDataController
    from gui.Scaleform.daapi.view.battle.pve_base.primary_objective.primary_objective import PvePrimaryObjective
    from gui.Scaleform.daapi.view.battle.pve_base.secondary_objectives.secondary_objectives import PveSecondaryObjectives
    from gui.Scaleform.daapi.view.battle.pve_base.pve_player_lives import PvePlayerLives
    from gui.Scaleform.daapi.view.battle.pve_base import minimap
    from gui.Scaleform.daapi.view.battle.pve_base import fullmap
    from gui.Scaleform.daapi.view.battle.pve_base import postmortem_panel
    from gui.Scaleform.daapi.view.battle.pve_base import players_panel
    from gui.Scaleform.daapi.view.battle.pve_base.pve_prebattle_timer import PvePrebattleTimer
    from gui.Scaleform.daapi.view.battle.pve_base.hint_panel import PveBattleHintPanel
    from gui.Scaleform.daapi.view.battle.pve_base.status_notifications import panel as sn_panel
    from gui.Scaleform.daapi.view.battle.pve_base.damage_log_panel import PveDamageLogPanel
    from gui.Scaleform.daapi.view.battle.pve_base.ribbons_panel import PveRibbonsPanel
    return OverridableViewSettingsMapping((ViewSettings(battlePageAlias, battlePageClass, swfUrl, WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PROGRESS_COUNTER, PveProgressCounter, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_STATISTIC_DATA_CONTROLLER, PveStatisticsDataController, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PRIMARY_OBJECTIVE, PvePrimaryObjective, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_SECONDARY_OBJECTIVES, PveSecondaryObjectives, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PVE_PLAYER_LIVES, PvePlayerLives, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.MINIMAP, minimap.PveMinimapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.FULLSCREEN_MAP, fullmap.PveFullMapComponent, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.HINT_PANEL, PveBattleHintPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, PvePrebattleTimer, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.POSTMORTEM_PANEL, postmortem_panel.PvePostmortemPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PLAYERS_PANEL, players_panel.PvePlayersPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.STATUS_NOTIFICATIONS_PANEL, sn_panel.PveStatusNotificationTimerPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_DAMAGE_LOG_PANEL, PveDamageLogPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RIBBONS_PANEL, PveRibbonsPanel, ScopeTemplates.DEFAULT_SCOPE)))


def getDefaultContextMenuHandler():
    return OverridableContextMenuHandlers()


def getDefaultBusinessHandlers(battlePageAlias):
    from gui.Scaleform.daapi.view.battle import shared
    return (BattlePageBusinessHandler(battlePageAlias),) + shared.getBusinessHandlers()
