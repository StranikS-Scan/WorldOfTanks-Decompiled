# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/Scaleform/daapi/view/battle/cosmic/__init__.py
import logging
from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic.battle_loading import CosmicBattleLoading
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic.cosmic_page import CosmicPage
from gui.Scaleform.framework import ViewSettings, ScopeTemplates, ComponentSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE
_logger = logging.getLogger(__name__)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from cosmic_event.gui.Scaleform.daapi.view.battle.cosmic import cosmic_hud
    return (ViewSettings(VIEW_ALIAS.COSMIC_BATTLE_PAGE, CosmicPage, 'cosmicBattlePage.swf', WindowLayer.VIEW, None, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(BATTLE_VIEW_ALIASES.BATTLE_LOADING, CosmicBattleLoading, ScopeTemplates.DEFAULT_SCOPE), ComponentSettings(BATTLE_VIEW_ALIASES.COSMIC_HUD, cosmic_hud.CosmicHud, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_CosmicPackageBusinessHandler(),)


class _CosmicPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        _logger.debug('_CosmicPackageBusinessHandler.__init__')
        listeners = ((VIEW_ALIAS.COSMIC_BATTLE_PAGE, self.loadViewBySharedEvent),)
        super(_CosmicPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)
