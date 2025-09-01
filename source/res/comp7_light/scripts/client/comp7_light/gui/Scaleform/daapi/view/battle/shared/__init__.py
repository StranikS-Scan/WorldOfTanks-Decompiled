# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/Scaleform/daapi/view/battle/shared/__init__.py
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewSettings, ScopeTemplates

def getContextMenuHandlers():
    pass


def getViewSettings():
    from comp7_light.gui.Scaleform.daapi.view.battle.shared.ingame_menu import Comp7LightIngameMenu
    return (ViewSettings(VIEW_ALIAS.INGAME_MENU, Comp7LightIngameMenu, 'ingameMenu.swf', WindowLayer.TOP_WINDOW, None, ScopeTemplates.DEFAULT_SCOPE, isModal=True, canClose=False, canDrag=False),)


def getBusinessHandlers():
    pass
