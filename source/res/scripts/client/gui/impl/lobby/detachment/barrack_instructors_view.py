# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/detachment/barrack_instructors_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.barrack_instructors_view_model import BarrackInstructorsViewModel
from gui.impl.gen.view_models.views.lobby.detachment.tooltips.perk_tooltip_model import PerkTooltipModel
from gui.impl.lobby.detachment.instructors_view_base import InstructorsViewBase
from gui.impl.lobby.detachment.tooltips.instructor_tooltip import getInstructorTooltip
from gui.impl.lobby.detachment.popovers.filters import ToggleFilters
from gui.impl.lobby.detachment.popovers.filters.instructor_filters import defaultInstructorPopoverFilter, defaultInstructorToggleFilter
from gui.impl.lobby.detachment.tooltips.perk_tooltip import PerkTooltip
from uilogging.detachment.loggers import InstructorListLogger
from uilogging.detachment.constants import GROUP
from gui.ClientUpdateManager import g_clientUpdateManager
from items import ITEM_TYPES
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from gui.shared.utils.requesters import REQ_CRITERIA

class BarrackInstructorsView(InstructorsViewBase):
    _COUNTED_RESULT_FILTERS = (ToggleFilters.REMOVED,)
    _popoverFilters = defaultInstructorPopoverFilter()
    _toggleFilters = defaultInstructorToggleFilter()
    _itemsCache = dependency.descriptor(IItemsCache)
    uiLogger = InstructorListLogger(GROUP.INSTRUCTOR_BARRACKS)

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = BarrackInstructorsViewModel()
        super(BarrackInstructorsView, self).__init__(settings, ctx=ctx)

    @property
    def viewModel(self):
        return super(BarrackInstructorsView, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        if event.contentID == R.views.lobby.detachment.tooltips.PerkTooltip():
            perkId = event.getArgument('id')
            instructorID = event.getArgument('instructorId')
            return PerkTooltip(perkId, instructorInvID=instructorID, tooltipType=PerkTooltipModel.INSTRUCTOR_PERK_TOOLTIP)
        if contentID == R.views.lobby.detachment.tooltips.InstructorTooltip():
            instructorID = event.getArgument('instructorInvID')
            return getInstructorTooltip(instructorInvID=instructorID)
        return super(BarrackInstructorsView, self).createToolTipContent(event, contentID)

    def _addListeners(self):
        super(BarrackInstructorsView, self)._addListeners()
        g_clientUpdateManager.addCallbacks({'inventory.{}'.format(ITEM_TYPES.tankman): self._onClientUpdate})

    def _removeListeners(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        super(BarrackInstructorsView, self)._removeListeners()

    def _fillViewModel(self, model):
        super(BarrackInstructorsView, self)._fillViewModel(model)
        model.setIsRecruitsTabEnabled(bool(self._itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.REGULAR)))
