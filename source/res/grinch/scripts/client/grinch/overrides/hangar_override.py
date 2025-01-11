# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/overrides/hangar_override.py
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.framework.view_overrider import OverrideData
from gui.impl.gen import R
from helpers import dependency
from skeletons.gui.impl import IGuiLoader
from grinch.skeletons.battle_controller import IGrinchController

def showHangar():
    if not isHangarLoaded():
        from grinch_progression.gui.shared.event_dispatcher import showGameBoardView
        showGameBoardView()


def isHangarLoaded():
    return isViewLoaded(R.views.grinch_progression.lobby.GameBoard())


def isViewLoaded(layoutID):
    uiLoader = dependency.instance(IGuiLoader)
    return True if uiLoader.windowsManager.getViewByLayoutID(layoutID) else False


class HangarOverride(OverrideData):
    __grinchCtrl = dependency.descriptor(IGrinchController)

    def __init__(self):
        from grinch_progression.gui.impl.lobby.views.game_board import GameBoardView
        super(HangarOverride, self).__init__(GuiImplViewLoadParams(R.views.grinch_progression.lobby.GameBoard(), GameBoardView, ScopeTemplates.LOBBY_SUB_SCOPE))

    def checkCondition(self, *args, **kwargs):
        return self.__grinchCtrl.isEventPrbActive()
