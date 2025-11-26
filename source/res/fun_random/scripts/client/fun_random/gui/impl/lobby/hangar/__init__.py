# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.app_loader import settings as app_settings
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from gui.Scaleform.framework import ScopeTemplates, ViewSettings
from gui.Scaleform.framework.package_layout import PackageBusinessHandler
from gui.shared import EVENT_BUS_SCOPE

def getStateMachineRegistrators():
    from fun_random.gui.impl.lobby.hangar.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getContextMenuHandlers():
    pass


def getViewSettings():
    from fun_random.gui.impl.lobby.hangar.fun_random_hangar import FunRandomHangarWindow
    return (ViewSettings(FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR, FunRandomHangarWindow, '', WindowLayer.SUB_VIEW, FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR, ScopeTemplates.LOBBY_SUB_SCOPE),)


def getBusinessHandlers():
    return (FunRandomHangarPackageBusinessHandler(),)


class FunRandomHangarPackageBusinessHandler(PackageBusinessHandler):

    def __init__(self):
        listeners = ((FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR, self.loadViewByCtxEvent),)
        super(FunRandomHangarPackageBusinessHandler, self).__init__(listeners, app_settings.APP_NAME_SPACE.SF_LOBBY, EVENT_BUS_SCOPE.LOBBY)
