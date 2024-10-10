# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/techtree/tech_tree_tooltips.py
from functools import wraps
import nations
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl import backport
from gui.impl.auxiliary.tooltips.simple_tooltip import createSimpleTooltip
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.techtree.vehicle_tech_tree_model import VehicleTechTreeModel
from helpers import dependency
from skeletons.gui.game_control import IEarlyAccessController
from skeletons.gui.techtree_events import ITechTreeEventsListener

def nationTechTreeTooltipDecorator(method):

    @wraps(method)
    def wrapper(self, event, *args, **kwargs):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent() and event.getArgument('tooltipId') == VehicleTechTreeModel.TECHTREE_NATION_TOOLTIP:
            nation = event.getArgument('nation')
            if isEventNation(nations.INDICES[nation]):
                tooltipData = createTooltipData(isSpecial=True, specialArgs=(nation,), specialAlias=TOOLTIPS_CONSTANTS.TECHTREE_NATION_EVENT)
                window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
                if window is None:
                    return
                window.load()
                return window
            return createSimpleTooltip(self.getParentWindow(), event, backport.text(R.strings.techtree.vehicle_tree.nationTooltip.dyn(nation)()))
        else:
            return method(self, event, *args, **kwargs)

    return wrapper


@dependency.replace_none_kwargs(earlyAccessController=IEarlyAccessController, techTreeEventsListener=ITechTreeEventsListener)
def isEventNation(nationID, earlyAccessController=None, techTreeEventsListener=None):
    hasEarlyAccess = earlyAccessController.isQuestActive() and nationID == earlyAccessController.getNationID()
    return hasEarlyAccess or nationID in techTreeEventsListener.getNations()
