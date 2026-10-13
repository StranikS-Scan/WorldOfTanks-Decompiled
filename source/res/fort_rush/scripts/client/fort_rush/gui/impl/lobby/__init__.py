# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/lobby/__init__.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.battle_results_view import FortRushPostBattleResultsWindow
from fort_rush.gui.scaleform.genConsts.FORT_RUSH_HANGAR_ALIASES import FORT_RUSH_HANGAR_ALIASES
from frameworks.wulf import WindowLayer
from gui.Scaleform.framework import ViewSettings, ScopeTemplates
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.app_loader import settings as app_settings
from gui.shared import EVENT_BUS_SCOPE

def getStateMachineRegistrators():
    from fort_rush.gui.impl.lobby.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    from fort_rush.gui.impl.lobby.hangar_view import FortRushHangarWindow
    return (ViewSettings(FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_HANGAR_WITH_AMMUNITION, FortRushHangarWindow, '', WindowLayer.SUB_VIEW, FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_HANGAR_WITH_AMMUNITION, ScopeTemplates.LOBBY_SUB_SCOPE), ViewSettings(FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_BATTLE_RESULTS, FortRushPostBattleResultsWindow, '', WindowLayer.SUB_VIEW, FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_BATTLE_RESULTS, ScopeTemplates.LOBBY_SUB_SCOPE))


def getBusinessHandlers():
    return (FortRushPackageBusinessHandler(),)


class FortRushPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_HANGAR_WITH_AMMUNITION, self.loadViewByCtxEvent), (FORT_RUSH_HANGAR_ALIASES.FORT_RUSH_BATTLE_RESULTS, self.loadView))
        super(FortRushPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)


def getContextMenuHandlers():
    pass
