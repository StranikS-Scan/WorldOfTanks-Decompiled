# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/header/__init__.py
from __future__ import absolute_import
from frameworks.wulf import WindowLayer
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import GroupedViewSettings, ScopeTemplates

def getContextMenuHandlers():
    pass


def getViewSettings():
    from comp7.gui.Scaleform.daapi.view.lobby.header.battle_type_select_popover import Comp7BattleTypeSelectPopover
    return (GroupedViewSettings(VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, Comp7BattleTypeSelectPopover, 'itemSelectorPopover.swf', WindowLayer.WINDOW, VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, VIEW_ALIAS.BATTLE_TYPE_SELECT_POPOVER, ScopeTemplates.DEFAULT_SCOPE),)


def getBusinessHandlers():
    pass
