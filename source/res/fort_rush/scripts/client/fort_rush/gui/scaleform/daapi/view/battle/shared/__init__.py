# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/scaleform/daapi/view/battle/shared/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates

def getContextMenuHandlers():
    pass


def getViewSettings():
    from fort_rush.gui.scaleform.daapi.view.battle.shared.fort_rush_ingame_menu import FortRushIngameMenu
    return (ViewSettings(VIEW_ALIAS.INGAME_MENU, FortRushIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),)


def getBusinessHandlers():
    pass
