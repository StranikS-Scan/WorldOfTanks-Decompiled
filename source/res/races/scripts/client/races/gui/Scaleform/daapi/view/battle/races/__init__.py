# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/Scaleform/daapi/view/battle/races/__init__.py
import logging
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from races.gui.Scaleform.daapi.view.battle.races.races_page import RacesPage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
from races.gui.Scaleform.daapi.view.battle.races.races_battle_loading import RacesBattleLoading
from races.gui.Scaleform.daapi.view.battle.races.races_prebattle_timer import RacesPreBattleTimer
from races.gui.Scaleform.daapi.view.battle.races.races_end_warning_panel import RacesEndWarningPanel
_logger = logging.getLogger(__name__)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from races.gui.Scaleform.daapi.view.battle.races import races_hud
    return (ViewSettings(VIEW_ALIAS.RACES_BATTLE_PAGE, RacesPage, 'racesBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, RacesBattleLoading, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.RACES_HUD, races_hud.RacesHud, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_END_WARNING_PANEL, RacesEndWarningPanel, ScopeTemplates.DEFAULT_SCOPE),
     ComponentSettings(BATTLE_VIEW_ALIASES.PREBATTLE_TIMER, RacesPreBattleTimer, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_RacesPackageBusinessHandler(),)


class _RacesPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        _logger.debug('_RacesPackageBusinessHandler.__init__')
        listeners = ((VIEW_ALIAS.RACES_BATTLE_PAGE, self.loadViewBySharedEvent),)
        super(_RacesPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
