# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/tutorial.py
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.battle.shared.minimap import component
from gui.Scaleform.daapi.view.battle.shared.minimap import common
from gui.Scaleform.daapi.view.battle.shared.minimap import settings
from gui.Scaleform.daapi.view.battle.shared import SharedPage
from gui.Scaleform.daapi.view.meta.BattleTutorialMeta import BattleTutorialMeta
from gui.Scaleform.framework import ViewSettings, ViewTypes, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.Scaleform.genConsts.BATTLE_VIEW_ALIASES import BATTLE_VIEW_ALIASES
from gui.app_loader.settings import APP_NAME_SPACE
from gui.battle_control import minimap_utils
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.shared import EVENT_BUS_SCOPE
_TUTORIAL_COMPONENTS_TO_CTRLS = ((BATTLE_CTRL_ID.ARENA_PERIOD, (BATTLE_VIEW_ALIASES.BATTLE_TIMER, BATTLE_VIEW_ALIASES.PREBATTLE_TIMER)),)

def getContextMenuHandlers():
    pass


def getViewSettings():
    from gui.Scaleform.daapi.view.battle.shared import destroy_timers_panel
    from gui.Scaleform.daapi.view.battle.shared import battle_timers
    return (ViewSettings(VIEW_ALIAS.TUTORIAL_BATTLE_PAGE, TutorialPage, 'tutorialPage.swf', ViewTypes.DEFAULT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TUTORIAL, TutorialComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.DESTROY_TIMERS_PANEL, destroy_timers_panel.DestroyTimersPanel, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.BATTLE_TIMER, battle_timers.BattleTimer, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE),
     ViewSettings(BATTLE_VIEW_ALIASES.MINIMAP, TutorialMinimapComponent, None, ViewTypes.COMPONENT, None, ScopeTemplates.DEFAULT_SCOPE))


def getBusinessHandlers():
    return (_TutorialPackageBusinessHandler(),)


class _TutorialPackageBusinessHandler(PackageBusinessHandler):
    __slots__ = ()

    def __init__(self):
        listeners = ((VIEW_ALIAS.TUTORIAL_BATTLE_PAGE, self.loadViewBySharedEvent),)
        super(_TutorialPackageBusinessHandler, self).__init__(listeners, APP_NAME_SPACE.SF_BATTLE, EVENT_BUS_SCOPE.BATTLE)


class TutorialComponent(BattleTutorialMeta):

    def _populate(self):
        super(TutorialComponent, self)._populate()

    def _dispose(self):
        super(TutorialComponent, self)._dispose()


class TutorialPage(SharedPage):

    def __init__(self):
        super(TutorialPage, self).__init__(components=_TUTORIAL_COMPONENTS_TO_CTRLS)

    def _handleToggleFullStats(self, event):
        pass

    def _handleGUIToggled(self, event):
        pass

    def _handleRadialMenuCmd(self, event):
        pass


class TutorialMinimapComponent(component.MinimapComponent):

    def _setupPlugins(self, arenaVisitor):
        setup = super(TutorialMinimapComponent, self)._setupPlugins(arenaVisitor)
        setup['tutorial'] = TutorialTargetPlugin
        return setup


class TutorialTargetPlugin(common.EntriesPlugin):

    def addTarget(self, markerID, position):
        matrix = minimap_utils.makePositionMatrix(position)
        model = self._addEntryEx(markerID, settings.ENTRY_SYMBOL_NAME.TUTORIAL_TARGET, settings.CONTAINER_NAME.ICONS, matrix=matrix, active=True)
        return model is not None

    def delTarget(self, markerID):
        return self._delEntryEx(markerID)
