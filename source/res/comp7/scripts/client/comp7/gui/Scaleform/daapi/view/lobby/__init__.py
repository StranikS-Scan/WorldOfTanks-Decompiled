# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/Scaleform/daapi/view/lobby/__init__.py
from gui.Scaleform.framework import ComponentSettings, ScopeTemplates
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.impl.gen import R
from gui.shared.system_factory import registerBattleModifiersPanel

def getContextMenuHandlers():
    pass


def getViewSettings():
    from comp7.gui.Scaleform.daapi.view.lobby.hangar.comp7_modifiers_panel import Comp7ModifiersPanel
    registerBattleModifiersPanel(R.views.lobby.comp7.SeasonModifier(), Comp7ModifiersPanel)


def getBusinessHandlers():
    pass
