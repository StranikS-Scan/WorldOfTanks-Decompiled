# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/blueprints/__init__.py
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import createTooltipData
from gui.impl.gen.view_models.views.lobby.blueprints.blueprint_screen_tooltips import BlueprintScreenTooltips

def getStateMachineRegistrators():
    from gui.impl.lobby.blueprints.states import registerStates, registerTransitions
    return (registerStates, registerTransitions)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass


def getContextMenuHandlers():
    pass


def getBlueprintTooltipData(ttId, itemCD):
    return createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.BLUEPRINT_FRAGMENT_INFO, specialArgs=[int(itemCD)]) if ttId == BlueprintScreenTooltips.TOOLTIP_BLUEPRINT and itemCD is not None else None
